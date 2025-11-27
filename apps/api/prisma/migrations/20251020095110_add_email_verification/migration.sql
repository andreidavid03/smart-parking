/*
  Warnings:

  - You are about to drop the column `end` on the `Session` table. All the data in the column will be lost.
  - You are about to drop the column `paid` on the `Session` table. All the data in the column will be lost.
  - You are about to drop the column `start` on the `Session` table. All the data in the column will be lost.
  - The primary key for the `Spot` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - You are about to drop the column `index` on the `Spot` table. All the data in the column will be lost.
  - You are about to drop the column `isReserved` on the `Spot` table. All the data in the column will be lost.
  - You are about to drop the column `location` on the `Spot` table. All the data in the column will be lost.
  - You are about to drop the column `preference` on the `Spot` table. All the data in the column will be lost.
  - The `status` column on the `Spot` table would be dropped and recreated. This will lead to data loss if there is data in the column.
  - You are about to drop the column `preference` on the `User` table. All the data in the column will be lost.
  - A unique constraint covering the columns `[verificationToken]` on the table `User` will be added. If there are existing duplicate values, this will fail.

*/
-- DropForeignKey
ALTER TABLE "public"."Session" DROP CONSTRAINT "Session_spotId_fkey";

-- DropIndex
DROP INDEX "public"."Spot_index_key";

-- AlterTable
ALTER TABLE "public"."Session" DROP COLUMN "end",
DROP COLUMN "paid",
DROP COLUMN "start",
ADD COLUMN     "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN     "endTime" TIMESTAMP(3),
ADD COLUMN     "startTime" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN     "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ALTER COLUMN "spotId" SET DATA TYPE TEXT;

-- AlterTable
ALTER TABLE "public"."Spot" DROP CONSTRAINT "Spot_pkey",
DROP COLUMN "index",
DROP COLUMN "isReserved",
DROP COLUMN "location",
DROP COLUMN "preference",
ADD COLUMN     "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN     "name" TEXT NOT NULL DEFAULT '',
ADD COLUMN     "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ALTER COLUMN "id" DROP DEFAULT,
ALTER COLUMN "id" SET DATA TYPE TEXT,
DROP COLUMN "status",
ADD COLUMN     "status" TEXT NOT NULL DEFAULT 'available',
ADD CONSTRAINT "Spot_pkey" PRIMARY KEY ("id");
DROP SEQUENCE "Spot_id_seq";

-- AlterTable
ALTER TABLE "public"."User" DROP COLUMN "preference",
ADD COLUMN     "emailVerified" BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN     "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN     "verificationToken" TEXT;

-- DropEnum
DROP TYPE "public"."SpotPreferenceType";

-- DropEnum
DROP TYPE "public"."SpotStatus";

-- CreateIndex
CREATE UNIQUE INDEX "User_verificationToken_key" ON "public"."User"("verificationToken");

-- AddForeignKey
ALTER TABLE "public"."Session" ADD CONSTRAINT "Session_spotId_fkey" FOREIGN KEY ("spotId") REFERENCES "public"."Spot"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
