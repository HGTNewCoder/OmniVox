"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { publicUrl, type ImageResolver } from "@/lib/asset";
import { boardProblem, customImages, type Board } from "@/lib/board";
import type { AppData, Lang } from "@/lib/types";
import { Device } from "../demo/Device";
import { useSimulator } from "../demo/useSimulator";
import { useSpeech } from "../demo/useSpeech";
import { CardEditor, CardList, type PickTarget } from "./Editor";
import { ImagePicker } from "./ImagePicker";
import { DemoTransport, detectMaster, LiveTransport, TransportError, type DeviceInfo, type Transport } from "./transport";

interface Props {
  translations: AppData["translations"];
  base: Board;       // json_page/board.json — seeds the simulated devices
  bundled: string[]; // pictures bundled with the site
}

type Status = { kind: "ok" | "error" | "busy"; text: string } | null;

const sameCards = (a?: Board, b?: Board) => !!a && !!b && JSON.stringify(a.cards) === JSON.stringify(b.cards);
const errText = (e: unknown) => (e instanceof Error ? e.message : "Something went wrong");

// ---------------------------------------------------------------- live preview of one device
function Preview({ translations, board, resolve, focus, ping, announce }: {
  translations: AppData["translations"]; board: Board; resolve: ImageResolver;
  focus: string | null; ping: { text: string; id: number } | null; announce: boolean;
}) {
  const [muted, setMuted] = useState(true);
  const [toast, setToast] = useState<string | null>(null);
  const speech = useSpeech(muted);
  const onSpeak = useCallback((text: string, lang: Lang, fb?: string | null, fbLang?: Lang | null) => {
    speech.speak(text, lang, fb, fbLang);
    setToast(text);
  }, [speech]);
  const sim = useSimulator(translations, board, { muted, onSpeak, resolveImage: resolve, announceUpdates: announce });

  useEffect(() => {
    if (!toast) return;
    const id = setTimeout(() => setToast(null), 2600);
    return () => clearTimeout(id);
  }, [toast]);

  // Jump to the card being edited.
  useEffect(() => {
    if (focus) sim.openCard(focus);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focus]);

  useEffect(() => {
    if (ping) sim.showBanner(ping.text);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ping]);

  return (
    <>
      <Device sim={sim} toast={toast} label="Preview of the selected OmniVox" />
      <div className="device-toolbar">
        <button className="chip" type="button" onClick={() => sim.go("menu")}>☰ Menu</button>
        <button className="chip" type="button" aria-pressed={muted} onClick={() => setMuted((m) => !m)}>
          {muted ? "🔇 Sound off" : "🔊 Sound on"}
        </button>
        <button className="chip" type="button" onClick={() => { speech.cancel(); sim.reset(); }}>↺ Restart</button>
      </div>
    </>
  );
}

