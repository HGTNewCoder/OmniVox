# Qt 6.11.0 Build Guide for aarch64 (Linux)

## Prerequisites

### 1. System Update
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

### 2. Install Dependencies
```bash
sudo apt-get install \
  libboost-all-dev libudev-dev libinput-dev libts-dev libmtdev-dev \
  libjpeg-dev libfontconfig1-dev libssl-dev libdbus-1-dev libglib2.0-dev \
  libxkbcommon-dev libegl1-mesa-dev libgbm-dev libgles2-mesa-dev \
  mesa-common-dev libasound2-dev libpulse-dev gstreamer1.0-omx \
  libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev gstreamer1.0-alsa \
  libvpx-dev libsrtp2-dev libsnappy-dev libnss3-dev "^libxcb.*" \
  flex bison libxslt-dev ruby gperf libbz2-dev libcups2-dev \
  libatkmm-1.6-dev libxi6 libxcomposite1 libfreetype6-dev libicu-dev \
  libsqlite3-dev libxslt1-dev software-properties-common

sudo apt install \
  libgles2-mesa-dev libegl1-mesa-dev mesa-common-dev libdrm-dev
```

---

## Download Sources
```bash
wget https://download.qt.io/official_releases/qt/6.11/6.11.0/submodules/qtbase-everywhere-src-6.11.0.tar.xz
wget https://files.pythonhosted.org/packages/8b/47/b25c13eca5bebc6505394d0223e46d7ebf0c57dcac2ed908d7d19b18ab6b/pyqt6-6.11.0.tar.gz
```

---

## Extract Archives
```bash
tar xf qtbase-everywhere-src-6.11.0.tar.xz
tar -xzf pyqt6-6.11.0.tar.gz
```

---

## Build Qt Base

### 1. Create Build Directory
```bash
mkdir qtbase-everywhere-src-6.11.0/build
cd qtbase-everywhere-src-6.11.0/build
```

### 2. Configure
```bash
export PKG_CONFIG_PATH=/usr/lib/aarch64-linux-gnu/pkgconfig

cmake -G Ninja \
  -DCMAKE_INSTALL_PREFIX=/opt/Qt/6.11.0-aarch64 \
  -DQT_FEATURE_opengles2=ON \
  -DQT_FEATURE_opengles3=ON \
  -DQT_FEATURE_kms=ON \
  -DQT_AVOID_CMAKE_ARCHIVING_API=ON \
  ..
```

### 3. Compile
```bash
cmake --build . --parallel 2
```

### 4. Install
```bash
cmake --install .
```
