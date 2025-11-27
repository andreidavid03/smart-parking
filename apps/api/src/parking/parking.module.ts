import { Module } from '@nestjs/common';
import { ParkingController } from './parking.controller';
import { ParkingService } from './parking.service';
import { ParkingConfigController } from './parking-config.controller';
import { ParkingConfigService } from './parking-config.service';
import { PrismaModule } from '../prisma/pristma.module';

@Module({
  imports: [PrismaModule],
  controllers: [ParkingController, ParkingConfigController],
  providers: [ParkingService, ParkingConfigService],
})
export class ParkingModule {}
