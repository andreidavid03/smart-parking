import { BadRequestException, Body, Controller, Post } from '@nestjs/common';
import { EntryService } from './entry.service';

type EntryScanBody = {
  userEmail: string;
  qrCode?: string;
  preferenceType?: string;
};

@Controller('entry')
export class EntryController {
  constructor(private entryService: EntryService) {}

  @Post('scan')
  async scan(@Body() body: EntryScanBody) {
    if (!body?.userEmail)
      throw new BadRequestException('userEmail is required');
    return this.entryService.reserveSpot(body.userEmail, body.preferenceType);
  }
}
