"use client";

import { bundledImage, type ImageResolver } from "@/lib/asset";
import { boardProblem, type Board } from "@/lib/board";

export interface DeviceInfo {
  id: string;
  name: string;
  online: boolean;
  address?: string;
  pinRequired?: boolean;
  cards?: number;
  updated?: string | null;
  manual?: boolean;
}

export class TransportError extends Error {
  constructor(message: string, public status = 0) {
    super(message);
  }
}

/** How the Card Manager reaches devices: the real master server, or simulated beds. */
export interface Transport {
  mode: "live" | "demo";
  listDevices(): Promise<DeviceInfo[]>;
  addDevice?(address: string): Promise<DeviceInfo>;
  forgetDevice?(id: string): Promise<void>;
  getBoard(id: string): Promise<Board>;
  saveBoard(id: string, board: Board): Promise<Board>;
  listAssets(id: string): Promise<string[]>;
  uploadImage(id: string, blob: Blob): Promise<string>;
  copyImages(fromId: string, toId: string, paths: string[]): Promise<void>;
  rename(id: string, name: string): Promise<void>;
  identify(id: string): Promise<void>;
  imageUrl(id: string): ImageResolver;
  setPin?(id: string, pin: string): void;
  reset?(): void;
}

// ---------------------------------------------------------------- live (master/server.py)
const PIN_KEY = "omnivox-pins";

export class LiveTransport implements Transport {
  mode = "live" as const;
  private pins: Record<string, string> = {};

  constructor() {
    try { this.pins = JSON.parse(sessionStorage.getItem(PIN_KEY) || "{}"); } catch { this.pins = {}; }
  }

  setPin(id: string, pin: string) {
    this.pins[id] = pin;
    try { sessionStorage.setItem(PIN_KEY, JSON.stringify(this.pins)); } catch { /* private mode */ }
  }

  private async call<T>(path: string, init: RequestInit = {}, deviceId?: string): Promise<T> {
    const headers = new Headers(init.headers);
    if (deviceId && this.pins[deviceId]) headers.set("X-OmniVox-Pin", this.pins[deviceId]);
    let res: Response;
    try {
      res = await fetch(path, { ...init, headers, cache: "no-store" });
    } catch {
      throw new TransportError("The Card Manager server is not running.", 0);
    }
    const isJson = (res.headers.get("Content-Type") || "").includes("json");
    const body = isJson ? await res.json() : null;
    if (!res.ok) throw new TransportError(body?.error || `Request failed (${res.status})`, res.status);
    return body as T;
  }

  private dev(id: string, sub: string) {
    return `/api/devices/${encodeURIComponent(id)}/${sub}`;
  }

  async listDevices() {
    const r = await this.call<{ devices: (DeviceInfo & { pin_required?: boolean })[] }>("/api/devices");
    return r.devices.map((d) => ({ ...d, pinRequired: d.pin_required }));
  }

  async addDevice(address: string) {
    return this.call<DeviceInfo>("/api/devices", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ address }),
    });
  }

  async forgetDevice(id: string) {
    await this.call(`/api/devices/${encodeURIComponent(id)}`, { method: "DELETE" });
  }

  getBoard(id: string) {
    return this.call<Board>(this.dev(id, "api/board"), {}, id);
  }

  async saveBoard(id: string, board: Board) {
    await this.call(this.dev(id, "api/board"), {
      method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(board),
    }, id);
    return this.getBoard(id); // the device fills in defaults; show exactly what it saved
  }

  async listAssets(id: string) {
    return (await this.call<{ assets: string[] }>(this.dev(id, "api/assets"), {}, id)).assets;
  }

  async uploadImage(id: string, blob: Blob) {
    const r = await this.call<{ path: string }>(this.dev(id, "api/assets"), {
      method: "POST", headers: { "Content-Type": blob.type || "application/octet-stream" }, body: blob,
    }, id);
    return r.path;
  }

  async copyImages(fromId: string, toId: string, paths: string[]) {
    for (const p of paths) {
      const res = await fetch(this.dev(fromId, p), { cache: "no-store" });
      if (!res.ok) throw new TransportError(`Could not read ${p} from the first device`, res.status);
      await this.uploadImage(toId, await res.blob());
    }
  }

  async rename(id: string, name: string) {
    await this.call(this.dev(id, "api/device"), {
      method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name }),
    }, id);
  }

  async identify(id: string) {
    await this.call(this.dev(id, "api/identify"), { method: "POST" }, id);
  }

  imageUrl(id: string): ImageResolver {
    return (p) => (!p ? "" : /^(data:|blob:)/.test(p) ? p : this.dev(id, p));
  }
}

