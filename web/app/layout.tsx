import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Sidelith | Structural Intelligence.",
  description: "Upgrade your IDE from a code editor to a Strategic Partner with Sidelith. Intelligence infrastructure for modern engineering.",
  keywords: ["Sidelith", "AI strategist", "strategic decisions", "codebase health", "MCP", "Cursor", "developer tools", "technical debt", "architecture", "CTO"],
  authors: [{ name: "Sidelith" }],
  openGraph: {
    title: "Sidelith | Structural Intelligence",
    description: "Palantir-level intelligence for your software architecture.",
    url: "https://sidelith.com",
    siteName: "Sidelith",
    type: "website",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Sidelith - Structural Intelligence for Engineers.",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Sidelith | Intelligence Infrastructure.",
    description: "Cursor writes code. Sidelith makes sure it holds the weight.",
    images: ["/og-image.png"],
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || "https://sidelith.com"),
};

import { CSPostHogProvider } from "./providers";
import { GlobalErrorBoundary } from "@/components/observability/GlobalErrorBoundary";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <GlobalErrorBoundary>
          <CSPostHogProvider>
            {children}
          </CSPostHogProvider>
        </GlobalErrorBoundary>
      </body>
    </html>
  );
}
