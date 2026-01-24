import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextResponse, type NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
    const requestUrl = new URL(request.url)
    const code = requestUrl.searchParams.get('code')
    const next = requestUrl.searchParams.get('next') ?? '/dashboard'
    const origin = (process.env.NEXT_PUBLIC_APP_URL?.trim() || requestUrl.origin)

    if (code) {
        const cookieStore = await cookies()

        // CONTAINER: Capture cookies here instead of setting on response headers
        // This avoids the "Header Overflow" issue on Railway/Proxies
        const cookiesToHydrate: any[] = [];

        const supabase = createServerClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL!,
            process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
            {
                cookies: {
                    getAll() {
                        return cookieStore.getAll()
                    },
                    setAll(cookiesToSet) {
                        // Capture cookies for client-side hydration
                        console.log(`[CALLBACK] Capturing ${cookiesToSet.length} cookies for client hydration.`);
                        cookiesToSet.forEach((c) => {
                            cookiesToHydrate.push({
                                ...c,
                                options: {
                                    ...c.options,
                                    path: '/', // Force root path
                                    sameSite: 'lax', // Force lax
                                    secure: true, // Force secure
                                }
                            })
                        });
                    },
                },
            }
        )

        const { data, error } = await supabase.auth.exchangeCodeForSession(code)

        if (!error) {
            console.log(`[AUTH CALLBACK] Exchange successful for User ID: ${data.user?.id}. Hydrating client...`);

            // Generate safe JSON payload
            const cookiePayload = JSON.stringify(cookiesToHydrate).replace(/</g, '\\u003c');
            const targetUrl = `${origin}${next}`;

            const html = `
<!DOCTYPE html>
<html>
<head>
    <title>Authenticating...</title>
    <meta charset="utf-8">
    <style>
        body { background: #000; color: #333; font-family: monospace; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .loader { width: 24px; height: 24px; border: 2px solid #333; border-top-color: #00bcd4; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        p { color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="loader"></div>
    <p>Hydrating Secure Session...</p>
    <script>
        try {
            const cookies = ${cookiePayload};
            cookies.forEach(({ name, value, options }) => {
                let cookieString = \`\${name}=\${value}\`;
                
                // Map options to cookie string format
                if (options.path) cookieString += \`; path=\${options.path}\`;
                if (options.maxAge) cookieString += \`; max-age=\${options.maxAge}\`;
                if (options.domain) cookieString += \`; domain=\${options.domain}\`;
                if (options.secure) cookieString += \`; secure\`;
                if (options.sameSite) cookieString += \`; samesite=\${options.sameSite}\`;
                
                document.cookie = cookieString;
            });
            
            // Redirect immediately after hydration
            window.location.href = "${targetUrl}";
        } catch (e) {
            console.error("Hydration failed", e);
            document.body.innerHTML = "<p style='color:red'>Authentication Error. Please refresh.</p>";
        }
    </script>
</body>
</html>`;

            return new NextResponse(html, {
                status: 200,
                headers: { 'Content-Type': 'text/html' }
            });
        }

        console.error('[AUTH CALLBACK] Exchange error:', error.message);
    }

    return NextResponse.redirect(`${origin}/login?error=auth_callback_failed`)
}
