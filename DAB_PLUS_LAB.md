# DAB+ Labs สำหรับ Raspberry Pi

โครงการแล็บการเรียนรู้ DAB+ (Digital Audio Broadcasting Plus) โดยใช้ Raspberry Pi และ RTL-SDR

## 📋 รายการแล็บทั้งหมด

### Lab 0: Introduction to DAB+, Python, FRP และ PyQt5 (เตรียมพร้อม)
- แนะนำเทคโนโลยี DAB+ และข้อดีเมื่อเทียบกับ FM
- เรียนรู้พื้นฐาน Python programming สำหรับมือใหม่
- ติดตั้งและใช้งาน FRP Client สำหรับเข้าถึง RTL-SDR ระยะไกล
- เรียนรู้พื้นฐาน PyQt5 GUI programming
- การสร้าง Touch-Friendly UI สำหรับหน้าจอสัมผัส 7"
- ความรู้เบื้องต้นเกี่ยวกับ RTL-SDR และ welle.io

### Lab 1: การติดตั้งและทดสอบ RTL-SDR
- ทดสอบการเชื่อมต่อและการทำงานของ RTL-SDR dongle บน Raspberry Pi
- ตรวจสอบการรู้จำอุปกรณ์และแก้ไขปัญหาไดรเวอร์
- เขียนฟังก์ชัน Python ทดสอบพื้นฐาน

### Lab 2: การใช้งาน welle.io ผ่าน Python
- เรียนรู้การควบคุม welle.io เพื่อรับสัญญาณ DAB+
- สแกนหาสถานี DAB+ และเล่นเสียง
- จัดการข้อมูลเมทาดาต้าและสไลด์โชว์

### Lab 3: Learning DAB+ with RTL-SDR (Progressive Development) ✅ COMPLETED
- **Progressive Development**: เรียนรู้ DAB+ แบบ step-by-step ใน 5 phases
- **Phase 1a**: lab3_1a.py - RTL-SDR I/Q data acquisition (pyrtlsdr)
- **Phase 1b**: lab3_1b.py - Network RTL-SDR client (rtl_tcp)
- **Phase 2**: lab3_2.py - ETI stream processing (eti-cmdline from `/home/pi/DAB_Plus_Labs/eti/`)
- **Phase 3**: lab3_3.py - ETI parser และ service extraction (uses JSON from eti-cmdline)
- **Phase 4**: lab3_4.py - Audio playback (ni2out from `/home/pi/DAB_Plus_Labs/eti/`)
- **Phase 5**: lab3_5.py - Complete PyQt5 GUI application with real audio integration

### Lab 4: สร้าง DAB+ Station Scanner (การบ้าน - 3-4 ชั่วโมง)
- สร้างแอปพลิเคชันสแกนสถานี DAB+ อย่างง่าย
- ใช้ Lab 3 pipeline สำหรับหาสถานี
- เก็บข้อมูลสถานีในฐานข้อมูล SQLite พื้นฐาน

### Lab 5: สร้าง DAB+ Program Recorder (การบ้าน - 3-4 ชั่วโมง)
- สร้างระบบบันทึกรายการ DAB+ อย่างง่าย
- ใช้ Lab 3 pipeline สำหรับบันทึกเสียง
- จัดการตารางเวลาการบันทึกพื้นฐาน

### Lab 6: สร้าง DAB+ Signal Analyzer (การบ้าน - 3-4 ชั่วโมง)
- สร้างเครื่องมือวิเคราะห์สัญญาณ DAB+ อย่างง่าย
- ใช้ Lab 3 pipeline สำหรับวิเคราะห์สัญญาณ
- แสดงค่า SNR, RSSI, BER แบบ real-time

## 🔧 ข้อกำหนดระบบ

### Hardware ที่จำเป็น:
- **Raspberry Pi 4** (แนะนำ 4GB RAM ขึ้นไป)
- **RTL-SDR V4 dongle** หรือเทียบเท่า
- **หน้าจอสัมผัส HDMI 7 นิ้ว** (อุปกรณ์เสริม)
- **หูฟัง 3.5mm** สำหรับฟังเสียง
- **เสาอากาศ DAB/FM** สำหรับรับสัญญาณ

### Software ที่จำเป็น:
- **Raspberry Pi OS Bookworm** (64-bit แนะนำ)
- **Python 3.11+**
- **PyQt5** สำหรับ GUI
- **RTL-SDR drivers และ libraries**
- **welle.io** สำหรับ DAB+ decoding

