import { Module } from '@nestjs/common';
import { EntryController } from './entry.controller';
import { EntryService } from './entry.service';
import { PrismaService } from '../prisma/prisma.service';

@Module({
  controllers: [EntryController],
  providers: [EntryService, PrismaService],
})
export class EntryModule {}
