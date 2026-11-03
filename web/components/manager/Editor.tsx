"use client";

import { useState } from "react";
import type { ImageResolver } from "@/lib/asset";
import {
  LIMITS, newCard, newItem, TYPE_INFO,
  type Board, type BoardCard, type BoardItem, type CardType, type I18n,
} from "@/lib/board";

export type PickTarget = { card: string; item?: number };

interface Props {
  board: Board;
  selected: string | null;
  resolve: ImageResolver;
  onChange: (b: Board) => void;
  onSelect: (id: string | null) => void;
  onPick: (t: PickTarget) => void;
}

const move = <T,>(list: T[], from: number, to: number) => {
  if (to < 0 || to >= list.length) return list;
  const out = list.slice();
  const [x] = out.splice(from, 1);
  out.splice(to, 0, x);
  return out;
};

function Thumb({ src, color, size = 44 }: { src: string; color: string; size?: number }) {
  return (
    <span className="mg-logo" style={{ background: color, width: size, height: size }}>
      {src ? <img src={src} alt="" /> : <span aria-hidden="true">＋</span>}
    </span>
  );
}

/** Two inputs side by side: English and Thai. */
function Bilingual({ label, value, onChange, placeholder, hint, required }: {
  label: string; value: I18n; onChange: (v: I18n) => void; placeholder?: string; hint?: string; required?: boolean;
}) {
  return (
    <div className="mg-field">
      <span className="mg-label">{label}{required && <i aria-hidden="true"> *</i>}</span>
      <div className="mg-bi">
        <label>
          <span className="mg-lang">EN</span>
          <input className="mg-input" value={value.en} maxLength={LIMITS.text} placeholder={placeholder}
            onChange={(e) => onChange({ ...value, en: e.target.value })} />
        </label>
        <label>
          <span className="mg-lang" lang="th">ไทย</span>
          <input className="mg-input" lang="th" value={value.th} maxLength={LIMITS.text} placeholder="—"
            onChange={(e) => onChange({ ...value, th: e.target.value })} />
        </label>
      </div>
      {hint && <span className="mg-hint">{hint}</span>}
    </div>
  );
}

function ColorField({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <label className="mg-field mg-color">
      <span className="mg-label">{label}</span>
      <span className="mg-color-row">
        <input type="color" value={value} onChange={(e) => onChange(e.target.value.toUpperCase())} />
        <code>{value}</code>
      </span>
    </label>
  );
}

function Toggle({ label, checked, onChange, hint }: { label: string; checked: boolean; onChange: (v: boolean) => void; hint?: string }) {
  return (
    <label className="mg-toggle">
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      <span className="mg-switch" aria-hidden="true" />
      <span><b>{label}</b>{hint && <small>{hint}</small>}</span>
    </label>
  );
}

