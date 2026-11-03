"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { bundledImage, publicUrl, type ImageResolver } from "@/lib/asset";
import { spoken, text, type Board, type BoardCard } from "@/lib/board";
import { MOODS, translate } from "@/lib/i18n";
import type { AppData, Lang } from "@/lib/types";

/** Fixed pages, or "c:<card id>" for a page built from the board. */
export type PageKey = "welcome" | "menu" | "yesno" | "clock" | "alert" | "full" | `c:${string}`;
export type TryKey = "mood" | "lang" | "speak" | "bathroom" | "yesno" | "bell" | "power";
export type ClockMode = "ALARM" | "TIMER";

export interface FullItem {
  name: string;
  sub?: string;
  image: string;
  fallbackBg: string;
  back: PageKey;
}

export interface SimOptions {
  muted: boolean;
  onSpeak: (text: string, lang: Lang, fallbackText?: string | null, fallbackLang?: Lang | null) => void;
  onTry?: (key: TryKey) => void;
  resolveImage?: ImageResolver;
  /** Show "Cards updated" and leave card pages when the board changes (default true). */
  announceUpdates?: boolean;
}

export const IDLE_TIMEOUT_MS = 300_000; // gpio_button_daemon.IDLE_TIMEOUT_SECONDS
const pad = (n: number) => String(n).padStart(2, "0");