## 🚀 การติดตั้ง

### วิธีที่ 1: ใช้สคริปต์อัตโนมัติ (แนะนำ)

```bash
# โคลนโครงการ
git clone <repository-url> DAB_Plus_Labs
cd DAB_Plus_Labs

# รันสคริปต์ติดตั้งอัตโนมัติ
chmod +x install_deps.sh
sudo ./install_deps.sh

# ติดตั้ง Python packages
pip install -r requirements.txt
```

### วิธีที่ 2: ติดตั้งแมนนวล

```bash
# อัพเดทระบบ
sudo apt update && sudo apt upgrade -y

# ติดตั้ง dependencies หลัก
sudo apt install -y python3-pyqt5 python3-pyqt5.qtmultimedia \
    rtl-sdr librtlsdr0 librtlsdr-dev \
    cmake build-essential git \
    python3-matplotlib python3-scipy python3-numpy

# ติดตั้ง welle.io
sudo apt install -y qt5-qmake qtbase5-dev qtchooser \
    qtmultimedia5-dev libqt5multimedia5-plugins \
    libfaad-dev libmpg123-dev libfftw3-dev

# คอมไพล์ welle.io จากซอร์ส (ถ้าไม่มีใน apt)
git clone https://github.com/AlbrechtL/welle.io.git
cd welle.io && mkdir build && cd build
cmake .. && make -j4
sudo make install
```

## 📱 การรองรับหน้าจอสัมผัส

โครงการนี้รองรับหน้าจอสัมผัส 7 นิ้วด้วย:
- ปุ่มขนาดใหญ่ที่เหมาะสำหรับการสัมผัส
- Font ขนาดใหญ่เพื่อการมองเห็นที่ชัดเจน
- การจัดเรียง UI ที่เหมาะกับหน้าจอเล็ก
- รองรับ touch events และ gestures

### การตั้งค่าหน้าจอสัมผัส:

```bash
# ตั้งค่าความละเอียดใน /boot/config.txt
echo "hdmi_group=2" | sudo tee -a /boot/config.txt
echo "hdmi_mode=87" | sudo tee -a /boot/config.txt
echo "hdmi_cvt 1024 600 60 6 0 0 0" | sudo tee -a /boot/config.txt

# รีสตาร์ทระบบ
sudo reboot
```

## 🔊 การตั้งค่าเสียง

```bash
# ตั้งให้เสียงออกทาง 3.5mm jack
sudo raspi-config nonint do_audio 1

# ทดสอบเสียง
speaker-test -t wav -c 2
```

## 📚 วิธีใช้งาน

### สำหรับผู้เรียน (ใช้โฟลเดอร์ Labs/):
1. เปิดไฟล์ `Labs/Lab[X]/lab[X].py`
2. อ่านคู่มือใน `Labs/Lab[X]/LAB[X].md`
3. เติมโค้ดในส่วนที่มี TODO comments
4. ทดสอบการทำงานตามคู่มือ

### สำหรับผู้สอน (ใช้โฟลเดอร์ Solutions/):
- ไฟล์ใน `Solutions/` เป็นเฉลยครบถ้วน
- สามารถใช้เป็นตัวอย่างหรือเฉลยให้ผู้เรียน

### การรันแล็บแต่ละตัว:

```bash
# Lab 0: PyQt5 Introduction (เริ่มต้นที่นี่)
cd Labs/Lab0
python3 lab0.py

# Lab 1: RTL-SDR Testing
cd Labs/Lab1
python3 lab1.py

# Lab 2: Welle.io Integration
cd Labs/Lab2
python3 lab2.py

# ฯลฯ สำหรับแล็บอื่นๆ
```

## 🔍 การแก้ไขปัญหาเบื้องต้น

### ปัญหา RTL-SDR ไม่รู้จำอุปกรณ์:
```bash
# ตรวจสอบการเชื่อมต่อ USB
lsusb | grep RTL

# ตรวจสอบไดรเวอร์
rtl_test -t
```

### ปัญหา welle.io ไม่ทำงาน:
```bash
# ตรวจสอบการติดตั้ง
which welle-io

# ทดสอบการทำงาน
welle-io --help
```

