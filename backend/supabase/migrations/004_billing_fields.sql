-- Add Billing Fields to Profiles
-- Needed to link users to LemonSqueezy Customer Portal

alter table profiles 
add column if not exists billing_customer_id text,
add column if not exists billing_subscription_id text;

-- Index for searching (if needed)
create index if not exists idx_profiles_billing_customer on profiles(billing_customer_id);
