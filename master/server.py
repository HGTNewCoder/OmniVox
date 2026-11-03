"""
OmniVox master — the card manager that controls OmniVox devices on the same Wi-Fi.

Run it on any laptop or PC (Python 3.9+, nothing to install):

    python master/server.py

It finds every OmniVox on the network, then opens the Card Manager in your
browser at http://localhost:8800. The manager page itself is the website's
/manager page (web/out), built once with `npm run build` in web/.

Options:
    --port 8800             port for the manager page
    --host 0.0.0.0          also allow phones/tablets on the network to open it
    --device 192.168.1.20   add a device by address (repeatable) when discovery
                            is blocked, e.g. on guest Wi-Fi
    --ui PATH               folder with the built website (default ../web/out)
    --no-browser            do not open a browser window
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_UI = os.path.normpath(os.path.join(HERE, "..", "web", "out"))
DEVICES_FILE = os.path.join(HERE, "devices.json")
DISCOVERY_PORT = 47800
DISCOVERY_QUERY = b"OMNIVOX?"
DEVICE_PORT = 8765
MAX_PROXY_BODY = 9_000_000
PROXY_HEADERS = ("Content-Type", "X-OmniVox-Pin")


class Registry:
    """Devices the master knows about: found by discovery or added by address."""

    def __init__(self, path: str):
        self.path = path
        self.lock = threading.Lock()
        self.devices: dict[str, dict] = {}
        self.manual: list[str] = []
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.manual = list(json.load(f).get("manual", []))
            except (OSError, ValueError):
                self.manual = []

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"manual": self.manual}, f, indent=2)

    @staticmethod
    def normalise_address(address: str) -> str:
        address = address.strip().removeprefix("http://").rstrip("/")
        if not address or "/" in address:
            raise ValueError("Enter an address like 192.168.1.20 or 192.168.1.20:8765")
        if ":" not in address:
            address = f"{address}:{DEVICE_PORT}"
        return address

    def add_manual(self, address: str):
        with self.lock:
            if address not in self.manual:
                self.manual.append(address)
                self.save()

    def forget(self, device_id: str):
        with self.lock:
            dev = self.devices.pop(device_id, None)
            if dev and dev["address"] in self.manual:
                self.manual.remove(dev["address"])
                self.save()

    def address_of(self, device_id: str) -> str | None:
        with self.lock:
            dev = self.devices.get(device_id)
            return dev["address"] if dev else None


def fetch_info(address: str, timeout: float = 1.5) -> dict | None:
    try:
        with urllib.request.urlopen(f"http://{address}/api/info", timeout=timeout) as r:
            info = json.loads(r.read().decode("utf-8"))
        return info if info.get("app") == "omnivox-client" else None
    except (OSError, ValueError, urllib.error.URLError):
        return None


def discover(wait: float = 1.0) -> list[str]:
    """Broadcast on the local network and collect device addresses that answer."""
    found = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(0.2)
        for target in ("255.255.255.255", "<broadcast>", "127.0.0.1"):
            try:
                sock.sendto(DISCOVERY_QUERY, (target, DISCOVERY_PORT))
            except OSError:
                pass
        end = time.time() + wait
        while time.time() < end:
            try:
                data, (ip, _port) = sock.recvfrom(1024)
            except socket.timeout:
                continue
            except OSError:
                break
            try:
                reply = json.loads(data.decode("utf-8"))
            except ValueError:
                continue
            if reply.get("app") == "omnivox-client":
                addr = f"{ip}:{int(reply.get('port', DEVICE_PORT))}"
                if addr not in found:
                    found.append(addr)
    finally:
        sock.close()
    return found


def scan(registry: Registry, use_discovery: bool = True) -> list[dict]:
    addresses = list(dict.fromkeys((discover() if use_discovery else []) + registry.manual))
    with ThreadPoolExecutor(max_workers=16) as pool:
        infos = list(pool.map(fetch_info, addresses))
    seen = {}
    for addr, info in zip(addresses, infos):
        if info and info["id"] not in seen:
            seen[info["id"]] = {
                "id": info["id"], "name": info["name"], "address": addr, "online": True,
                "pin_required": info.get("pin_required", False), "cards": info.get("cards", 0),
                "updated": info.get("updated"), "manual": addr in registry.manual,
            }
    with registry.lock:
        # Keep devices that went quiet in the list, marked offline.
        for dev_id, dev in registry.devices.items():
            if dev_id not in seen:
                seen[dev_id] = {**dev, "online": False}
        registry.devices = seen
        return sorted(seen.values(), key=lambda d: (not d["online"], d["name"].lower()))


class MasterHandler(BaseHTTPRequestHandler):
    registry: Registry
    ui_dir: str
    use_discovery: bool
    server_version = "OmniVoxMaster/1"

    def log_message(self, fmt, *args):
        if self.path.startswith("/api/") and "/assets/" not in self.path:
            print(f"[master] {fmt % args}")

    def _json(self, status: int, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> bytes | None:
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = -1
        if length < 0 or length > MAX_PROXY_BODY:
            self._json(413, {"error": "That is too large to send"})
            return None
        return self.rfile.read(length)

    # ---------------------------------------------------------------- routing
    def do_GET(self):
        self._route("GET")

    def do_POST(self):
        self._route("POST")

    def do_PUT(self):
        self._route("PUT")

    def do_DELETE(self):
        self._route("DELETE")

    def _route(self, method: str):
        path = urlparse(self.path).path
        if path == "/api/master" and method == "GET":
            return self._json(200, {"app": "omnivox-master", "version": 1})
        if path == "/api/devices":
            if method == "GET":
                return self._json(200, {"devices": scan(self.registry, self.use_discovery)})
            if method == "POST":
                return self._add_device()
        if path.startswith("/api/devices/"):
            rest = path[len("/api/devices/"):]
            dev_id, _, sub = rest.partition("/")
            if not sub and method == "DELETE":
                self.registry.forget(dev_id)
                return self._json(200, {"ok": True})
            if sub:
                return self._proxy(method, dev_id, sub)
        if method == "GET" and not path.startswith("/api/"):
            return self._static(path)
        self._json(404, {"error": "Not found"})

    def _add_device(self):
        body = self._read_body()
        if body is None:
            return
        try:
            address = Registry.normalise_address(json.loads(body or b"{}").get("address", ""))
        except (ValueError, AttributeError) as e:
            return self._json(422, {"error": str(e) or "Enter an address"})
        info = fetch_info(address, timeout=3)
        if not info:
            return self._json(404, {"error": f"No OmniVox answered at {address}"})
        self.registry.add_manual(address)
        devices = scan(self.registry, use_discovery=False)
        return self._json(200, next((d for d in devices if d["id"] == info["id"]), {}))

    def _proxy(self, method: str, dev_id: str, sub: str):
        address = self.registry.address_of(dev_id)
        if not address:
            scan(self.registry, self.use_discovery)
            address = self.registry.address_of(dev_id)
        if not address:
            return self._json(404, {"error": "That device is not on the network"})
        body = self._read_body() if method in ("POST", "PUT") else None
        if body is None and method in ("POST", "PUT"):
            return
        query = urlparse(self.path).query
        url = f"http://{address}/{sub}" + (f"?{query}" if query else "")
        req = urllib.request.Request(url, data=body, method=method)
        for h in PROXY_HEADERS:
            if self.headers.get(h):
                req.add_header(h, self.headers[h])
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                status, ctype, data = r.status, r.headers.get("Content-Type", ""), r.read()
        except urllib.error.HTTPError as e:
            status, ctype, data = e.code, e.headers.get("Content-Type", ""), e.read()
        except (OSError, urllib.error.URLError):
            return self._json(502, {"error": "The device did not answer — is it switched on?"})
        self.send_response(status)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store" if sub.startswith("api/") else "public, max-age=300")
        self.end_headers()
        self.wfile.write(data)

    def _static(self, path: str):
        if path in ("", "/"):
            self.send_response(302)
            self.send_header("Location", "/manager/")
            self.end_headers()
            return
        rel = unquote(path).lstrip("/")
        full = os.path.realpath(os.path.join(self.ui_dir, rel))
        base = os.path.realpath(self.ui_dir)
        if full != base and not full.startswith(base + os.sep):
            return self._json(404, {"error": "Not found"})
        if os.path.isdir(full):
            full = os.path.join(full, "index.html")
        if not os.path.isfile(full):
            return self._json(404, {"error": "Not found"})
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(full)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    p = argparse.ArgumentParser(description="OmniVox master: manage the cards on OmniVox devices.")
    p.add_argument("--port", type=int, default=8800)
    p.add_argument("--host", default="127.0.0.1", help="use 0.0.0.0 to allow other devices to open the manager")
    p.add_argument("--device", action="append", default=[], help="device address to add (repeatable)")
    p.add_argument("--ui", default=DEFAULT_UI, help="folder with the built website (web/out)")
    p.add_argument("--no-discovery", action="store_true", help="only use devices added by address")
    p.add_argument("--no-browser", action="store_true")
    args = p.parse_args()

    mimetypes.add_type("application/javascript", ".js")
    mimetypes.add_type("text/css", ".css")
    mimetypes.add_type("image/webp", ".webp")

    if not os.path.isfile(os.path.join(args.ui, "manager", "index.html")):
        sys.exit(f"Card Manager page not found in {args.ui}.\n"
                 "Build it once:  cd web && npm install && npm run build")

    registry = Registry(DEVICES_FILE)
    for d in args.device:
        registry.add_manual(Registry.normalise_address(d))

    MasterHandler.registry = registry
    MasterHandler.ui_dir = args.ui
    MasterHandler.use_discovery = not args.no_discovery
    httpd = ThreadingHTTPServer((args.host, args.port), MasterHandler)
    httpd.daemon_threads = True
    url = f"http://localhost:{args.port}/manager/"
    print(f"[master] OmniVox Card Manager running at {url}")
    found = scan(registry, MasterHandler.use_discovery)
    print(f"[master] {len([d for d in found if d['online']])} device(s) online: "
          + (", ".join(f"{d['name']} ({d['address']})" for d in found) or "none yet"))
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[master] stopped")


if __name__ == "__main__":
    main()