### ปัญหา PyQt5 GUI ไม่แสดง:
```bash
# ตรวจสอบ X11 forwarding (ถ้าใช้ SSH)
echo $DISPLAY

# ตั้งค่า DISPLAY variable
export DISPLAY=:0.0
```

## 📈 การพัฒนาเพิ่มเติม

หลังจากทำแล็บทั้ง 6 แล็บแล้ว สามารถพัฒนาต่อได้ด้วย:
- การเชื่อมต่อกับ web API สำหรับข้อมูลสถานี
- การสร้าง mobile app ควบคุมผ่าน HTTP
- การบันทึกข้อมูลลง database
- การสร้าง streaming server

## 🤝 การสนับสนุน

หากพบปัญหาหรือต้องการความช่วยเหลือ:
1. ตรวจสอบไฟล์ LAB[X].md ในแต่ละแล็บ
2. ดู Solutions/ สำหรับตัวอย่างโค้ดที่ใช้งานได้
3. ตรวจสอบ logs และ error messages
4. ทดสอบ hardware connections

---

# 📚 เนื้อหาครบถ้วนของแต่ละ LAB

## 🎓 LAB 0: Introduction to DAB+, Python, FRP และ PyQt5

### ส่วนที่ 1: Introduction to DAB+ (15 นาที)

**DAB+** (Digital Audio Broadcasting Plus) คือเทคโนโลยีการแพร่สัญญาณวิทยุแบบดิจิทัล

#### ข้อดีของ DAB+ เมื่อเทียบกับ FM:
- **คุณภาพเสียงดิจิทัล** ไม่มี static หรือสัญญาณรบกวน
- **ข้อมูลเพิ่มเติม** Program Information, DLS, MOT Slideshow, EPG
- **ประสิทธิภาพการใช้คลื่น** Multiplexing และ SFN

#### ความถี่ DAB+ ในประเทศไทย:
- **Block 9A**: 202.928 MHz - กรุงเทพฯ (สถานีธรรมะ)
- **Block 6C**: 185.360 MHz - ขอนแก่น (สถานีท้องถิ่น)

#### เทคโนโลยีที่เกี่ยวข้อง:
- **RTL-SDR**: ตัวรับสัญญาณ USB ราคาถูก 24-1700 MHz
- **welle.io**: DAB+ Decoder แบบ open source

### ส่วนที่ 2: Introduction to Python สำหรับมือใหม่ (30 นาที)

#### Python คืออะไร?
Python คือภาษาโปรแกรมมิ่งที่ออกแบบมาให้เรียนรู้ง่าย เหมาะสำหรับผู้เริ่มต้น

#### ตัวอย่างโค้ด Python พื้นฐาน:
```python
# Variables และ Data Types
name = "DAB+ Radio"
frequency = 202.928
is_digital = True

# Lists และ Dictionaries
frequencies = [202.928, 185.360, 227.360]
station_info = {
    "name": "Thai PBS",
    "frequency": 202.928,
    "location": "Bangkok"
}

# Functions
def calculate_wavelength(frequency_mhz):
    speed_of_light = 299.792458  # million m/s
    wavelength = speed_of_light / frequency_mhz
    return wavelength

# Classes
class DABStation:
    def __init__(self, name, frequency):
        self.name = name
        self.frequency = frequency

    def get_info(self):
        return f"{self.name} - {self.frequency} MHz"
```

### ส่วนที่ 3: FRP Client สำหรับการเข้าถึง RTL-SDR ระยะไกล (30 นาที)

#### FRP (Fast Reverse Proxy) คืออะไร?
FRP เป็นเครื่องมือ reverse proxy ที่ช่วยให้เข้าถึง Raspberry Pi จากภายนอกผ่านอินเทอร์เน็ตได้ โดยไม่ต้องตั้งค่า Port Forwarding บน Router

#### การติดตั้ง FRP Client บน Raspberry Pi
```bash
# ดาวน์โหลด FRP สำหรับ ARM64
wget https://github.com/fatedier/frp/releases/download/v0.61.1/frp_0.61.1_linux_arm64.tar.gz
tar -xzvf frp_0.61.1_linux_arm64.tar.gz
cd frp_0.61.1_linux_arm64

# สำหรับ ARMv7 (32-bit)
wget https://github.com/fatedier/frp/releases/download/v0.61.1/frp_0.61.1_linux_arm.tar.gz
```

