"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { ImageResolver } from "@/lib/asset";
import { preparePicture } from "./imageTools";

interface Props {
  title: string;
  current: string;
  assets: string[];
  resolve: ImageResolver;
  maxSide: number;
  upload: (blob: Blob) => Promise<string>;
  onPick: (path: string) => void;
  onClose: () => void;
}

/** Choose a picture already on the device, or upload a new one. */
export function ImagePicker({ title, current, assets, resolve, maxSide, upload, onPick, onClose }: Props) {
  const [query, setQuery] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);
  const boxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    boxRef.current?.focus();
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const shown = useMemo(() => {
    const q = query.trim().toLowerCase();
    const list = assets.filter((a) => !/alarm|mood_|^assets\/(yes|no|bell)\./.test(a));
    const filtered = q ? list.filter((a) => a.toLowerCase().includes(q)) : list;
    // Newly uploaded pictures first.
    return [...filtered.filter((a) => a.includes("/custom/")), ...filtered.filter((a) => !a.includes("/custom/"))];
  }, [assets, query]);

  const onFile = async (file: File | undefined) => {
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      const blob = await preparePicture(file, maxSide);
      onPick(await upload(blob));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mg-dim" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="mg-dialog mg-picker" role="dialog" aria-modal="true" aria-label={title} tabIndex={-1} ref={boxRef}>
        <div className="mg-dialog-head">
          <h3>{title}</h3>
          <button className="mg-icon-btn" onClick={onClose} aria-label="Close">✕</button>
        </div>
        <div className="mg-picker-tools">
          <button className="btn btn-primary btn-sm" disabled={busy} onClick={() => fileRef.current?.click()}>
            {busy ? "Uploading…" : "⬆ Upload a picture"}
          </button>
          <input
            ref={fileRef}
            type="file"
            accept="image/png,image/jpeg,image/webp,image/gif"
            hidden
            onChange={(e) => { void onFile(e.target.files?.[0]); e.target.value = ""; }}
          />
          <input
            className="mg-input"
            type="search"
            placeholder="Search pictures on the device…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button className="btn btn-ghost btn-sm" onClick={() => onPick("")}>No picture</button>
        </div>
        {error && <p className="mg-error">{error}</p>}
        <div className="mg-picker-grid">
          {shown.map((a) => (
            <button
              key={a}
              className={`mg-thumb${a === current ? " on" : ""}`}
              onClick={() => onPick(a)}
              title={a.replace(/^assets\//, "")}
            >
              <img src={resolve(a)} alt="" loading="lazy" />
              <span>{a.replace(/^assets\/(custom\/)?/, "").replace(/\.\w+$/, "")}</span>
            </button>
          ))}
          {shown.length === 0 && <p className="fine">No pictures match.</p>}
        </div>
      </div>
    </div>
  );
}
