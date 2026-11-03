"use client";

import { forwardRef, useEffect, useRef, useState } from "react";
import {
  AlertScreen, ClockScreen, FullItemScreen, GridScreen, ListScreen,
  MenuScreen, ScaleContext, WelcomeScreen, YesNoScreen,
} from "./Screens";
import type { Sim } from "./useSimulator";

const BASE_W = 1280;

function ActivePage({ sim }: { sim: Sim }) {
  const p = sim.page;
  if (p.startsWith("c:")) {
    const card = sim.cardById(p.slice(2));
    if (!card) return <MenuScreen sim={sim} />;
    return card.type === "grid"
      ? <GridScreen key={p} sim={sim} card={card} />
      : <ListScreen key={p} sim={sim} card={card} />;
  }
  switch (p) {
    case "welcome": return <WelcomeScreen sim={sim} />;
    case "menu": return <MenuScreen sim={sim} />;
    case "yesno": return <YesNoScreen sim={sim} />;
    case "clock": return <ClockScreen sim={sim} />;
    case "alert": return <AlertScreen sim={sim} />;
    case "full": return <FullItemScreen sim={sim} />;
    default: return null;
  }
}

/** The tablet: bezel, side button and the 1280x800 OmniVox screen scaled to fit. */
export const Device = forwardRef<HTMLDivElement, { sim: Sim; toast?: string | null; label?: string }>(
  function Device({ sim, toast, label = "OmniVox simulator" }, ref) {
    const [scale, setScale] = useState(0);
    const [pulse, setPulse] = useState(0);
    const fitRef = useRef<HTMLDivElement>(null);

    // Scale the fixed 1280x800 canvas to whatever width the frame has.
    useEffect(() => {
      const el = fitRef.current;
      if (!el) return;
      const ro = new ResizeObserver(() => setScale(el.clientWidth / BASE_W));
      ro.observe(el);
      return () => ro.disconnect();
    }, []);

    return (
      <div className="device" ref={ref}>
        <div className="device-bezel">
          <div className="device-cam" aria-hidden="true" />
          <div className="screen-fit" ref={fitRef}>
            <div
              className="screen"
              role="application"
              aria-label={label}
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
                <span>{toast}</span>
              </div>

              <div className={`sim-banner${sim.banner ? " show" : ""}`} role="status">{sim.banner?.text}</div>

              <div className={`backlight${sim.backlight ? "" : " off"}`} onClick={() => setPulse((n) => n + 1)}>
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
    );
  },
);
