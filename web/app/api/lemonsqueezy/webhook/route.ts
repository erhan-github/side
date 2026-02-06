import { createClient } from "@supabase/supabase-js";
import { NextResponse } from "next/server";

// Helper to get Supabase Admin client
const getSupabaseAdmin = () => {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;

    if (!url || !key) {
        throw new Error("Supabase Admin environment variables are missing.");
    }

    return createClient(url, key);
};

export async function POST(request: Request) {
    try {
        const supabaseAdmin = getSupabaseAdmin();
        const body = await request.text();
        const signature = request.headers.get("x-signature");

        if (!signature) {
            return NextResponse.json({ error: "No signature" }, { status: 401 });
        }

        // Verify signature using timing-safe comparison (CIA-grade)
        const secret = process.env.LEMONSQUEEZY_WEBHOOK_SECRET!;
        const crypto = require('crypto');
        const hmac = crypto.createHmac('sha256', secret);
        const digest = hmac.update(body).digest('hex');

        // Prevent timing attacks
        const signatureBuffer = Buffer.from(signature, 'hex');
        const digestBuffer = Buffer.from(digest, 'hex');

        if (signatureBuffer.length !== digestBuffer.length || !crypto.timingSafeEqual(signatureBuffer, digestBuffer)) {
            console.error('[SECURITY] Invalid webhook signature detected');
            return NextResponse.json({ error: "Invalid signature" }, { status: 401 });
        }

        const payload = JSON.parse(body);
        const eventName = payload.meta.event_name;
        const customData = payload.meta.custom_data;
        const userId = customData?.user_id;

        if (!userId) {
            console.error("Webhook received without user_id in custom_data");
            return NextResponse.json({ error: "No user_id" }, { status: 400 });
        }

        console.log(`Processing Lemon Squeezy event: ${eventName} for user: ${userId}`);

        // 1. Handle Subscription Created / Updated
        if (eventName === "subscription_created" || eventName === "subscription_updated") {
            const variantId = String(payload.data.attributes.variant_id);
            let tier = "hobby";
            let tokens = 50;

            if (variantId === process.env.LEMONSQUEEZY_VARIANT_ID_PRO) {
                tier = "pro";
                tokens = 500;
            } else if (variantId === process.env.LEMONSQUEEZY_VARIANT_ID_ELITE) {
                tier = "elite";
                tokens = 2500;
            }

            // Capture Billing IDs for Portal Access
            const customerId = String(payload.data.attributes.customer_id);
            const subscriptionId = String(payload.data.id);

            // Log to Transaction Ledger (Reset Logic for now)
            // Ideally we calculate diff, but for sub start/update we accept the reset.
            // We log the *New Allowance*.
            await supabaseAdmin.from("transaction_history").insert({
                user_id: userId,
                amount: tokens,
                type: eventName === "subscription_created" ? 'subscription_new' : 'subscription_renewal',
                description: `Tier Update: ${tier.toUpperCase()}`,
                external_id: subscriptionId,
                balance_after: tokens // Since we reset
            });

            const { error } = await supabaseAdmin
                .from("profiles")
                .update({
                    tier,
                    tokens_monthly: tokens,
                    tokens_used: 0, // Reset usage on upgrade/renewal? Typically yes for new cycle.
                    billing_customer_id: customerId,
                    billing_subscription_id: subscriptionId,
                    updated_at: new Date().toISOString()
                })
                .eq("id", userId);

            if (error) throw error;
        }

        // 2. Handle Refill (One-time Purchase)
        if (eventName === "order_created") {
            const variantId = String(payload.data.attributes.first_order_item.variant_id);

            // Handle Refill
            if (variantId === process.env.LEMONSQUEEZY_VARIANT_ID_REFILL) {
                const refillAmount = 250;

                const { data: profile } = await supabaseAdmin
                    .from("profiles")
                    .select("tokens_monthly, tokens_used")
                    .eq("id", userId)
                    .single();

                const currentLimit = profile?.tokens_monthly || 0;
                const currentUsed = profile?.tokens_used || 0;
                const newLimit = currentLimit + refillAmount;

                // Log to Transaction Ledger
                await supabaseAdmin.from("transaction_history").insert({
                    user_id: userId,
                    amount: refillAmount,
                    type: 'refill',
                    description: 'Refill Pack (+250)',
                    external_id: String(payload.data.id),
                    balance_after: newLimit - currentUsed
                });

                const { error } = await supabaseAdmin
                    .from("profiles")
                    .update({
                        tokens_monthly: newLimit,
                        updated_at: new Date().toISOString()
                    })
                    .eq("id", userId);

                if (error) throw error;
            }
        }

        return NextResponse.json({ success: true });
    } catch (err: any) {
        console.error("Webhook Error:", err.message);
        return NextResponse.json({ error: err.message }, { status: 500 });
    }
}