#### ตัวอย่าง Configuration (frpc.toml)
```toml
serverAddr = "xxx.xxx.xxx.xxx"
serverPort = 7000
auth.method = "token"
auth.token = "your_secret_token"

[[proxies]]
name = "piXX-tcp-1234"
type = "tcp"
localIP = "127.0.0.1"
localPort = 1234
remotePort = 60XX
```

#### ติดตั้งเป็น Systemd Service
```bash
# สร้าง service file
sudo nano /etc/systemd/system/frpc.service

# เนื้อหาใน service file:
[Unit]
Description=FRP Client
After=network.target

[Service]
Type=simple
ExecStart=/home/pi/frp/frpc -c /home/pi/frp/frpc.toml
Restart=always
User=pi

[Install]
WantedBy=multi-user.target

# เปิดใช้งาน
sudo systemctl enable frpc
sudo systemctl start frpc
```

#### การทดสอบจาก Google Colab
```python
import socket
import struct

# เชื่อมต่อไปยัง rtl_tcp ผ่าน FRP tunnel
server_ip = "xxx.xxx.xxx.xxx"  # FRP server IP
server_port = 60XX              # Remote port

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server_ip, server_port))
print(f"Connected to RTL-SDR via FRP tunnel")

# ตั้งค่าความถี่ 185.360 MHz (DAB+ Thailand)
freq = 185360000
cmd = struct.pack('>BI', 0x01, freq)
sock.send(cmd)
```

### ส่วนที่ 4: PyQt5 GUI Programming (30 นาที)

#### PyQt5 คืออะไร?
PyQt5 คือไลบรารีสำหรับสร้าง GUI (Graphical User Interface) ด้วย Python

#### ตัวอย่าง PyQt5 พื้นฐาน:
```python
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QLabel, QPushButton, QLineEdit

class DABPlayerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DAB+ Player")
        self.setGeometry(100, 100, 800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout(central_widget)

        # Widgets
        self.station_label = QLabel("📻 Station: Not Selected")
        self.frequency_input = QLineEdit()
        self.frequency_input.setPlaceholderText("Enter frequency (MHz)")

        self.tune_button = QPushButton("🎯 Tune")
        self.tune_button.clicked.connect(self.tune_station)

        # Add to layout
        layout.addWidget(self.station_label)
        layout.addWidget(self.frequency_input)
        layout.addWidget(self.tune_button)

    def tune_station(self):
        frequency = self.frequency_input.text()
        self.station_label.setText(f"📻 Station: {frequency} MHz")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DABPlayerApp()
    window.show()
    sys.exit(app.exec_())
```

---

## 🔌 LAB 1: การติดตั้งและทดสอบ RTL-SDR

### วัตถุประสงค์
- ทดสอบการเชื่อมต่อและการทำงานของ RTL-SDR dongle บน Raspberry Pi
- ตรวจสอบการรู้จำอุปกรณ์และแก้ไขปัญหาไดรเวอร์ DVB-T
- เขียนฟังก์ชัน Python ทดสอบพื้นฐาน

### อุปกรณ์ที่ใช้
- **Raspberry Pi 4** พร้อม Raspberry Pi OS Bookworm
- **RTL-SDR V4 dongle**
- **เสาอากาศ wideband** สำหรับรับสัญญาณ

### การติดตั้ง RTL-SDR
```bash
# ติดตั้ง RTL-SDR tools
sudo apt update && sudo apt upgrade -y
sudo apt install -y rtl-sdr librtlsdr0 librtlsdr-dev

# Blacklist DVB drivers
sudo nano /etc/modprobe.d/blacklist-rtl.conf
# เพิ่ม: blacklist dvb_usb_rtl28xxu

# udev rules
sudo nano /etc/udev/rules.d/20-rtlsdr.rules
# เพิ่ม: SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", GROUP="adm", MODE="0666"
```

### การทดสอบ
```bash
# ตรวจสอบอุปกรณ์
lsusb | grep RTL

# ทดสอบการทำงาน
rtl_test -t

# ทดสอบการอ่านข้อมูล
rtl_test -s 2048000
```

### การรัน rtl_tcp Server
```bash
# เริ่ม rtl_tcp server สำหรับ remote access
rtl_tcp -a 0.0.0.0 -p 1234 -d 0

# ตรวจสอบ server ทำงาน
netstat -an | grep 1234
```

