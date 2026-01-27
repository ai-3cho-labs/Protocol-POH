-- Migration 006: Rename copper_amount to gold_amount in buybacks table
-- This aligns the database column with the service layer which uses gold_amount
-- Since this system buys back GOLD tokens (not copper), the field name should reflect that

ALTER TABLE buybacks RENAME COLUMN copper_amount TO gold_amount;
