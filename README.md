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

