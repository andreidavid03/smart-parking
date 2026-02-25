/*
  Warnings:

  - A unique constraint covering the columns `[name]` on the table `Spot` will be added. If there are existing duplicate values, this will fail.

*/
-- AlterTable
ALTER TABLE "public"."ParkingConfig" ADD COLUMN     "machetaBottomRightLat" DOUBLE PRECISION,
ADD COLUMN     "machetaBottomRightLng" DOUBLE PRECISION,
ADD COLUMN     "machetaOverlayUrl" TEXT,
ADD COLUMN     "machetaTopLeftLat" DOUBLE PRECISION,
ADD COLUMN     "machetaTopLeftLng" DOUBLE PRECISION,
ADD COLUMN     "parkingCostPerHour" DOUBLE PRECISION NOT NULL DEFAULT 5.0,
ADD COLUMN     "speedLimit" INTEGER NOT NULL DEFAULT 10;

-- CreateIndex
CREATE UNIQUE INDEX "Spot_name_key" ON "public"."Spot"("name");
