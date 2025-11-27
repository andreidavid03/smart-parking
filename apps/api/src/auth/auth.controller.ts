import { Controller, Post, Body, Get, Patch, Query } from '@nestjs/common';
import { AuthService } from './auth.service';

@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Post('signup')
  signup(@Body() body: { email: string; password: string }) {
    return this.authService.signup(body.email, body.password);
  }

  @Post('login')
  login(@Body() body: { email: string; password: string }) {
    return this.authService.login(body.email, body.password);
  }

  @Get('verify-email')
  verifyEmail(@Query('token') token: string) {
    return this.authService.verifyEmail(token);
  }

  @Post('forgot-password')
  forgotPassword(@Body() body: { email: string }) {
    return this.authService.forgotPassword(body.email);
  }

  @Post('reset-password')
  resetPassword(@Body() body: { token: string; newPassword: string }) {
    return this.authService.resetPassword(body.token, body.newPassword);
  }

  @Post('logout')
  logout() {
    return { message: 'Logged out successfully' };
  }

  @Post('update-car-color')
  updateCarColor(@Body() body: { email: string; carColor: string }) {
    return this.authService.updateCarColor(body.email, body.carColor);
  }

  @Post('set-preferred-spot')
  setPreferredSpot(
    @Body() body: { email: string; preferredSpot: string | null },
  ) {
    return this.authService.setPreferredSpot(body.email, body.preferredSpot);
  }

  @Post('profile')
  getUserProfile(@Body() body: { email: string }) {
    return this.authService.getUserProfile(body.email);
  }

  @Get('profile')
  getProfile(@Query('email') email: string) {
    return this.authService.getUserProfile(email);
  }

  @Patch('update-preference')
  updatePreference(
    @Body()
    body: {
      email: string;
      spotPreferenceType: string;
      preferredSpot?: string;
    },
  ) {
    return this.authService.updatePreference(
      body.email,
      body.spotPreferenceType,
      body.preferredSpot,
    );
  }

  @Patch('update-car-color')
  updateCarColorPatch(@Body() body: { email: string; carColor: string }) {
    return this.authService.updateCarColor(body.email, body.carColor);
  }
}
