import type { AppData, CatKey, Lang } from "./types";

/** Port of translate() in app.py: exact key, then UPPER, then whitespace-normalised UPPER. */
export function translate(data: AppData, text: string, lang: Lang): string {
  if (!text) return "";
  const map = data.translations[lang] ?? {};
  const norm = text.split(/\s+/).join(" ").toUpperCase();
  return map[text] ?? map[text.toUpperCase()] ?? map[norm] ?? text;
}

/** BathroomPage._bathroom_translate */
export function bathTranslate(data: AppData, text: string, lang: Lang): string {
  return data.bathroom.translations[lang]?.[text] ?? translate(data, text, lang);
}

export interface CategoryConfig {
  title: string;
  prefix: string;
  color: string;
  translate: boolean; // translate_item_names
  speak: boolean;     // speak_on_select
  large: boolean;     // LARGE_BOX_LABEL_FONT_PX
  textOnly?: boolean; // RecommendPage shows text instead of a photo
  say?: (item: string, lang: Lang) => string;
}

export const CATEGORIES: Record<CatKey, CategoryConfig> = {
  food: { title: "FOOD MENU", prefix: "food", color: "#FDEBD0", translate: false, speak: false, large: false },
  feeling: {
    title: "FEELING & MOOD", prefix: "feeling", color: "#F9E79F", translate: true, speak: true, large: true,
    say: (t, lang) => (lang === "th" ? `ฉันรู้สึก ${t}` : `I feel ${t.toLowerCase()}`),
  },
  position: { title: "POSITION & COMFORT", prefix: "position", color: "#D6EAF8", translate: true, speak: true, large: true },
  entertainment: { title: "ENTERTAINMENT", prefix: "entertainment", color: "#D5F5E3", translate: false, speak: false, large: false },
  recommend: { title: "RECOMMENDATIONS", prefix: "recommend", color: "#FCF3CF", translate: true, speak: true, large: true, textOnly: true },
};

export function categoryItems(data: AppData, key: CatKey, lang: Lang): string[] {
  const c = data.categories[key];
  const l = CATEGORIES[key].translate ? lang : "en";
  return c[l] ?? c.en ?? [];
}

export const MOODS = [
  { icon: "mood_great", label: "Great", bg: "#D5F5E3", fg: "#4D908E", reply: "You look wonderful today!" },
  { icon: "mood_good", label: "Good", bg: "#AED6F1", fg: "#2471A3", reply: "Glad to hear it!" },
  { icon: "mood_okay", label: "Okay", bg: "#F9E79F", fg: "#B7950B", reply: "We are here for you." },
  { icon: "mood_not_great", label: "Not great", bg: "#FADBD8", fg: "#A93226", reply: "Let us help you feel better." },
  { icon: "mood_in_pain", label: "In pain", bg: "#EBDEF0", fg: "#76448A", reply: "Staff will be notified right away." },
] as const;

/** MainMenuPage.navigate */
export const MENU_NAV: Record<string, string> = {
  "FOOD": "food",
  "FEELING": "feeling",
  "POSITION & COMFORT": "position",
  "BATHROOM": "bathroom",
  "YES / NO": "yesno",
  "ENTERTAINMENT": "entertainment",
  "RECOMMEND ANSWER": "recommend",
  "CLOCK": "clock",
};
