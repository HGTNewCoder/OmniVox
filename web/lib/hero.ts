import fs from "node:fs";
import path from "node:path";
import { img, publicUrl } from "@/lib/asset";

// The four floating pictures at the top of the page.
// To use your own: drop files named hero-1 … hero-4 (.jpg, .jpeg, .png or .webp)
// into web/public/hero/. Any slot without a file keeps the default picture below.
// Edit `caption` to change the text under each picture.
export const HERO_SLOTS = [
  { file: "hero-1", fallback: "feeling_7", caption: "I feel lonely" },
  { file: "hero-2", fallback: "position_3", caption: "Turn me to my side" },
  { file: "hero-3", fallback: "food_0", caption: "Pad Kra Pao" },
  { file: "hero-4", fallback: "shower_pic", caption: "I would like a shower" },
];

const EXTS = [".webp", ".jpg", ".jpeg", ".png"];
const HERO_DIR = path.join(process.cwd(), "public", "hero");

/** Runs at build time: picks the user's file for each slot if it exists. */
export function heroImages() {
  return HERO_SLOTS.map(({ file, fallback, caption }) => {
    const ext = EXTS.find((e) => fs.existsSync(path.join(HERO_DIR, file + e)));
    return { src: ext ? publicUrl(`hero/${file}${ext}`) : img(fallback), caption };
  });
}
