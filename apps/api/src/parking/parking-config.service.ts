import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class ParkingConfigService {
  constructor(private prisma: PrismaService) {}

  async getConfig() {
    // Get the first (and only) config, or create if doesn't exist
    let config = await this.prisma.parkingConfig.findFirst();

    if (!config) {
      config = await this.prisma.parkingConfig.create({
        data: {
          entranceLat: 37.7749,
          entranceLng: -122.4194,
          exitLat: 37.775,
          exitLng: -122.4195,
          shopLat: 37.7751,
          shopLng: -122.4196,
        },
      });
    }

    return config;
  }

  async updateConfig(data: {
    entranceLat: number;
    entranceLng: number;
    exitLat: number;
    exitLng: number;
    shopLat: number;
    shopLng: number;
  }) {
    // Always update the first config (or create if doesn't exist)
    const existing = await this.prisma.parkingConfig.findFirst();

    if (existing) {
      return this.prisma.parkingConfig.update({
        where: { id: existing.id },
        data,
      });
    } else {
      return this.prisma.parkingConfig.create({ data });
    }
  }
}