// ---------------------------------------------------------------- "send to other devices" dialog
function SendDialog({ devices, from, onSend, onClose }: {
  devices: DeviceInfo[]; from: DeviceInfo; onSend: (ids: string[]) => void; onClose: () => void;
}) {
  const others = devices.filter((d) => d.id !== from.id);
  const [chosen, setChosen] = useState<Set<string>>(new Set(others.filter((d) => d.online).map((d) => d.id)));
  const toggle = (id: string) => setChosen((s) => { const n = new Set(s); if (n.has(id)) n.delete(id); else n.add(id); return n; });
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);
  return (
    <div className="mg-dim" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="mg-dialog" role="dialog" aria-modal="true" aria-label="Send to other devices">
        <div className="mg-dialog-head">
          <h3>Copy these cards to other devices</h3>
          <button className="mg-icon-btn" onClick={onClose} aria-label="Close">✕</button>
        </div>
        <p className="fine">The cards you are editing for <b>{from.name}</b> will replace the cards on each device you tick. Pictures you uploaded are copied too.</p>
        <ul className="mg-check-list">
          {others.map((d) => (
            <li key={d.id}>
              <label className={d.online ? "" : "off"}>
                <input type="checkbox" disabled={!d.online} checked={chosen.has(d.id)} onChange={() => toggle(d.id)} />
                <span>{d.name}</span>
                <small>{d.online ? `${d.cards ?? "?"} cards now` : "offline"}</small>
              </label>
            </li>
          ))}
          {others.length === 0 && <li className="fine">No other devices found.</li>}
        </ul>
        <div className="mg-dialog-foot">
          <button className="btn btn-ghost btn-sm" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary btn-sm" disabled={!chosen.size} onClick={() => onSend([...chosen])}>
            Send to {chosen.size} device{chosen.size === 1 ? "" : "s"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------- the app
export default function CardManager({ translations, base, bundled }: Props) {
  const [transport, setTransport] = useState<Transport | null>(null);
  const [devices, setDevices] = useState<DeviceInfo[]>([]);
  const [scanning, setScanning] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [applied, setApplied] = useState<Record<string, Board>>({});
  const [drafts, setDrafts] = useState<Record<string, Board>>({});
  const [assets, setAssets] = useState<Record<string, string[]>>({});
  const [selectedCard, setSelectedCard] = useState<string | null>(null);
  const [picker, setPicker] = useState<PickTarget | null>(null);
  const [status, setStatus] = useState<Status>(null);
  const [needPin, setNeedPin] = useState<string | null>(null);
  const [pin, setPin] = useState("");
  const [pinWrong, setPinWrong] = useState(false);
  const pinAttempt = useRef<string | null>(null);
  const [previewDraft, setPreviewDraft] = useState(false);
  const [sending, setSending] = useState(false);
  const [sendDialog, setSendDialog] = useState(false);
  const [renaming, setRenaming] = useState<string | null>(null);
  const [address, setAddress] = useState("");
  const [ping, setPing] = useState<{ text: string; id: number } | null>(null);

  const device = devices.find((d) => d.id === selectedId) ?? null;
  const board = selectedId ? applied[selectedId] : undefined;
  const draft = selectedId ? drafts[selectedId] : undefined;
  const dirty = !!draft && !!board && !sameCards(draft, board);
  const problem = draft ? boardProblem(draft) : null;
  const resolve = useMemo<ImageResolver>(
    () => (transport && selectedId ? transport.imageUrl(selectedId) : () => ""),
    [transport, selectedId],
  );

  // Served by master/server.py → real devices. Otherwise (the public website) → simulated beds.
  useEffect(() => {
    let alive = true;
    void detectMaster().then((live) => {
      if (alive) setTransport(live ? new LiveTransport() : new DemoTransport(base, bundled));
    });
    return () => { alive = false; };
  }, [base, bundled]);

  const handle = useCallback((e: unknown, deviceId?: string) => {
    if (e instanceof TransportError && e.status === 401 && deviceId) {
      setNeedPin(deviceId);
      setPinWrong(pinAttempt.current === deviceId);
      setStatus(null);
    } else {
      setStatus({ kind: "error", text: errText(e) });
    }
  }, []);

  const loadDevice = useCallback(async (t: Transport, id: string) => {
    try {
      const [b, list] = await Promise.all([t.getBoard(id), t.listAssets(id)]);
      setApplied((m) => ({ ...m, [id]: b }));
      setDrafts((m) => (m[id] ? m : { ...m, [id]: b }));
      setAssets((m) => ({ ...m, [id]: list }));
      setNeedPin(null);
      setPinWrong(false);
    } catch (e) {
      handle(e, id);
    }
  }, [handle]);

  const scan = useCallback(async (t: Transport) => {
    setScanning(true);
    try {
      const list = await t.listDevices();
      setDevices(list);
      setSelectedId((cur) => cur && list.some((d) => d.id === cur) ? cur : (list.find((d) => d.online)?.id ?? null));
    } catch (e) {
      handle(e);
    } finally {
      setScanning(false);
    }
  }, [handle]);

  useEffect(() => { if (transport) void scan(transport); }, [transport, scan]);

  useEffect(() => {
    if (transport && selectedId && device?.online && !applied[selectedId]) void loadDevice(transport, selectedId);
  }, [transport, selectedId, device?.online, applied, loadDevice]);

  // Refresh the picture list whenever the picker opens (another master may have uploaded).
  useEffect(() => {
    if (!picker || !transport || !selectedId) return;
    void transport.listAssets(selectedId).then((list) => setAssets((m) => ({ ...m, [selectedId]: list }))).catch(() => {});
  }, [picker, transport, selectedId]);

  useEffect(() => {
    if (status?.kind !== "ok") return;
    const id = setTimeout(() => setStatus(null), 5000);
    return () => clearTimeout(id);
  }, [status]);

  // Pick a sensible card when switching devices.
  useEffect(() => {
    if (draft && !draft.cards.some((c) => c.id === selectedCard)) setSelectedCard(draft.cards[0]?.id ?? null);
  }, [draft, selectedCard]);

  const setDraft = (b: Board) => selectedId && setDrafts((m) => ({ ...m, [selectedId]: b }));

  const send = async () => {
    if (!transport || !selectedId || !draft || !device) return;
    if (problem) { setStatus({ kind: "error", text: problem }); return; }
    setSending(true);
    setStatus({ kind: "busy", text: `Sending to ${device.name}…` });
    try {
      const saved = await transport.saveBoard(selectedId, draft);
      setApplied((m) => ({ ...m, [selectedId]: saved }));
      setDrafts((m) => ({ ...m, [selectedId]: saved }));
      setDevices((list) => list.map((d) => (d.id === selectedId ? { ...d, cards: saved.cards.length, updated: saved.updated } : d)));
      setPreviewDraft(false);
      setStatus({ kind: "ok", text: `Sent to ${device.name} — its screen has updated.` });
    } catch (e) {
      handle(e, selectedId);
    } finally {
      setSending(false);
    }
  };

  const sendToOthers = async (ids: string[]) => {
    if (!transport || !selectedId || !draft) return;
    setSendDialog(false);
    if (problem) { setStatus({ kind: "error", text: problem }); return; }
    setSending(true);
    const pictures = customImages(draft);
    const done: string[] = [];
    try {
      for (const id of ids) {
        const name = devices.find((d) => d.id === id)?.name ?? id;
        setStatus({ kind: "busy", text: `Sending to ${name}…` });
        await transport.copyImages(selectedId, id, pictures);
        const saved = await transport.saveBoard(id, draft);
        setApplied((m) => ({ ...m, [id]: saved }));
        setDrafts((m) => ({ ...m, [id]: saved }));
        setDevices((list) => list.map((d) => (d.id === id ? { ...d, cards: saved.cards.length, updated: saved.updated } : d)));
        done.push(name);
      }
      setStatus({ kind: "ok", text: `Sent to ${done.join(", ")}.` });
    } catch (e) {
      setStatus({ kind: "error", text: `${done.length ? `Sent to ${done.join(", ")}, then: ` : ""}${errText(e)}` });
    } finally {
      setSending(false);
    }
  };

  const pick = (path: string) => {
    if (!picker || !draft) return;
    setDraft({
      ...draft,
      cards: draft.cards.map((c) => {
        if (c.id !== picker.card) return c;
        if (picker.item === undefined) return { ...c, image: path };
        return { ...c, items: c.items.map((it, i) => (i === picker.item ? { ...it, image: path } : it)) };
      }),
    });
    setPicker(null);
  };

  const upload = async (blob: Blob) => {
    if (!transport || !selectedId) throw new Error("No device selected");
    const path = await transport.uploadImage(selectedId, blob);
    setAssets((m) => ({ ...m, [selectedId]: [...new Set([...(m[selectedId] ?? []), path])] }));
    return path;
  };

  const rename = async (id: string, name: string) => {
    if (!transport || !name.trim()) { setRenaming(null); return; }
    try {
      await transport.rename(id, name.trim());
      setDevices((list) => list.map((d) => (d.id === id ? { ...d, name: name.trim() } : d)));
    } catch (e) {
      handle(e, id);
    }
    setRenaming(null);
  };

  const identify = async () => {
    if (!transport || !device) return;
    try {
      await transport.identify(device.id);
      setPing({ text: `📍 ${device.name}`, id: Date.now() });
      setStatus({ kind: "ok", text: `${device.name} is showing its name on screen.` });
    } catch (e) {
      handle(e, device.id);
    }
  };

  const addByAddress = async () => {
    if (!transport?.addDevice || !address.trim()) return;
    try {
      const d = await transport.addDevice(address.trim());
      setAddress("");
      await scan(transport);
      if (d?.id) setSelectedId(d.id);
    } catch (e) {
      handle(e);
    }
  };

  const submitPin = () => {
    if (!transport?.setPin || !needPin) return;
    transport.setPin(needPin, pin);
    setPin("");
    pinAttempt.current = needPin;
    void loadDevice(transport, needPin);
  };

  const resetDemo = () => {
    if (!transport?.reset) return;
    transport.reset();
    setApplied({}); setDrafts({}); setAssets({}); setSelectedCard(null); setPreviewDraft(false);
    void scan(transport);
    setStatus({ kind: "ok", text: "Demo reset to the original cards." });
  };

  const live = transport?.mode === "live";
  const previewBoard = previewDraft && draft ? draft : board;

  return (
    <div className="mg-app">
      <header className="mg-top">
        <a className="brand" href={live ? undefined : publicUrl("")}>
          <span className="brand-mark" aria-hidden="true">
            <svg viewBox="0 0 32 32" width="26" height="26">
              <circle cx="16" cy="16" r="15" fill="currentColor" />
              <path d="M10 13v6M14 10v12M18 12v8M22 14v4" stroke="var(--bg)" strokeWidth="2.4" strokeLinecap="round" />
            </svg>
          </span>
          OmniVox <span className="mg-top-sub">Card Manager</span>
        </a>
        <span className={`mg-mode ${live ? "live" : "demo"}`}>
          {!transport ? "Connecting…" : live ? "● Live — controlling real devices" : "Demo — simulated devices"}
        </span>
        {!live && transport && <a className="btn btn-ghost btn-sm" href={publicUrl("")}>← Back to the site</a>}
      </header>

      {transport && !live && (
        <div className="mg-note">
          <p>
            This is the <b>master</b> program running in demo mode with three simulated bedside devices. Edit a card, then
            press <b>Send to device</b> and watch the device preview update. Changes stay in this browser.
          </p>
          <button className="btn btn-ghost btn-sm" onClick={resetDemo}>Reset demo</button>
        </div>
      )}

      <div className="mg-body">
        <aside className="mg-side">
          <section className="mg-devices">
            <div className="mg-section-head">
              <h3>Devices</h3>
              <button className="mg-icon-btn" onClick={() => transport && void scan(transport)} disabled={scanning} aria-label="Look for devices again" title="Look for devices again">
                <span className={scanning ? "mg-spin" : ""}>⟳</span>
              </button>
            </div>
            <ul className="mg-device-list">
              {devices.map((d) => (
                <li key={d.id}>
                  {renaming === d.id ? (
                    <form className="mg-rename" onSubmit={(e) => { e.preventDefault(); void rename(d.id, new FormData(e.currentTarget).get("name") as string); }}>
                      <input className="mg-input" name="name" defaultValue={d.name} autoFocus maxLength={40} aria-label="Device name"
                        onBlur={(e) => void rename(d.id, e.target.value)} />
                    </form>
                  ) : (
                    <button
                      className={`mg-device${d.id === selectedId ? " on" : ""}${d.online ? "" : " off"}`}
                      onClick={() => { setSelectedId(d.id); setSelectedCard(null); setPreviewDraft(false); }}
                      aria-current={d.id === selectedId}
                    >
                      <span className="mg-dot" aria-hidden="true" />
                      <span className="mg-device-text">
                        <b>{d.name}</b>
                        <small>
                          {d.online ? `${d.cards ?? "?"} cards` : "offline"}
                          {drafts[d.id] && applied[d.id] && !sameCards(drafts[d.id], applied[d.id]) ? " · unsent changes" : ""}
                        </small>
                      </span>
                    </button>
                  )}
                </li>
              ))}
              {transport && !scanning && devices.length === 0 && (
                <li className="mg-empty">No OmniVox found on this network yet. Check the device is switched on and on the same Wi-Fi, or add it by address.</li>
              )}
            </ul>
            {live && (
              <form className="mg-add-addr" onSubmit={(e) => { e.preventDefault(); void addByAddress(); }}>
                <input className="mg-input" placeholder="Add by address, e.g. 192.168.1.20" value={address}
                  onChange={(e) => setAddress(e.target.value)} aria-label="Device address" />
                <button className="btn btn-ghost btn-sm" disabled={!address.trim()}>Add</button>
              </form>
            )}
          </section>

          {draft && (
            <CardList board={draft} selected={selectedCard} resolve={resolve} onChange={setDraft} onSelect={setSelectedCard} />
          )}
        </aside>

        <main className="mg-main" id="editor">
          {device && (
            <div className="mg-device-head">
              <div>
                <span className="eyebrow">Editing</span>
                <h1>{device.name}</h1>
                <small className="fine">
                  {device.address}{board?.updated ? ` · last changed ${new Date(board.updated).toLocaleString()}` : ""}
                </small>
              </div>
              <div className="mg-head-tools">
                <button className="btn btn-ghost btn-sm" onClick={() => setRenaming(device.id)}>Rename</button>
                <button className="btn btn-ghost btn-sm" onClick={identify} disabled={!device.online}>📍 Identify</button>
              </div>
            </div>
          )}

          {needPin && needPin === selectedId && (
            <form className="mg-pin" onSubmit={(e) => { e.preventDefault(); submitPin(); }}>
              <p><b>{device?.name}</b> is protected with a PIN. Enter the PIN from its <code>device.json</code>.</p>
              <input className="mg-input" type="password" inputMode="numeric" value={pin} onChange={(e) => setPin(e.target.value)} aria-label="PIN" autoFocus />
              <button className="btn btn-primary btn-sm" disabled={!pin}>Unlock</button>
              {pinWrong && <span className="mg-error" role="alert">That PIN is not right. Try again.</span>}
            </form>
          )}

          {device && !device.online && <p className="mg-empty">This device is offline. Switch it on, then press ⟳.</p>}
          {!transport && <p className="mg-empty">Connecting…</p>}
          {transport && device?.online && !draft && !needPin && <p className="mg-empty">Loading cards…</p>}

          {draft && (
            <CardEditor board={draft} selected={selectedCard} resolve={resolve} onChange={setDraft}
              onSelect={setSelectedCard} onPick={setPicker} />
          )}
        </main>

        <aside className="mg-preview" aria-label="Device preview">
          <div className="mg-preview-head">
            <h3>{device ? device.name : "Device"}</h3>
            <div className="mg-seg" role="group" aria-label="What the preview shows">
              <button aria-pressed={!previewDraft} onClick={() => setPreviewDraft(false)}>On device</button>
              <button aria-pressed={previewDraft} onClick={() => setPreviewDraft(true)} disabled={!draft}>
                My edits{dirty ? " •" : ""}
              </button>
            </div>
          </div>
          {previewBoard && selectedId ? (
            <Preview
              key={`${selectedId}-${previewDraft ? "draft" : "device"}`}
              translations={translations}
              board={previewBoard}
              resolve={resolve}
              focus={previewDraft ? selectedCard : null}
              ping={ping}
              announce={!previewDraft}
            />
          ) : (
            <div className="mg-preview-empty">The selected device appears here.</div>
          )}
          <p className="fine">
            {previewDraft
              ? "Showing your unsent edits. The real screen does not change until you send."
              : "This is what the device is showing now. It is fully interactive — tap around."}
          </p>
        </aside>
      </div>

      {(dirty || status) && draft && (
        <div className={`mg-savebar${status?.kind === "error" ? " err" : ""}`} role="status" aria-live="polite">
          <span className="mg-save-text">
            {status ? status.text : problem ? `⚠ ${problem}` : "You have changes that are not on the device yet."}
          </span>
          {dirty && (
            <span className="mg-save-tools">
              <button className="btn btn-ghost btn-sm" disabled={sending} onClick={() => selectedId && board && setDrafts((m) => ({ ...m, [selectedId]: board }))}>Discard</button>
              {devices.length > 1 && <button className="btn btn-ghost btn-sm" disabled={sending || !!problem} onClick={() => setSendDialog(true)}>Send to others…</button>}
              <button className="btn btn-primary btn-sm" disabled={sending || !!problem} onClick={send}>
                {sending ? "Sending…" : `Send to ${device?.name ?? "device"}`}
              </button>
            </span>
          )}
          {!dirty && devices.length > 1 && status?.kind === "ok" && (
            <button className="btn btn-ghost btn-sm" onClick={() => setSendDialog(true)}>Copy to other devices…</button>
          )}
        </div>
      )}

      {picker && draft && selectedId && (
        <ImagePicker
          title={picker.item === undefined ? "Choose a logo" : "Choose a picture"}
          current={picker.item === undefined
            ? draft.cards.find((c) => c.id === picker.card)?.image ?? ""
            : draft.cards.find((c) => c.id === picker.card)?.items[picker.item]?.image ?? ""}
          assets={assets[selectedId] ?? []}
          resolve={resolve}
          maxSide={live ? 1280 : 720}
          upload={upload}
          onPick={pick}
          onClose={() => setPicker(null)}
        />
      )}

      {sendDialog && device && (
        <SendDialog devices={devices} from={device} onSend={(ids) => void sendToOthers(ids)} onClose={() => setSendDialog(false)} />
      )}
    </div>
  );
}
