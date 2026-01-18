import { NextRequest, NextResponse } from "next/server";
import { stripe } from "@/lib/stripe";
import { supabase } from "@/lib/supabase";
import Stripe from "stripe";

// This is necessary for webhook signature verification
export const config = {
    api: {
        bodyParser: false,
    },
};

export async function POST(req: NextRequest) {
    const body = await req.text();
    const signature = req.headers.get("stripe-signature") as string;

    let event: Stripe.Event;

    try {
        event = stripe.webhooks.constructEvent(
            body,
            signature,
            process.env.STRIPE_WEBHOOK_SECRET!
        );
    } catch (error: any) {
        console.error(`Webhook signature verification failed: ${error.message}`);
        return new NextResponse(`Webhook Error: ${error.message}`, { status: 400 });
    }

    // Handle the event
    if (event.type === "checkout.session.completed") {
        const session = event.data.object as Stripe.Checkout.Session;

        // Extract metadata
        const userId = session.metadata?.userId;
        const tokens = parseInt(session.metadata?.tokens || "0");
        const type = session.metadata?.type;

        if (type === "token_refill" && userId) {
            // CTO Production Hardening: Idempotency Check
            const { data: existingTx } = await supabase
                .from("transactions")
                .select("id")
                .eq("stripe_session_id", session.id)
                .single();

            if (existingTx) {
                console.log(`[STRIPE] Skipping duplicate webhook for session ${session.id}`);
                return new NextResponse(null, { status: 200 });
            }

            // CTO Production Hardening: Atomic Update with RPC
            // Using an RPC function 'refill_tokens' ensures we don't have race conditions
            // between reading current balance and updating it.
            const { error: refillError } = await supabase.rpc('refill_tokens', {
                p_user_id: userId,
                p_amount: tokens,
                p_session_id: session.id
            });

            if (refillError) {
                console.error("[SUPABASE_ERROR] Atomic refill failed", refillError);
                return new NextResponse("Database Error", { status: 500 });
            }

            console.log(`[STRIPE] Atomic refill successful for user ${userId}`);
        }
    }

    return new NextResponse(null, { status: 200 });
}
