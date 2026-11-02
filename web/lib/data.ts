// Server-only: runs at build time (static export), never shipped to the browser.
import { readFileSync } from "node:fs";
import path from "node:path";
import type { AppData, BathroomItem, CatKey, Lang, MenuCard } from "./types";

// The same content files the PyQt app loads (json_page/ at the repo root).
const JSON_DIR = path.join(process.cwd(), "..", "json_page");

type LangBlock = { language: string; data: Record<string, string> | string[] };

function read<T>(name: string): T {
  return JSON.parse(readFileSync(path.join(JSON_DIR, `${name}.json`), "utf8")) as T;
}

const assetName = (p: string) => path.basename(p).replace(/\.png$/i, "");

function byLang(blocks: LangBlock[]): Partial<Record<Lang, string[]>> {
  return Object.fromEntries(
    blocks.map((b) => [b.language, Array.isArray(b.data) ? b.data : Object.values(b.data)]),
  );
}

const CATEGORY_FILES: Record<CatKey, string> = {
  food: "food",
  feeling: "feelings",
  position: "position",
  entertainment: "entertainment",
  recommend: "recommend",
};

export function loadAppData(): AppData {
  const translations = Object.fromEntries(
    read<{ language: string; data: Record<string, string> }[]>("translation").map((x) => [x.language, x.data]),
  );

  const cards: MenuCard[] = read<(Omit<MenuCard, "image"> & { image: string })[]>("cards").map((c) => ({
    ...c,
    image: assetName(c.image),
  }));

  const rawBath = read<{
    items: { id: string; message_key?: string; message?: string; color: string; image_path: string; row: number; col: number }[];
    translations?: { language: string; data: Record<string, string> }[];
  }>("bathroom");
  const bathroom = {
    items: rawBath.items.map<BathroomItem>((b) => ({
      id: b.id,
      message: b.message_key ?? b.message ?? "",
      color: b.color,
      image: assetName(b.image_path),
      row: b.row,
      col: b.col,
    })),
    translations: Object.fromEntries((rawBath.translations ?? []).map((x) => [x.language, x.data])),
  };

  const categories = Object.fromEntries(
    (Object.keys(CATEGORY_FILES) as CatKey[]).map((k) => [k, byLang(read<LangBlock[]>(CATEGORY_FILES[k]))]),
  ) as AppData["categories"];

  return { translations, cards, bathroom, categories };
}
