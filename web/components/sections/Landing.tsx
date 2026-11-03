import { publicUrl } from "@/lib/asset";
import { heroImages } from "@/lib/hero";
import type { AppData } from "@/lib/types";

const REPO = "https://github.com/HGTNewCoder/OmniVox";

export function Nav() {
  return (
    <header className="nav">
      <div className="wrap nav-inner">
        <a className="brand" href={publicUrl("")} aria-label="OmniVox home">
          <span className="brand-mark" aria-hidden="true">
            <svg viewBox="0 0 32 32" width="28" height="28">
              <circle cx="16" cy="16" r="15" fill="currentColor" />
              <path d="M10 13v6M14 10v12M18 12v8M22 14v4" stroke="var(--bg)" strokeWidth="2.4" strokeLinecap="round" />
            </svg>
          </span>
          OmniVox
        </a>
        <nav className="nav-links" aria-label="Sections">
          {/* Absolute links so the menu also works from /team and other pages */}
          <a href={`${publicUrl("")}#demo`}>Live demo</a>
          <a href={`${publicUrl("")}#how`}>How it works</a>
          <a href={publicUrl("manager/")}>Card Manager</a>
          <a href={publicUrl("team/")}>Team</a>
        </nav>
        <a className="btn btn-ghost btn-sm" href={REPO} target="_blank" rel="noopener noreferrer">GitHub</a>
      </div>
    </header>
  );
}

/** Total number of things a patient can tap to say, counted from json_page/board.json. */
export function countChoices(data: AppData) {
  const cards = data.board.cards.filter((c) => c.visible);
  const items = cards.reduce((n, c) => n + c.items.length, 0);
  const yesNo = cards.some((c) => c.type === "yesno") ? 2 : 0;
  return items + yesNo + 5 /* moods */;
}

export function Hero({ data }: { data: AppData }) {
  const [h1, h2, h3, h4] = heroImages();
  return (
    <section className="hero">
      <div className="wrap hero-grid">
        <div className="hero-copy">
          <p className="eyebrow">Augmentative communication</p>
          <h1>A voice for Mr. D.</h1>
          <p className="lede">
            OmniVox is a touchscreen communication board for patients and older adults who find it hard to speak.
            Tap a picture and it says it out loud, in English or Thai.
          </p>
          <div className="hero-cta">
            <a className="btn btn-primary" href="#demo">Try the live demo</a>
            <a className="btn btn-ghost" href="#how">See how it works</a>
          </div>
          <dl className="stats">
            <div><dt>{countChoices(data)}</dt><dd>tap-to-speak choices</dd></div>
            <div><dt>{data.board.cards.filter((c) => c.visible).length}</dt><dd>care categories</dd></div>
            <div><dt>{Object.keys(data.translations).length}</dt><dd>languages, one tap to switch</dd></div>
          </dl>
        </div>
        <div className="hero-art" aria-hidden="true">
          <div className="bubble b1"><img src={h1.src} alt="" /><span>{h1.caption}</span></div>
          <div className="bubble b2"><img src={h2.src} alt="" /><span>{h2.caption}</span></div>
          <div className="bubble b3"><img src={h3.src} alt="" /><span>{h3.caption}</span></div>
          <div className="bubble b4"><img src={h4.src} alt="" /><span>{h4.caption}</span></div>
        </div>
      </div>
    </section>
  );
}

export function ManagerTeaser() {
  return (
    <section id="manager" className="mgr-teaser">
      <div className="wrap mgr-teaser-grid">
        <div>
          <p className="eyebrow">Card Manager</p>
          <h2>Change the cards from a laptop.</h2>
          <p>
            The master finds every OmniVox on the same Wi-Fi and lets a caregiver add cards, rename them, change
            their pictures and edit the sub-cards inside.
          </p>
          <div className="hero-cta">
            <a className="btn btn-primary" href={publicUrl("manager/")}>Open the Card Manager demo</a>
          </div>
        </div>
        <ol className="mgr-steps">
          <li><span className="flow-n">1</span><div><h4>Find</h4><p>The master finds every OmniVox on the Wi-Fi.</p></div></li>
          <li><span className="flow-n">2</span><div><h4>Edit</h4><p>Cards, names in English and Thai, logos, colours and sub-cards.</p></div></li>
          <li><span className="flow-n">3</span><div><h4>Send</h4><p>The device saves the new cards and redraws its menu.</p></div></li>
        </ol>
      </div>
    </section>
  );
}

type Flow = { dir: "to" | "from"; label: string };
type Part = {
  side: "top" | "left" | "right" | "bottom";
  icon: keyof typeof ICONS;
  title: string;
  sub: string;
  flows: Flow[];
};

