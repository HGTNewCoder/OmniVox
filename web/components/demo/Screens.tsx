"use client";

import { createContext, useContext, useEffect, useLayoutEffect, useRef, useState, type CSSProperties } from "react";
import { img } from "@/lib/asset";
import { text, type BoardCard } from "@/lib/board";
import { MOODS } from "@/lib/i18n";
import type { Sim } from "./useSimulator";

const STEP = 155; // box (140) + spacing (15), as in build_big_screen_page
const pad = (n: number) => String(n).padStart(2, "0");

/** Current CSS scale of the 1280x800 canvas — needed to convert mouse drags. */
export const ScaleContext = createContext(1);

type Props = { sim: Sim };

/** Image that swaps to a coloured text panel if the file is missing (app.py does the same). */
function CoverImage({ src, alt, bg }: { src: string; alt: string; bg: string }) {
  const [failed, setFailed] = useState(false);
  if (failed) return <div className="bs-fallback" style={{ background: bg }}>{alt}</div>;
  return <img src={src} alt={alt} onError={() => setFailed(true)} />;
}

/** Briefly applies a "pressed" class, like CommBox's 150 ms colour flash. */
function usePressed(ms = 150) {
  const [pressed, setPressed] = useState(false);
  const flash = () => { setPressed(true); setTimeout(() => setPressed(false), ms); };
  return [pressed, flash] as const;
}

