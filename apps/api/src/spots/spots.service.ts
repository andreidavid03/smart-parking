import { Injectable } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

@Injectable()
export class SpotsService {
  async findAll() {
    return prisma.spot.findMany({
      orderBy: { name: 'asc' },
    });
  }

  async create(name: string) {
    return prisma.spot.create({
      data: {
        name,
        status: 'available',
      },
    });
  }

  async updateStatus(id: string, status: string) {
    return prisma.spot.update({
      where: { id },
      data: { status },
    });
  }

  async updateCoordinates(id: string, spotLat: number, spotLng: number) {
    return prisma.spot.update({
      where: { id },
      data: { spotLat, spotLng },
    });
  }

  async delete(id: string) {
    return prisma.spot.delete({
      where: { id },
    });
  }
}
