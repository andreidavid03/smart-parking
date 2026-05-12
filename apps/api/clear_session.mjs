import { PrismaClient } from '@prisma/client';
const p = new PrismaClient();

const updated = await p.session.updateMany({
  where: { endTime: null },
  data: { endTime: new Date() },
});

console.log(`Cleared ${updated.count} active session(s).`);

const spots = await p.spot.updateMany({
  where: { status: 'occupied' },
  data: { status: 'available' },
});

console.log(`Reset ${spots.count} occupied spot(s) to available.`);
await p.$disconnect();
