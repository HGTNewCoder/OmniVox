import { existsSync } from "node:fs";
import path from "node:path";
import type { Metadata } from "next";
import { Footer, Nav } from "@/components/sections/Landing";
import { publicUrl } from "@/lib/asset";
import { TEAM, TEAM_PHOTO_CAPTION, THANKS } from "@/lib/team";

export const metadata: Metadata = {
  title: "Team · OmniVox",
  description: "The people behind OmniVox, and everyone who helped.",
};

/** Text in [brackets] is an unfilled placeholder from lib/team.ts. */
const isTodo = (s?: string) => !!s && /^\[.*\]$/.test(s.trim());

/** Runs at build time: finds web/public/team/team.(jpg|jpeg|png|webp) if it exists. */
function teamPhoto() {
  const ext = [".jpg", ".jpeg", ".png", ".webp"].find((e) =>
    existsSync(path.join(process.cwd(), "public", "team", `team${e}`)));
  return ext ? publicUrl(`team/team${ext}`) : null;
}

export default function TeamPage() {
  const photo = teamPhoto();
  return (
    <>
      <Nav />
      <main className="tm">
        <section className="tm-hero">
          <div className="wrap">
            <p className="eyebrow">Team</p>
            <h1>The people behind OmniVox.</h1>
            <figure className="tm-photo">
              {photo
                ? <img src={photo} alt={TEAM_PHOTO_CAPTION} />
                : <div className="tm-photo-empty todo">[Team photo — add web/public/team/team.jpg]</div>}
              {photo && <figcaption>{TEAM_PHOTO_CAPTION}</figcaption>}
            </figure>
          </div>
        </section>

        <section className="tm-section">
          <div className="wrap">
            <h2>Project team</h2>
            <ul className="tm-people">
              {TEAM.map((p) => (
                <li key={p.name} className="tm-person">
                  <h3 className={isTodo(p.name) ? "todo" : ""}>{p.name}</h3>
                  <p className={`tm-role${isTodo(p.role) ? " todo" : ""}`}>{p.role}</p>
                  {p.email && <a href={`mailto:${p.email}`}>{p.email}</a>}
                  {p.linkedin && (
                    <a className="tm-gh" href={p.linkedin} target="_blank" rel="noopener noreferrer">LinkedIn</a>
                  )}
                  {p.github && (
                    <a className="tm-gh" href={`https://github.com/${p.github}`} target="_blank" rel="noopener noreferrer">
                      github.com/{p.github}
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className="tm-section tm-alt">
          <div className="wrap">
            <h2>Special thanks</h2>
            <ul className="tm-thanks">
              {THANKS.map((t) => (
                <li key={t.who}>
                  <b className={isTodo(t.who) ? "todo" : ""}>{t.who}</b>
                  <span>{t.why}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
