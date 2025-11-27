import {
  Injectable,
  NotFoundException,
  BadRequestException,
} from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { randomBytes } from 'crypto';

@Injectable()
export class ParkingService {
  constructor(private prisma: PrismaService) {}

  // Helper function to calculate distance between two coordinates
  private calculateDistance(
    lat1: number,
    lng1: number,
    lat2: number,
    lng2: number,
  ): number {
    const R = 6371e3; // Earth radius in meters
    const φ1 = (lat1 * Math.PI) / 180;
    const φ2 = (lat2 * Math.PI) / 180;
    const Δφ = ((lat2 - lat1) * Math.PI) / 180;
    const Δλ = ((lng2 - lng1) * Math.PI) / 180;

    const a =
      Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
      Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c; // Distance in meters
  }

  async findBestSpot(userId: string) {
    const user = await this.prisma.user.findUnique({
      where: { id: userId },
    });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    const availableSpots = await this.prisma.spot.findMany({
      where: { status: 'available' },
    });

    if (availableSpots.length === 0) {
      throw new BadRequestException('No available spots');
    }

    // If user has specific spot preference and it's available
    if (user.spotPreferenceType === 'specific' && user.preferredSpot) {
      const preferredSpot = availableSpots.find(
        (spot) => spot.name === user.preferredSpot,
      );
      if (preferredSpot) {
        return preferredSpot;
      }
    }

    // For entrance/exit/shop preferences, need parking config
    if (
      user.spotPreferenceType === 'entrance' ||
      user.spotPreferenceType === 'exit' ||
      user.spotPreferenceType === 'shop'
    ) {
      const config = await this.prisma.parkingConfig.findFirst();

      if (config) {
        let targetLat: number;
        let targetLng: number;

        switch (user.spotPreferenceType) {
          case 'entrance':
            targetLat = config.entranceLat;
            targetLng = config.entranceLng;
            break;
          case 'exit':
            targetLat = config.exitLat;
            targetLng = config.exitLng;
            break;
          case 'shop':
            targetLat = config.shopLat;
            targetLng = config.shopLng;
            break;
        }

        // Filter spots that have coordinates
        const spotsWithCoordinates = availableSpots.filter(
          (spot) => spot.spotLat !== null && spot.spotLng !== null,
        );

        if (spotsWithCoordinates.length > 0) {
          // Calculate distances and find closest spot
          const spotsWithDistances = spotsWithCoordinates.map((spot) => ({
            spot,
            distance: this.calculateDistance(
              targetLat,
              targetLng,
              spot.spotLat as number,
              spot.spotLng as number,
            ),
          }));

          // Sort by distance and return closest
          spotsWithDistances.sort((a, b) => a.distance - b.distance);
          return spotsWithDistances[0].spot;
        }
        // If no spots have coordinates, fall through to default
      }
    }

    // Default: return first available spot
    return availableSpots[0];
  }

  async generateQRCode(email: string) {
    const user = await this.prisma.user.findUnique({
      where: { email },
    });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    // Generate unique QR code
    const qrCode = randomBytes(16).toString('hex');

    await this.prisma.user.update({
      where: { id: user.id },
      data: { qrCode },
    });

    return { qrCode, userId: user.id, email: user.email };
  }

  async scanQRCode(qrCode: string, spotId?: string) {
    const user = await this.prisma.user.findUnique({
      where: { qrCode },
      include: {
        sessions: {
          where: { endTime: null },
          orderBy: { startTime: 'desc' },
          take: 1,
        },
      },
    });

    if (!user) {
      throw new NotFoundException('Invalid QR code');
    }

    const activeSession = user.sessions[0];

    // If there's an active session, end it (exit)
    if (activeSession) {
      await this.prisma.session.update({
        where: { id: activeSession.id },
        data: { endTime: new Date() },
      });

      // Update spot status to available
      await this.prisma.spot.update({
        where: { id: activeSession.spotId },
        data: { status: 'available' },
      });

      return {
        action: 'exit',
        message: 'Parking session ended',
        session: await this.prisma.session.findUnique({
          where: { id: activeSession.id },
          include: { spot: true },
        }),
      };
    }

    // If no active session, start one (entrance)
    // Use smart allocation if no specific spot is provided
    let targetSpot: { id: string; status: string } | null = null;

    if (spotId) {
      targetSpot = await this.prisma.spot.findUnique({
        where: { id: spotId },
      });

      if (!targetSpot) {
        throw new NotFoundException('Spot not found');
      }

      if (targetSpot.status !== 'available') {
        throw new BadRequestException('Spot is not available');
      }
    } else {
      // Smart allocation based on user preferences
      targetSpot = await this.findBestSpot(user.id);
    }

    if (!targetSpot) {
      throw new BadRequestException('No available spot found');
    }

    const newSession = await this.prisma.session.create({
      data: {
        userId: user.id,
        spotId: targetSpot.id,
      },
      include: { spot: true },
    });

    // Update spot status to occupied
    await this.prisma.spot.update({
      where: { id: targetSpot.id },
      data: { status: 'occupied' },
    });

    return {
      action: 'entrance',
      message: 'Parking session started',
      session: newSession,
      allocatedSpot: targetSpot,
    };
  }

  async getCurrentSession(email: string) {
    const user = await this.prisma.user.findUnique({
      where: { email },
      include: {
        sessions: {
          where: { endTime: null },
          orderBy: { startTime: 'desc' },
          take: 1,
          include: { spot: true },
        },
      },
    });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    return {
      hasActiveSession: user.sessions.length > 0,
      session: user.sessions[0] || null,
      qrCode: user.qrCode,
    };
  }
}