/** All state and behaviour of WellBeingApp, as a React hook. */
export function useSimulator(translations: AppData["translations"], board: Board, opts: SimOptions) {
  const [page, setPage] = useState<PageKey>("welcome");
  const [lang, setLang] = useState<Lang>("en");
  const [alarm, setAlarm] = useState<string | null>(null);
  const [timer, setTimer] = useState(0);
  const [cur, setCur] = useState<Record<string, number>>({});
  const [clock, setClock] = useState<{ mode: ClockMode; h: number; m: number }>({ mode: "ALARM", h: 0, m: 0 });
  const [full, setFull] = useState<FullItem | null>(null);
  const [fullOk, setFullOk] = useState(false);
  const [alert, setAlert] = useState<{ text: string; emergency: boolean }>({ text: "ALARM!", emergency: false });
  const [mood, setMood] = useState<number | null>(null);
  const [modal, setModal] = useState(false);
  const [answer, setAnswer] = useState<"YES" | "NO" | null>(null);
  const [backlight, setBacklight] = useState(true);
  const [idleLeft, setIdleLeft] = useState(IDLE_TIMEOUT_MS / 1000);
  const [today, setToday] = useState<Date | null>(null);
  const [run, setRun] = useState(0); // bumps on restart so the welcome animation replays
  const [banner, setBanner] = useState<{ text: string; id: number } | null>(null);

  const lastActivity = useRef(Date.now());
  const timeouts = useRef(new Set<ReturnType<typeof setTimeout>>());
  const audio = useRef<HTMLAudioElement | null>(null);
  const optsRef = useRef(opts);
  optsRef.current = opts;

  const t = useCallback((s: string) => translate(translations, s, lang), [translations, lang]);
  const image = useCallback((p: string) => (opts.resolveImage ?? bundledImage)(p), [opts.resolveImage]);
  const cardById = useCallback((id: string) => board.cards.find((c) => c.id === id), [board]);

  const later = useCallback((fn: () => void, ms: number) => {
    const id = setTimeout(() => { timeouts.current.delete(id); fn(); }, ms);
    timeouts.current.add(id);
  }, []);

  const speak = useCallback(
    (text: string, fallbackText?: string | null) =>
      optsRef.current.onSpeak(text, lang, lang === "th" ? fallbackText : null, lang === "th" && fallbackText ? "en" : null),
    [lang],
  );
  const tried = (k: TryKey) => optsRef.current.onTry?.(k);

  const nowClock = () => { const d = new Date(); return { h: d.getHours(), m: d.getMinutes() }; };

  // Client-only initial values (avoid build-time dates in the static HTML).
  useEffect(() => {
    audio.current = new Audio(publicUrl("assets/alarm.wav"));
    audio.current.loop = true;
    setToday(new Date());
    setClock((c) => ({ ...c, ...nowClock() }));
    const pending = timeouts.current;
    return () => { pending.forEach(clearTimeout); audio.current?.pause(); };
  }, []);

  useEffect(() => { if (audio.current) audio.current.muted = opts.muted; }, [opts.muted]);

  // New cards arrived (WellBeingApp.apply_new_board): leave card pages, show a banner.
  const firstBoard = useRef(board);
  useEffect(() => {
    if (board === firstBoard.current || optsRef.current.announceUpdates === false) return;
    setPage((p) => (p === "full" || p.startsWith("c:") ? "menu" : p));
    setBanner({ text: translate(translations, "CARDS UPDATED", lang), id: Date.now() });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [board]);
  useEffect(() => {
    if (!banner) return;
    const id = setTimeout(() => setBanner(null), 3500);
    return () => clearTimeout(id);
  }, [banner]);

  const triggerAlert = useCallback((text: string) => {
    const emergency = text.includes("Emergency") || text.toLowerCase().includes("pain");
    setAlert({ text, emergency });
    if (audio.current) {
      audio.current.currentTime = 0;
      audio.current.muted = optsRef.current.muted;
      audio.current.play().catch(() => {});
    }
    setPage("alert");
  }, []);

  // 1-second tick: WellBeingApp.process_time_events + PhoneStyleScreenManager.monitor
  const live = useRef({ alarm, timer, backlight });
  live.current = { alarm, timer, backlight };
  useEffect(() => {
    const id = setInterval(() => {
      const s = live.current;
      const d = new Date();
      if (s.alarm && `${pad(d.getHours())}:${pad(d.getMinutes())}` === s.alarm) {
        setAlarm(null);
        triggerAlert("ALARM!");
      }
      if (s.timer > 0) {
        setTimer(s.timer - 1);
        if (s.timer - 1 === 0) triggerAlert("TIMER FINISHED!");
      }
      const left = Math.max(0, IDLE_TIMEOUT_MS - (Date.now() - lastActivity.current));
      if (s.backlight && left === 0) { setPage("welcome"); setBacklight(false); }
      setIdleLeft(Math.ceil(left / 1000));
      if (d.getSeconds() === 0) setToday(d);
    }, 1000);
    return () => clearInterval(id);
  }, [triggerAlert]);

  // ---------------- actions ----------------
  const go = (p: PageKey) => setPage(p);

  const toggleLang = () => { setLang((l) => (l === "en" ? "th" : "en")); tried("lang"); };

  const selectMood = (i: number) => {
    setMood(i);
    tried("mood");
    const done = () => { setPage("menu"); setMood(null); };
    if (MOODS[i].label === "In pain") {
      later(() => setModal(true), 1000);
      later(() => { setModal(false); done(); }, 2500);
    } else {
      later(done, 1000);
    }
  };

  /** MainMenuPage.navigate */
  const openCard = (id: string) => {
    const card = cardById(id);
    if (!card) return;
    setPage(card.type === "yesno" ? "yesno" : card.type === "clock" ? "clock" : `c:${card.id}`);
  };

  const callForHelp = () => { tried("bell"); triggerAlert("Emergency! Staff has been alerted!"); };

  /** A tap on a list or phrases card's item. */
  const selectItem = (card: BoardCard, idx: number) => {
    const item = card.items[idx];
    if (!item) return;
    setCur((c) => ({ ...c, [card.id]: idx }));
    if (card.type === "phrases" || card.speak) {
      speak(spoken(card, item, lang), spoken(card, item, "en"));
      tried("speak");
    }
    if (card.type === "phrases") return;
    setFull({ name: text(item.label, lang), image: image(item.image), fallbackBg: card.accent, back: `c:${card.id}` });
    setPage("full");
  };

  const scrolledTo = (cardId: string, idx: number) =>
    setCur((c) => (c[cardId] === idx ? c : { ...c, [cardId]: idx }));

  /** A tap on a grid card's tile (BathroomPage.handle_bathroom_selection). */
  const selectGridItem = (card: BoardCard, idx: number) => {
    const item = card.items[idx];
    if (!item) return;
    speak(spoken(card, item, lang), spoken(card, item, "en"));
    tried("bathroom");
    setFull({
      name: text(item.label, lang),
      sub: spoken(card, item, lang),
      image: image(item.image),
      fallbackBg: item.color ?? card.accent,
      back: `c:${card.id}`,
    });
    setPage("full");
  };

  const answerYesNo = (choice: "YES" | "NO") => {
    speak(t(choice), choice);
    tried("yesno");
    setAnswer(choice);
    later(() => { setAnswer(null); setPage("menu"); }, 3000);
  };

  const setClockMode = (mode: ClockMode) =>
    setClock({ mode, ...(mode === "ALARM" ? nowClock() : { h: 0, m: 0 }) });

  const spin = (dh: number, dm: number) =>
    setClock((c) => {
      const total = (((c.h * 60 + c.m + dh * 60 + dm) % 1440) + 1440) % 1440; // QTime wraps at 24h
      return { ...c, h: Math.floor(total / 60), m: total % 60 };
    });

  const confirmClock = () => {
    if (clock.mode === "ALARM") setAlarm(`${pad(clock.h)}:${pad(clock.m)}`);
    else setTimer(clock.h * 3600 + clock.m * 60);
    setClockMode(clock.mode);
    setPage("welcome");
  };

  const alertOff = () => { audio.current?.pause(); setPage("menu"); };

  const fullBack = () => setPage(full?.back ?? "menu");
  const fullSelect = () => {
    setFullOk(true);
    later(() => { setPage(full?.back ?? "menu"); setFullOk(false); }, 400);
  };

  const power = () => {
    tried("power");
    if (backlight) { setPage("welcome"); later(() => setBacklight(false), 100); }
    else { setBacklight(true); lastActivity.current = Date.now(); setIdleLeft(IDLE_TIMEOUT_MS / 1000); }
  };

  const simulateIdle = () => { lastActivity.current = Date.now() - IDLE_TIMEOUT_MS; };
  const activity = () => { if (backlight) lastActivity.current = Date.now(); };

  const reset = () => {
    timeouts.current.forEach(clearTimeout);
    timeouts.current.clear();
    audio.current?.pause();
    setPage("welcome"); setLang("en"); setAlarm(null); setTimer(0); setCur({});
    setClock({ mode: "ALARM", ...nowClock() }); setFull(null); setFullOk(false); setMood(null);
    setModal(false); setAnswer(null); setBacklight(true); setBanner(null);
    lastActivity.current = Date.now();
    setIdleLeft(IDLE_TIMEOUT_MS / 1000);
    setRun((r) => r + 1);
  };

  return {
    board, page, lang, alarm, timer, cur, clock, full, fullOk, alert, mood, modal, answer,
    backlight, idleLeft, today, run, banner, t, image, cardById,
    go, toggleLang, selectMood, openCard, callForHelp, selectItem, scrolledTo, selectGridItem,
    answerYesNo, setClockMode, spin, confirmClock, cancelAlarm: () => setAlarm(null),
    cancelTimer: () => setTimer(0), alertOff, fullBack, fullSelect, closeModal: () => setModal(false),
    power, simulateIdle, activity, reset,
    showBanner: (message: string) => setBanner({ text: message, id: Date.now() }),
  };
}

export type Sim = ReturnType<typeof useSimulator>;
