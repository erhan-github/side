import { NextRequest, NextResponse } from "next/server";
import { supabase, isSupabaseConfigured } from "@/lib/supabase";

export async function POST(req: NextRequest) {
    try {
        const { email } = await req.json();

        if (!email) {
            return NextResponse.json(
                { error: "Email is required" },
                { status: 400 }
            );
        }

        // Check if Supabase is properly configured
        if (!isSupabaseConfigured) {
            // Return success for demo purposes
            console.log(`[DEV MODE] Magic link would be sent to: ${email}`);
            return NextResponse.json({ success: true, demo: true });
        }

        const { error } = await supabase.auth.signInWithOtp({
            email,
            options: {
                emailRedirectTo: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard`,
            },
        });

        if (error) {
            console.error("Magic link error:", error);
            return NextResponse.json(
                { error: error.message },
                { status: 400 }
            );
        }

        return NextResponse.json({ success: true });
    } catch (error) {
        console.error("Magic link error:", error);
        return NextResponse.json(
            { error: "Failed to send magic link" },
            { status: 500 }
        );
    }
}
