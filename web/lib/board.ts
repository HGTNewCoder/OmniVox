// The card board shared by the device (app.py), the master and this website.
// Mirrors omnivox_board.py — keep the two in step.

export type Lang = "en" | "th";
export const LANGS: Lang[] = ["en", "th"];
export type I18n = { en: string; th: string };
export type CardType = "list" | "grid" | "phrases" | "yesno" | "clock";

export interface BoardItem {
  id: string;
  label: I18n;
  image: string;        // "assets/..." or "" for none
  message?: I18n;       // grid cards: the sentence that is spoken
  color?: string;       // grid cards: tile colour
}

export interface BoardCard {
  id: string;
  type: CardType;
  title: I18n;
  description: I18n;
  page_title: I18n;
  color: string;
  accent: string;
  image: string;
  visible: boolean;
  speak: boolean;
  speak_template: I18n;
  large_text: boolean;
  items: BoardItem[];
}

export interface Board {
  version: number;
  updated: string;
  cards: BoardCard[];
}

export const LIMITS = { cards: 12, items: 80, gridItems: 8, text: 200 };

export const TYPE_INFO: Record<CardType, { label: string; hint: string; hasItems: boolean }> = {
  list: { label: "Picture list", hint: "A scrolling strip of pictures with a big preview — like Food or Feeling.", hasItems: true },
  grid: { label: "Picture grid", hint: "Up to 8 big picture tiles that each say a sentence — like Bathroom.", hasItems: true },
  phrases: { label: "Quick phrases", hint: "Text-only phrases that are spoken when tapped — like Recommend answer.", hasItems: true },
  yesno: { label: "Yes / No", hint: "The built-in Yes / No answer page.", hasItems: false },
  clock: { label: "Clock", hint: "The built-in alarm and timer page.", hasItems: false },
};

export const text = (v: Partial<I18n> | undefined, lang: Lang) => v?.[lang] || v?.en || "";

/** boardlib.spoken(): what the device says for an item. */
export function spoken(card: BoardCard, item: BoardItem, lang: Lang) {
  if (card.type === "grid") return text(item.message, lang) || text(item.label, lang);
  const label = text(item.label, lang);
  const tpl = text(card.speak_template, lang) || "{text}";
  return tpl.replaceAll("{text}", label).replaceAll("{lower}", label.toLowerCase());
}

const ID_RE = /^[a-z0-9][a-z0-9_-]{0,39}$/;
const COLOR_RE = /^#[0-9a-fA-F]{6}$/;

/** Light version of normalize_board(): returns the first problem, or null. */
export function boardProblem(b: Board): string | null {
  const visible = b.cards.filter((c) => c.visible).length;
  if (!b.cards.length) return "Add at least one card.";
  if (!visible) return "At least one card must be visible.";
  if (visible > LIMITS.cards) return `The device menu fits at most ${LIMITS.cards} visible cards — hide or delete ${visible - LIMITS.cards}.`;
  const ids = new Set<string>();
  for (const c of b.cards) {
    const name = c.title.en || "A card";
    if (!c.title.en.trim()) return "Every card needs an English name.";
    if (!ID_RE.test(c.id) || ids.has(c.id)) return `“${name}” has an invalid id.`;
    ids.add(c.id);
    if (!COLOR_RE.test(c.color) || !COLOR_RE.test(c.accent)) return `“${name}” has an invalid colour.`;
    const max = c.type === "grid" ? LIMITS.gridItems : LIMITS.items;
    if (c.items.length > max) return `“${name}” can have at most ${max} sub-cards.`;
    const itemIds = new Set<string>();
    for (const it of c.items) {
      if (!it.label.en.trim()) return `Every sub-card in “${name}” needs an English name.`;
      if (itemIds.has(it.id)) return `Two sub-cards in “${name}” share an id.`;
      itemIds.add(it.id);
    }
  }
  return null;
}

/** Make a short unique id from a name ("My Family" -> "my-family-2"). */
export function makeId(name: string, taken: Iterable<string>) {
  const used = new Set(taken);
  const base = name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 32) || "card";
  let id = base;
  for (let n = 2; used.has(id); n++) id = `${base}-${n}`;
  return id;
}

export function newCard(type: CardType, taken: Iterable<string>): BoardCard {
  const names: Record<CardType, string> = {
    list: "New pictures", grid: "New grid", phrases: "New phrases", yesno: "Yes / No", clock: "Clock",
  };
  const t = { en: names[type], th: "" };
  return {
    id: makeId(t.en, taken), type, title: t, description: { en: "", th: "" }, page_title: { ...t },
    color: "#D6EAF8", accent: "#D6EAF8", image: "", visible: true,
    speak: type !== "list", speak_template: { en: "", th: "" }, large_text: type !== "grid", items: [],
  };
}

export function newItem(card: BoardCard): BoardItem {
  const item: BoardItem = { id: makeId("item", card.items.map((i) => i.id)), label: { en: "", th: "" }, image: "" };
  if (card.type === "grid") { item.message = { en: "", th: "" }; item.color = card.accent; }
  return item;
}

/** Every "assets/custom/..." picture a board uses (these must travel with the board). */
export function customImages(b: Board) {
  const out = new Set<string>();
  for (const c of b.cards) {
    if (c.image.startsWith("assets/custom/")) out.add(c.image);
    for (const it of c.items) if (it.image.startsWith("assets/custom/")) out.add(it.image);
  }
  return [...out];
}
