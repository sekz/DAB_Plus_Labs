#!/bin/bash
# install_deps.sh - สคริปต์ติดตั้งอัตโนมัติสำหรับ DAB+ Labs
# สำหรับ Raspberry Pi OS Bookworm

set -e  # หยุดทำงานถ้าเกิด error

echo "=== การติดตั้ง DAB+ Labs Dependencies ==="
echo "สำหรับ Raspberry Pi OS Bookworm"
echo ""

# ตรวจสอบว่าเป็น root หรือไม่
if [[ $EUID -ne 0 ]]; then
   echo "โปรดรันสคริปต์นี้ด้วย sudo"
   echo "sudo $0 $*"
   exit 1
fi

echo "กำลังอัพเดทระบบ..."
apt update && apt upgrade -y

echo "กำลังติดตั้ง Python และ PyQt5..."
apt install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-pyqt5 \
    python3-pyqt5.qtmultimedia \
    python3-pyqt5.qtwidgets \
    python3-pyqt5.qtgui \
    python3-pyqt5.qtcore

echo "กำลังติดตั้ง scientific Python packages..."
apt install -y \
    python3-numpy \
    python3-scipy \
    python3-matplotlib \
    python3-requests

echo "กำลังติดตั้ง RTL-SDR dependencies..."
apt install -y \
    rtl-sdr \
    librtlsdr0 \
    librtlsdr-dev \
    usbutils

echo "กำลังติดตั้ง build tools สำหรับคอมไพล์..."
apt install -y \
    cmake \
    build-essential \
    git \
    pkg-config \
    libudev-dev

echo "กำลังติดตั้ง Qt5 development packages สำหรับ welle.io..."
apt install -y \
    qt5-qmake \
    qtbase5-dev \
    qtchooser \
    qt5-qmake \
    qtbase5-dev-tools \
    qtmultimedia5-dev \
    libqt5multimedia5-plugins \
    qttools5-dev-tools

echo "กำลังติดตั้ง audio codecs..."
apt install -y \
    libfaad-dev \
    libmpg123-dev \
    libfftw3-dev \
    libasound2-dev \
    pulseaudio

echo "กำลังติดตั้ง additional libraries..."
apt install -y \
    libusb-1.0-0-dev \
    libjack-jackd2-dev \
    jackd2

# ตั้งค่า udev rules สำหรับ RTL-SDR
echo "กำลังตั้งค่า udev rules สำหรับ RTL-SDR..."
cat > /etc/udev/rules.d/20-rtlsdr.rules << 'EOF'
# RTL-SDR rules
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2832", GROUP="adm", MODE="0666", SYMLINK+="rtl_sdr"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", GROUP="adm", MODE="0666", SYMLINK+="rtl_sdr"
SUBSYSTEM=="usb", ATTRS{idVendor}=="1d50", ATTRS{idProduct}=="604b", GROUP="adm", MODE="0666", SYMLINK+="rtl_sdr"
SUBSYSTEM=="usb", ATTRS{idVendor}=="1209", ATTRS{idProduct}=="2832", GROUP="adm", MODE="0666", SYMLINK+="rtl_sdr"
EOF

# Blacklist DVB-T drivers ที่อาจขัดแย้ง
echo "กำลังตั้งค่า blacklist DVB-T drivers..."
cat > /etc/modprobe.d/blacklist-rtl.conf << 'EOF'
# Blacklist DVB-T drivers that conflict with RTL-SDR
blacklist dvb_usb_rtl28xxu
blacklist rtl2832
blacklist rtl2830
blacklist dvb_usb_rtl2832u
blacklist dvb_core
blacklist dvb_usb
blacklist usbcore
EOF

# ตั้งค่าให้ user อยู่ใน group ที่จำเป็น
echo "กำลังเพิ่ม user ใน groups ที่จำเป็น..."
usermod -a -G audio,dialout,plugdev pi 2>/dev/null || echo "User pi not found, skipping usermod"

# ตั้งค่า audio output เป็น 3.5mm jack
echo "กำลังตั้งค่า audio output..."
if command -v raspi-config >/dev/null 2>&1; then
    raspi-config nonint do_audio 1  # Force 3.5mm jack
fi

echo "กำลังคอมไพล์และติดตั้ง welle.io..."
cd /tmp

# ตรวจสอบว่ามี welle.io อยู่แล้วหรือไม่
if ! command -v welle-io >/dev/null 2>&1; then
    echo "กำลังดาวน์โหลด welle.io source code..."
    if [ -d "welle.io" ]; then
        rm -rf welle.io
    fi
    
    git clone https://github.com/AlbrechtL/welle.io.git
    cd welle.io
    
    mkdir -p build
    cd build
    
    echo "กำลังคอมไพล์ welle.io (อาจใช้เวลาหลายนาที)..."
    cmake .. -DRTLSDR=ON -DCLI=ON -DGUI=ON
    make -j$(nproc)
    
    echo "กำลังติดตั้ง welle.io..."
    make install
    ldconfig
    
    echo "welle.io ติดตั้งสำเร็จแล้ว"
else
    echo "welle.io ติดตั้งอยู่แล้ว"
fi

cd /

echo "กำลังติดตั้ง pyrtlsdr..."
pip3 install pyrtlsdr

echo "กำลังตั้งค่า touchscreen (ถ้ามี)..."
# เพิ่มการตั้งค่าสำหรับหน้าจอสัมผัส 7 นิ้ว
if ! grep -q "hdmi_group=2" /boot/config.txt; then
    echo "" >> /boot/config.txt
    echo "# Settings for 7-inch touchscreen" >> /boot/config.txt
    echo "hdmi_group=2" >> /boot/config.txt
    echo "hdmi_mode=87" >> /boot/config.txt
    echo "hdmi_cvt 1024 600 60 6 0 0 0" >> /boot/config.txt
    echo "display_rotate=0" >> /boot/config.txt
fi

echo "กำลัง reload udev rules..."
udevadm control --reload-rules
udevadm trigger

echo ""
echo "=== การติดตั้งเสร็จสิ้น ==="
echo ""
echo "สิ่งที่ติดตั้งแล้ว:"
echo "✓ Python 3 และ PyQt5"
echo "✓ RTL-SDR drivers และ libraries"
echo "✓ welle.io DAB+ decoder"
echo "✓ Scientific Python packages"
echo "✓ Audio และ touchscreen support"
echo ""
echo "ขั้นตอนต่อไป:"
echo "1. รีสตาร์ทระบบ: sudo reboot"
echo "2. เสียบ RTL-SDR USB dongle"
echo "3. ทดสอบด้วย: rtl_test -t"
echo "4. รันแล็บแรก: cd Labs/Lab1 && python3 lab1.py"
echo ""
echo "หมายเหตุ:"
echo "- ควรรีสตาร์ทระบบก่อนใช้งาน"
echo "- ตรวจสอบว่า RTL-SDR dongle เสียบแล้ว"
echo "- ใช้คำสั่ง 'rtl_test' เพื่อทดสอบอุปกรณ์"
echo ""

read -p "ต้องการรีสตาร์ทระบบตอนนี้หรือไม่? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "กำลังรีสตาร์ทระบบ..."
    sleep 2
    reboot
else
    echo "โปรดรีสตาร์ทระบบด้วยตนเองด้วย: sudo reboot"
fi