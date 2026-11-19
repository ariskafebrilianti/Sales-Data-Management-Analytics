ALTER TABLE public.transactions
DROP CONSTRAINT IF EXISTS chk_selling_price;

ALTER TABLE public.transactions
ADD CONSTRAINT chk_selling_price
CHECK (selling_price > 0);