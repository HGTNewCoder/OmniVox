const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

/** URL of a web-optimised image in public/assets (name without extension). */
export const img = (name: string) => `${BASE}/assets/${name}.webp`;

/** URL of any file under public/. */
export const publicUrl = (p: string) => `${BASE}/${p.replace(/^\//, "")}`;

/** Turns a device picture path ("assets/food.png") into a URL. */
export type ImageResolver = (path: string) => string;

/** Device pictures are bundled with the site as WebP: assets/food.png -> /assets/food.webp */
export const bundledImage: ImageResolver = (p) => {
  if (!p) return "";
  if (/^(data:|blob:|https?:)/.test(p)) return p;
  const m = /^assets\/(.+)\.(png|jpe?g|webp|gif)$/i.exec(p);
  return m && !m[1].includes("/") ? img(m[1]) : publicUrl(p);
};
