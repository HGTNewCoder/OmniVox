"use client";

/**
 * Shrink a picture in the browser before it is sent to a device, so a phone
 * photo (often 5–10 MB) arrives as a few hundred KB. Logos keep transparency
 * (PNG); photos become JPEG.
 */
export async function preparePicture(file: Blob, maxSide = 1280): Promise<Blob> {
  if (!file.type.startsWith("image/")) throw new Error("Please choose a picture file.");
  const bitmap = await createImageBitmap(file).catch(() => {
    throw new Error("That picture could not be opened. Try a PNG or JPEG.");
  });
  const scale = Math.min(1, maxSide / Math.max(bitmap.width, bitmap.height));
  const w = Math.max(1, Math.round(bitmap.width * scale));
  const h = Math.max(1, Math.round(bitmap.height * scale));
  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("This browser cannot resize pictures.");
  ctx.drawImage(bitmap, 0, 0, w, h);
  bitmap.close();
  const keepAlpha = file.type === "image/png" || file.type === "image/gif" || file.type === "image/webp";
  const type = keepAlpha ? "image/png" : "image/jpeg";
  const blob = await new Promise<Blob | null>((r) => canvas.toBlob(r, type, 0.86));
  if (!blob) throw new Error("The picture could not be prepared.");
  return blob;
}