### ตัวอย่างโค้ด Python สำหรับทดสอบ RTL-SDR (Direct Access)
```python
from rtlsdr import RtlSdr
import numpy as np

# เชื่อมต่อ RTL-SDR โดยตรง
sdr = RtlSdr()
sdr.sample_rate = 2.4e6
sdr.center_freq = 202.928e6  # DAB+ frequency

# อ่าน samples
samples = sdr.read_samples(1024)
print(f"Received {len(samples)} samples")

# คำนวณ power spectrum
fft_data = np.fft.fft(samples)
power = 20 * np.log10(np.abs(fft_data))

sdr.close()
```

### ตัวอย่างโค้ด Python สำหรับ rtl_tcp Client (Network Access)
```python
import socket
import struct
import numpy as np

# เชื่อมต่อไปยัง rtl_tcp server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 1234))

# ตั้งค่าความถี่ DAB+ Thailand (185.360 MHz)
freq_hz = 185360000
cmd = struct.pack('>BI', 0x01, freq_hz)
sock.send(cmd)

# ตั้งค่า sample rate (2.048 MHz)
sample_rate = 2048000
cmd = struct.pack('>BI', 0x02, sample_rate)
sock.send(cmd)

# รับ I/Q samples (8192 bytes = 4096 complex samples)
data = sock.recv(8192)
iq_uint8 = np.frombuffer(data, dtype=np.uint8)
iq_float = (iq_uint8 - 127.5) / 127.5
samples = iq_float[::2] + 1j * iq_float[1::2]

print(f"Received {len(samples)} complex samples")
sock.close()
```

### rtl_tcp Protocol Commands
```python
# Command format: 1 byte command + 4 bytes parameter (big endian)
# 0x01: Set frequency (Hz)
# 0x02: Set sample rate (Hz)
# 0x03: Set gain mode (0=auto, 1=manual)
# 0x04: Set gain (tenths of dB)
# 0x05: Set frequency correction (ppm)
```

---

## 📻 LAB 2: การใช้งาน welle.io ผ่าน Python

### วัตถุประสงค์
- เรียนรู้การควบคุม welle.io เพื่อรับสัญญาณ DAB+
- สแกนหาสถานี DAB+ และเล่นเสียง
- จัดการข้อมูลเมทาดาต้าและสไลด์โชว์

### การติดตั้ง welle.io
```bash
# ติดตั้ง dependencies
sudo apt install -y qt5-qmake qtbase5-dev libfaad-dev libmpg123-dev

# คอมไพล์จาก source
git clone https://github.com/AlbrechtL/welle.io.git
cd welle.io && mkdir build && cd build
cmake .. && make -j4 && sudo make install
```

### ความถี่ DAB+ ในไทย
- **Block 9A**: 202.928 MHz (กรุงเทพฯ)
- **Block 6C**: 185.360 MHz (ขอนแก่น)

### ตัวอย่างโค้ด Python Integration
```python
import subprocess
import json
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtMultimedia import QMediaPlayer

class DABReceiver:
    def __init__(self):
        self.frequencies = [202.928e6, 185.360e6]
        self.media_player = QMediaPlayer()

    def scan_stations(self):
        stations = []
        for freq in self.frequencies:
            cmd = ['welle-cli', '-D', '0', '-c', str(int(freq/1000))]
            result = subprocess.run(cmd, capture_output=True, text=True)
            # Parse welle.io output for stations
            stations.extend(self.parse_output(result.stdout))
        return stations

    def tune_station(self, frequency, service):
        cmd = ['welle-cli', '-D', '0', '-c', str(frequency), '-s', service]
        self.process = subprocess.Popen(cmd)
```

---

## 🔬 LAB 3: Learning DAB+ with RTL-SDR (Progressive Development) ✅ COMPLETED

### วัตถุประสงค์
- **เรียนรู้ Progressive Development**: สร้างระบบ DAB+ receiver แบบ step-by-step
- **เข้าใจ DAB+ Protocol**: ETI stream, FIC/FIG decoding, service multiplexing
- **สร้าง Complete GUI**: PyQt5 application สำหรับ 7" touchscreen
- **Audio Processing Chain**: I/Q → ETI → AAC → PyAudio

