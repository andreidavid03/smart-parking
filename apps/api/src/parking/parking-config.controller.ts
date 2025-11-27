import { Controller, Get, Post, Body } from '@nestjs/common';
import { ParkingConfigService } from './parking-config.service';

@Controller('parking/config')
export class ParkingConfigController {
  constructor(private readonly configService: ParkingConfigService) {}

  @Get()
  getConfig() {
    return this.configService.getConfig();
  }

  @Post()
  updateConfig(
    @Body()
    body: {
      entranceLat: number;
      entranceLng: number;
      exitLat: number;
      exitLng: number;
      shopLat: number;
      shopLng: number;
    },
  ) {
    return this.configService.updateConfig(body);
  }
}
