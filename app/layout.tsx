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
  title: "sideMCP | Your Strategic Sidecar.",
  description: "Upgrade your IDE from a code editor to a Strategic Sidecar. Native support for Cursor, Windsurf, Claude, and VS Code.",
  keywords: ["AI strategist", "strategic decisions", "codebase health", "MCP", "Cursor", "developer tools", "technical debt", "architecture", "CTO"],
  authors: [{ name: "CSO.ai" }],
  openGraph: {
    title: "CSO.ai | Your CTO on call. 24/7.",
    description: "Cursor writes code. CSO.ai makes sure you're not wasting months building the wrong thing.",
    url: "https://cso.ai",
    siteName: "CSO.ai",
    type: "website",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "CSO.ai - Your CTO on call. 24/7.",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "CSO.ai | Your CTO on call. 24/7.",
    description: "Cursor writes code. CSO.ai makes sure you're not wasting months building the wrong thing.",
    images: ["/og-image.png"],
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"),
};

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
        {children}
      </body>
    </html>
  );
}
