"""
OmniVox client agent — lets the master (card manager) control this device over Wi-Fi.

app.py starts it in the background. It can also run on its own, without the
touchscreen app, which is handy for trying the master on a laptop:

    python client_agent.py                      # serves this folder's cards
    python client_agent.py --port 8781 --name "Test bed"

What it offers (HTTP on port 8765, JSON):
    GET  /api/info        name, id and card count (no PIN needed)
    GET  /api/board       the current board.json
    PUT  /api/board       replace the board; the touchscreen reloads its cards
    GET  /api/assets      list of pictures on the device
    POST /api/assets      upload a picture (raw PNG / JPEG / WebP / GIF bytes)
    GET  /assets/<file>   download a picture
    PUT  /api/device      rename the device   {"name": "Bed 4"}
    POST /api/identify    flash the device name on its screen

Discovery: the master broadcasts "OMNIVOX?" on UDP port 47800 and every device
answers with its id, name and HTTP port.

Security: anyone on the same network can reach the agent. Set a PIN in
device.json ("pin": "1234") and the master will ask for it before changing
anything.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import mimetypes
import os
import socket
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

import omnivox_board as boardlib

AGENT_VERSION = 1
DEFAULT_PORT = 8765
DISCOVERY_PORT = 47800
DISCOVERY_QUERY = b"OMNIVOX?"
MAX_BOARD_BYTES = 1_000_000
MAX_IMAGE_BYTES = 8_000_000
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif")
_MAGIC = {
    b"\x89PNG\r\n\x1a\n": "png",
    b"\xff\xd8\xff": "jpg",
    b"GIF87a": "gif",
    b"GIF89a": "gif",
}


def sniff_image(data: bytes) -> str | None:
    """Return the file extension for PNG / JPEG / GIF / WebP bytes, else None."""
    for magic, ext in _MAGIC.items():
        if data.startswith(magic):
            return ext
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


class DeviceIdentity:
    """device.json: a stable id, a friendly name and an optional PIN."""

    def __init__(self, path: str, default_name: str | None = None):
        self.path = path
        self._lock = threading.Lock()
        data = {}
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, ValueError):
                data = {}
        self.id = str(data.get("id") or uuid.uuid4().hex[:12])
        self.name = str(data.get("name") or default_name or socket.gethostname())
        self.pin = str(data.get("pin") or "")
        if data.get("id") != self.id or data.get("name") != self.name:
            self.save()

    def save(self):
        with self._lock:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"id": self.id, "name": self.name, "pin": self.pin}, f, ensure_ascii=False, indent=2)
            os.replace(tmp, self.path)

    def rename(self, name: str):
        name = " ".join(str(name).split())[:40]
        if not name:
            raise ValueError("The name cannot be empty")
        self.name = name
        self.save()


class ClientAgent:
    def __init__(self, root: str = ".", json_dir: str | None = None, device_file: str | None = None,
                 port: int = DEFAULT_PORT, name: str | None = None,
                 on_change=None, on_identify=None, discovery: bool = True):
        self.root = os.path.abspath(root)
        self.json_dir = os.path.abspath(json_dir or os.path.join(self.root, "json_page"))
        self.assets_dir = os.path.join(self.root, "assets")
        self.identity = DeviceIdentity(device_file or os.path.join(self.root, "device.json"), name)
        self.port = port
        self.on_change = on_change or (lambda board: None)
        self.on_identify = on_identify or (lambda name: None)
        self.discovery = discovery
        self._board_lock = threading.Lock()
        self._httpd: ThreadingHTTPServer | None = None
        self._udp: socket.socket | None = None
        self.board = boardlib.load_board(self.json_dir)

    # ---------------------------------------------------------------- info
    def info(self) -> dict:
        return {
            "app": "omnivox-client",
            "version": AGENT_VERSION,
            "id": self.identity.id,
            "name": self.identity.name,
            "port": self.port,
            "pin_required": bool(self.identity.pin),
            "updated": self.board.get("updated"),
            "cards": len(self.board["cards"]),
        }

    def check_pin(self, given: str | None) -> bool:
        if not self.identity.pin:
            return True
        return hmac.compare_digest((given or "").encode(), self.identity.pin.encode())

    # ---------------------------------------------------------------- board & pictures
    def replace_board(self, raw) -> dict:
        with self._board_lock:
            self.board = boardlib.save_board(self.json_dir, raw)
        self.on_change(self.board)
        return self.board

    def list_assets(self) -> list[str]:
        out = []
        for dirpath, _dirs, files in os.walk(self.assets_dir):
            for fn in files:
                if fn.lower().endswith(IMAGE_EXTS):
                    rel = os.path.relpath(os.path.join(dirpath, fn), self.root).replace(os.sep, "/")
                    out.append(rel)
        return sorted(out)

    def save_asset(self, data: bytes) -> str:
        ext = sniff_image(data)
        if not ext:
            raise ValueError("Only PNG, JPEG, WebP or GIF pictures can be uploaded")
        name = f"{hashlib.sha1(data).hexdigest()[:16]}.{ext}"
        folder = os.path.join(self.assets_dir, "custom")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, name)
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(data)
        return f"assets/custom/{name}"

    def asset_file(self, rel: str) -> str | None:
        """Map a URL path like 'assets/food.png' to a file, refusing anything outside assets/."""
        rel = unquote(rel).lstrip("/")
        if not rel.lower().endswith(IMAGE_EXTS):
            return None
        full = os.path.realpath(os.path.join(self.root, rel))
        base = os.path.realpath(self.assets_dir) + os.sep
        if not full.startswith(base) or not os.path.isfile(full):
            return None
        return full

    # ---------------------------------------------------------------- servers
    def start(self):
        agent = self

        class Handler(_Handler):
            pass
        Handler.agent = agent

        self._httpd = ThreadingHTTPServer(("0.0.0.0", self.port), Handler)
        self._httpd.daemon_threads = True
        threading.Thread(target=self._httpd.serve_forever, name="omnivox-http", daemon=True).start()
        if self.discovery:
            threading.Thread(target=self._discovery_loop, name="omnivox-discovery", daemon=True).start()
        return self

    def stop(self):
        if self._httpd:
            self._httpd.shutdown()
            self._httpd.server_close()
        if self._udp:
            self._udp.close()

    def _discovery_loop(self):
        try:
            udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp.bind(("0.0.0.0", DISCOVERY_PORT))
        except OSError as e:
            print(f"[agent] discovery disabled ({e}); add this device by IP in the master")
            return
        self._udp = udp
        while True:
            try:
                data, addr = udp.recvfrom(512)
            except OSError:
                return
            if data.strip() == DISCOVERY_QUERY:
                reply = {"app": "omnivox-client", "id": self.identity.id,
                         "name": self.identity.name, "port": self.port}
                try:
                    udp.sendto(json.dumps(reply).encode(), addr)
                except OSError:
                    pass


class _Handler(BaseHTTPRequestHandler):
    agent: ClientAgent
    server_version = "OmniVoxClient/1"

    def log_message(self, fmt, *args):
        if not self.path.startswith(("/assets/", "/api/info")):
            print(f"[agent] {self.address_string()} {fmt % args}")

    # ---------------------------------------------------------------- helpers
    def _json(self, status: int, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status: int, message: str):
        self._json(status, {"error": message})

    def _body(self, limit: int) -> bytes | None:
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = -1
        if length < 0 or length > limit:
            self._error(413, "That is too large to send")
            return None
        return self.rfile.read(length)

    def _authorised(self) -> bool:
        if self.agent.check_pin(self.headers.get("X-OmniVox-Pin")):
            return True
        self._error(401, "This device needs its PIN")
        return False

    def _json_body(self, limit: int):
        if "application/json" not in (self.headers.get("Content-Type") or ""):
            self._error(415, "Send JSON")
            return None
        raw = self._body(limit)
        if raw is None:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            self._error(400, "That is not valid JSON")
            return None

    # ---------------------------------------------------------------- routes
    def do_GET(self):
        path = urlparse(self.path).path
        a = self.agent
        if path == "/api/info":
            return self._json(200, a.info())
        if path.startswith("/assets/"):
            return self._send_asset(path)
        if not self._authorised():
            return
        if path == "/api/board":
            return self._json(200, a.board)
        if path == "/api/assets":
            return self._json(200, {"assets": a.list_assets()})
        self._error(404, "Not found")

    def do_PUT(self):
        path = urlparse(self.path).path
        a = self.agent
        if not self._authorised():
            return
        if path == "/api/board":
            raw = self._json_body(MAX_BOARD_BYTES)
            if raw is None:
                return
            try:
                board = a.replace_board(raw)
            except boardlib.BoardError as e:
                return self._error(422, str(e))
            return self._json(200, {"ok": True, "updated": board["updated"], "cards": len(board["cards"])})
        if path == "/api/device":
            raw = self._json_body(10_000)
            if raw is None:
                return
            try:
                a.identity.rename(raw.get("name", "") if isinstance(raw, dict) else "")
            except ValueError as e:
                return self._error(422, str(e))
            return self._json(200, a.info())
        self._error(404, "Not found")

    def do_POST(self):
        path = urlparse(self.path).path
        a = self.agent
        if not self._authorised():
            return
        if path == "/api/assets":
            data = self._body(MAX_IMAGE_BYTES)
            if data is None:
                return
            try:
                return self._json(201, {"path": a.save_asset(data)})
            except ValueError as e:
                return self._error(415, str(e))
        if path == "/api/identify":
            a.on_identify(a.identity.name)
            return self._json(200, {"ok": True})
        self._error(404, "Not found")

    def _send_asset(self, path: str):
        full = self.agent.asset_file(path)
        if not full:
            return self._error(404, "No such picture")
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(full)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "public, max-age=300")
        self.end_headers()
        self.wfile.write(data)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)  # show log lines immediately, even under systemd
    p = argparse.ArgumentParser(description="Run the OmniVox client agent without the touchscreen app.")
    p.add_argument("--root", default=os.path.dirname(os.path.abspath(__file__)),
                   help="folder that holds json_page/ and assets/")
    p.add_argument("--json-dir", help="use a different json_page folder (e.g. for a test device)")
    p.add_argument("--device-file", help="use a different device.json")
    p.add_argument("--port", type=int, default=int(os.environ.get("OMNIVOX_PORT", DEFAULT_PORT)))
    p.add_argument("--name", help="device name used the first time device.json is created")
    p.add_argument("--no-discovery", action="store_true", help="do not answer discovery broadcasts")
    args = p.parse_args()

    agent = ClientAgent(root=args.root, json_dir=args.json_dir, device_file=args.device_file,
                        port=args.port, name=args.name, discovery=not args.no_discovery,
                        on_change=lambda b: print(f"[agent] new board saved: {len(b['cards'])} cards"),
                        on_identify=lambda n: print(f"[agent] identify: {n}"))
    agent.start()
    print(f"[agent] '{agent.identity.name}' ({agent.identity.id}) listening on port {agent.port}")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        agent.stop()


if __name__ == "__main__":
    main()
