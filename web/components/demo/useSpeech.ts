"use client";

import { useCallback, useEffect, useRef } from "react";
import type { Lang } from "@/lib/types";

export interface SpokenLine {
  text: string;
  note: string;
  at: Date;
}

/**
 * Browser stand-in for SpeechService (edge-tts + pygame):
 * a new phrase always interrupts the previous one, and if the requested
 * language has no voice the fallback phrase is used instead.
 */
export function useSpeech(muted: boolean) {
  const voices = useRef<SpeechSynthesisVoice[]>([]);

  useEffect(() => {
    if (!("speechSynthesis" in window)) return;
    const load = () => { voices.current = window.speechSynthesis.getVoices(); };
    load();
    window.speechSynthesis.addEventListener("voiceschanged", load);
    return () => window.speechSynthesis.removeEventListener("voiceschanged", load);
  }, []);

  useEffect(() => { if (muted) window.speechSynthesis?.cancel(); }, [muted]);

  const voiceFor = useCallback((lang: Lang) => {
    const list = voices.current.filter((v) => v.lang.toLowerCase().startsWith(lang));
    return list.find((v) => /natural|neural|premwadee|jenny|google/i.test(v.name)) ?? list[0] ?? null;
  }, []);

  /** Speaks and returns a short note describing which voice was used. */
  const speak = useCallback(
    (text: string, lang: Lang, fallbackText?: string | null, fallbackLang?: Lang | null): string => {
      const supported = typeof window !== "undefined" && "speechSynthesis" in window;
      let sayText = text;
      let sayLang = lang;
      let note = lang === "th" ? "Thai" : "English";
      if (supported && voices.current.length && !voiceFor(lang) && fallbackText && fallbackLang) {
        sayText = fallbackText;
        sayLang = fallbackLang;
        note = "Thai voice unavailable → English";
      }
      if (!supported || muted) return note;
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(sayText);
      u.lang = sayLang === "th" ? "th-TH" : "en-US";
      const v = voiceFor(sayLang);
      if (v) u.voice = v;
      u.rate = 0.95;
      window.speechSynthesis.speak(u);
      return note;
    },
    [muted, voiceFor],
  );

  const cancel = useCallback(() => window.speechSynthesis?.cancel(), []);

  return { speak, cancel };
}
