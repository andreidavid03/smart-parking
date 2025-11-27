/*
  Warnings:

  - A unique constraint covering the columns `[qrCode]` on the table `User` will be added. If there are existing duplicate values, this will fail.

*/
-- AlterTable
ALTER TABLE "public"."User" ADD COLUMN     "qrCode" TEXT;

-- CreateIndex
CREATE UNIQUE INDEX "User_qrCode_key" ON "public"."User"("qrCode");
