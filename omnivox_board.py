"""
OmniVox card board — the single description of every card the device shows.

Both programs use this module:
  * the client (app.py on the Raspberry Pi) loads the board to build its pages;
  * the client agent validates boards sent by the master and saves them.

The board lives in json_page/board.json:

{
  "version": 1,
  "updated": "2026-11-02T10:00:00Z",
  "cards": [
    {
      "id": "feeling",                       # unique, a-z 0-9 _ -
      "type": "list",                        # list | grid | phrases | yesno | clock
      "title": {"en": "Feeling", "th": "..."},          # text on the menu card
      "description": {"en": "...", "th": "..."},        # line under the title
      "page_title": {"en": "Feeling & Mood", "th": "..."},
      "color": "#F9E79F",                    # menu card colour
      "accent": "#F9E79F",                   # border / fallback colour on its page
      "image": "assets/feeling.png",         # logo on the menu card
      "visible": true,
      "speak": true,                         # list cards: say the item when tapped
      "speak_template": {"en": "I feel {lower}", "th": "ฉันรู้สึก {text}"},
      "large_text": true,
      "items": [                             # the sub-cards
        {"id": "happy", "label": {"en": "Happy", "th": "..."},
         "image": "assets/feeling_0.png",
         "message": {"en": "", "th": ""},    # grid cards: sentence that is spoken
         "color": "#F9E79F"}                 # grid cards: tile colour
      ]
    }
  ]
}

Card types:
  list     scrollable strip of pictures with a big preview (Food, Feeling, ...)
  grid     up to 8 large picture tiles that speak a sentence (Bathroom)
  phrases  text-only quick phrases that are always spoken (Recommend answer)
  yesno    the built-in Yes / No page (no sub-cards)
  clock    the built-in alarm & timer page (no sub-cards)
"""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import time
from datetime import datetime, timezone

BOARD_VERSION = 1
BOARD_FILENAME = "board.json"
CARD_TYPES = ("list", "grid", "phrases", "yesno", "clock")
TYPES_WITH_ITEMS = ("list", "grid", "phrases")
LANGS = ("en", "th")

MAX_CARDS = 12          # 3 rows of 4 on the 1280x800 menu
MAX_ITEMS = 80
MAX_GRID_ITEMS = 8
MAX_TEXT = 200
BACKUPS_KEPT = 10

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,39}$")
_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
_IMAGE_RE = re.compile(r"^assets/[A-Za-z0-9_\-./]{1,120}\.(png|jpe?g|webp|gif)$", re.IGNORECASE)


class BoardError(ValueError):
    """Raised when a board is malformed. The message is safe to show to a user."""


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
def text(value: dict | None, lang: str) -> str:
    """Pick the text for a language, falling back to English."""
    if not value:
        return ""
    return value.get(lang) or value.get("en") or ""


def spoken(card: dict, item: dict, lang: str) -> str:
    """The sentence the device says when an item of this card is chosen."""
    if card["type"] == "grid":
        return text(item.get("message"), lang) or text(item.get("label"), lang)
    label = text(item.get("label"), lang)
    template = text(card.get("speak_template"), lang) or "{text}"
    return template.replace("{text}", label).replace("{lower}", label.lower())


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Validation / normalisation
# ---------------------------------------------------------------------------
def _i18n(raw, where: str, required: bool = False) -> dict:
    if raw is None:
        raw = {}
    if isinstance(raw, str):
        raw = {"en": raw}
    if not isinstance(raw, dict):
        raise BoardError(f"{where} must be text")
    out = {}
    for lang in LANGS:
        v = raw.get(lang, "")
        if not isinstance(v, str):
            raise BoardError(f"{where} ({lang}) must be text")
        v = " ".join(v.split()) if lang != "th" else v.strip()
        if len(v) > MAX_TEXT:
            raise BoardError(f"{where} ({lang}) is longer than {MAX_TEXT} characters")
        out[lang] = v
    if required and not out["en"]:
        raise BoardError(f"{where} needs an English text")
    return out


def _color(raw, where: str, default: str) -> str:
    if raw in (None, ""):
        return default
    if not isinstance(raw, str) or not _COLOR_RE.match(raw):
        raise BoardError(f"{where} must be a colour like #AED6F1")
    return raw.upper()


def _image(raw, where: str) -> str:
    if raw in (None, ""):
        return ""
    if not isinstance(raw, str) or ".." in raw or not _IMAGE_RE.match(raw):
        raise BoardError(f"{where} must be a picture inside assets/")
    return raw


