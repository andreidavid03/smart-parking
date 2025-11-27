import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

async function main() {
  // Delete existing demo users
  await prisma.user.deleteMany({
    where: {
      email: {
        in: ['admin@smartparking.com', 'user@smartparking.com'],
      },
    },
  });

  // Create parking spots with zones A and B
  const spots = [
    // Zone A - 10 spots
    ...Array.from({ length: 10 }, (_, i) => ({
      name: `A${i + 1}`,
      status: 'available',
    })),
    // Zone B - 10 spots
    ...Array.from({ length: 10 }, (_, i) => ({
      name: `B${i + 1}`,
      status: 'available',
    })),
  ];

  await prisma.spot.createMany({ data: spots, skipDuplicates: true });
  console.log(`✅ Created ${spots.length} parking spots`);

  // Create demo admin user
  await prisma.user.create({
    data: {
      email: 'admin@smartparking.com',
      password: '$2b$10$Od2m/ig9x.NK2pgtNxCD4uEruo2VC.jezLKRJ.qAH5Krb6iZdlMWm', // hashed "admin123"
      role: 'admin',
      emailVerified: true,
    },
  });
  console.log('✅ Created admin user (admin@smartparking.com / admin123)');

  // Create demo regular user
  await prisma.user.create({
    data: {
      email: 'user@smartparking.com',
      password: '$2b$10$Od2m/ig9x.NK2pgtNxCD4uEruo2VC.jezLKRJ.qAH5Krb6iZdlMWm', // hashed "admin123"
      role: 'user',
      emailVerified: true,
    },
  });
  console.log('✅ Created regular user (user@smartparking.com / admin123)');
}

void (async () => {
  try {
    await main();
  } catch (e) {
    console.error(e);
    process.exitCode = 1;
  } finally {
    await prisma.$disconnect();
  }
})();
