import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

@Injectable()
export class PrismaService
  extends PrismaClient
  implements OnModuleInit, OnModuleDestroy
{
  async onModuleInit() {
    // Prisma connects lazily on first query — avoid eager connect that crashes if DB isn't ready yet
  }
  async onModuleDestroy() {
    await this.$disconnect();
  }
}
