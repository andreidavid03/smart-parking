-- CreateEnum
CREATE TYPE "public"."SpotPreferenceType" AS ENUM ('NEAR_ENTRANCE', 'COVERED', 'EV_CHARGING', 'HANDICAP');

-- AlterTable
ALTER TABLE "public"."Spot" ADD COLUMN     "isReserved" BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN     "location" TEXT,
ADD COLUMN     "preference" "public"."SpotPreferenceType";

-- AlterTable
ALTER TABLE "public"."User" ADD COLUMN     "preference" "public"."SpotPreferenceType";
