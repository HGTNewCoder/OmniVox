# Qt 6.11.0 Build Guide for aarch64 (Linux)

## Target Environment
- **Device:** Raspberry Pi 4 / 5
- **OS:** Raspberry Pi OS Bookworm (64-bit)
- **Python:** 3.8 or higher

## Setup

### 1. System Update
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

### 2. Install Dependencies
```bash
sudo apt-get install -y \
  python3 python3-pip python3-venv python3-dev \
  build-essential cmake ninja-build pkg-config \
  flex bison ruby gperf \
  libboost-all-dev libudev-dev libinput-dev libts-dev libmtdev-dev \
  libssl-dev libdbus-1-dev libglib2.0-dev \
  libicu-dev libsqlite3-dev libbz2-dev libsnappy-dev \
  libxslt-dev libxslt1-dev libfontconfig1-dev libfreetype6-dev \
  libjpeg-dev libcups2-dev libpq-dev \
  libgl1-mesa-dev libgles2-mesa-dev libegl1-mesa-dev \
  mesa-common-dev libgbm-dev libdrm-dev \
  libx11-dev libx11-xcb-dev libxext-dev libxfixes-dev \
  libxi-dev libxi6 libxrender-dev libxcomposite1 \
  libxcb1-dev libxcb-glx0-dev libxcb-keysyms1-dev libxcb-image0-dev \
  libxcb-shm0-dev libxcb-icccm4-dev libxcb-sync-dev libxcb-xfixes0-dev \
  libxcb-shape0-dev libxcb-randr0-dev libxcb-render-util0-dev \
  libxcb-util-dev libxcb-xinerama0-dev libxcb-xkb-dev \
  libxkbcommon-dev libxkbcommon-x11-dev \
  libatspi2.0-dev libatkmm-1.6-dev \
  libnss3-dev libvpx-dev libsrtp2-dev \
  libasound2-dev libpulse-dev \
  libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
  gstreamer1.0-alsa gstreamer1.0-tools \
  gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
  gstreamer1.0-libcamera \ qt5-qmake \ qtbase5-dev
```

### 3. Clone the Repository
```bash
git clone https://github.com/HGTNewCoder/rasperrypi.git
cd rasperrypi
```

### 4. Set Up Python Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Run this every time you open a new terminal
pip install -r requirements.txt
```

### 5. Run the App
```bash
python app.py
```

# Optional
### 6. Install components for Raspberry Pi
```bash
wget https://files.waveshare.com/wiki/common/Brightness.zip
unzip Brightness.zip
cd Brightness
sudo chmod +x install.sh
./install.sh
```


sudo usermod -a -G gpio $USER

# Website (Next.js)
A landing page plus an interactive browser replica of the app lives in `web/`.
It reads `json_page/` at build time, so content changes show up automatically.

```bash
cd web
npm install
npm run dev        # http://localhost:3000
npm run build      # static site in web/out
npm run assets     # re-run after changing images in assets/ (needs Pillow)
```

The site is hosted on Vercel (project root: `web/`) and redeploys on every push to `main`.

The Card Manager demo is at `/manager/` on the website (simulated devices).

# Card Manager (master) and devices (clients)
OmniVox is two programs:

- **Client** (`app.py`, on each Raspberry Pi): the touchscreen board. Its cards and
  sub-cards come from `json_page/board.json`. A small background service
  (`client_agent.py`, port 8765) lets the Card Manager read and replace them; the
  screen redraws within a second, without a restart.
- **Master** (`master/server.py`, on any laptop on the same Wi-Fi): the Card
  Manager. It finds every OmniVox, then opens an editor in the browser for card
  names (English + Thai), logos, colours and sub-cards, with a live preview. Send
  the cards to one device, or copy them to several.

```bash
# once, on the laptop: build the manager page
cd web && npm install && npm run build && cd ..

# then, whenever you want to edit cards
python master/server.py                    # opens http://localhost:8800
python master/server.py --device 192.168.1.20   # if discovery is blocked (guest Wi-Fi)
```

Discovery uses UDP port 47800; the device listens on TCP 8765. Both must be
allowed on the network.

**Protect a device with a PIN.** Anyone on the same Wi-Fi can reach a device.
On each Pi, edit `device.json` (created on first run) and set `"pin": "1234"`,
then restart the app. The manager asks for the PIN before showing or changing cards.

**Try it without a Pi:** `python client_agent.py --port 8781 --name "Test bed"`
runs a device service on its own, using this folder's cards.

Each save keeps the previous `board.json` in `json_page/backups/` (last 10).
Older installs with `cards.json`, `food.json`, … are converted to `board.json`
automatically the first time the app starts.
