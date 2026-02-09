import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  poweredByHeader: false,

  // Fix for workspace root inference issues
  turbopack: {
    root: __dirname,
  },

  // Webpack configuration for memory optimization
  webpack: (config, { dev, isServer }) => {
    if (dev) {
      // Disable webpack cache in development to prevent memory buildup
      config.cache = false;

      // Optimize file watching to reduce memory usage
      config.watchOptions = {
        ...config.watchOptions,
        ignored: /node_modules/,
        aggregateTimeout: 300,
      };
    }

    return config;
  },

  // Experimental features for memory management
  experimental: {
    // Reduce memory usage by limiting worker threads
    workerThreads: false,
    cpus: 1,
  },

  // Proxy API requests to Python backend
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*',
      },
      // Proxy side:// resources (optional, for direct resource access if needed)
      {
        source: '/side/:path*',
        destination: 'http://127.0.0.1:8000/side/:path*',
      },
    ];
  },
};

export default nextConfig;
