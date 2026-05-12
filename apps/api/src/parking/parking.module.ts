import { Module, forwardRef } from '@nestjs/common';
import { ParkingController } from './parking.controller';
import { ParkingService } from './parking.service';
import { ParkingConfigController } from './parking-config.controller';
import { ParkingConfigService } from './parking-config.service';
import { PrismaModule } from '../prisma/pristma.module';
import { MqttModule } from '../mqtt/mqtt.module';

@Module({
  imports: [PrismaModule, forwardRef(() => MqttModule)],
  controllers: [ParkingController, ParkingConfigController],
  providers: [ParkingService, ParkingConfigService],
  exports: [ParkingService],
})
export class ParkingModule {}
