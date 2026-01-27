-- Migration: 005_add_manual_trigger
-- Description: Add 'manual' as a valid trigger type for distributions
-- Author: Claude
-- Date: 2026-01-27

-- Drop and recreate the check constraint to include 'manual' and 'hourly'
ALTER TABLE distributions DROP CONSTRAINT IF EXISTS valid_trigger;
ALTER TABLE distributions ADD CONSTRAINT valid_trigger CHECK (trigger_type IN ('threshold', 'time', 'manual', 'hourly'));