def _id(raw, where: str, taken: set) -> str:
    if not isinstance(raw, str) or not _ID_RE.match(raw):
        raise BoardError(f"{where} id must be 1-40 lowercase letters, digits, - or _")
    if raw in taken:
        raise BoardError(f"{where} id '{raw}' is used twice")
    taken.add(raw)
    return raw


def normalize_board(raw) -> dict:
    """Validate a board (e.g. one sent by the master) and fill in defaults."""
    if not isinstance(raw, dict) or not isinstance(raw.get("cards"), list):
        raise BoardError("A board needs a list of cards")
    cards_in = raw["cards"]
    if not cards_in:
        raise BoardError("A board needs at least one card")

    card_ids: set = set()
    cards = []
    for ci, c in enumerate(cards_in):
        where = f"Card {ci + 1}"
        if not isinstance(c, dict):
            raise BoardError(f"{where} is malformed")
        ctype = c.get("type")
        if ctype not in CARD_TYPES:
            raise BoardError(f"{where} has an unknown type '{ctype}'")
        card = {
            "id": _id(c.get("id"), where, card_ids),
            "type": ctype,
            "title": _i18n(c.get("title"), f"{where} title", required=True),
            "description": _i18n(c.get("description"), f"{where} description"),
            "page_title": _i18n(c.get("page_title"), f"{where} page title"),
            "color": _color(c.get("color"), f"{where} colour", "#D6EAF8"),
            "accent": _color(c.get("accent"), f"{where} accent colour", "#D6EAF8"),
            "image": _image(c.get("image"), f"{where} logo"),
            "visible": bool(c.get("visible", True)),
            "speak": bool(c.get("speak", ctype != "list")),
            "speak_template": _i18n(c.get("speak_template"), f"{where} spoken sentence"),
            "large_text": bool(c.get("large_text", False)),
            "items": [],
        }
        where = f"'{card['title']['en']}'"
        if not card["page_title"]["en"]:
            card["page_title"] = dict(card["title"])

        items_in = c.get("items") or []
        if ctype in TYPES_WITH_ITEMS:
            if not isinstance(items_in, list):
                raise BoardError(f"{where} sub-cards must be a list")
            limit = MAX_GRID_ITEMS if ctype == "grid" else MAX_ITEMS
            if len(items_in) > limit:
                raise BoardError(f"{where} can have at most {limit} sub-cards")
            item_ids: set = set()
            for ii, it in enumerate(items_in):
                iw = f"{where} sub-card {ii + 1}"
                if not isinstance(it, dict):
                    raise BoardError(f"{iw} is malformed")
                item = {
                    "id": _id(it.get("id"), iw, item_ids),
                    "label": _i18n(it.get("label"), f"{iw} name", required=True),
                    "image": _image(it.get("image"), f"{iw} picture"),
                }
                if ctype == "grid":
                    item["message"] = _i18n(it.get("message"), f"{iw} sentence")
                    item["color"] = _color(it.get("color"), f"{iw} colour", card["accent"])
                card["items"].append(item)
        cards.append(card)

    if sum(1 for c in cards if c["visible"]) > MAX_CARDS:
        raise BoardError(f"The menu can show at most {MAX_CARDS} cards")
    if not any(c["visible"] for c in cards):
        raise BoardError("At least one card must be visible")

    return {"version": BOARD_VERSION, "updated": raw.get("updated") or utc_now(), "cards": cards}


# ---------------------------------------------------------------------------
# Load / save
# ---------------------------------------------------------------------------
def board_path(json_dir: str) -> str:
    return os.path.join(json_dir, BOARD_FILENAME)


def load_board(json_dir: str = "json_page") -> dict:
    """Load board.json, creating it from the older per-page files the first time."""
    path = board_path(json_dir)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return normalize_board(json.load(f))
    board = migrate_legacy(json_dir)
    save_board(json_dir, board, backup=False)
    return board


