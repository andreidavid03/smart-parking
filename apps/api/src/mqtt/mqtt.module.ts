import { Module, forwardRef } from '@nestjs/common';
import { MqttService } from './mqtt.service';
import { ParkingModule } from '../parking/parking.module';

@Module({
  imports: [forwardRef(() => ParkingModule)],
  providers: [MqttService],
  exports: [MqttService],
})
export class MqttModule {}
