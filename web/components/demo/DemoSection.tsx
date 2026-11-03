"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { AppData, Lang } from "@/lib/types";
import { Device } from "./Device";
import { useSimulator, type TryKey } from "./useSimulator";
import { useSpeech, type SpokenLine } from "./useSpeech";

const TRIES: { key: TryKey; label: React.ReactNode }[] = [
  { key: "mood", label: "Pick a mood on the welcome screen" },
  { key: "lang", label: <>Switch the language to <span lang="th">ไทย</span> in the top-right</> },
  { key: "speak", label: <>Open <b>Feeling</b> and tap a card to hear it spoken</> },
  { key: "bathroom", label: "Ask for bathroom help" },
  { key: "yesno", label: <>Answer a question with <b>Yes / No</b></> },
  { key: "bell", label: <>Press <b>Call for help</b></> },
  { key: "power", label: "Press the side button on the tablet" },
];

export default function DemoSection({ data }: { data: AppData }) {
  const [muted, setMuted] = useState(false);
  const [log, setLog] = useState<SpokenLine[]>([]);
  const [done, setDone] = useState<Set<TryKey>>(new Set());
  const [toast, setToast] = useState<{ text: string; id: number } | null>(null);
  const speech = useSpeech(muted);
  const deviceRef = useRef<HTMLDivElement>(null);

  const onSpeak = useCallback(
    (text: string, lang: Lang, fb?: string | null, fbLang?: Lang | null) => {
      const note = speech.speak(text, lang, fb, fbLang);
      setLog((l) => [{ text, note, at: new Date() }, ...l].slice(0, 30));
      setToast({ text, id: Date.now() });
    },
    [speech],
  );
  const onTry = useCallback((k: TryKey) => setDone((d) => (d.has(k) ? d : new Set(d).add(k))), []);

  const sim = useSimulator(data.translations, data.board, { muted, onSpeak, onTry });

  // Hide the speech caption after a moment.
  useEffect(() => {
    if (!toast) return;
    const id = setTimeout(() => setToast(null), 2600);
    return () => clearTimeout(id);
  }, [toast]);

  const toggleFullscreen = () => {
    if (document.fullscreenElement) void document.exitFullscreen();
    else void deviceRef.current?.requestFullscreen?.().catch(() => {});
  };

  const restart = () => { speech.cancel(); sim.reset(); };
  const idleText = sim.backlight ? `${Math.floor(sim.idleLeft / 60)}:${String(sim.idleLeft % 60).padStart(2, "0")}` : "—";

  return (
    <section id="demo" className="demo">
      <div className="wrap">
        <div className="section-head wide">
          <p className="eyebrow">Live demo</p>
          <h2>Use the real interface, right here.</h2>
          <p>This is a browser replica of the OmniVox app, built from the same content files the device uses.</p>
        </div>

        <div className="demo-grid">
          <div className="device-col">
            <Device ref={deviceRef} sim={sim} toast={toast?.text} />
            <div className="device-toolbar">
              <button className="chip" type="button" onClick={toggleFullscreen}>⤢ Full screen</button>
              <button className="chip" type="button" aria-pressed={muted} onClick={() => setMuted((m) => !m)}>
                {muted ? "🔇 Sound off" : "🔊 Sound on"}
              </button>
              <button className="chip" type="button" onClick={restart}>↺ Restart</button>
            </div>
          </div>

          <aside className="demo-side">
            <div className="panel">
              <h3>Things to try</h3>
              <ol className="tries">
                {TRIES.map((x) => <li key={x.key} className={done.has(x.key) ? "done" : ""}>{x.label}</li>)}
              </ol>
            </div>

            <div className="panel">
              <h3>What OmniVox said</h3>
              <ul className="speech-log" aria-live="polite">
                {log.length === 0 && <li className="empty">Nothing yet — tap something on the screen.</li>}
                {log.map((l, i) => (
                  <li key={log.length - i}>
                    <span>“{l.text}”</span>
                    <small>{l.note} · {l.at.toTimeString().slice(0, 5)}</small>
                  </li>
                ))}
              </ul>
            </div>

            <div className="panel hw-panel">
              <h3>Hardware simulation</h3>
              <div className="hw-row"><span>Backlight</span><strong>{sim.backlight ? "On" : "Off"}</strong></div>
              <div className="hw-row"><span>Auto-sleep in</span><strong>{idleText}</strong></div>
              <button className="chip" type="button" onClick={sim.simulateIdle}>Simulate 5 min idle</button>
            </div>
          </aside>
        </div>
      </div>
    </section>
  );
}
