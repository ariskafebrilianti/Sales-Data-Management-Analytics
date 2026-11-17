
-- ==================================================
-- ADD TRANSACTION CREATED AT
-- Purpose: Track when transactions are inserted
-- ==================================================

BEGIN;

-- Add timestamp column.
-- Existing transactions remain NULL.
ALTER TABLE public.transactions
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ;

-- Automatically timestamp future transactions.
ALTER TABLE public.transactions
ALTER COLUMN created_at SET DEFAULT NOW();

-- Add index for recent transaction monitoring.
CREATE INDEX IF NOT EXISTS idx_transactions_created_at
ON public.transactions (created_at DESC)
WHERE created_at IS NOT NULL;

-- Document the column.
COMMENT ON COLUMN public.transactions.created_at
IS 'Timestamp when the transaction was inserted into the database';

COMMIT;
