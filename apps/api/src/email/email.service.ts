import { Injectable } from '@nestjs/common';
import * as nodemailer from 'nodemailer';
import type { Transporter } from 'nodemailer';
import * as os from 'os';

@Injectable()
export class EmailService {
  private transporter: Transporter;

  constructor() {
    this.transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS,
      },
    });
  }

  private getLocalIpAddress(): string {
    const interfaces = os.networkInterfaces();
    for (const devName in interfaces) {
      const iface = interfaces[devName];
      if (iface) {
        for (const alias of iface) {
          if (alias.family === 'IPv4' && alias.address !== '127.0.0.1' && !alias.internal) {
            return alias.address;
          }
        }
      }
    }
    return 'localhost';
  }

  async sendVerificationEmail(email: string, token: string) {
    const host = this.getLocalIpAddress();
    const verificationUrl = `http://${host}:3000/auth/verify-email?token=${token}`;

    await this.transporter.sendMail({
      from: process.env.EMAIL_USER,
      to: email,
      subject: '✅ Verify your Smart Parking account',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">🚗 Smart Parking</h1>
          </div>
          <div style="background: #f7f7f7; padding: 30px; border-radius: 0 0 10px 10px;">
            <h2 style="color: #333;">Bun venit!</h2>
            <p style="color: #666; font-size: 16px;">Mulțumim că te-ai înregistrat la Smart Parking.</p>
            <p style="color: #666; font-size: 16px;">Pentru a-ți activa contul, te rugăm să verifici adresa de email făcând click pe butonul de mai jos:</p>
            
            <div style="text-align: center; margin: 30px 0;">
              <a href="${verificationUrl}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 16px;">
                ✅ Verifică Email-ul
              </a>
            </div>
            
            <p style="color: #999; font-size: 14px;">Sau copiază acest link în browser:</p>
            <p style="background: white; padding: 15px; border-radius: 5px; word-break: break-all; color: #667eea; font-family: monospace; font-size: 12px;">
              ${verificationUrl}
            </p>
            
            <p style="color: #ff6b6b; font-size: 14px; margin-top: 20px;">
              ⚠️ Acest link expiră în 24 ore.
            </p>
            
            <p style="color: #999; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px;">
              Dacă nu ai creat acest cont, poți ignora acest email.
            </p>
          </div>
        </div>
      `,
    });
  }

  async sendPasswordResetEmail(email: string, token: string) {
    const host = this.getLocalIpAddress();
    const resetUrl = `http://${host}:3000/auth/reset-password?token=${token}`;

    await this.transporter.sendMail({
      from: process.env.EMAIL_USER,
      to: email,
      subject: '🔐 Reset your Smart Parking password',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">🔐 Reset Parolă</h1>
          </div>
          <div style="background: #f7f7f7; padding: 30px; border-radius: 0 0 10px 10px;">
            <h2 style="color: #333;">Resetare Parolă</h2>
            <p style="color: #666; font-size: 16px;">Ai solicitat resetarea parolei pentru contul tău Smart Parking.</p>
            <p style="color: #666; font-size: 16px;">Click pe butonul de mai jos pentru a seta o parolă nouă:</p>
            
            <div style="text-align: center; margin: 30px 0;">
              <a href="${resetUrl}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 16px;">
                🔑 Resetează Parola
              </a>
            </div>
            
            <p style="color: #999; font-size: 14px;">Sau copiază acest link în browser:</p>
            <p style="background: white; padding: 15px; border-radius: 5px; word-break: break-all; color: #f5576c; font-family: monospace; font-size: 12px;">
              ${resetUrl}
            </p>
            
            <p style="color: #ff6b6b; font-size: 14px; margin-top: 20px;">
              ⚠️ Acest link expiră în 1 oră.
            </p>
            
            <p style="color: #999; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px;">
              Dacă nu ai solicitat resetarea parolei, poți ignora acest email în siguranță.
            </p>
          </div>
        </div>
      `,
    });
  }
}
