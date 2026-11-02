import type { NextConfig } from "next";

// Set BASE_PATH=/OmniVox when deploying to https://<user>.github.io/OmniVox
const basePath = process.env.BASE_PATH ?? "";

const nextConfig: NextConfig = {
  output: "export", // fully static site in ./out — host anywhere (GitHub Pages, Netlify, a Pi)
  basePath,
  trailingSlash: true,
  images: { unoptimized: true },
  env: { NEXT_PUBLIC_BASE_PATH: basePath },
};

export default nextConfig;
