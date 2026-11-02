"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { AppData, CatKey, Lang } from "@/lib/types";
import { CATEGORIES } from "@/lib/i18n";
import {
  AlertScreen, BathroomScreen, CategoryScreen, ClockScreen, FullItemScreen,
  MenuScreen, ScaleContext, WelcomeScreen, YesNoScreen,
} from "./Screens";
import { useSimulator, type Sim, type TryKey } from "./useSimulator";
import { useSpeech, type SpokenLine } from "./useSpeech";

const BASE_W = 1280;

const TRIES: { key: TryKey; label: React.ReactNode }[] = [
  { key: "mood", label: "Pick a mood on the welcome screen" },
  { key: "lang", label: <>Switch the language to <span lang="th">ไทย</span> in the top-right</> },
  { key: "speak", label: <>Open <b>Feeling</b> and tap a card to hear it spoken</> },
  { key: "bathroom", label: "Ask for bathroom help" },
  { key: "yesno", label: <>Answer a question with <b>Yes / No</b></> },
  { key: "bell", label: <>Press <b>Call for help</b></> },
  { key: "clock", label: <>Set a 1-minute timer from <b>Clock</b></> },
  { key: "power", label: "Press the side button on the tablet" },
];

function ActivePage({ sim }: { sim: Sim }) {
  const p = sim.page;
  if (p in CATEGORIES) return <CategoryScreen key={p} sim={sim} cat={p as CatKey} />;
  switch (p) {
    case "welcome": return <WelcomeScreen sim={sim} />;
    case "menu": return <MenuScreen sim={sim} />;
    case "bathroom": return <BathroomScreen sim={sim} />;
    case "yesno": return <YesNoScreen sim={sim} />;
    case "clock": return <ClockScreen sim={sim} />;
    case "alert": return <AlertScreen sim={sim} />;
    case "full": return <FullItemScreen sim={sim} />;
    default: return null;
  }
}

export default function DemoSection({ data }: { data: AppData }) {
  const [muted, setMuted] = useState(false);
  const [log, setLog] = useState<SpokenLine[]>([]);
  const [done, setDone] = useState<Set<TryKey>>(new Set());
  const [toast, setToast] = useState<{ text: string; id: number } | null>(null);
  const [scale, setScale] = useState(0);
  const [pulse, setPulse] = useState(0);
  const speech = useSpeech(muted);
  const fitRef = useRef<HTMLDivElement>(null);
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

  const sim = useSimulator(data, { muted, onSpeak, onTry });

  // Hide the speech caption after a moment.
  useEffect(() => {
    if (!toast) return;
    const id = setTimeout(() => setToast(null), 2600);
    return () => clearTimeout(id);
  }, [toast]);

  // Scale the fixed 1280x800 canvas to whatever width the frame has.
  useEffect(() => {
    const el = fitRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setScale(el.clientWidth / BASE_W));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const toggleFullscreen = () => {
    if (document.fullscreenElement) void document.exitFullscreen();
    else void deviceRef.current?.requestFullscreen?.().catch(() => {});
  };

  const restart = () => { speech.cancel(); sim.reset(); };
  const idleText = sim.backlight ? `${Math.floor(sim.idleLeft / 60)}:${String(sim.idleLeft % 60).padStart(2, "0")}` : "—";

  return (
    <section id="demo" className="demo">
      <div className="wrap">
        <div className="section-head">
          <p className="eyebrow">Live demo</p>
          <h2>Use the real interface, right here.</h2>
          <p>
            This is a browser replica of the OmniVox app, built from the same content files the device uses.
            Turn your sound on — selections are spoken aloud.
          </p>
        </div>

        <div className="demo-grid">
          <div className="device-col">
            <div className="device" ref={deviceRef}>
              <div className="device-bezel">
                <div className="device-cam" aria-hidden="true" />
                <div className="screen-fit" ref={fitRef}>
                  <div
                    className="screen"
                    role="application"
                    aria-label="OmniVox simulator"
                    lang={sim.lang}
                    style={{ transform: `scale(${scale})`, visibility: scale ? "visible" : "hidden" }}
                    onPointerDown={sim.activity}
                  >
                    <ScaleContext.Provider value={scale || 1}>
                      <ActivePage sim={sim} />
                    </ScaleContext.Provider>

                    <div className={`modal-dim${sim.modal ? " show" : ""}`}>
                      <div className="modal">
                        <h4>Alert</h4>
                        <p>Staff Alerted — patient reports pain!</p>
                        <button onClick={sim.closeModal}>OK</button>
                      </div>
                    </div>

                    <div className={`toast-say${toast ? " show" : ""}`} aria-hidden="true">
                      <span className="wave"><i /><i /><i /><i /></span>
                      <span>{toast?.text}</span>
                    </div>

                    <div
                      className={`backlight${sim.backlight ? "" : " off"}`}
                      onClick={() => setPulse((p) => p + 1)}
                    >
                      <span>Screen off — press the side button</span>
                    </div>
                  </div>
                </div>
              </div>
              <button
                key={pulse}
                className={`hw-button${sim.backlight ? "" : " pulse"}`}
                type="button"
                title="Side power button (GPIO 17)"
                onClick={sim.power}
              >
                <span className="sr-only">Press side power button</span>
              </button>
            </div>
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
