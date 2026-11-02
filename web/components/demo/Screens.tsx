"use client";

import { createContext, useContext, useEffect, useLayoutEffect, useRef, useState, type CSSProperties } from "react";
import { img } from "@/lib/asset";
import { bathTranslate, CATEGORIES, categoryItems, MOODS } from "@/lib/i18n";
import type { CatKey } from "@/lib/types";
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
function MenuCard({ sim, card }: Props & { card: Sim["data"]["cards"][number] }) {
  const [pressed, flash] = usePressed();
  return (
    <div
      className={`card${pressed ? " pressed" : ""}`}
      style={{ gridRow: card.row + 1, gridColumn: card.column + 1 }}
      onClick={() => { flash(); sim.openCard(card.title); }}
    >
      <div className="card-top" style={{ background: card.color }}>
        <div className="card-title">{sim.t(card.title)}</div>
        <img src={img(card.image)} alt="" />
      </div>
      <div className="card-bottom">
        <div className="card-desc">{sim.t(card.description.toUpperCase())}</div>
        <button className="card-btn">{sim.t("TALK WITH US")}</button>
      </div>
    </div>
  );
}

export function MenuScreen({ sim }: Props) {
  const { t, lang, today } = sim;
  const [bellPressed, flashBell] = usePressed(200);
  const date = !today
    ? " "
    : lang === "th"
      ? today.toLocaleDateString("th-TH", { dateStyle: "full" })
      : today.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" });
  return (
    <section className="page pg-menu">
      <div className="mm-header">
        <div className="mm-titles">
          <div className="mm-title">{t("MY DAILY WELL-BEING")}</div>
          <div className="mm-date">{date}</div>
        </div>
        <button className="lang-btn" onClick={sim.toggleLang}>{lang === "th" ? "THAI / ไทย" : "ENGLISH"}</button>
      </div>
      <div className="mm-grid">
        {sim.data.cards.map((c) => <MenuCard key={c.title} sim={sim} card={c} />)}
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

// ---------------------------------------------------------------- Category pages
export function CategoryScreen({ sim, cat }: Props & { cat: CatKey }) {
  const cfg = CATEGORIES[cat];
  const items = categoryItems(sim.data, cat, sim.lang);
  const idx = Math.min(sim.cur[cat], Math.max(0, items.length - 1));
  const scale = useContext(ScaleContext);
  const strip = useRef<HTMLDivElement>(null);
  const lockUntil = useRef(0);
  const drag = useRef({ down: false, moved: false, x: 0, left: 0 });

  // Restore the strip position when the page is shown (hbar.setValue(idx * total_step)).
  useLayoutEffect(() => {
    if (!strip.current || cfg.textOnly) return;
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
    if (cfg.textOnly || !strip.current || Date.now() < lockUntil.current) return; // Recommend: no-op
    const i = Math.round(strip.current.scrollLeft / STEP);
    if (i >= 0 && i < items.length) sim.scrolledTo(cat, i);
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
    if (!cfg.textOnly && strip.current) {
      lockUntil.current = Date.now() + 800;
      strip.current.scrollLeft = i * STEP;
    }
    sim.selectItem(cat, i);
  };

  return (
    <section className="page pg-cat">
      <div className="pg-header">{sim.t(cfg.title)}</div>
      <div className="big-screen" style={cfg.textOnly ? { background: cfg.color } : undefined}>
        {cfg.textOnly
          ? <div className="bs-text">{items[idx]}</div>
          : items.length > 0 && <CoverImage key={`${cat}-${idx}-${items[idx]}`} src={img(`${cfg.prefix}_${idx}`)} alt={items[idx]} bg={cfg.color} />}
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
            key={i}
            className={`box${cfg.large ? " large" : ""}${cfg.textOnly && i === idx ? " sel" : ""}`}
            style={{ "--bc": cfg.color } as CSSProperties}
            onClick={() => click(i)}
          >
            <span>{name}</span>
          </button>
        ))}
      </div>
      {/* Warm up the next photos so scrolling feels instant */}
      {!cfg.textOnly && (
        <div hidden>
          {[idx + 1, idx + 2].filter((n) => n < items.length).map((n) => <img key={n} src={img(`${cfg.prefix}_${n}`)} alt="" />)}
        </div>
      )}
      <button className="back-btn" onClick={() => sim.go("menu")}>{sim.t("GO BACK")}</button>
    </section>
  );
}

// ---------------------------------------------------------------- Bathroom
function BathroomCard({ sim, item }: Props & { item: Sim["data"]["bathroom"]["items"][number] }) {
  const [pressed, flash] = usePressed();
  return (
    <div
      className={`bcard${pressed ? " pressed" : ""}`}
      style={{ gridRow: item.row + 1, gridColumn: item.col + 1 }}
      onClick={() => { flash(); sim.selectBathroom(item); }}
    >
      <div className="bcard-img" style={{ backgroundImage: `url('${img(item.image)}')` }} />
      <div className="bcard-desc">{bathTranslate(sim.data, item.id, sim.lang)}</div>
    </div>
  );
}

export function BathroomScreen({ sim }: Props) {
  return (
    <section className="page pg-bath">
      <div className="pg-header" style={{ padding: "20px 0 16px" }}>{sim.t("BATHROOM ASSISTANCE")}</div>
      <div className="bath-grid">
        {sim.data.bathroom.items.map((b) => <BathroomCard key={b.id} sim={sim} item={b} />)}
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
