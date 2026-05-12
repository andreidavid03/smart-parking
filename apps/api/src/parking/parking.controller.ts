import {
  BadRequestException,
  Controller,
  Get,
  Inject,
  Post,
  Body,
  forwardRef,
} from '@nestjs/common';
import { ParkingService } from './parking.service';
import { MqttService } from '../mqtt/mqtt.service';

@Controller('parking')
export class ParkingController {
  constructor(
    private readonly parkingService: ParkingService,
    @Inject(forwardRef(() => MqttService))
    private readonly mqttService: MqttService,
  ) {}

  @Post('generate-qr')
  async generateQR(@Body('email') email: string) {
    return this.parkingService.generateQRCode(email);
  }

  @Post('scan-qr')
  async scanQR(
    @Body('qrCode') qrCode: string,
    @Body('spotId') spotId?: string,
  ) {
    return this.parkingService.scanQRCode(qrCode, spotId);
  }

  @Post('current-session')
  async getCurrentSession(@Body('email') email: string) {
    return this.parkingService.getCurrentSession(email);
  }

  /**
   * POST /parking/hardware-scan
   * Body: { "qrCode": "<raw scanned string>" }
   *
   * Called by the PC-side script that captures input from the GM65 USB HID
   * QR scanner. Validates the code, runs smart spot allocation, then publishes
   * the hardware command to the ESP32 via MQTT (parking/commands).
   */
  @Get('admin-status')
  async getAdminStatus() {
    const status = await this.parkingService.getAdminStatus();
    return {
      ...status,
      mqttConnected: this.mqttService.isConnected,
      environment: this.mqttService.environmentData,
      speed: this.mqttService.speedData,
      diagnostics: this.mqttService.diagnosticsData,
    };
  }

  /**
   * POST /parking/mock-sensor
   * Body: { "spotName": "A1", "status": "occupied" | "available" }
   *
   * Simulates a hardware ultrasonic/IR sensor event from the dashboard.
   * Publishes to parking/sensor/<spotName>, which the MqttService subscriber
   * picks up and persists to the DB — identical to a real sensor event.
   */
  @Post('last-session')
  async getLastSession(@Body('email') email: string) {
    return this.parkingService.getLastSession(email);
  }

  @Get('mqtt-log')
  getMqttLog(): {
    log: Array<{
      time: string;
      direction: string;
      topic: string;
      payload: string;
    }>;
  } {
    return { log: this.mqttService.mqttLog };
  }

  @Get('alerts')
  getAlerts() {
    return {
      alerts: this.mqttService.alerts,
      unread: this.mqttService.unreadAlertsCount,
    };
  }

  @Post('alerts/read')
  markAlertsRead() {
    this.mqttService.markAlertsRead();
    return { ok: true };
  }

  @Post('alerts/mock')
  addMockAlerts() {
    this.mqttService.addMockAlerts();
    return { ok: true, message: 'Mock alerts added' };
  }

  @Post('mock-sensor')
  mockSensor(
    @Body('spotName') spotName: string,
    @Body('status') status: string,
  ) {
    if (!spotName?.trim()) {
      throw new BadRequestException('spotName is required');
    }
    if (status !== 'occupied' && status !== 'available') {
      throw new BadRequestException('status must be "occupied" or "available"');
    }
    this.mqttService.publishSensorUpdate(spotName.trim(), status);
    return { ok: true, spotName: spotName.trim(), status };
  }

  @Post('hardware-scan')
  async hardwareScan(@Body('qrCode') qrCode: string) {
    if (!qrCode?.trim()) {
      throw new BadRequestException('qrCode is required');
    }

    const result = await this.parkingService.scanQRCode(qrCode.trim());

    if (result.action === 'entrance') {
      // session is created with { include: { spot: true } } in scanQRCode
      const session = result.session as { spot: { name: string } } | null;
      const spotName = session?.spot?.name ?? '';
      this.mqttService.publishCommand({
        command: 'OPEN_ENTRY',
        spot: spotName,
      });
    } else {
      // exit — include spot so ESP32 can turn off the LED
      const session = result.session as { spot: { name: string } } | null;
      const spotName = session?.spot?.name ?? '';
      this.mqttService.publishCommand({ command: 'OPEN_EXIT', spot: spotName });
    }

    return result;
  }

  /**
   * POST /parking/exit
   * Body: { "email": "<user email>" }
   *
   * Called when the camera detects the car at the exit barrier and the user
   * (or admin) presses Exit. Ends the active session, calculates the cost,
   * and sends OPEN_EXIT via MQTT to open the barrier.
   */
  @Post('exit')
  async exitParking(@Body('email') email: string) {
    if (!email?.trim()) {
      throw new BadRequestException('email is required');
    }
    const result = await this.parkingService.exitSession(email.trim());
    this.mqttService.publishCommand({ command: 'OPEN_EXIT', spot: result.spotName });
    return result;
  }

  @Post('history')
  async getSessionHistory(@Body('email') email: string) {
    if (!email?.trim()) {
      throw new BadRequestException('email is required');
    }
    return this.parkingService.getSessionHistory(email.trim());
  }

  /**
   * POST /parking/open-barrier
   * Body: { "command": "OPEN_ENTRY" | "OPEN_EXIT" }
   *
   * Admin-only shortcut to manually trigger a barrier open command.
   * Used by the web dashboard bypass buttons.
   */
  @Post('open-barrier')
  openBarrier(@Body('command') command: string) {
    if (command !== 'OPEN_ENTRY' && command !== 'OPEN_EXIT') {
      throw new BadRequestException('command must be OPEN_ENTRY or OPEN_EXIT');
    }
    this.mqttService.publishCommand({ command });
    return { ok: true, command };
  }

  /**
   * POST /parking/reserve-spot
   * Body: { "email": "<user email>", "spotName": "A1" }
   *
   * Sends RESERVE_SPOT MQTT command → LED turns BLUE on the physical model.
   * Does not change DB status (no migration needed for demo).
   */
  @Post('reserve-spot')
  async reserveSpot(
    @Body('email') email: string,
    @Body('spotName') spotName: string,
  ) {
    if (!email?.trim()) throw new BadRequestException('email is required');
    if (!spotName?.trim()) throw new BadRequestException('spotName is required');

    const validSpots = ['A1','A2','A3','A4','A5','B1','B2','B3','B4','B5'];
    if (!validSpots.includes(spotName.trim().toUpperCase())) {
      throw new BadRequestException('Invalid spot name. Valid spots: A1-A5, B1-B5');
    }

    const spot = await this.parkingService.getSpotByName(spotName.trim().toUpperCase());
    if (!spot) throw new BadRequestException('Spot not found');
    if (spot.status !== 'available') {
      throw new BadRequestException('Spot is not available');
    }

    this.mqttService.publishCommand({ command: 'RESERVE_SPOT', spot: spotName.trim().toUpperCase() });
    return { ok: true, spotName: spotName.trim().toUpperCase(), message: 'Spot reserved — LED turned blue' };
  }

  /**
   * POST /parking/cancel-reservation
   * Body: { "spotName": "A1" }
   *
   * Sends CANCEL_RESERVATION MQTT command → LED turns back GREEN.
   */
  @Post('cancel-reservation')
  cancelReservation(@Body('spotName') spotName: string) {
    if (!spotName?.trim()) throw new BadRequestException('spotName is required');

    this.mqttService.publishCommand({ command: 'CANCEL_RESERVATION', spot: spotName.trim().toUpperCase() });
    return { ok: true, spotName: spotName.trim().toUpperCase(), message: 'Reservation cancelled — LED turned green' };
  }
}
