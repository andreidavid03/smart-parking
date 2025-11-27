import { Controller, Post, Body } from '@nestjs/common';
import { ParkingService } from './parking.service';

@Controller('parking')
export class ParkingController {
  constructor(private readonly parkingService: ParkingService) {}

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
}