def save_board(json_dir: str, board: dict, backup: bool = True) -> dict:
    """Validate and atomically write board.json, keeping a few old copies."""
    board = normalize_board(board)
    board["updated"] = utc_now()
    path = board_path(json_dir)
    if backup and os.path.exists(path):
        bdir = os.path.join(json_dir, "backups")
        os.makedirs(bdir, exist_ok=True)
        shutil.copy2(path, os.path.join(bdir, f"board-{time.strftime('%Y%m%d-%H%M%S')}.json"))
        old = sorted(n for n in os.listdir(bdir) if n.startswith("board-"))
        for name in old[:-BACKUPS_KEPT]:
            os.remove(os.path.join(bdir, name))
    fd, tmp = tempfile.mkstemp(dir=json_dir, prefix=".board-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(board, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)
    return board


# ---------------------------------------------------------------------------
# One-time migration from the original files (cards.json, food.json, ...)
# ---------------------------------------------------------------------------
_LEGACY = {
    # menu title: (id, type, page title, data file, image prefix, accent, speak, template, large)
    "FOOD": ("food", "list", "FOOD MENU", "food.json", "food", "#FDEBD0", False, None, False),
    "FEELING": ("feeling", "list", "FEELING & MOOD", "feelings.json", "feeling", "#F9E79F", True,
                {"en": "I feel {lower}", "th": "ฉันรู้สึก {text}"}, True),
    "POSITION & COMFORT": ("position", "list", "POSITION & COMFORT", "position.json", "position",
                           "#D6EAF8", True, None, True),
    "BATHROOM": ("bathroom", "grid", "BATHROOM ASSISTANCE", "bathroom.json", None, "#D1F2EB", True, None, False),
    "YES / NO": ("yesno", "yesno", "CHOOSE ANSWER", None, None, "#D5F5E3", True, None, False),
    "ENTERTAINMENT": ("entertainment", "list", "ENTERTAINMENT", "entertainment.json", "entertainment",
                      "#D5F5E3", False, None, False),
    "RECOMMEND ANSWER": ("recommend", "phrases", "RECOMMENDATIONS", "recommend.json", None, "#FCF3CF",
                         True, None, True),
    "CLOCK": ("clock", "clock", "CLOCK SETTINGS", None, None, "#FAD7A1", False, None, False),
}


def _slug(s: str, taken: set) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:32] or "item"
    out, n = base, 2
    while out in taken:
        out, n = f"{base}-{n}", n + 1
    taken.add(out)
    return out


def migrate_legacy(json_dir: str) -> dict:
    def read(name):
        with open(os.path.join(json_dir, name), "r", encoding="utf-8") as f:
            return json.load(f)

    tr = {x["language"]: x["data"] for x in read("translation.json")}

    def t(key, lang):
        m = tr.get(lang, {})
        norm = " ".join(key.split()).upper()
        return m.get(key, m.get(key.upper(), m.get(norm, key)))

    def both(key):
        return {"en": t(key, "en"), "th": t(key, "th")}

    cards = []
    legacy_cards = sorted(read("cards.json"), key=lambda c: (c["row"], c["column"]))
    for c in legacy_cards:
        cid, ctype, page, data_file, prefix, accent, speak, template, large = _LEGACY.get(
            c["title"], (None, "list", c["title"], None, None, "#D6EAF8", False, None, False))
        cid = cid or _slug(c["title"], set())
        card = {
            "id": cid, "type": ctype,
            "title": both(c["title"]),
            "description": both(c["description"].upper()),
            "page_title": both(page),
            "color": c["color"], "accent": accent,
            "image": c["image"], "visible": True,
            "speak": speak, "speak_template": template or {},
            "large_text": large, "items": [],
        }
        if ctype in ("list", "phrases") and data_file:
            blocks = {b["language"]: b["data"] for b in read(data_file)}
            en, th = blocks.get("en", {}), blocks.get("th", {})
            keys = list(en.keys()) if isinstance(en, dict) else list(range(len(en)))
            taken: set = set()
            for i, k in enumerate(keys):
                label_en = en[k]
                label_th = th.get(k, "") if isinstance(th, dict) else (th[i] if i < len(th) else "")
                card["items"].append({
                    "id": _slug(label_en, taken),
                    "label": {"en": label_en, "th": label_th},
                    # The original app looked pictures up by position: assets/<prefix>_<index>.png
                    "image": f"assets/{prefix}_{i}.png" if prefix else "",
                })
        elif ctype == "grid" and data_file:
            payload = read(data_file)
            btr = {x["language"]: x["data"] for x in payload.get("translations", [])}

            def bt(key, lang):
                return btr.get(lang, {}).get(key) or t(key, lang)

            taken = set()
            for it in sorted(payload.get("items", []), key=lambda x: (x.get("row", 0), x.get("col", 0))):
                msg = it.get("message_key", it.get("message", ""))
                card["items"].append({
                    "id": _slug(it["id"], taken),
                    "label": {"en": bt(it["id"], "en"), "th": bt(it["id"], "th")},
                    "message": {"en": bt(msg, "en"), "th": bt(msg, "th")},
                    "color": it.get("color", accent),
                    "image": it.get("image_path", ""),
                })
        cards.append(card)
    return normalize_board({"cards": cards})


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "json_page"
    b = load_board(target)
    print(f"{board_path(target)}: {len(b['cards'])} cards, "
          f"{sum(len(c['items']) for c in b['cards'])} sub-cards")