const ICONS = {
  screen: <><rect x="3" y="5" width="18" height="12" rx="2" /><path d="M9 20h6M12 17v3" /></>,
  laptop: <><rect x="5" y="5" width="14" height="10" rx="1.5" /><path d="M2.5 18.5h19" /></>,
  voice: <><path d="M5 10v4M9 7v10M13 4v16M17 8v8M21 11v2" /></>,
  button: <><circle cx="12" cy="12" r="4" /><circle cx="12" cy="12" r="8.5" /></>,
  chip: <><rect x="6" y="6" width="12" height="12" rx="2" /><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4" /></>,
};

const PARTS: Part[] = [
  {
    side: "top", icon: "screen", title: "Touchscreen", sub: "DSI display on the Pi",
    flows: [{ dir: "to", label: "Taps" }, { dir: "from", label: "Pages & pictures" }],
  },
  {
    side: "left", icon: "laptop", title: "Card Manager", sub: "master/server.py on a laptop, same Wi-Fi",
    flows: [{ dir: "from", label: "Answers “who's there?” (UDP 47800)" }, { dir: "to", label: "New cards & pictures (HTTP 8765)" }],
  },
  {
    side: "right", icon: "voice", title: "Voice", sub: "edge-tts makes the speech (online), pygame plays it on the speaker",
    flows: [{ dir: "from", label: "The phrase to say" }],
  },
  {
    side: "bottom", icon: "button", title: "GPIO button", sub: "Push button on GPIO 17 (pin 11)",
    flows: [{ dir: "to", label: "Press: screen on / off" }],
  },
];

function Icon({ name }: { name: keyof typeof ICONS }) {
  return (
    <svg className="hwf-icon" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor"
      strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {ICONS[name]}
    </svg>
  );
}

/** How the parts talk to each other, with the Raspberry Pi in the middle. */
function HardwareFlow() {
  return (
    <figure className="hwf" aria-labelledby="hwf-cap">
      <figcaption id="hwf-cap" className="hwf-cap">
        <span><i className="hwf-key to" /> into the Raspberry Pi</span>
        <span><i className="hwf-key from" /> out of the Raspberry Pi</span>
      </figcaption>
      <div className="hwf-grid">
        <div className="hwf-pi">
          <div className="hwf-head"><Icon name="chip" /><div><b>Raspberry Pi</b><small>runs everything on the device</small></div></div>
          <ul>
            <li><code>app.py</code> touch UI</li>
            <li><code>board.json</code> the cards</li>
            <li><code>client_agent.py</code> Wi-Fi link</li>
            <li><code>gpio_button_daemon.py</code> screen sleep</li>
          </ul>
        </div>
        {PARTS.map((p) => (
          <div key={p.side} className={`hwf-arm hwf-${p.side}`}>
            <div className="hwf-wire" data-side={p.side}>
              <div className="hwf-line" aria-hidden="true">
                {p.flows.map((f, i) => <i key={i} className={f.dir} style={{ animationDelay: `${i * -1.2}s` }} />)}
              </div>
              <ul className="hwf-labels">
                {p.flows.map((f) => <li key={f.label} className={f.dir}>{f.label}</li>)}
              </ul>
            </div>
            <div className="hwf-part">
              <div className="hwf-head"><Icon name={p.icon} /><div><b>{p.title}</b><small>{p.sub}</small></div></div>
            </div>
          </div>
        ))}
      </div>
    </figure>
  );
}

export function HowItWorks() {
  return (
    <section id="how" className="how">
      <div className="wrap">
        <div className="section-head">
          <p className="eyebrow">How it works</p>
          <h2>From a tap to a spoken sentence.</h2>
        </div>

        <ol className="flow" aria-label="Interaction flow">
          <li><span className="flow-n">1</span><h4>Tap</h4><p>A card on the PyQt6 touch UI is pressed.</p></li>
          <li><span className="flow-n">2</span><h4>Look up</h4><p>The phrase is read from <code>json_page/</code> in the current language.</p></li>
          <li><span className="flow-n">3</span><h4>Synthesize</h4><p><code>edge-tts</code> turns it into an MP3 on a background thread.</p></li>
          <li><span className="flow-n">4</span><h4>Speak</h4><p><code>pygame</code> plays it, cancelling anything already playing.</p></li>
        </ol>

        <HardwareFlow />
      </div>
    </section>
  );
}

export function Footer() {
  return (
    <footer className="footer">
      <div className="wrap footer-inner">
        <span className="brand small">OmniVox</span>
        <span>An open-source communication board for care settings.</span>
        <a href={publicUrl("team/")}>Team &amp; acknowledgements</a>
        <a href={REPO} target="_blank" rel="noopener noreferrer">github.com/HGTNewCoder/OmniVox</a>
      </div>
    </footer>
  );
}