// ---------------------------------------------------------------- card list
function CardList({ board, selected, resolve, onChange, onSelect }: Omit<Props, "onPick">) {
  const [adding, setAdding] = useState(false);
  const cards = board.cards;
  const visible = cards.filter((c) => c.visible).length;
  const has = (t: CardType) => cards.some((c) => c.type === t);

  const add = (type: CardType) => {
    const card = newCard(type, cards.map((c) => c.id));
    onChange({ ...board, cards: [...cards, card] });
    onSelect(card.id);
    setAdding(false);
  };
  const setCards = (next: BoardCard[]) => onChange({ ...board, cards: next });

  return (
    <div className="mg-cards">
      <div className="mg-section-head">
        <h3>Cards <small>{visible} of {LIMITS.cards} shown on the menu</small></h3>
        <button className="btn btn-primary btn-sm" onClick={() => setAdding((a) => !a)} aria-expanded={adding}>＋ Add card</button>
      </div>
      {adding && (
        <div className="mg-add">
          {(["list", "grid", "phrases", "yesno", "clock"] as CardType[])
            .filter((t) => (t !== "yesno" && t !== "clock") || !has(t))
            .map((t) => (
              <button key={t} onClick={() => add(t)}>
                <b>{TYPE_INFO[t].label}</b>
                <span>{TYPE_INFO[t].hint}</span>
              </button>
            ))}
        </div>
      )}
      <ol className="mg-card-list">
        {cards.map((c, i) => (
          <li key={c.id} className={`${c.id === selected ? "on" : ""}${c.visible ? "" : " hidden-card"}`}>
            <button className="mg-card-main" onClick={() => onSelect(c.id)} aria-current={c.id === selected}>
              <Thumb src={resolve(c.image)} color={c.color} />
              <span className="mg-card-text">
                <b>{c.title.en || "Untitled"}</b>
                <small>
                  {TYPE_INFO[c.type].label}
                  {TYPE_INFO[c.type].hasItems && ` · ${c.items.length} sub-card${c.items.length === 1 ? "" : "s"}`}
                  {!c.visible && " · hidden"}
                </small>
              </span>
            </button>
            <span className="mg-row-tools">
              <button className="mg-icon-btn" onClick={() => setCards(move(cards, i, i - 1))} disabled={i === 0} aria-label={`Move ${c.title.en} up`}>▲</button>
              <button className="mg-icon-btn" onClick={() => setCards(move(cards, i, i + 1))} disabled={i === cards.length - 1} aria-label={`Move ${c.title.en} down`}>▼</button>
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}

// ---------------------------------------------------------------- sub-cards
function ItemsEditor({ card, resolve, update, onPick }: {
  card: BoardCard; resolve: ImageResolver; update: (c: BoardCard) => void; onPick: (t: PickTarget) => void;
}) {
  const [filter, setFilter] = useState("");
  const max = card.type === "grid" ? LIMITS.gridItems : LIMITS.items;
  const setItems = (items: BoardItem[]) => update({ ...card, items });
  const setItem = (i: number, patch: Partial<BoardItem>) =>
    setItems(card.items.map((it, j) => (j === i ? { ...it, ...patch } : it)));
  const pictures = card.type !== "phrases";
  const q = filter.trim().toLowerCase();
  const rows = card.items.map((it, i) => ({ it, i }))
    .filter(({ it }) => !q || `${it.label.en} ${it.label.th}`.toLowerCase().includes(q));

  return (
    <div className="mg-items">
      <div className="mg-section-head">
        <h3>Sub-cards <small>{card.items.length} of {max}</small></h3>
        <span className="mg-head-tools">
          {card.items.length > 8 && (
            <input className="mg-input mg-filter" type="search" placeholder="Find…" value={filter}
              onChange={(e) => setFilter(e.target.value)} aria-label="Find a sub-card" />
          )}
          <button
            className="btn btn-primary btn-sm"
            disabled={card.items.length >= max}
            onClick={() => { setFilter(""); setItems([...card.items, newItem(card)]); }}
          >＋ Add sub-card</button>
        </span>
      </div>
      {card.items.length === 0 && <p className="mg-empty">No sub-cards yet. Add the first one — it appears on the device as soon as you send.</p>}
      <ol className="mg-item-list">
        {rows.map(({ it, i }) => (
          <li key={it.id} className="mg-item">
            {pictures && (
              <button className="mg-item-pic" onClick={() => onPick({ card: card.id, item: i })} aria-label={`Change picture for ${it.label.en || "sub-card"}`}>
                <Thumb src={resolve(it.image)} color={it.color ?? card.accent} size={64} />
                <span>{it.image ? "Change" : "Add picture"}</span>
              </button>
            )}
            <div className="mg-item-fields">
              <Bilingual label="Name" required value={it.label} placeholder="e.g. Turn me over" onChange={(label) => setItem(i, { label })} />
              {card.type === "grid" && (
                <Bilingual label="Sentence it says" value={it.message ?? { en: "", th: "" }} placeholder="e.g. I need to use the toilet."
                  onChange={(message) => setItem(i, { message })} />
              )}
              {card.type === "grid" && <ColorField label="Tile colour" value={it.color ?? card.accent} onChange={(color) => setItem(i, { color })} />}
            </div>
            <span className="mg-row-tools vertical">
              <button className="mg-icon-btn" onClick={() => setItems(move(card.items, i, i - 1))} disabled={i === 0 || !!q} aria-label="Move up">▲</button>
              <button className="mg-icon-btn" onClick={() => setItems(move(card.items, i, i + 1))} disabled={i === card.items.length - 1 || !!q} aria-label="Move down">▼</button>
              <button className="mg-icon-btn danger" onClick={() => setItems(card.items.filter((_, j) => j !== i))} aria-label={`Delete ${it.label.en || "sub-card"}`}>🗑</button>
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}

// ---------------------------------------------------------------- one card
function CardForm({ board, card, resolve, onChange, onSelect, onPick }: Omit<Props, "selected"> & { card: BoardCard }) {
  const [confirmDelete, setConfirmDelete] = useState(false);
  const update = (next: BoardCard) => onChange({ ...board, cards: board.cards.map((c) => (c.id === card.id ? next : c)) });
  const set = (patch: Partial<BoardCard>) => update({ ...card, ...patch });
  // The page heading follows the card name until someone edits it separately.
  const setTitle = (title: I18n) => {
    const follow = (l: "en" | "th") => !card.page_title[l] || card.page_title[l] === card.title[l];
    set({
      title,
      page_title: { en: follow("en") ? title.en : card.page_title.en, th: follow("th") ? title.th : card.page_title.th },
    });
  };
  const info = TYPE_INFO[card.type];

  return (
    <div className="mg-form">
      <div className="mg-form-head">
        <button className="mg-logo-btn" onClick={() => onPick({ card: card.id })} aria-label="Change the card logo">
          <Thumb src={resolve(card.image)} color={card.color} size={84} />
          <span>Change logo</span>
        </button>
        <div>
          <span className="mg-type">{info.label}</span>
          <h2>{card.title.en || "Untitled card"}</h2>
          <p className="fine">{info.hint}</p>
        </div>
      </div>

      <div className="mg-grid2">
        <Bilingual label="Card name" required value={card.title} onChange={setTitle} />
        <Bilingual label="Page heading" value={card.page_title} onChange={(page_title) => set({ page_title })}
          hint="Shown at the top of the card's page." />
        <Bilingual label="Description" value={card.description} placeholder="One short line under the name"
          onChange={(description) => set({ description })} />
        <div className="mg-colors">
          <ColorField label="Card colour" value={card.color} onChange={(color) => set({ color })} />
          {info.hasItems && <ColorField label="Page colour" value={card.accent} onChange={(accent) => set({ accent })} />}
        </div>
      </div>

      <div className="mg-toggles">
        <Toggle label="Show on the menu" checked={card.visible} onChange={(visible) => set({ visible })} />
        {card.type === "list" && (
          <Toggle label="Speak when tapped" checked={card.speak} onChange={(speak) => set({ speak })}
            hint="Say the sub-card's name out loud." />
        )}
        {info.hasItems && card.type !== "grid" && (
          <Toggle label="Large text" checked={card.large_text} onChange={(large_text) => set({ large_text })} />
        )}
      </div>

      {(card.type === "phrases" || (card.type === "list" && card.speak)) && (
        <Bilingual label="Spoken sentence" value={card.speak_template} placeholder="{text}"
          onChange={(speak_template) => set({ speak_template })}
          hint="Use {text} for the sub-card name, or {lower} for it in lower case — e.g. “I feel {lower}”. Leave empty to say just the name." />
      )}

      {info.hasItems && <ItemsEditor card={card} resolve={resolve} update={update} onPick={onPick} />}

      <div className="mg-danger">
        {!confirmDelete
          ? <button className="btn btn-ghost btn-sm" onClick={() => setConfirmDelete(true)}>Delete this card…</button>
          : (
            <span>
              Delete “{card.title.en}”{card.items.length ? ` and its ${card.items.length} sub-cards` : ""}?{" "}
              <button className="btn btn-danger btn-sm" onClick={() => {
                onChange({ ...board, cards: board.cards.filter((c) => c.id !== card.id) });
                onSelect(null);
              }}>Delete</button>{" "}
              <button className="btn btn-ghost btn-sm" onClick={() => setConfirmDelete(false)}>Keep it</button>
            </span>
          )}
      </div>
    </div>
  );
}

export { CardList };

export function CardEditor(props: Props) {
  const card = props.board.cards.find((c) => c.id === props.selected);
  return card
    ? <CardForm key={card.id} {...props} card={card} />
    : <div className="mg-form mg-placeholder"><p>Choose a card on the left to edit its name, logo and sub-cards.</p></div>;
}
