import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // The Docker build sets NEXT_STANDALONE=true to get a minimal server.js
  // bundle; local builds keep the regular output so `npm start` still works.
  output: process.env.NEXT_STANDALONE === "true" ? "standalone" : undefined,
  experimental: {
    agentFeedback: true,
  },
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": [
        {
          loaders: ["@tailwindcss/turbopack"],
          as: "*.css",
        },
      ],
    },
  },
};

export default nextConfig;
