export type Lang = "en" | "th";

export interface MenuCard {
  title: string;
  description: string;
  color: string;
  image: string; // asset name without extension, e.g. "food"
  row: number;
  column: number;
}

export interface BathroomItem {
  id: string;
  message: string;
  color: string;
  image: string; // asset name without extension
  row: number;
  col: number;
}

export type CatKey = "food" | "feeling" | "position" | "entertainment" | "recommend";

/** Everything the simulator needs, read from ../json_page at build time. */
export interface AppData {
  translations: Record<string, Record<string, string>>;
  cards: MenuCard[];
  bathroom: { items: BathroomItem[]; translations: Record<string, Record<string, string>> };
  categories: Record<CatKey, Partial<Record<Lang, string[]>>>;
}
