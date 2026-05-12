import { PrismaClient } from '@prisma/client';
const p = new PrismaClient();

const users = await p.user.findMany({ select: { email: true, qrCode: true, emailVerified: true } });
const sessions = await p.session.findMany({
  where: { endTime: null },
  include: { user: { select: { email: true } }, spot: { select: { name: true } } }
});
const spots = await p.spot.findMany({ select: { name: true, status: true }, take: 5 });

console.log('=== USERS ===');
users.forEach(u => console.log(u.email, '| qr:', u.qrCode, '| verified:', u.emailVerified));

console.log('\n=== ACTIVE SESSIONS ===');
if (!sessions.length) console.log('none');
sessions.forEach(s => console.log(s.user.email, '-> spot', s.spot.name));

console.log('\n=== SPOTS (first 5) ===');
spots.forEach(s => console.log(s.name, ':', s.status));

await p.$disconnect();
