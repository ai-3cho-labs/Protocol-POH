-- ===========================================
-- TWAB Query Optimization
-- Version: 004
-- ===========================================

-- Add optimized index for batch TWAB queries
-- The calculate_all_hash_powers() query joins balances to snapshots
-- filtering by timestamp range, then orders by wallet.
-- This composite index supports the JOIN and sort efficiently.
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_balances_snapshot_wallet
ON balances(snapshot_id, wallet);

-- Add index on snapshots timestamp for range queries (ASC for range scans)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_snapshots_timestamp_asc
ON snapshots(timestamp ASC);
