import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { HealthController } from './health/health.controller';
import { SpotsModule } from './spots/spots.module';
import { PrismaModule } from './prisma/pristma.module';
import { EntryModule } from './entry/entry.module';
import { AuthModule } from './auth/auth.module';
import { ParkingModule } from './parking/parking.module';

@Module({
  imports: [
    ConfigModule.forRoot(),
    PrismaModule,
    SpotsModule,
    EntryModule,
    AuthModule,
    ParkingModule,
  ],
  controllers: [HealthController],
  providers: [],
})
export class AppModule {}