/** True when this page is served by master/server.py rather than the public website. */
export async function detectMaster(): Promise<boolean> {
  try {
    const r = await fetch("/api/master", { cache: "no-store" });
    if (!r.ok) return false;
    return (await r.json())?.app === "omnivox-master";
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------- demo (simulated beds)
const DEMO_KEY = "omnivox-demo-v1";
const wait = (ms: number) => new Promise((r) => setTimeout(r, ms));
const clone = <T,>(x: T): T => JSON.parse(JSON.stringify(x));

interface DemoDevice { id: string; name: string; board: Board }
interface DemoState { devices: DemoDevice[]; images: Record<string, string> }

function seed(base: Board): DemoState {
  const ward = clone(base);
  // Bed 2 starts with a slightly different set, to show each bed can be different.
  ward.cards = ward.cards.filter((c) => c.id !== "entertainment");
  return {
    devices: [
      { id: "bed-1", name: "Bed 1 · Mr. D", board: clone(base) },
      { id: "bed-2", name: "Bed 2 · Mrs. S", board: ward },
      { id: "dayroom", name: "Day room", board: clone(base) },
    ],
    images: {},
  };
}

function blobToDataUrl(blob: Blob) {
  return new Promise<string>((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(String(r.result));
    r.onerror = () => reject(r.error);
    r.readAsDataURL(blob);
  });
}

async function shortHash(blob: Blob) {
  const buf = await crypto.subtle.digest("SHA-1", await blob.arrayBuffer());
  return [...new Uint8Array(buf)].slice(0, 8).map((b) => b.toString(16).padStart(2, "0")).join("");
}

export class DemoTransport implements Transport {
  mode = "demo" as const;
  private state: DemoState;

  constructor(private base: Board, private bundled: string[]) {
    this.state = seed(base);
    try {
      const saved = JSON.parse(localStorage.getItem(DEMO_KEY) || "null") as DemoState | null;
      if (saved?.devices?.length) this.state = saved;
    } catch { /* storage blocked: start fresh */ }
  }

  private persist() {
    try { localStorage.setItem(DEMO_KEY, JSON.stringify(this.state)); } catch { /* full or blocked: keep in memory */ }
  }

  private device(id: string) {
    const d = this.state.devices.find((x) => x.id === id);
    if (!d) throw new TransportError("That device is not on the network", 404);
    return d;
  }

  reset() {
    this.state = seed(this.base);
    try { localStorage.removeItem(DEMO_KEY); } catch { /* ignore */ }
  }

  async listDevices() {
    await wait(250);
    return this.state.devices.map((d) => ({
      id: d.id, name: d.name, online: true, cards: d.board.cards.length, updated: d.board.updated,
      address: `simulated · ${d.id}`,
    }));
  }

  async getBoard(id: string) {
    await wait(150);
    return clone(this.device(id).board);
  }

  async saveBoard(id: string, board: Board) {
    await wait(450);
    const problem = boardProblem(board);
    if (problem) throw new TransportError(problem, 422);
    const saved = { ...clone(board), updated: new Date().toISOString().replace(/\.\d+Z$/, "Z") };
    this.device(id).board = saved;
    this.persist();
    return clone(saved);
  }

  async listAssets() {
    return [...this.bundled, ...Object.keys(this.state.images)].sort();
  }

  async uploadImage(_id: string, blob: Blob) {
    const ext = blob.type === "image/png" ? "png" : blob.type === "image/webp" ? "webp" : "jpg";
    const path = `assets/custom/${await shortHash(blob)}.${ext}`;
    this.state.images[path] = await blobToDataUrl(blob);
    this.persist();
    return path;
  }

  async copyImages() { /* simulated beds share one picture store */ }

  async rename(id: string, name: string) {
    this.device(id).name = name.trim().slice(0, 40) || this.device(id).name;
    this.persist();
  }

  async identify() { await wait(100); }

  imageUrl(): ImageResolver {
    return (p) => this.state.images[p] ?? bundledImage(p);
  }
}