### ✅ Phase 1a: RTL-SDR I/Q Data Acquisition (lab3_1a.py)
```python
# ✅ COMPLETED - RTL-SDR direct access
from rtlsdr import RtlSdr
import numpy as np

class RTLSDRDataAcquisition:
    def __init__(self):
        self.frequency = 185360000  # DAB+ Thailand
        self.sample_rate = 2048000  # 2.048 MHz

    def capture_samples(self, duration_seconds=10):
        # Real-time I/Q capture และ spectrum analysis
        # Export: raw_iq_data.bin, spectrum_analysis.png
```

### ✅ Phase 1b: Network RTL-SDR Client (lab3_1b.py)
```python
# ✅ COMPLETED - rtl_tcp client implementation
class RTLTCPClient:
    def connect_to_server(self):
        # TCP client สำหรับ remote RTL-SDR access
        # Export: networked_iq_data.bin
```

### ✅ Phase 2: ETI Stream Processing (lab3_2.py)
```python
# ✅ COMPLETED - eti-cmdline integration
# Tool path: /home/pi/DAB_Plus_Labs/eti/eti-cmdline
# I/Q data → ETI stream (6144-byte frames)
# Sync monitoring และ error rate tracking
# Export: dab_ensemble.eti, ensemble-ch-6C.json
```

### ✅ Phase 3: ETI Parser และ Service Extraction (lab3_3.py)
```python
# ✅ COMPLETED - Simplified ETI analyzer using JSON from eti-cmdline
# Uses ensemble-ch-6C.json created by eti-cmdline (-J option)
# No manual ETI parsing required - uses pre-decoded data
# Export: service_list.json, subchannel_info.json
```

### ✅ Phase 4: Audio Playback และ Slideshow (lab3_4.py)
```python
# ✅ COMPLETED - Complete audio processing using ni2out
# Tool path: /home/pi/DAB_Plus_Labs/eti/ni2out
# ETI → AAC extraction (ni2out) → PCM decode (ffmpeg) → PyAudio playback
# Command-line options: -s for service ID, -l to list services
# ⚠️ MOT slideshow: ni2out does NOT support MOT extraction
# Use dablin_gtk or XPADxpert for MOT slideshow viewing
# Export: extracted_audio/*.aac, *_pcm.wav
```

### ✅ Phase 5: Complete GUI Application (lab3_5.py)
```python
# ✅ COMPLETED - Professional PyQt5 GUI
class DABPlusGUI(QMainWindow):
    def __init__(self):
        # 📱 Touch-optimized for 7" HDMI touchscreen
        # 📊 Real-time spectrum analyzer (pyqtgraph)
        # 🎵 Audio controls พร้อม QMediaPlayer
        # 🖼️ Slideshow viewer พร้อม auto-advance
        # ⚙️ RTL-SDR settings panel
        # 🌑 Dark theme optimized
```

### 🎯 Lab 3 Features Summary:
- **5 Complete Phases** - Progressive learning approach
- **Full Audio Chain** - I/Q capture → ETI → Service decode → Audio playback
- **Professional GUI** - Touch-friendly PyQt5 interface
- **Real-time Analysis** - Spectrum analyzer, signal quality monitoring
- **Complete Integration** - ทุก phase ทำงานร่วมกันได้
- **Thailand DAB+ Ready** - 185.360 MHz, 202.928 MHz support

