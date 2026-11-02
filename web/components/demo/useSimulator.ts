"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { publicUrl, img } from "@/lib/asset";
import { bathTranslate, CATEGORIES, categoryItems, MENU_NAV, MOODS, translate } from "@/lib/i18n";
import type { AppData, BathroomItem, CatKey, Lang } from "@/lib/types";

export type PageKey = "welcome" | "menu" | CatKey | "bathroom" | "yesno" | "clock" | "alert" | "full";
export type TryKey = "mood" | "lang" | "speak" | "bathroom" | "yesno" | "bell" | "clock" | "power";
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
  onTry: (key: TryKey) => void;
}

export const IDLE_TIMEOUT_MS = 300_000; // gpio_button_daemon.IDLE_TIMEOUT_SECONDS
const pad = (n: number) => String(n).padStart(2, "0");
const ZERO_CUR: Record<CatKey, number> = { food: 0, feeling: 0, position: 0, entertainment: 0, recommend: 0 };

/** All state and behaviour of WellBeingApp, as a React hook. */
export function useSimulator(data: AppData, opts: SimOptions) {
  const [page, setPage] = useState<PageKey>("welcome");
  const [lang, setLang] = useState<Lang>("en");
  const [alarm, setAlarm] = useState<string | null>(null);
  const [timer, setTimer] = useState(0);
  const [cur, setCur] = useState(ZERO_CUR);
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

  const lastActivity = useRef(Date.now());
  const timeouts = useRef(new Set<ReturnType<typeof setTimeout>>());
  const audio = useRef<HTMLAudioElement | null>(null);
  const optsRef = useRef(opts);
  optsRef.current = opts;

  const t = useCallback((s: string) => translate(data, s, lang), [data, lang]);

  const later = useCallback((fn: () => void, ms: number) => {
    const id = setTimeout(() => { timeouts.current.delete(id); fn(); }, ms);
    timeouts.current.add(id);
  }, []);

  const speak = useCallback(
    (text: string, fallbackText?: string | null) =>
      optsRef.current.onSpeak(text, lang, lang === "th" ? fallbackText : null, lang === "th" && fallbackText ? "en" : null),
    [lang],
  );
  const tried = (k: TryKey) => optsRef.current.onTry(k);

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

  const openCard = (title: string) => { const p = MENU_NAV[title]; if (p) setPage(p as PageKey); };

  const callForHelp = () => { tried("bell"); triggerAlert("Emergency! Staff has been alerted!"); };

  const selectItem = (key: CatKey, idx: number) => {
    const cfg = CATEGORIES[key];
    const list = categoryItems(data, key, lang);
    setCur((c) => ({ ...c, [key]: idx }));
    if (cfg.speak) {
      const say = cfg.say ?? ((x: string) => x);
      const en = data.categories[key].en?.[idx];
      speak(say(list[idx], lang), en ? say(en, "en") : null);
      if (key === "feeling") tried("speak");
    }
    if (cfg.textOnly) return;
    setFull({ name: list[idx], image: img(`${cfg.prefix}_${idx}`), fallbackBg: cfg.color, back: key });
    setPage("full");
  };

  const scrolledTo = (key: CatKey, idx: number) => setCur((c) => (c[key] === idx ? c : { ...c, [key]: idx }));

  const selectBathroom = (item: BathroomItem) => {
    speak(bathTranslate(data, item.message, lang), translate(data, item.message, "en"));
    tried("bathroom");
    setFull({
      name: bathTranslate(data, item.id, lang),
      sub: bathTranslate(data, item.message, lang),
      image: img(item.image),
      fallbackBg: item.color,
      back: "bathroom",
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
    if (clock.mode === "ALARM") {
      setAlarm(`${pad(clock.h)}:${pad(clock.m)}`);
    } else {
      const secs = clock.h * 3600 + clock.m * 60;
      setTimer(secs);
      if (secs > 0) tried("clock");
    }
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
    setPage("welcome"); setLang("en"); setAlarm(null); setTimer(0); setCur(ZERO_CUR);
    setClock({ mode: "ALARM", ...nowClock() }); setFull(null); setFullOk(false); setMood(null);
    setModal(false); setAnswer(null); setBacklight(true);
    lastActivity.current = Date.now();
    setIdleLeft(IDLE_TIMEOUT_MS / 1000);
    setRun((r) => r + 1);
  };

  return {
    data, page, lang, alarm, timer, cur, clock, full, fullOk, alert, mood, modal, answer,
    backlight, idleLeft, today, run, t,
    go, toggleLang, selectMood, openCard, callForHelp, selectItem, scrolledTo, selectBathroom,
    answerYesNo, setClockMode, spin, confirmClock, cancelAlarm: () => setAlarm(null),
    cancelTimer: () => setTimer(0), alertOff, fullBack, fullSelect, closeModal: () => setModal(false),
    power, simulateIdle, activity, reset,
  };
}

export type Sim = ReturnType<typeof useSimulator>;
