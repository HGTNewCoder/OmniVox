import { img } from "@/lib/asset";
import { translate } from "@/lib/i18n";
import type { AppData } from "@/lib/types";

const REPO = "https://github.com/HGTNewCoder/OmniVox";

export function Nav() {
  return (
    <header className="nav">
      <div className="wrap nav-inner">
        <a className="brand" href="#top" aria-label="OmniVox home">
          <span className="brand-mark" aria-hidden="true">
            <svg viewBox="0 0 32 32" width="28" height="28">
              <circle cx="16" cy="16" r="15" fill="currentColor" />
              <path d="M10 13v6M14 10v12M18 12v8M22 14v4" stroke="var(--bg)" strokeWidth="2.4" strokeLinecap="round" />
            </svg>
          </span>
          OmniVox
        </a>
        <nav className="nav-links" aria-label="Sections">
          <a href="#demo">Live demo</a>
          <a href="#features">Features</a>
          <a href="#how">How it works</a>
          <a href="#hardware">Hardware</a>
          <a href="#run">Run it</a>
        </nav>
        <a className="btn btn-ghost btn-sm" href={REPO} target="_blank" rel="noopener noreferrer">GitHub</a>
      </div>
    </header>
  );
}

/** Total number of things a patient can tap to say, counted from json_page. */
export function countChoices(data: AppData) {
  const cats = Object.values(data.categories).reduce((n, c) => n + (c.en?.length ?? 0), 0);
  return cats + data.bathroom.items.length + 2 /* yes/no */ + 5 /* moods */;
}

export function Hero({ data }: { data: AppData }) {
  return (
    <section className="hero">
      <div className="wrap hero-grid">
        <div className="hero-copy">
          <p className="eyebrow">Augmentative communication · Raspberry Pi</p>
          <h1>A voice for every bedside.</h1>
          <p className="lede">
            OmniVox is a touchscreen communication board for patients and older adults who find it hard to speak.
            Tap a picture — <em>“I feel worried”</em>, <em>“Turn me to my side”</em>, <em>“I need my glasses”</em> — and
            it says it out loud, in English or Thai.
          </p>
          <div className="hero-cta">
            <a className="btn btn-primary" href="#demo">Try the live demo</a>
            <a className="btn btn-ghost" href="#how">See how it works</a>
          </div>
          <dl className="stats">
            <div><dt>{countChoices(data)}</dt><dd>tap-to-speak choices</dd></div>
            <div><dt>{data.cards.length}</dt><dd>care categories</dd></div>
            <div><dt>{Object.keys(data.translations).length}</dt><dd>languages, one tap to switch</dd></div>
            <div><dt>1</dt><dd>big red call button</dd></div>
          </dl>
        </div>
        <div className="hero-art" aria-hidden="true">
          <div className="bubble b1"><img src={img("feeling_7")} alt="" /><span>I feel lonely</span></div>
          <div className="bubble b2"><img src={img("position_3")} alt="" /><span>Turn me to my side</span></div>
          <div className="bubble b3"><img src={img("food_0")} alt="" /><span>Pad Kra Pao</span></div>
          <div className="bubble b4"><span>หิว</span><small>“Hungry” in Thai</small></div>
          <div className="bell-orb"><img src={img("bell")} alt="" /></div>
        </div>
      </div>
    </section>
  );
}

