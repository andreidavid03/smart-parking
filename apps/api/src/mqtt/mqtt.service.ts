import {
  Injectable,
  Logger,
  OnModuleDestroy,
  OnModuleInit,
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

  constructor(
    private readonly prisma: PrismaService,
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

  private async handleMessage(topic: string, payload: string) {
    if (topic.startsWith('parking/sensor/')) {
      await this.handleSensorUpdate(topic, payload);
    } else if (topic === 'parking/scan') {
      await this.handleBarrierScan(payload);
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
    this.client.publish('parking/status', JSON.stringify(spots));
  }
}
