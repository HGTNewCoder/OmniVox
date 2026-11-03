import type { Board, Lang } from "./board";

export type { Lang };

/** Everything the simulator needs, read from ../json_page at build time. */
export interface AppData {
  translations: Record<string, Record<string, string>>; // UI words (json_page/translation.json)
  board: Board;                                           // the cards (json_page/board.json)
}
