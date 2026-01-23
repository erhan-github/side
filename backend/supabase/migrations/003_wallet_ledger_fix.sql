-- Wallet & Ledger Migration (FIXED)
-- Idempotent version: Drops policies if they exist before creating.

create table if not exists transaction_history (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    amount integer not null, -- Positive for Credit, Negative for Usage
    type text not null,      -- 'subscription_renewal', 'refill', 'usage', 'adjustment'
    description text,        -- Human readable description
    external_id text,        -- LemonSqueezy Order ID or Stripe ID
    balance_after integer,   -- Snapshot of balance after transaction for quick audit
    metadata jsonb,          -- Extra details (e.g. usage query_id)
    created_at timestamptz default now()
);

-- Indices
create index if not exists idx_transaction_history_user on transaction_history(user_id);
create index if not exists idx_transaction_history_created on transaction_history(created_at desc);

-- RLS
alter table transaction_history enable row level security;

-- Drop existing policies to prevent "already exists" error
drop policy if exists "Users can view own transactions" on transaction_history;
drop policy if exists "Service role can insert history" on transaction_history;

-- Re-create policies
create policy "Users can view own transactions"
    on transaction_history for select
    using (auth.uid() = user_id);

create policy "Service role can insert history"
    on transaction_history for insert
    with check (true);

-- ============================================================================
-- RPC: Increment Tokens (Modified to Log Transaction)
-- ============================================================================
create or replace function increment_tokens(p_user_id uuid, p_amount int)
returns void
language plpgsql
security definer
as $$
declare
    v_new_usage int;
    v_monthly_limit int;
begin
    -- 1. Update Profile Usage
    update profiles
    set tokens_used = tokens_used + p_amount,
        updated_at = now()
    where id = p_user_id
    returning tokens_used, tokens_monthly into v_new_usage, v_monthly_limit;

    -- 2. Log to Ledger (Usage is negative)
    insert into transaction_history (
        user_id,
        amount,
        type,
        description,
        balance_after
    ) values (
        p_user_id,
        -p_amount, -- Log as negative
        'usage',
        'AI Usage',
        v_monthly_limit - v_new_usage -- Calculated Balance
    );
end;
$$;
