# DAB+ Labs สำหรับ Raspberry Pi

โครงการแล็บการเรียนรู้ DAB+ (Digital Audio Broadcasting Plus) โดยใช้ Raspberry Pi และ RTL-SDR

## 📋 รายการแล็บทั้งหมด

### Lab 0: Introduction to DAB+ และ PyQt5 (เตรียมพร้อม)
- แนะนำเทคโนโลยี DAB+ และข้อดีเมื่อเทียบกับ FM
- เรียนรู้พื้นฐาน PyQt5 GUI programming ใน 1 ชั่วโมง
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
- **Phase 2**: lab3_2.py - ETI stream processing (eti-cmdline)
- **Phase 3**: lab3_3.py - ETI parser และ service extraction
- **Phase 4**: lab3_4.py - Audio playback และ slideshow
- **Phase 5**: lab3_5.py - Complete PyQt5 GUI application

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

## 🎓 LAB 0: Introduction to DAB+, Python และ PyQt5

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

### ส่วนที่ 3: PyQt5 GUI Programming (30 นาที)

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

### ตัวอย่างโค้ด Python สำหรับทดสอบ RTL-SDR
```python
from rtlsdr import RtlSdr
import numpy as np

# เชื่อมต่อ RTL-SDR
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
# I/Q data → ETI stream (6144-byte frames)
# Sync monitoring และ error rate tracking
# Export: dab_ensemble.eti
```

### ✅ Phase 3: ETI Parser และ Service Extraction (lab3_3.py)
```python
# ✅ COMPLETED - Complete ETI analyzer
class ETIFrameParser:
    def parse_eti_frame(self, frame_data):
        # Parse 6144-byte ETI-NI frames
        # FIC/FIG decoding สำหรับ service information
        # Export: service_list.json, subchannel_info.json
```

### ✅ Phase 4: Audio Playback และ Slideshow (lab3_4.py)
```python
# ✅ COMPLETED - Complete audio processing
class DABServicePlayer:
    def play_service(self, service_id):
        # ETI → AAC decode → PyAudio playback
        # Dynamic Label Segment (DLS) extraction
        # MOT slideshow image handling
        # Export: decoded_audio.wav, slideshow_images/
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

