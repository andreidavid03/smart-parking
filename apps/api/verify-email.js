const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function verifyUser(email) {
  try {
    const user = await prisma.user.findUnique({
      where: { email }
    });
    
    if (!user) {
      console.log(`❌ User not found: ${email}`);
      await prisma.$disconnect();
      return;
    }
    
    await prisma.user.update({
      where: { email },
      data: { 
        emailVerified: true,
        verificationToken: null 
      }
    });
    
    console.log(`✅ Email verified for: ${email}`);
  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await prisma.$disconnect();
  }
}

const email = process.argv[2] || 'mella.palm@icloud.com';
verifyUser(email);
