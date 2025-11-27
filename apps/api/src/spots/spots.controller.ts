import {
  Controller,
  Get,
  Post,
  Delete,
  Patch,
  Param,
  Body,
} from '@nestjs/common';
import { SpotsService } from './spots.service';

@Controller('spots')
export class SpotsController {
  constructor(private readonly spotsService: SpotsService) {}

  @Get()
  findAll() {
    return this.spotsService.findAll();
  }

  @Post()
  create(@Body('name') name: string) {
    return this.spotsService.create(name);
  }

  @Patch(':id')
  updateStatus(@Param('id') id: string, @Body('status') status: string) {
    return this.spotsService.updateStatus(id, status);
  }

  @Patch(':id/coordinates')
  updateCoordinates(
    @Param('id') id: string,
    @Body('spotLat') spotLat: number,
    @Body('spotLng') spotLng: number,
  ) {
    return this.spotsService.updateCoordinates(id, spotLat, spotLng);
  }

  @Delete(':id')
  delete(@Param('id') id: string) {
    return this.spotsService.delete(id);
  }
}