const FEATURE_COPY: Record<string, { copy: string; key?: keyof AppData["categories"] | "bathroom"; unit?: string }> = {
  "FOOD": { copy: "Thai dishes with photos — curries, noodles, rice plates and street food.", key: "food", unit: "dishes" },
  "FEELING": { copy: "Emotions from excited to worried, each spoken as a sentence: “I feel …”.", key: "feeling", unit: "feelings" },
  "POSITION & COMFORT": { copy: "Ask to be turned, pulled up, moved to a wheelchair, or made warmer or cooler.", key: "position", unit: "requests" },
  "BATHROOM": { copy: "Picture cards for toilet, shower, washing, clothes, diaper and grooming.", key: "bathroom", unit: "needs" },
  "YES / NO": { copy: "Huge, unmistakable answer cards for staff questions — spoken and shown full-screen." },
  "ENTERTAINMENT": { copy: "Pick a channel or app: sports, movies, news, Thai TV, YouTube.", key: "entertainment", unit: "channels" },
  "RECOMMEND ANSWER": { copy: "Ready-made everyday phrases — glasses, lights, visitors, the doctor.", key: "recommend", unit: "phrases" },
  "CLOCK": { copy: "Set an alarm or a countdown timer with oversized arrow controls." },
};

export function Features({ data }: { data: AppData }) {
  return (
    <section id="features" className="features">
      <div className="wrap">
        <div className="section-head">
          <p className="eyebrow">What it does</p>
          <h2>Everything a patient needs to say, one tap away.</h2>
          <p>
            Eight large, high-contrast categories cover daily care, comfort, feelings and fun. Every card is a big touch
            target designed for shaky hands and tired eyes.
          </p>
        </div>
        <div className="feature-grid">
          {data.cards.map((c) => {
            const f = FEATURE_COPY[c.title] ?? { copy: c.description };
            let count = "";
            let eg = "";
            if (f.key === "bathroom") {
              count = `${data.bathroom.items.length} ${f.unit}`;
            } else if (f.key) {
              const list = data.categories[f.key].en ?? [];
              count = `${list.length} ${f.unit}`;
              eg = list.slice(0, 3).map((s) => s.replace(/\s*\(.*\)/, "")).join(" · ");
            }
            return (
              <article className="feature" key={c.title}>
                <div className="feature-art" style={{ background: c.color }}>
                  <img src={img(c.image)} alt="" loading="lazy" />
                </div>
                <div className="feature-body">
                  {count && <span className="count">{count}</span>}
                  <h3>{translate(data, c.title, "en")}</h3>
                  <p>{f.copy}</p>
                  {eg && <div className="eg">e.g. {eg}</div>}
                </div>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}

const HIGHLIGHTS = [
  {
    icon: "🗣️", title: "Natural neural voices",
    body: <>Speech comes from Microsoft Edge neural TTS — <code>en-US-JennyNeural</code> and <code>th-TH-PremwadeeNeural</code>. A new tap instantly interrupts the previous phrase, so the board keeps up with the person.</>,
  },
  {
    icon: "🇹🇭", title: "Truly bilingual",
    body: <>Every label, button, date and spoken phrase switches between English and Thai with one button. If Thai speech fails, OmniVox falls back to the English phrase so nothing goes unsaid.</>,
  },
  {
    icon: "🔔", title: "Help is always visible",
    body: <>The <b>Call for help</b> bar sits on the home screen, and choosing <i>“In pain”</i> at check-in flags staff. Alerts take over the full screen with a looping sound until someone turns them off.</>,
  },
  {
    icon: "⏰", title: "Alarms & timers",
    body: <>Big arrow controls set an alarm or a countdown — for medication, a visit, or a nap. Upcoming alarms and running timers show on the welcome screen.</>,
  },
  {
    icon: "📝", title: "Content lives in JSON",
    body: <>Menus, phrases and translations are plain files in <code>json_page/</code>. Caregivers can add a local dish or a favourite channel without touching code.</>,
  },
  {
    icon: "🔋", title: "Sleeps like a phone",
    body: <>A physical button toggles the backlight and the screen dims itself after five idle minutes, always waking on the friendly welcome check-in.</>,
  },
];

export function Highlights() {
  return (
    <section className="highlights">
      <div className="wrap hl-grid">
        {HIGHLIGHTS.map((h) => (
          <article className="hl" key={h.title}>
            <div className="hl-icon" aria-hidden="true">{h.icon}</div>
            <h3>{h.title}</h3>
            <p>{h.body}</p>
          </article>
        ))}
      </div>
    </section>
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

        <div
          className="arch"
          role="img"
          aria-label="Architecture: the PyQt6 user interface reads JSON content and sends phrases to the speech service; a GPIO daemon controls the backlight; alerts play an alarm sound."
        >
          <div className="arch-col">
            <div className="arch-box tone-a">
              <h5>Touch UI <small>app.py · PyQt6</small></h5>
              <p>12 screens in a <code>QStackedWidget</code>: welcome check-in, menu, 6 category pages, clock, alert and full-screen item view.</p>
            </div>
            <div className="arch-box tone-b">
              <h5>Content <small>json_page/*.json</small></h5>
              <p>Cards, food, feelings, positions, bathroom, entertainment, recommendations and the EN↔TH dictionary.</p>
            </div>
          </div>
          <div className="arch-col">
            <div className="arch-box tone-c">
              <h5>SpeechService <small>edge-tts + pygame</small></h5>
              <p>Queue + worker thread with a stop flag, so the newest tap always wins. Falls back to English if Thai synthesis fails.</p>
            </div>
            <div className="arch-box tone-d">
              <h5>Alerts &amp; time <small>QTimer · QSoundEffect</small></h5>
              <p>A 1-second tick checks alarms and timers; the bell and “In pain” trigger a full-screen alert with <code>alarm.wav</code>.</p>
            </div>
          </div>
          <div className="arch-col">
            <div className="arch-box tone-e">
              <h5>Screen manager <small>gpio_button_daemon.py</small></h5>
              <p><code>gpiozero</code> button on GPIO 17 toggles the backlight via <code>/sys/class/backlight</code>; a monitor thread sleeps the screen after 5 idle minutes.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export function Hardware() {
  const parts = [
    ["Raspberry Pi 4 or 5", "Raspberry Pi OS Bookworm, 64-bit"],
    ["DSI touchscreen", "Waveshare display with software brightness control"],
    ["Momentary push button", "GPIO 17 (physical pin 11) to ground — screen on/off"],
    ["Speaker", "3.5 mm, USB or HDMI audio for spoken phrases and alarms"],
    ["Python 3.8+", "PyQt6 · edge-tts · pygame · gpiozero"],
  ];
  return (
    <section id="hardware" className="hardware">
      <div className="wrap hw-grid">
        <div>
          <p className="eyebrow">Hardware</p>
          <h2>Built from parts you can buy today.</h2>
          <p>OmniVox runs full-screen on a Raspberry Pi with a touch display — small enough to mount on a bed rail or set on a tray table.</p>
        </div>
        <ul className="parts">
          {parts.map(([b, s]) => <li key={b}><b>{b}</b><span>{s}</span></li>)}
        </ul>
      </div>
    </section>
  );
}

export function RunIt() {
  return (
    <section id="run" className="run">
      <div className="wrap">
        <div className="section-head">
          <p className="eyebrow">Run it</p>
          <h2>Up and running in a few commands.</h2>
        </div>
        <div className="run-grid">
          <div className="code-card">
            <div className="code-title">On the Raspberry Pi</div>
            <pre><code>{`git clone ${REPO}.git
cd OmniVox
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py`}</code></pre>
          </div>
          <div className="code-card">
            <div className="code-title">Allow the button to read GPIO</div>
            <pre><code>{`sudo usermod -a -G gpio $USER
# Optional: Waveshare brightness tools
wget https://files.waveshare.com/wiki/common/Brightness.zip
unzip Brightness.zip && cd Brightness
sudo chmod +x install.sh && ./install.sh`}</code></pre>
          </div>
        </div>
        <p className="fine center">
          Full system dependencies are listed in the project <a href={`${REPO}#readme`}>README</a>.
        </p>
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
        <a href={REPO} target="_blank" rel="noopener noreferrer">github.com/HGTNewCoder/OmniVox</a>
      </div>
    </footer>
  );
}
