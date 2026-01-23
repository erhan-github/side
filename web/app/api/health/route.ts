import { NextResponse } from "next/server";

export async function GET() {
    console.log("🏥 Healthcheck hit at " + new Date().toISOString());
    return NextResponse.json({ status: "ok", timestamp: new Date().toISOString() });
}
