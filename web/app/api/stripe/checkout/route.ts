import { NextRequest, NextResponse } from "next/server";
import { stripe } from "@/lib/stripe";
import { supabase } from "@/lib/supabase";

export async function POST(req: NextRequest) {
    try {
        // Get the current user from Supabase Auth
        const { data: { user }, error: authError } = await supabase.auth.getUser();

        if (authError || !user) {
            return new NextResponse("Unauthorized", { status: 401 });
        }

        const userId = user.id;

        const { quantity = 1 } = await req.json();

        // Use production Price ID from environment variables
        const priceId = process.env.STRIPE_PRICE_ID;

        if (!priceId && !process.env.STRIPE_SECRET_KEY?.startsWith("sk_test")) {
            console.error("Missing STRIPE_PRICE_ID environment variable");
            return new NextResponse("Configuration Error", { status: 500 });
        }

        // MOCK MODE: Return success URL immediately if using mock keys
        if (process.env.STRIPE_SECRET_KEY?.startsWith("mock")) {
            // Simulate network delay
            await new Promise(resolve => setTimeout(resolve, 1000));
            return NextResponse.json({
                url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard?success=true`
            });
        }

        const session = await stripe.checkout.sessions.create({
            line_items: [
                {
                    price_data: {
                        currency: "usd",
                        product_data: {
                            name: "50,000 Strategic Tokens",
                            description: "Refill for CSO.ai Intelligence",
                        },
                        unit_amount: 2000, // $20.00
                    },
                    quantity: quantity,
                },
            ],
            mode: "payment",
            success_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard?success=true`,
            cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard?canceled=true`,
            metadata: {
                userId: userId,
                type: "token_refill",
                tokens: "50000",
            },
        });

        return NextResponse.json({ url: session.url });
    } catch (error) {
        console.error("[STRIPE_CHECKOUT_ERROR]", error);
        return new NextResponse("Internal Error", { status: 500 });
    }
}
