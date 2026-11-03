import type { AppData, Lang } from "./types";

type Translations = AppData["translations"];

/** Port of translate() in app.py: exact key, then UPPER, then whitespace-normalised UPPER. */
export function translate(translations: Translations, text: string, lang: Lang): string {
  if (!text) return "";
  const map = translations[lang] ?? {};
  const norm = text.split(/\s+/).join(" ").toUpperCase();
  return map[text] ?? map[text.toUpperCase()] ?? map[norm] ?? text;
}

export const MOODS = [
  { icon: "mood_great", label: "Great", bg: "#D5F5E3", fg: "#4D908E", reply: "You look wonderful today!" },
  { icon: "mood_good", label: "Good", bg: "#AED6F1", fg: "#2471A3", reply: "Glad to hear it!" },
  { icon: "mood_okay", label: "Okay", bg: "#F9E79F", fg: "#B7950B", reply: "We are here for you." },
  { icon: "mood_not_great", label: "Not great", bg: "#FADBD8", fg: "#A93226", reply: "Let us help you feel better." },
  { icon: "mood_in_pain", label: "In pain", bg: "#EBDEF0", fg: "#76448A", reply: "Staff will be notified right away." },
] as const;
