const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  const users = await prisma.user.findMany({
    select: {
      email: true,
      role: true,
      emailVerified: true,
      verificationToken: true,
    }
  });
  
  console.log('\n📧 USERS IN DATABASE:');
  console.log('═'.repeat(80));
  
  if (users.length === 0) {
    console.log('No users found.');
  } else {
    users.forEach((user, i) => {
      console.log(`\n${i + 1}. ${user.email}`);
      console.log(`   Role: ${user.role === 'admin' ? '👑 ADMIN' : '👤 USER'}`);
      console.log(`   Status: ${user.emailVerified ? '✅ VERIFIED' : '❌ NOT VERIFIED'}`);
      
      if (user.verificationToken) {
        const url = `http://10.222.30.70:3000/auth/verify-email?token=${user.verificationToken}`;
        console.log(`   🔗 Verification URL:\n   ${url}`);
      }
    });
  }
  
  console.log('\n' + '═'.repeat(80));
  console.log('\n💡 Admin users can login with their registered password');
  console.log('💡 If you forgot the password, use the signup screen to create a new admin\n');
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
