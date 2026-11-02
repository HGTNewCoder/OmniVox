import type { Metadata, Viewport } from "next";
import { Atkinson_Hyperlegible, Fraunces, Noto_Sans_Thai } from "next/font/google";
import { img } from "@/lib/asset";
import "./globals.css";

const atkinson = Atkinson_Hyperlegible({ subsets: ["latin"], weight: ["400", "700"], variable: "--font-atkinson" });
const fraunces = Fraunces({ subsets: ["latin"], weight: ["500", "700"], variable: "--font-fraunces" });
const notoThai = Noto_Sans_Thai({ subsets: ["thai"], weight: ["400", "700"], variable: "--font-thai" });

export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.SITE_URL ??
      (process.env.VERCEL_PROJECT_PRODUCTION_URL
        ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`
        : "https://hgtnewcoder.github.io"),
  ),
  title: "OmniVox — A voice for every bedside",
  description:
    "OmniVox is a bilingual English/Thai touchscreen communication board for patients and older adults. Tap a picture and it speaks for you. Runs on a Raspberry Pi.",
  icons: { icon: img("bell") },
  openGraph: {
    title: "OmniVox — A voice for every bedside",
    description: "A bilingual picture-to-speech communication board for patients, built on a Raspberry Pi.",
    images: [img("bell")],
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${atkinson.variable} ${fraunces.variable} ${notoThai.variable}`}>
      <body>{children}</body>
    </html>
  );
}
