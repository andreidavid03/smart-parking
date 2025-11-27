import { Injectable, BadRequestException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class EntryService {
  constructor(private prisma: PrismaService) {}

  // eslint-disable-next-line @typescript-eslint/require-await, @typescript-eslint/no-unused-vars
  async reserveSpot(userEmail: string, preferenceType?: string) {
    // TODO: Update this service to match current Prisma schema
    // Current schema doesn't have: SpotStatus enum, SpotPreferenceType enum, spot.index, session.start
    // Need to add these fields to schema or refactor logic
    throw new BadRequestException('Entry service needs to be updated');

    /* Original code - commented until schema is updated
    const user = await this.prisma.user.findUnique({
      where: { email: userEmail },
    });
    if (!user) throw new BadRequestException('user not found');

    const result = await this.prisma.$transaction(async (tx) => {
      const spot = await tx.spot.findFirst({
        where: {
          status: SpotStatus.FREE,
          ...(preferenceType && {
            preference: preferenceType as SpotPreferenceType,
          }),
        },
        orderBy: { index: 'asc' },
      });
      if (!spot) throw new BadRequestException('no free spot available');

      await tx.spot.update({
        where: { id: spot.id },
        data: { status: SpotStatus.RESERVED },
      });

      const session = await tx.session.create({
        data: { userId: user.id, spotId: spot.id },
        select: { id: true, start: true },
      });

      return {
        spotId: spot.id,
        spotIndex: spot.index,
        sessionId: session.id,
        start: session.start,
      };
    });

    return { ok: true, ...result };
    */
  }
}