### 🛠️ Lab 3 Tool Paths และข้อกำหนด:
**eti-tools Required** (build from https://github.com/JvanKatwijk/eti-tools):
- **eti-cmdline**: `/home/pi/DAB_Plus_Labs/eti/eti-cmdline` - I/Q → ETI conversion
- **ni2out**: `/home/pi/DAB_Plus_Labs/eti/ni2out` - ETI → Audio extraction

**⚠️ MOT Slideshow Limitations**:
- ni2out **ไม่รองรับ** MOT extraction
- **Alternative tools** for MOT viewing:
  - `dablin_gtk -i dab_ensemble.eti` (GUI with MOT display)
  - `XPADxpert.jar` (Java GUI tool for MOT extraction)
  - `welle-io` (Full DAB+ receiver with MOT support)

**Workflow Commands**:
```bash
# Phase 2: Generate ETI + JSON
/home/pi/DAB_Plus_Labs/eti/eti-cmdline -C 6C -B BAND_III -O dab_ensemble.eti -J

# Phase 4: List services from ETI
/home/pi/DAB_Plus_Labs/eti/ni2out --list -i dab_ensemble.eti

# Phase 4: Extract audio for specific service
/home/pi/DAB_Plus_Labs/eti/ni2out -i dab_ensemble.eti -s 0xa001 > audio.aac
```

### 📁 Output Files ที่ได้:
```
Lab3_Outputs/
├── raw_iq_data.bin              # Phase 1a: I/Q samples
├── networked_iq_data.bin        # Phase 1b: Network I/Q
├── dab_ensemble.eti             # Phase 2: ETI stream
├── service_list.json            # Phase 3: Services
├── subchannel_info.json         # Phase 3: Subchannels
├── extracted_audio/             # Phase 4: Audio files
├── slideshow_images/            # Phase 4: MOT images
└── spectrum_analysis.png        # Phase 1-5: Visualizations
```

### 🌐 Google Colab Version (สำหรับเรียนรู้ทางไกล)

LAB 3 มี Google Colab notebooks สำหรับผู้ที่ไม่มี Raspberry Pi หรือต้องการเรียนรู้ทางไกลผ่าน FRP tunnel

#### Lab3_Phase1_IQ_Acquisition_Colab.ipynb
- **RTLTCPClient class**: เชื่อมต่อ rtl_tcp ผ่าน FRP tunnel
- **I/Q Sample Acquisition**: รับและแปลงข้อมูล uint8 → complex
- **Spectrum Analysis**: FFT, PSD, constellation diagram
- **Real-time Monitoring**: signal strength, data rate tracking

```python
# ตัวอย่างการใช้งานใน Colab
client = RTLTCPClient(
    host='frp_server_ip',
    port=60XX  # FRP remote port
)
client.connect()
client.set_frequency(185360000)  # DAB+ Thailand
client.set_sample_rate(2048000)
samples = client.read_samples(num_samples=1024*1024)
```

#### Lab3_Phase2_ETI_Processing_Colab.ipynb
- **ETIFrameParser class**: วิเคราะห์ ETI frame structure
- **Simulated ETI Frames**: สำหรับการเรียนรู้โครงสร้าง
- **Sync Monitoring**: FSYNC pattern detection
- **FIC Extraction**: Fast Information Channel data

```python
# ตัวอย่าง ETI frame parsing
parser = ETIFrameParser()
header = parser.parse_header(frame_bytes)
if header['fsync_valid']:
    print(f"✓ Valid ETI frame, FC={header['fc']}")
```

#### Prerequisites สำหรับ Colab Notebooks:
1. **FRP Client** ติดตั้งบน Raspberry Pi
2. **rtl_tcp** server รันอยู่บน Raspberry Pi
3. **FRP Server** เปิด remote port สำหรับ rtl_tcp
4. **Internet Connection** สำหรับเชื่อมต่อ Colab → FRP → RPI

#### ข้อจำกัดของ Colab Version:
- **Network Latency**: อาจมีความล่าช้าจากการส่งข้อมูลผ่าน internet
- **No eti-cmdline**: ไม่สามารถรัน native tools บน Colab ได้
- **Educational Purpose**: เน้นการเรียนรู้โครงสร้างมากกว่าการทำงานจริง
- **Simulated Data**: บาง phase ใช้ข้อมูลจำลองสำหรับการศึกษา

#### ข้อดีของ Colab Version:
- **No Hardware Required**: เรียนได้โดยไม่ต้องมี RTL-SDR
- **Remote Learning**: เหมาะสำหรับการเรียนรู้ทางไกล
- **Code Examples**: ตัวอย่างโค้ดที่ชัดเจนและทดสอบง่าย
- **Visualization Ready**: matplotlib, numpy พร้อมใช้งาน

---

## 🔍 LAB 4: สร้าง DAB+ Station Scanner

### วัตถุประสงค์
- พัฒนาแอปพลิเคชันสแกนและติดตามสถานี DAB+
- ติดตามคุณภาพสัญญาณแบบเรียลไทม์
- สร้าง GUI ด้วย PyQt5 สำหรับหน้าจอสัมผัส

### Database Management
```python
import sqlite3

class DatabaseManager:
    def init_database(self):
        cursor.execute("""
            CREATE TABLE ensembles (
                frequency REAL,
                ensemble_label TEXT,
                scan_time TIMESTAMP
            )
        """)
```

### Automatic Scanning
- **ความถี่ DAB+ Band III** (174-240 MHz)
- **SQLite Database** เก็บข้อมูลสถานี
- **Real-time Quality** monitoring
- **Advanced PyQt5** TreeWidget, TableWidget

---

## ⏺️ LAB 5: สร้าง DAB+ Program Recorder

### วัตถุประสงค์
- พัฒนาระบบบันทึกรายการ DAB+ ตามตารางเวลา
- จัดการการบันทึกแบบแมนนวลและอัตโนมัติ
- จัดเก็บไฟล์เสียง สไลด์ และเมทาดาต้า

### Scheduling System
```python
import schedule
from datetime import datetime

class RecordingScheduler:
    def add_schedule(self, station, start_time, duration, repeat='once'):
        schedule_item = {
            'station': station,
            'start_time': start_time,
            'duration': duration
        }
```

### File Organization
```
DAB_Recordings/
├── 2024-12-08/
│   ├── Thai_PBS/
│   │   ├── audio.wav
│   │   ├── slideshow/
│   │   └── metadata.json
│   └── NBT/
└── logs/
```

---

## 📊 LAB 6: สร้าง DAB+ Signal Analyzer

### วัตถุประสงค์
- พัฒนาเครื่องมือวิเคราะห์สัญญาณ DAB+ อย่างละเอียด
- วิเคราะห์คุณภาพสัญญาณ (SNR, RSSI, BER)
- สร้างกราฟและรายงานการวิเคราะห์

### Advanced Analysis
- **OFDM Structure** วิเคราะห์
- **SNR, MER, BER** คุณภาพสัญญาณ
- **Constellation Diagram** I/Q แสดงผล
- **Waterfall Plot** spectrum ตามเวลา

### Visualization & Reports
- **Real-time Metrics** LCD displays
- **Professional Reports** PDF generation
- **Data Export** CSV, JSON formats
- **Advanced Matplotlib** integration

---

## 📄 License

โครงการนี้ใช้ MIT License - ดูรายละเอียดใน LICENSE file

## 🎯 สรุป

หลังจากเรียนจบ 7 Labs นี้แล้ว ผู้เรียนจะสามารถ:

1. **เข้าใจเทคโนโลยี DAB+** และข้อดีเมื่อเทียบกับ FM
2. **ใช้งาน RTL-SDR** สำหรับรับสัญญาณ RF และ DAB+
3. **เขียนโปรแกรม Python** และ PyQt5 GUI สำหรับหน้าจอสัมผัส
4. **ควบคุม welle.io** สำหรับถอดรหัส DAB+
5. **วิเคราะห์สัญญาณ RF** ด้วย DSP และ matplotlib
6. **สร้างแอปพลิเคชัน** scanner, recorder, และ analyzer
7. **จัดการฐานข้อมูล** SQLite และการ export ข้อมูล

### 📊 เวลาเรียนรวม: ~14-15 ชั่วโมง + 9-12 ชั่วโมงการบ้าน

#### หลักสูตรหลัก (Labs 1-3): 14-15 ชั่วโมง
- **Lab 1**: การติดตั้งและทดสอบ RTL-SDR (2-3 ชั่วโมง)
- **Lab 2**: การใช้งาน welle.io ผ่าน Python (3-4 ชั่วโมง)
- **Lab 3**: Learning DAB+ with RTL-SDR (5 phases, 9-8 ชั่วโมง)

#### การบ้าน (Labs 4-6): 9-12 ชั่วโมง
- **Lab 4**: DAB+ Station Scanner (3-4 ชั่วโมง)
- **Lab 5**: DAB+ Program Recorder (3-4 ชั่วโมง)
- **Lab 6**: DAB+ Signal Analyzer (3-4 ชั่วโมง)

**เป้าหมาย**: สร้างนักพัฒนา DAB+ ที่มีความรู้ครบถ้วนทั้งด้าน Hardware, Software และ GUI Development

---

**เวอร์ชัน**: 1.1
**วันที่**: กันยายน 2025
**ผู้เขียน**: DAB+ Learning Project
**เป้าหมาย**: Raspberry Pi OS Bookworm + RTL-SDR V4

---

**หมายเหตุ**: โครงการนี้พัฒนาขึ้นเพื่อการศึกษาเรียนรู้เท่านั้น ไม่ใช่เพื่อการใช้งานเชิงพาณิชย์

