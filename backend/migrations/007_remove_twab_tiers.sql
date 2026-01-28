-- Migration: Remove TWAB and Tier System
-- Simplifies distribution from Hash Power (TWAB x Tier) to Balance / Total Supply
-- Date: 2026-01-28

-- Drop HoldStreak table (entire tier system)
DROP TABLE IF EXISTS hold_streaks CASCADE;

-- Remove TWAB/tier columns from distribution_recipients
-- Note: These columns may not exist if this is a fresh install
ALTER TABLE distribution_recipients
  DROP COLUMN IF EXISTS twab,
  DROP COLUMN IF EXISTS multiplier,
  DROP COLUMN IF EXISTS hash_power;

-- Add balance column for tracking snapshot balance at distribution time
-- This replaces twab/hash_power for historical records
ALTER TABLE distribution_recipients
  ADD COLUMN IF NOT EXISTS balance BIGINT NOT NULL DEFAULT 0;

-- Update Distribution table to rename total_hashpower to total_supply
-- Keep total_hashpower for backward compatibility, add total_supply
ALTER TABLE distributions
  ADD COLUMN IF NOT EXISTS total_supply BIGINT;

-- Copy existing data from total_hashpower to total_supply for historical records
UPDATE distributions SET total_supply = total_hashpower::BIGINT WHERE total_supply IS NULL;

-- Update constraint for trigger_type to only allow 'hourly' and 'manual'
-- First drop the old constraint, then add the new one
ALTER TABLE distributions DROP CONSTRAINT IF EXISTS valid_trigger;
ALTER TABLE distributions ADD CONSTRAINT valid_trigger
  CHECK (trigger_type IN ('hourly', 'manual'));

-- Create index on balance for efficient leaderboard queries
CREATE INDEX IF NOT EXISTS idx_distribution_recipients_balance ON distribution_recipients(balance DESC);
