import {
  Injectable,
  UnauthorizedException,
  ConflictException,
  NotFoundException,
  BadRequestException,
} from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { EmailService } from '../email/email.service';
import * as bcrypt from 'bcrypt';
import { randomBytes } from 'crypto';

@Injectable()
export class AuthService {
  constructor(
    private prisma: PrismaService,
    private emailService: EmailService,
  ) {}

  async signup(email: string, password: string) {
    // Check if user already exists
    const existingUser = await this.prisma.user.findUnique({
      where: { email },
    });

    if (existingUser) {
      throw new ConflictException('Email already in use');
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const verificationToken = randomBytes(32).toString('hex');

    await this.prisma.user.create({
      data: {
        email,
        password: hashedPassword,
        emailVerified: false,
        verificationToken,
      },
    });

    await this.emailService.sendVerificationEmail(email, verificationToken);

    return {
      message:
        'Signup successful. Please check your email to verify your account.',
    };
  }

  async login(email: string, password: string) {
    const user = await this.prisma.user.findUnique({ where: { email } });
    if (!user) {
      throw new UnauthorizedException('Invalid credentials');
    }

    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      throw new UnauthorizedException('Invalid credentials');
    }

    if (!user.emailVerified) {
      throw new UnauthorizedException(
        'Please verify your email before logging in',
      );
    }

    return {
      message: 'Login successful',
      role: user.role,
    };
  }

  async verifyEmail(token: string) {
    const user = await this.prisma.user.findUnique({
      where: { verificationToken: token },
    });

    if (!user) {
      throw new UnauthorizedException('Invalid or expired token');
    }

    await this.prisma.user.update({
      where: { id: user.id },
      data: {
        emailVerified: true,
        verificationToken: null,
      },
    });

    return { message: 'Email verified successfully! You can now login.' };
  }

  async forgotPassword(email: string) {
    const user = await this.prisma.user.findUnique({ where: { email } });

    if (!user) {
      throw new NotFoundException('User with this email does not exist');
    }

    // Generate reset token and expiry (1 hour from now)
    const resetToken = randomBytes(32).toString('hex');
    const resetExpires = new Date(Date.now() + 3600000); // 1 hour

    await this.prisma.user.update({
      where: { id: user.id },
      data: {
        resetPasswordToken: resetToken,
        resetPasswordExpires: resetExpires,
      },
    });

    await this.emailService.sendPasswordResetEmail(email, resetToken);

    return {
      message: 'Password reset link has been sent to your email',
    };
  }

  async resetPassword(token: string, newPassword: string) {
    const user = await this.prisma.user.findUnique({
      where: { resetPasswordToken: token },
    });

    if (!user) {
      throw new BadRequestException('Invalid or expired reset token');
    }

    // Check if token is expired
    if (user.resetPasswordExpires && user.resetPasswordExpires < new Date()) {
      throw new BadRequestException('Reset token has expired');
    }

    const hashedPassword = await bcrypt.hash(newPassword, 10);

    await this.prisma.user.update({
      where: { id: user.id },
      data: {
        password: hashedPassword,
        resetPasswordToken: null,
        resetPasswordExpires: null,
      },
    });

    return { message: 'Password has been reset successfully' };
  }

  async updateCarColor(email: string, carColor: string) {
    const user = await this.prisma.user.findUnique({
      where: { email },
    });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    await this.prisma.user.update({
      where: { id: user.id },
      data: { carColor },
    });

    return { message: 'Car color updated successfully', carColor };
  }

  async setPreferredSpot(email: string, preferredSpot: string | null) {
    const user = await this.prisma.user.findUnique({
      where: { email },
    });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    let spotPreferenceType: string | null = null;

    // Validate and determine preference type
    if (preferredSpot !== null) {
      // Check if it's a specific spot (A1-B10)
      const validSpots = [
        ...Array.from({ length: 10 }, (_, i) => `A${i + 1}`),
        ...Array.from({ length: 10 }, (_, i) => `B${i + 1}`),
      ];

      if (validSpots.includes(preferredSpot)) {
        spotPreferenceType = 'specific';
      } else if (preferredSpot === 'entrance') {
        spotPreferenceType = 'entrance';
      } else if (preferredSpot === 'exit') {
        spotPreferenceType = 'exit';
      } else if (preferredSpot === 'shop') {
        spotPreferenceType = 'shop';
      } else {
        throw new BadRequestException(
          'Invalid preference. Must be A1-B10, entrance, exit, or shop',
        );
      }
    }

    await this.prisma.user.update({
      where: { id: user.id },
      data: {
        preferredSpot,
        spotPreferenceType,
      },
    });

    const messages = {
      specific: `Preferred spot set to ${preferredSpot}`,
      entrance: 'Preference set to: Closest to entrance',
      exit: 'Preference set to: Closest to exit',
      shop: 'Preference set to: Closest to shop',
    };

    return {
      message: preferredSpot
        ? messages[spotPreferenceType as keyof typeof messages]
        : 'Preferred spot cleared',
      preferredSpot,
      spotPreferenceType,
    };
  }

  async getUserProfile(email: string) {
    const user = await this.prisma.user.findUnique({
      where: { email },
      select: {
        id: true,
        email: true,
        role: true,
        carColor: true,
        preferredSpot: true,
        spotPreferenceType: true,
        emailVerified: true,
        createdAt: true,
      },
    });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    return user;
  }

  async updatePreference(
    email: string,
    spotPreferenceType: string,
    preferredSpot?: string,
  ) {
    const user = await this.prisma.user.findUnique({ where: { email } });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    await this.prisma.user.update({
      where: { email },
      data: {
        spotPreferenceType,
        preferredSpot: spotPreferenceType === 'specific' ? preferredSpot : null,
      },
    });

    return { message: 'Preference updated successfully' };
  }
}
