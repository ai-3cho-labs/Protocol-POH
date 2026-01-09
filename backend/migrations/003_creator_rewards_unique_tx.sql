-- ===========================================
-- Migration 003: Add UNIQUE constraint on creator_rewards.tx_signature
-- Prevents webhook replay attacks by ensuring each transaction is only recorded once
-- ===========================================

-- Add unique constraint on tx_signature (WHERE NOT NULL to allow multiple NULL values)
-- This prevents the same transaction from being recorded multiple times due to webhook retries
CREATE UNIQUE INDEX IF NOT EXISTS idx_creator_rewards_tx_signature_unique
ON creator_rewards(tx_signature)
WHERE tx_signature IS NOT NULL;

-- Add index for faster idempotency lookups
CREATE INDEX IF NOT EXISTS idx_creator_rewards_tx_signature
ON creator_rewards(tx_signature)
WHERE tx_signature IS NOT NULL;
