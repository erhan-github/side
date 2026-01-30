import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  poweredByHeader: false,
  // Fix for workspace root inference issues
  turbopack: {
    root: __dirname,
  }
};

export default nextConfig;