// ---------------------------------------------------------------- Welcome
export function WelcomeScreen({ sim }: Props) {
  const { t, alarm, timer, mood } = sim;
  const hasStatus = !!alarm || timer > 0;
  const fade = (ms: number): CSSProperties => ({ animationDelay: `${200 + ms}ms` });
  return (
    <section className={`page pg-welcome${hasStatus ? " has-status" : ""}`} key={sim.run}>
      <div className="fade" style={fade(0)}>
        <div className="w-name">{t("Good morning, Mr. K.D")}</div>
        <div className="w-sub">{t("Welcome to your daily well-being check-in")}</div>
      </div>

      {hasStatus && (
        <div className="w-status">
          {timer > 0 && (
            <>
              <div className="w-timer">Timer: {pad(Math.floor(timer / 60))}:{pad(timer % 60)} remaining</div>
              <button className="w-cancel-timer" onClick={sim.cancelTimer}>{t("Cancel Timer")}</button>
            </>
          )}
          {alarm && (
            <div className="alarm-banner">
              <img className="ab-icon" src={img("clock")} alt="" />
              <div className="ab-text">
                <span className="ab-l1">{t("ALARM SCHEDULED")}</span>
                <span className="ab-time">{alarm}</span>
                <span className="ab-l3">{t("RINGS ONCE — TAP BELL TO DISMISS")}</span>
              </div>
              <div className="ab-btns">
                <button onClick={() => sim.go("clock")}>{t("EDIT TIME")}</button>
                <button onClick={sim.cancelAlarm}>{t("CANCEL ALARM")}</button>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="w-q fade" style={fade(700)}>{t("How are you feeling today?")}</div>
      <div className="moods">
        {MOODS.map((m, i) => (
          <button
            key={m.label}
            className="mood fade"
            style={{ ...fade(1300 + i * 200), ...(mood === i ? { background: m.bg, borderColor: m.fg } : {}) }}
            onClick={() => sim.selectMood(i)}
          >
            <img src={img(m.icon)} alt="" />
            <span style={{ color: m.fg }}>{t(m.label)}</span>
          </button>
        ))}
      </div>
      <div className="w-reply">{mood !== null ? t(MOODS[mood].reply) : ""}</div>
      <button className="w-continue fade" style={fade(2600)} onClick={() => sim.go("menu")}>
        {t("Continue to Menu")}
      </button>
    </section>
  );
}

// ---------------------------------------------------------------- Main menu
function MenuCard({ sim, card }: Props & { card: BoardCard }) {
  const [pressed, flash] = usePressed();
  return (
    <div className={`card${pressed ? " pressed" : ""}`} onClick={() => { flash(); sim.openCard(card.id); }}>
      <div className="card-top" style={{ background: card.color }}>
        <div className="card-title">{text(card.title, sim.lang)}</div>
        {card.image && <img src={sim.image(card.image)} alt="" />}
      </div>
      <div className="card-bottom">
        <div className="card-desc">{text(card.description, sim.lang)}</div>
        <button className="card-btn">{sim.t("TALK WITH US")}</button>
      </div>
    </div>
  );
}

export function MenuScreen({ sim }: Props) {
  const { t, lang, today } = sim;
  const [bellPressed, flashBell] = usePressed(200);
  const cards = sim.board.cards.filter((c) => c.visible);
  const rows = Math.max(1, Math.ceil(cards.length / 4));
  const date = !today
    ? " "
    : lang === "th"
      ? today.toLocaleDateString("th-TH", { dateStyle: "full" })
      : today.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" });
  return (
    <section className={`page pg-menu rows-${rows}`}>
      <div className="mm-header">
        <div className="mm-titles">
          <div className="mm-title">{t("MY DAILY WELL-BEING")}</div>
          <div className="mm-date">{date}</div>
        </div>
        <button className="lang-btn" onClick={sim.toggleLang}>{lang === "th" ? "THAI / ไทย" : "ENGLISH"}</button>
      </div>
      <div className="mm-grid" style={{ gridTemplateRows: `repeat(${rows}, 1fr) ${rows > 2 ? 96 : 118}px` }}>
        {cards.map((c) => <MenuCard key={c.id} sim={sim} card={c} />)}
        <div className={`bell${bellPressed ? " pressed" : ""}`} onClick={() => { flashBell(); sim.callForHelp(); }}>
          <img src={img("bell")} alt="" />
          <div className="bell-text">
            <div className="bell-title">{t("CALL FOR HELP")}</div>
            <div className="bell-desc">{t("PRESS TO ALERT A STAFF MEMBER IMMEDIATELY.")}</div>
          </div>
          <div className="bell-call">{t("CALL NOW")}</div>
        </div>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------- List & phrases pages
export function ListScreen({ sim, card }: Props & { card: BoardCard }) {
  const textOnly = card.type === "phrases";
  const items = card.items.map((it) => text(it.label, sim.lang));
  const idx = Math.min(sim.cur[card.id] ?? 0, Math.max(0, items.length - 1));
  const scale = useContext(ScaleContext);
  const strip = useRef<HTMLDivElement>(null);
  const lockUntil = useRef(0);
  const drag = useRef({ down: false, moved: false, x: 0, left: 0 });

  // Restore the strip position when the page is shown (hbar.setValue(idx * total_step)).
  useLayoutEffect(() => {
    if (!strip.current || textOnly) return;
    lockUntil.current = Date.now() + 300;
    strip.current.style.scrollBehavior = "auto";
    strip.current.scrollLeft = idx * STEP;
    strip.current.style.scrollBehavior = "";
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Vertical mouse wheel scrolls the strip sideways (needs a non-passive listener).
  useEffect(() => {
    const el = strip.current;
    if (!el) return;
    const onWheel = (e: WheelEvent) => {
      if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) { el.scrollLeft += e.deltaY; e.preventDefault(); }
    };
    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
  }, []);

  const onScroll = () => {
    if (textOnly || !strip.current || Date.now() < lockUntil.current) return; // phrases: no-op
    const i = Math.round(strip.current.scrollLeft / STEP);
    if (i >= 0 && i < items.length) sim.scrolledTo(card.id, i);
  };

  // Mouse drag-to-scroll, like QScroller's LeftMouseButtonGesture.
  const onPointerDown = (e: React.PointerEvent) => {
    if (e.pointerType !== "mouse" || !strip.current) return;
    drag.current = { down: true, moved: false, x: e.clientX, left: strip.current.scrollLeft };
  };
  const onPointerMove = (e: React.PointerEvent) => {
    const d = drag.current;
    if (!d.down || !strip.current) return;
    const dx = (e.clientX - d.x) / scale;
    if (Math.abs(dx) > 6) { d.moved = true; strip.current.classList.add("dragging"); }
    if (d.moved) strip.current.scrollLeft = d.left - dx;
  };
  const endDrag = () => {
    drag.current.down = false;
    strip.current?.classList.remove("dragging");
  };

  const click = (i: number) => {
    if (drag.current.moved) { drag.current.moved = false; return; }
    if (!textOnly && strip.current) {
      lockUntil.current = Date.now() + 800;
      strip.current.scrollLeft = i * STEP;
    }
    sim.selectItem(card, i);
  };

  const pic = (i: number) => card.items[i]?.image ?? "";

  return (
    <section className="page pg-cat">
      <div className="pg-header">{text(card.page_title, sim.lang)}</div>
      <div className="big-screen" style={textOnly ? { background: card.accent } : undefined}>
        {items.length === 0
          ? <div className="bs-fallback" style={{ background: card.accent }}>—</div>
          : textOnly
            ? <div className="bs-text">{items[idx]}</div>
            : pic(idx)
              ? <CoverImage key={`${card.id}-${idx}-${pic(idx)}`} src={sim.image(pic(idx))} alt={items[idx]} bg={card.accent} />
              : <div className="bs-fallback" style={{ background: card.accent }}>{items[idx]}</div>}
      </div>
      <div
        className="strip"
        ref={strip}
        onScroll={onScroll}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={endDrag}
        onPointerLeave={endDrag}
      >
        {items.map((name, i) => (
          <button
            key={card.items[i].id}
            className={`box${card.large_text ? " large" : ""}${textOnly && i === idx ? " sel" : ""}`}
            style={{ "--bc": card.accent } as CSSProperties}
            onClick={() => click(i)}
          >
            <span>{name}</span>
          </button>
        ))}
      </div>
      {/* Warm up the next photos so scrolling feels instant */}
      {!textOnly && (
        <div hidden>
          {[idx + 1, idx + 2].filter((n) => n < items.length && pic(n)).map((n) => <img key={n} src={sim.image(pic(n))} alt="" />)}
        </div>
      )}
      <button className="back-btn" onClick={() => sim.go("menu")}>{sim.t("GO BACK")}</button>
    </section>
  );
}

// ---------------------------------------------------------------- Grid page (Bathroom)
function GridTile({ sim, card, idx }: Props & { card: BoardCard; idx: number }) {
  const [pressed, flash] = usePressed();
  const item = card.items[idx];
  return (
    <div className={`bcard${pressed ? " pressed" : ""}`} onClick={() => { flash(); sim.selectGridItem(card, idx); }}>
      <div
        className="bcard-img"
        style={item.image ? { backgroundImage: `url('${sim.image(item.image)}')` } : { background: item.color ?? card.accent }}
      />
      <div className="bcard-desc">{text(item.label, sim.lang)}</div>
    </div>
  );
}

export function GridScreen({ sim, card }: Props & { card: BoardCard }) {
  const cols = card.items.length > 6 ? 4 : 3;
  return (
    <section className="page pg-bath">
      <div className="pg-header" style={{ padding: "20px 0 16px" }}>{text(card.page_title, sim.lang)}</div>
      <div className="bath-grid" style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
        {card.items.map((it, i) => <GridTile key={it.id} sim={sim} card={card} idx={i} />)}
      </div>
      <button className="back-btn" style={{ marginBottom: 20 }} onClick={() => sim.go("menu")}>{sim.t("GO BACK")}</button>
    </section>
  );
}

// ---------------------------------------------------------------- Yes / No
export function YesNoScreen({ sim }: Props) {
  const { t, answer } = sim;
  const card = (choice: "YES" | "NO", bg: string, fg: string) => (
    <div className="yn-card" style={{ background: bg }}>
      <img src={img(choice.toLowerCase())} alt="" />
      <div className="yn-label" style={{ color: fg }}>{t(choice)}</div>
      <button style={{ background: fg }} onClick={() => sim.answerYesNo(choice)}>{t("CONFIRM")}</button>
    </div>
  );
  if (answer) {
    return (
      <section className="page pg-yesno" style={{ background: answer === "YES" ? "#D5F5E3" : "#FADBD8" }}>
        <div className="yn-result"><img src={img(answer.toLowerCase())} alt={answer} /></div>
      </section>
    );
  }
  return (
    <section className="page pg-yesno">
      <div className="yn-title">{t("CHOOSE ANSWER")}</div>
      <div className="yn-cards">
        {card("YES", "#D5F5E3", "#4D908E")}
        {card("NO", "#FADBD8", "#A93226")}
      </div>
      <button className="back-btn" onClick={() => sim.go("menu")}>{t("GO BACK")}</button>
    </section>
  );
}

// ---------------------------------------------------------------- Clock
export function ClockScreen({ sim }: Props) {
  const { t, clock } = sim;
  const alarm = clock.mode === "ALARM";
  return (
    <section className="page pg-clock">
      <div className="ck-top">{t("CLOCK SETTINGS")}</div>
      <div className="ck-body">
        <div className="ck-modes">
          <button className={alarm ? "on" : ""} onClick={() => sim.setClockMode("ALARM")}>{t("ALARM")}</button>
          <button className={!alarm ? "on" : ""} onClick={() => sim.setClockMode("TIMER")}>{t("TIMER")}</button>
        </div>
        <div className="ck-card">
          <div className="ck-spin">
            <div className="ck-arrows">
              <button onClick={() => sim.spin(1, 0)} aria-label="Hour up">▲</button>
              <button onClick={() => sim.spin(-1, 0)} aria-label="Hour down">▼</button>
            </div>
            <div className="ck-time">{pad(clock.h)}:{pad(clock.m)}</div>
            <div className="ck-arrows">
              <button onClick={() => sim.spin(0, 1)} aria-label="Minute up">▲</button>
              <button onClick={() => sim.spin(0, -1)} aria-label="Minute down">▼</button>
            </div>
          </div>
          <div className="ck-label">{t(alarm ? "Tap arrows to set alarm" : "Tap arrows to set duration")}</div>
        </div>
        <div className="ck-actions">
          <button style={{ background: "#BDBDBD" }} onClick={() => sim.go("menu")}>{t("CANCEL")}</button>
          <button style={{ background: "#4D908E" }} onClick={sim.confirmClock}>{t(alarm ? "SET ALARM" : "START TIMER")}</button>
        </div>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------- Alert
export function AlertScreen({ sim }: Props) {
  const { alert } = sim;
  return (
    <section className={`page pg-alert${alert.emergency ? " emergency" : ""}`}>
      <img className="al-icon" src={img(alert.emergency ? "bell" : "clock")} alt="" />
      <div className="al-msg">{sim.t(alert.text)}</div>
      <button className="al-off" onClick={sim.alertOff}>{sim.t("TURN OFF")}</button>
    </section>
  );
}

// ---------------------------------------------------------------- Full-screen item
export function FullItemScreen({ sim }: Props) {
  const { full } = sim;
  if (!full) return null;
  return (
    <section className="page pg-full">
      <div className="fs-img">
        <CoverImage key={full.image} src={full.image} alt={full.name} bg={full.fallbackBg} />
      </div>
      <div className={`fs-bar${sim.fullOk ? " ok" : ""}`}>
        <button className="fs-back" onClick={sim.fullBack}>{sim.t("GO BACK")}</button>
        <div className="fs-name">
          {full.name}
          {full.sub && <small>{full.sub}</small>}
        </div>
        <button className="fs-select" onClick={sim.fullSelect}>{sim.t("SELECT")}</button>
      </div>
    </section>
  );
}
