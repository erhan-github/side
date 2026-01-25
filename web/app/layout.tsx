import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "Side | Sovereign Intelligence Layer",
    template: "%s | Side"
  },
  description: "The professional System of Record for modern engineering. Side monitors project trajectory and architectural integrity in real-time.",
  keywords: ["Sovereign Intelligence", "Deterministic Code Audit", "Strategic Registry", "System of Record", "Architecture Forensics", "Local-First AI"],
  authors: [{ name: "Sidelith OS" }],
  viewport: "width=device-width, initial-scale=1, maximum-scale=5",
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || "https://sidelith.com"),
};

import { CSPostHogProvider } from "./providers";
import { GlobalErrorBoundary } from "@/components/observability/GlobalErrorBoundary";
import { AuthSync } from "@/components/auth/AuthSync";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} ${outfit.variable} antialiased`}
      >
        <GlobalErrorBoundary>
          <CSPostHogProvider>
            <AuthSync />
            {children}
          </CSPostHogProvider>
        </GlobalErrorBoundary>
      </body>
    </html>
  );
}
