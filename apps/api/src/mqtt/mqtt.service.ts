import {
  Inject,
  Injectable,
  Logger,
  OnModuleDestroy,
  OnModuleInit,
  forwardRef,
} from '@nestjs/common';
import { connect, MqttClient } from 'mqtt';
import { PrismaService } from '../prisma/prisma.service';
import { ParkingService } from '../parking/parking.service';

/**
 * MQTT Integration Service
 *
 * Subscribed topics (hardware → backend):
 *   parking/sensor/<spot_name>   payload: "occupied" | "available"
 *     → Physical ultrasonic/IR sensor detected a car entering or leaving a spot.
 *     Example: topic "parking/sensor/A1", payload "occupied"
 *
 *   parking/scan                 payload: "<qrCode>"
 *     → A physical QR scanner at the barrier scanned a user QR code.
 *     The backend resolves the code to a check-in or check-out action.
 *
 * Published topics (backend → hardware):
 *   parking/status               payload: JSON array of { name, status } for all spots
 *     → Sent whenever any spot status changes so displays/barriers stay in sync.
 */
@Injectable()
export class MqttService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(MqttService.name);
  private client: MqttClient;
  private readonly _mqttLog: Array<{
    time: string;
    direction: 'in' | 'out';
    topic: string;
    payload: string;
  }> = [];

  private _lastEnvironment: {
    temp?: number;
    humidity?: number;
    pressure?: number;
    bmp_temp?: number;
    gas1?: number;
    gas2?: number;
    flame1?: boolean;
    flame2?: boolean;
    updatedAt?: string;
  } | null = null;

  private _lastSpeed: {
    speed_kmh?: number;
    elapsed_ms?: number;
    updatedAt?: string;
  } | null = null;

  private _lastDiagnostics: Record<string, unknown> | null = null;

  // ─── Alerts store ───────────────────────────────────────────────────────────
  private _alerts: Array<{
    id: string;
    type: 'speed' | 'temperature' | 'flame' | 'gas';
    severity: 'warning' | 'critical';
    title: string;
    detail: string;
    value: number | null;
    threshold: number | null;
    timestamp: string;
    read: boolean;
  }> = [];

  private _alertCounter = 0;

  private _pushAlert(
    type: 'speed' | 'temperature' | 'flame' | 'gas',
    severity: 'warning' | 'critical',
    title: string,
    detail: string,
    value: number | null = null,
    threshold: number | null = null,
  ) {
    this._alerts.unshift({
      id: `alert-${++this._alertCounter}-${Date.now()}`,
      type,
      severity,
      title,
      detail,
      value,
      threshold,
      timestamp: new Date().toISOString(),
      read: false,
    });
    if (this._alerts.length > 200) this._alerts.pop();
    this.logger.warn(`[ALERT] ${title}: ${detail}`);
    // Trigger buzzer on ESP32 for critical alerts (flame, gas, speed)
    if (severity === 'critical' && this.client?.connected) {
      this.publishCommand({ command: 'ALERT_BUZZER' });
    }
  }

  get alerts() {
    return [...this._alerts];
  }

  get unreadAlertsCount() {
    return this._alerts.filter((a) => !a.read).length;
  }

  markAlertsRead() {
    this._alerts.forEach((a) => (a.read = true));
  }

  addMockAlerts() {
    const now = new Date();
    const t = (offsetSec: number) =>
      new Date(now.getTime() - offsetSec * 1000).toISOString();

    this._pushAlertRaw({ id: `mock-${++this._alertCounter}`, type: 'speed',       severity: 'critical', title: '🚨 Viteză depășită',          detail: '34.2 km/h (limita 10 km/h)',           value: 34.2, threshold: 10,  timestamp: t(15),  read: false });
    this._pushAlertRaw({ id: `mock-${++this._alertCounter}`, type: 'temperature',  severity: 'warning',  title: '🌡️ Temperatură ridicată',       detail: '43.5°C (prag 40°C)',                  value: 43.5, threshold: 40,  timestamp: t(45),  read: false });
    this._pushAlertRaw({ id: `mock-${++this._alertCounter}`, type: 'flame',        severity: 'critical', title: '🔥 Flacără detectată',           detail: 'Senzor flacără 1 activ',              value: null, threshold: null, timestamp: t(90),  read: false });
    this._pushAlertRaw({ id: `mock-${++this._alertCounter}`, type: 'gas',          severity: 'warning',  title: '💨 Nivel gaz ridicat',           detail: 'MQ-4 #1: 820 (prag 700)',             value: 820,  threshold: 700, timestamp: t(180), read: false });
    this._pushAlertRaw({ id: `mock-${++this._alertCounter}`, type: 'speed',        severity: 'warning',  title: '⚠️ Viteză ridicată',             detail: '18.7 km/h (limita 10 km/h)',           value: 18.7, threshold: 10,  timestamp: t(300), read: true  });
    this._pushAlertRaw({ id: `mock-${++this._alertCounter}`, type: 'temperature',  severity: 'warning',  title: '🌡️ Temperatură ridicată',       detail: '36.1°C (prag 35°C)',                  value: 36.1, threshold: 35,  timestamp: t(600), read: true  });
  }

  private _pushAlertRaw(alert: typeof this._alerts[0]) {
    this._alerts.unshift(alert);
    if (this._alerts.length > 200) this._alerts.pop();
  }

  get mqttLog() {
    return [...this._mqttLog];
  }

  get environmentData() {
    return this._lastEnvironment;
  }

  get speedData() {
    return this._lastSpeed;
  }

  get diagnosticsData() {
    return this._lastDiagnostics;
  }

  private _logMqtt(direction: 'in' | 'out', topic: string, payload: string) {
    this._mqttLog.unshift({
      time: new Date().toISOString(),
      direction,
      topic,
      payload: payload.length > 300 ? payload.slice(0, 300) + '…' : payload,
    });
    if (this._mqttLog.length > 100) this._mqttLog.pop();
  }

  constructor(
    private readonly prisma: PrismaService,
    @Inject(forwardRef(() => ParkingService))
    private readonly parkingService: ParkingService,
  ) {}

  onModuleInit() {
    const brokerUrl = process.env.MQTT_BROKER_URL ?? 'mqtt://localhost:1883';
    this.client = connect(brokerUrl, { clientId: 'smart-parking-api' });

    this.client.on('connect', () => {
      this.logger.log(`Connected to MQTT broker at ${brokerUrl}`);
      this.client.subscribe('parking/sensor/+', (err) => {
        if (err) this.logger.error('Failed to subscribe to sensor topics', err);
        else this.logger.log('Subscribed to parking/sensor/+');
      });
      this.client.subscribe('parking/scan', (err) => {
        if (err) this.logger.error('Failed to subscribe to parking/scan', err);
        else this.logger.log('Subscribed to parking/scan');
      });
      this.client.subscribe('parking/environment', (err) => {
        if (err)
          this.logger.error('Failed to subscribe to parking/environment', err);
        else this.logger.log('Subscribed to parking/environment');
      });
      this.client.subscribe('parking/speed', (err) => {
        if (err)
          this.logger.error('Failed to subscribe to parking/speed', err);
        else this.logger.log('Subscribed to parking/speed');
      });
      this.client.subscribe('parking/diagnostics', (err) => {
        if (err)
          this.logger.error('Failed to subscribe to parking/diagnostics', err);
        else this.logger.log('Subscribed to parking/diagnostics');
      });
    });

    this.client.on('message', (topic, message) => {
      void this.handleMessage(topic, message.toString());
    });

    this.client.on('error', (err) => {
      this.logger.error('MQTT client error', err);
    });
  }

  onModuleDestroy() {
    this.client?.end();
  }

  get isConnected(): boolean {
    return this.client?.connected ?? false;
  }

  private async handleMessage(topic: string, payload: string) {
    this._logMqtt('in', topic, payload);
    if (topic.startsWith('parking/sensor/')) {
      await this.handleSensorUpdate(topic, payload);
    } else if (topic === 'parking/scan') {
      await this.handleBarrierScan(payload);
    } else if (topic === 'parking/environment') {
      this.handleEnvironmentUpdate(payload);
    } else if (topic === 'parking/speed') {
      this.handleSpeedUpdate(payload);
    } else if (topic === 'parking/diagnostics') {
      try {
        this._lastDiagnostics = {
          ...(JSON.parse(payload) as Record<string, unknown>),
          updatedAt: new Date().toISOString(),
        };
      } catch {
        this.logger.warn(`Failed to parse diagnostics payload: ${payload}`);
      }
    }
  }

  private handleSpeedUpdate(payload: string) {
    try {
      const data = JSON.parse(payload) as { speed_kmh?: number; elapsed_ms?: number };
      this._lastSpeed = { ...data, updatedAt: new Date().toISOString() };
      this.logger.log(`Speed update: ${data.speed_kmh ?? '?'} km/h`);
      // Speed alerts disabled — IR beam distance on scale model causes
      // unrealistic readings (e.g. 360 km/h). Use demo trigger instead.
    } catch {
      this.logger.warn(`Failed to parse speed payload: ${payload}`);
    }
  }

  /** Camera confirmation mock: 'correct' logs silently; 'wrong' fires a critical alert */
  cameraConfirmAlert(spotName: string, result: 'correct' | 'wrong') {
    if (result === 'wrong') {
      this._pushAlertRaw({
        id: `cam-${++this._alertCounter}-${Date.now()}`,
        type: 'camera' as 'speed',
        severity: 'critical',
        title: '📷 Mașină neautorizată detectată',
        detail: `Camera a detectat o mașină nepotrivită pe locul ${spotName}`,
        value: null,
        threshold: null,
        timestamp: new Date().toISOString(),
        read: false,
      });
      if (this.client?.connected) {
        this.publishCommand({ command: 'ALERT_BUZZER' });
      }
      this.logger.warn(`[CAMERA ALERT] Wrong car on spot ${spotName}`);
    } else {
      if (this.client?.connected) {
        this.publishCommand({ command: 'CONFIRM_BEEP', spot: spotName });
      }
      this.logger.log(`[CAMERA OK] Spot ${spotName} confirmed correct — CONFIRM_BEEP sent`);
    }
  }

  /** Trigger a demo alert with realistic values and activate ALERT_BUZZER */
  triggerDemoAlert(type: 'speed' | 'flame' | 'gas' | 'temperature') {
    if (type === 'speed') {
      this._pushAlert('speed', 'critical', '🚨 Viteză depășită', '28.5 km/h (limita 10 km/h)', 28.5, 10);
    } else if (type === 'flame') {
      this._pushAlert('flame', 'critical', '🔥 Flacără detectată', 'Senzor flacără 1 activ');
    } else if (type === 'gas') {
      this._pushAlert('gas', 'critical', '💨 Nivel gaz ridicat', 'MQ-4 #1: 1050 (prag 1000)', 1050, 1000);
    } else if (type === 'temperature') {
      this._pushAlert('temperature', 'critical', '🌡️ Temperatură critică', '42.0°C (prag 40°C)', 42.0, 40);
    }
  }

  private handleEnvironmentUpdate(payload: string) {
    try {
      const data = JSON.parse(payload) as typeof this._lastEnvironment;
      this._lastEnvironment = { ...data, updatedAt: new Date().toISOString() };
      this.logger.debug(`Environment update: ${payload}`);

      // Temperature alert
      const temp = (data as { temp?: number })?.temp ?? null;
      if (temp !== null && temp > 35) {
        this._pushAlert(
          'temperature',
          temp > 40 ? 'critical' : 'warning',
          temp > 40 ? '🌡️ Temperatură critică' : '🌡️ Temperatură ridicată',
          `${temp.toFixed(1)}°C (prag ${temp > 40 ? 40 : 35}°C)`,
          temp,
          temp > 40 ? 40 : 35,
        );
      }

      // Flame alerts
      const d = data as { flame1?: boolean; flame2?: boolean; gas1?: number; gas2?: number };
      if (d.flame1 === true) {
        this._pushAlert('flame', 'critical', '🔥 Flacără detectată', 'Senzor flacără 1 activ');
      }
      if (d.flame2 === true) {
        this._pushAlert('flame', 'critical', '🔥 Flacără detectată', 'Senzor flacără 2 activ');
      }

      // Gas alerts
      if ((d.gas1 ?? 0) > 700) {
        this._pushAlert('gas', d.gas1! > 1000 ? 'critical' : 'warning', '💨 Nivel gaz ridicat', `MQ-4 #1: ${d.gas1} (prag 700)`, d.gas1!, 700);
      }
      if ((d.gas2 ?? 0) > 700) {
        this._pushAlert('gas', d.gas2! > 1000 ? 'critical' : 'warning', '💨 Nivel gaz ridicat', `MQ-4 #2: ${d.gas2} (prag 700)`, d.gas2!, 700);
      }
    } catch {
      this.logger.warn(`Failed to parse environment payload: ${payload}`);
    }
  }

  /** Hardware sensor reported a spot status change */
  private async handleSensorUpdate(topic: string, payload: string) {
    const spotName = topic.split('/')[2]; // e.g. "A1"
    const status = payload.trim().toLowerCase();

    if (status !== 'occupied' && status !== 'available') {
      this.logger.warn(`Unknown payload "${payload}" on topic ${topic}`);
      return;
    }

    const spot = await this.prisma.spot.findUnique({
      where: { name: spotName },
    });
    if (!spot) {
      this.logger.warn(`Received sensor update for unknown spot "${spotName}"`);
      return;
    }

    await this.prisma.spot.update({
      where: { name: spotName },
      data: { status },
    });

    this.logger.log(`Sensor update: ${spotName} → ${status}`);
    await this.publishAllSpotStatuses();

    // Notify ESP32 to update LED + beep when camera detects a vehicle
    if (this.client?.connected) {
      const cmd = status === 'occupied'
        ? { command: 'VEHICLE_DETECTED', spot: spotName }
        : { command: 'VEHICLE_LEFT',    spot: spotName };
      this.publishCommand(cmd);
    }
  }

  /** Physical QR scanner at the barrier scanned a user QR code */
  private async handleBarrierScan(qrCode: string) {
    const code = qrCode.trim();
    if (!code) return;

    try {
      const result = await this.parkingService.scanQRCode(code);
      this.logger.log(`Barrier scan (${result.action}): ${code}`);
      await this.publishAllSpotStatuses();

      // Optionally notify the barrier about the action result
      this.client.publish(
        'parking/barrier/response',
        JSON.stringify({ action: result.action, message: result.message }),
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      this.logger.error(`Barrier scan failed for QR "${code}": ${message}`);
      this.client.publish(
        'parking/barrier/response',
        JSON.stringify({ action: 'error', message }),
      );
    }
  }

  /** Publish the current status of all spots so hardware displays stay in sync */
  async publishAllSpotStatuses() {
    const spots = await this.prisma.spot.findMany({
      select: { name: true, status: true },
      orderBy: { name: 'asc' },
    });
    const payload = JSON.stringify(spots);
    this.client.publish('parking/status', payload);
    this._logMqtt('out', 'parking/status', payload);
  }

  /**
   * Publish a command to the hardware controller.
   * Topic: parking/commands
   * Example payload: { command: 'OPEN_ENTRY', spot: 'A1' }
   */
  publishCommand(payload: object): void {
    const msg = JSON.stringify(payload);
    this.client.publish('parking/commands', msg);
    this._logMqtt('out', 'parking/commands', msg);
    this.logger.log(`Published to parking/commands: ${msg}`);
  }

  /**
   * Simulate a hardware ultrasonic/IR sensor event.
   * Publishes to parking/sensor/<spotName> — the subscriber above picks it up
   * and updates the DB, exactly like a real sensor would.
   */
  publishSensorUpdate(
    spotName: string,
    status: 'occupied' | 'available',
  ): void {
    this.client.publish(`parking/sensor/${spotName}`, status);
    this._logMqtt('out', `parking/sensor/${spotName}`, status);
    this.logger.log(`Simulated sensor: ${spotName} → ${status}`);
  }
}
