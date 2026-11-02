const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

/** URL of a web-optimised image in public/assets (name without extension). */
export const img = (name: string) => `${BASE}/assets/${name}.webp`;

/** URL of any file under public/. */
export const publicUrl = (p: string) => `${BASE}/${p.replace(/^\//, "")}`;
