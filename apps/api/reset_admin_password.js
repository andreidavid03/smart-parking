const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcrypt');
const prisma = new PrismaClient();

async function main() {
  const adminEmail = 'admin@smartparking.com';
  const newPassword = 'admin123'; // Change this if you want a different password
  
  // Hash the password
  const hashedPassword = await bcrypt.hash(newPassword, 10);
  
  // Update admin user
  const admin = await prisma.user.update({
    where: { email: adminEmail },
    data: { 
      password: hashedPassword,
      emailVerified: true,
      role: 'admin'
    },
  });
  
  console.log('\n✅ Admin password reset successfully!');
  console.log('═'.repeat(60));
  console.log(`📧 Email: ${adminEmail}`);
  console.log(`🔑 Password: ${newPassword}`);
  console.log(`👑 Role: ${admin.role}`);
  console.log('═'.repeat(60) + '\n');
}

main()
  .catch((error) => {
    console.error('❌ Error:', error.message);
  })
  .finally(() => prisma.$disconnect());
