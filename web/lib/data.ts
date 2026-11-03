// Server-only: runs at build time (static export), never shipped to the browser.
import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import type { Board } from "./board";
import type { AppData } from "./types";

// The same content files the PyQt app loads (json_page/ at the repo root).
const JSON_DIR = path.join(process.cwd(), "..", "json_page");

function read<T>(name: string): T {
  return JSON.parse(readFileSync(path.join(JSON_DIR, `${name}.json`), "utf8")) as T;
}

export function loadAppData(): AppData {
  const translations = Object.fromEntries(
    read<{ language: string; data: Record<string, string> }[]>("translation").map((x) => [x.language, x.data]),
  );
  return { translations, board: read<Board>("board") };
}

/** Pictures bundled with the site, named like on the device ("assets/food.png"). */
export function bundledAssets(): string[] {
  const dir = path.join(process.cwd(), "public", "assets");
  return readdirSync(dir)
    .filter((f) => f.endsWith(".webp"))
    .map((f) => `assets/${f.replace(/\.webp$/, ".png")}`)
    .sort();
}
