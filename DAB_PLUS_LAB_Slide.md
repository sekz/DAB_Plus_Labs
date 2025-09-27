---
marp: true
theme: default
class: lead
paginate: true
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')
header: 'DAB+ Labs for Raspberry Pi'
footer: 'Digital Audio Broadcasting Plus Learning Project'
---

<style>

section {
  font-size: 1.85em;
  padding: 2em;
}
section table { font-size: 16px; }
h1 {
  font-size: 1.25em;
}
h2 {
  font-size: 0.825em;
}
h3 {
  font-size: 0.75em;
}
li, p, td {
  font-size: 0.81em;
}
.columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}
code {
    font-size: 10px;
}
pre {
    font-size: 14px;
    line-height: 1.25;
    padding: 12px;
  }
  pre code {
    font-size: inherit;
        font-family: 'Fira Code', monospace;
  }
.code-small {
  font-size: 0.5em;
}
</style>

# 📻 DAB+ Labs สำหรับ Raspberry Pi

## คู่มือการเรียนรู้ Digital Audio Broadcasting Plus
### พร้อม RTL-SDR และ PyQt5

เวอร์ชัน 1.1 | กันยายน 2025

---

# 🎯 วัตถุประสงค์โครงการ

<div class="columns">
<div>

## 📚 เรียนรู้เทคโนโลยี
- **DAB+** จากพื้นฐานจนถึงขั้นสูง  
- **Python & PyQt5** GUI programming
- **Software Defined Radio** (SDR)
- **RF Signal Processing**

</div>
<div>

## 🛠️ สร้างแอปพลิเคชัน
- DAB+ Station Scanner
- Program Recorder
- Signal Analyzer
- Touch-Friendly GUI

</div>
</div>

**🎯 เป้าหมาย**: สร้างแอปที่ใช้งานได้จริงบน Raspberry Pi

---

# 🔧 ข้อกำหนดระบบ

<div class="columns">
<div>

## 🖥️ Hardware
- **Raspberry Pi 4** (4GB+ RAM)
- **RTL-SDR V4** Dongle
- **หน้าจอสัมผัส 7"** (HDMI)
- **หูฟัง 3.5mm**
- **เสาอากาศ DAB+**

</div>
<div>

## 💿 Software  
- **Raspberry Pi OS Bookworm**
- **Python 3.11+**
- **PyQt5** GUI Framework
- **welle.io** DAB+ Decoder
- **RTL-SDR** Libraries

</div>
</div>

---

# 📚 ภาพรวมแล็บทั้งหมด

## 🎯 Lab Series พื้นฐาน (เดิม - เน้น tools)
| Lab | หัวข้อ | เวลา | ระดับ |
|-----|--------|------|--------|
| **1** | การตั้งค่าเบื้องต้น RTL-SDR | 20 นาที | ⭐⭐ |
| **2** | การรับสัญญาณ DAB+ พื้นฐาน | 25 นาที | ⭐⭐⭐ |
| **3** | Command Line Tools สำหรับ DAB+ | 15 นาที | ⭐⭐⭐ |
| **4** | ETISnoop Analysis | 15 นาที | ⭐⭐⭐⭐ |
| **5** | สรุปและวิเคราะห์ขั้นสูง | 10 นาที | ⭐⭐⭐⭐⭐ |

**รวมเวลา**: ~1.25 ชั่วโมง (75 นาที) | **🎯 เป้าหมาย**: เรียนรู้การใช้งาน DAB+ tools

---

# 📚 ภาพรวมแล็บทั้งหมด (ต่อ)

## 🚀 Lab Series ขั้นสูง (ใหม่ - เน้น development + trap exercises)
| Lab | หัวข้อ | เวลา | ระดับ |
|-----|--------|------|--------|
| **1** | RTL-SDR Setup + Hardware Detection Traps | 2 ชั่วโมง | ⭐⭐⭐ |
| **2** | welle.io Integration + Audio Routing Traps | 2 ชั่วโมง | ⭐⭐⭐⭐ |
| **3** | pyrtlsdr Spectrum Analysis + IQ Processing Traps | 2 ชั่วโมง | ⭐⭐⭐⭐ |
| **4** | DAB+ Station Scanner + Database Traps | 2 ชั่วโมง | ⭐⭐⭐⭐ |
| **5** | Program Recorder + Scheduling Traps | 2 ชั่วโมง | ⭐⭐⭐⭐⭐ |
| **6** | Signal Analyzer + OFDM Analysis Traps | 2 ชั่วโมง | ⭐⭐⭐⭐⭐ |

**รวมเวลา**: ~12 ชั่วโมง | **🎯 เป้าหมาย**: สร้าง professional DAB+ applications

---

# 🎓 LAB 0: Introduction to DAB+, Python และ PyQt5
## 🕒 เวลารวม: 75 นาที (1 ชั่วโมง 15 นาที)

### 📋 ภาพรวมเนื้อหา
**เป็นแล็บพื้นฐานสำหรับมือใหม่** ที่ยังไม่เคยใช้ Python หรือไม่รู้จัก DAB+

---

# 📡 ส่วนที่ 1: DAB+ Technology (15 นาที)

<div class="columns">
<div>

## 🆚 DAB+ vs FM Radio
- **เสียงดิจิทัล** ไม่มี static หรือสัญญาณรบกวน
- **คุณภาพคงที่** ไม่ขึ้นกับระยะทาง
- **Metadata** ชื่อเพลง, ศิลปิน แบบ real-time
- **MOT Slideshow** รูปภาพ album art
- **Multiplexing** หลายสถานีใช้ความถี่เดียว

</div>
<div>

## 🇹🇭 DAB+ ในประเทศไทย (Sep 2025)
**สถานีทดสองออกอากาศ:**
- **Block 9A**: 202.928 MHz Dharma Radio Station (Bangkok)
- **Block 6C**: 185.360 MHz Khon Kaen Station (Khon Kaen, Maha Sarakham)


see: https://www.worlddab.org/countries/thailand
</div>
</div>

## 🛠️ เทคโนโลยีที่ใช้
- **RTL-SDR**: ตัวรับสัญญาณ USB (~500-1500 บาท)
- **welle.io**: DAB+ decoder แบบ open source
- **Python**: สำหรับควบคุมและประมวลผล

---

# 🐍 ส่วนที่ 2: Python สำหรับมือใหม่ (30 นาที)

<div class="columns">
<div>

## 📝 Python Basics
```python
# Variables และ Data Types
name = "สวัสดี"       # String
age = 25              # Integer
height = 175.5        # Float
is_student = True     # Boolean

# Lists และการใช้งาน
fruits = ["แอปเปิ้ล", "กล้วย", "ส้ม"]
fruits.append("มะม่วง")
print(len(fruits))    # แสดง: 4
```

</div>
<div>

## 🔄 Control Flow
```python
# Loops (การวนซ้ำ)
for fruit in fruits:
    print("ผลไม้:", fruit)

# Conditions (เงื่อนไข)
if age >= 18:
    print("เป็นผู้ใหญ่แล้ว")
else:
    print("เป็นเด็ก")

# Functions (ฟังก์ชัน)
def say_hello(name):
    return "สวัสดี " + name
```

</div>
</div>

---

# 🐍 Python: Classes และ Hardware Integration

<div class="columns">
<div>

## 🏗️ Object-Oriented Programming
```python
class DABStation:
    def __init__(self, name, frequency):
        self.name = name
        self.frequency = frequency
        self.is_playing = False

    def start_playing(self):
        self.is_playing = True
        print(f"เริ่มเล่น {self.name}")

    def stop_playing(self):
        self.is_playing = False
```

</div>
<div>

## 🔧 Raspberry Pi GPIO
```python
try:
    import RPi.GPIO as GPIO
    import time

    # ตั้งค่า GPIO pin 18
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)

    # กะพริบ LED
    GPIO.output(18, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(18, GPIO.LOW)

except ImportError:
    print("ทำงานบนคอมพิวเตอร์ทั่วไป")
```

</div>
</div>

---

# 🖥️ ส่วนที่ 3: PyQt5 Hands-on (30 นาที)

<div class="columns">
<div>

## 🧩 PyQt5 Components
```python
from PyQt5.QtWidgets import *
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # สร้าง central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # สร้าง layout
        layout = QVBoxLayout(central_widget)
```

</div>
<div>

## 📱 Touch-Friendly Design
```python
# ปุ่มขนาดใหญ่สำหรับสัมผัส
button = QPushButton("กดที่นี่")
button.setMinimumSize(120, 60)

# Font ขนาดใหญ่
font = QFont()
font.setPointSize(14)
button.setFont(font)

# CSS Styling
button.setStyleSheet("""
    QPushButton {
        border-radius: 8px;
        background: #3498db;
        color: white;
    }
""")
```

</div>
</div>

---

# 🖥️ PyQt5: Signals & Slots

<div class="columns">
<div>

## 🔗 Event Handling
```python
class DABPlayerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()

    def setup_connections(self):
        # เชื่อม signals กับ slots
        self.play_button.clicked.connect(self.on_play)
        self.volume_slider.valueChanged.connect(self.on_volume_change)

    def on_play(self):
        print("เริ่มเล่นเพลง!")
```

</div>
<div>

## ⏱️ QTimer และ Updates
```python
from PyQt5.QtCore import QTimer

class SignalMonitor(QWidget):
    def __init__(self):
        super().__init__()

        # Timer สำหรับ real-time update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_signal)
        self.timer.start(1000)  # อัพเดททุก 1 วินาที

    def update_signal(self):
        # อัพเดทค่าสัญญาณ
        signal_strength = self.get_signal_strength()
        self.signal_bar.setValue(signal_strength)
```

</div>
</div>

---

# 🎯 LAB 0: Demo Applications

<div class="columns">
<div>

## 📱 Demo 1: Basic Widgets
- **QLabel** แสดงข้อความและรูปภาพ
- **QPushButton** ปุ่มกดขนาดใหญ่
- **QLineEdit** ช่องใส่ข้อความ
- **QTextEdit** พื้นที่ข้อความหลายบรรทัด
- **QSlider** แถบเลื่อนค่า
- **QProgressBar** แสดงความคืบหน้า

</div>
<div>

## 📱 Demo 2: Touch Interface
- **ขนาดปุ่ม** อย่างน้อย 60x40 pixels
- **Font Size** 12-16pt สำหรับหน้าจอ 7"
- **Visual Feedback** เปลี่ยนสีเมื่อกด
- **Layout Management** responsive design
- **Error Handling** การจัดการข้อผิดพลาด

</div>
</div>

### ✅ สิ่งที่นักเรียนต้องเติม:
1. **อ่านชื่อ** จาก QLineEdit และแสดงใน QLabel
2. **ควบคุม QProgressBar** ด้วย QSlider
3. **เริ่ม/หยุด QTimer** และแสดงเวลาปัจจุบัน
4. **เปลี่ยนสี** ของปุ่มเมื่อกด (CSS styling)

---

# 🏆 LAB 0: ผลลัพธ์ที่คาดหวัง

<div class="columns">
<div>

## 🎯 ความรู้ที่ได้รับ
**DAB+ Technology:**
- เข้าใจความแตกต่างจาก FM
- รู้จักเทคโนโลยี RTL-SDR
- เข้าใจ DAB+ ในประเทศไทย

**Python Programming:**
- Variables, functions, classes
- File handling และ modules
- GPIO programming พื้นฐาน

</div>
<div>

## 🛠️ Skills ที่พร้อมใช้
**PyQt5 GUI Development:**
- Widget การใช้งานพื้นฐาน
- Signals & Slots system
- Touch-friendly UI design
- Real-time updates ด้วย QTimer

**เตรียมพร้อม** สำหรับ Labs ขั้นสูง!

</div>
</div>

### 🚀 Next Step: LAB 1 - RTL-SDR Hardware Setup

---

# 🔌 LAB 1: การตั้งค่าเบื้องต้น RTL-SDR (20 นาที)


<div>

## 🛠️ การติดตั้ง RTL-SDR Drivers
```bash
# อัพเดทระบบ
sudo apt update && sudo apt upgrade -y

# ติดตั้ง dependencies
sudo apt install libusb-1.0-0-dev git cmake pkg-config build-essential

# ดาวน์โหลดและติดตั้ง RTL-SDR Blog drivers
git clone https://github.com/rtlsdrblog/rtl-sdr-blog
cd rtl-sdr-blog
mkdir build && cd build
cmake ../ -DINSTALL_UDEV_RULES=ON
make
sudo make install
sudo ldconfig

# Blacklist DVB-T drivers
echo 'blacklist dvb_usb_rtl28xxu' | sudo tee --append /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf
```

</div>

---

<div class="columns">
<div>

## ✅ การทดสอบ
```bash
# รีบูทเครื่อง
sudo reboot

# ทดสอบ RTL-SDR
rtl_test -t
```

**สิ่งที่ควรตรวจสอบ:**
- [ ] RTL-SDR ถูกตรวจพบโดยระบบ
- [ ] ไม่มี error messages
- [ ] Ready สำหรับ Lab 2

</div>
</div>

---

## 🎯 Trap Exercises LAB 1:

### **Trap 1.1: Hardware Detection Challenge**
หลังรัน `lsusb` ให้วิเคราะห์ output และระบุว่า RTL-SDR อยู่ที่ port ไหน

### **Trap 1.2: Driver Permission Investigation**
หลัง blacklist DVB-T drivers ให้อธิบายทำไมต้อง blacklist และผลกระทบคืออะไร

### **Trap 1.3: PPM Calibration Analysis**
หลัง `rtl_test -t` ให้วิเคราะห์ PPM error และอธิบายความหมาย

---

# 📻 LAB 2: การรับสัญญาณ DAB+ พื้นฐาน (25 นาที)

<div class="columns">
<div>

## 🔧 การติดตั้ง welle.io
```bash
# ติดตั้ง welle.io จาก package manager
sudo apt install welle.io
```

## 🎛️ การตั้งค่า welle.io
- [ ] เปิดโปรแกรม welle.io
- [ ] เลือก Input Device: RTL-SDR
- [ ] ตั้งค่า Gain: Auto หรือ 20-30 dB

</div>
<div>

## 📡 ความถี่ DAB+ ในประเทศไทย (ตาม NBTC)
- [ ] **Channel 5C**: 178.352 MHz (Bangkok, Pattaya, Hua Hin)
- [ ] **Channel 6C**: 185.360 MHz (National Network)
- [ ] **Channel 7C**: 192.352 MHz (เชียงใหม่, ภาคใต้)
- [ ] **Channel 8C**: 199.360 MHz (Bangkok, Pattaya, Hua Hin)

## 🔍 ขั้นตอนการ Scan
- [ ] เลือก "Band III" (174-230 MHz)
- [ ] กด "Automatic Scan"
- [ ] รอให้ scan เสร็จ (2-3 นาที)
- [ ] ตรวจสอบ Services ที่พบ

</div>
</div>

## 🎯 Trap Exercises LAB 2:

### **Trap 2.1: Gain Setting Optimization**
ทดลองเปลี่ยน gain จาก Auto เป็น 10, 20, 30 dB และเปรียบเทียบผล

### **Trap 2.2: Channel Planning Strategy**
เลือก 2 channels จาก 4 channels ที่มี และอธิบายเหตุผลการเลือก

### **Trap 2.3: Signal Quality Assessment**
ตรวจสอบ Signal Strength > 50%, Audio Quality: Good/Excellent, Error Rate < 5%

---

# 🔬 LAB 3: Learning DAB+ with Raspberry Pi (Progressive Development)
## 🕒 เวลารวม: 8-10 ชั่วโมง (แบ่งเป็น 5 phases)

### 📋 ภาพรวม Lab 3: การพัฒนา DAB+ แบบ Step-by-Step
**เป็นแล็บหลักที่สอนการสร้าง DAB+ receiver ตั้งแต่ต้นจนจบ**

---

# 📡 Lab 3 ภาพรวมของ LAB

![alt text](img/Lab3_DAB_Plus_Flow_Diagram.svg)

---

# 📡 Lab 3 รายละเอียด Technical Architecture

![alt text](img/Lab3_Technical_Architecture.svg)

---

# 📡 Lab 3 Phase 1: RTL-SDR Data Acquisition

<div class="columns">
<div>

### **Phase 1a: pyrtlsdr I/Q Capture**
**เรียนรู้**: การใช้ pyrtlsdr library ควบคุม RTL-SDR เพื่อรับสัญญาณ I/Q จากความถี่ DAB+ ในประเทศไทย
```python
# lab3_1a.py - RTL-SDR พื้นฐาน
import numpy as np
from rtlsdr import RtlSdr

class DABSignalCapture:
    def __init__(self):
        self.sdr = RtlSdr()
        self.dab_freq = 185.360e6  # Thailand
        self.sample_rate = 2.048e6

    def setup_sdr(self):
        # TODO: ตั้งค่า RTL-SDR parameters
        # TODO: center frequency, sample rate, gain
        pass

    def capture_iq_data(self, duration=5):
        # TODO: รับ I/Q samples
        # TODO: คำนวณ spectrum
        # TODO: บันทึก raw data
        pass
```
**ผลลัพธ์**: สามารถรับและวิเคราะห์ spectrum ของสัญญาณ DAB+ ได้

</div>
<div>

### **Phase 1b: rtl_tcp Network Client**
**เรียนรู้**: การสร้าง TCP client เชื่อมต่อ rtl_tcp server เพื่อรับ I/Q data แบบ network streaming
```python
# lab3_1b.py - Network รับ I/Q ผ่าน TCP
import socket
import struct
import numpy as np

class RTLTCPClient:
    def __init__(self, host='localhost', port=1234):
        self.host = host
        self.port = port
        self.socket = None

    def connect_to_server(self):
        # TODO: เชื่อมต่อ rtl_tcp server
        # TODO: ส่งคำสั่งตั้งค่า frequency
        pass

    def receive_iq_stream(self):
        # TODO: รับ I/Q data แบบ streaming
        # TODO: แปลง bytes เป็น complex samples
        pass
```
**ผลลัพธ์**: สามารถรับ I/Q data ผ่าน network และเปรียบเทียบกับ USB direct connection

</div>
</div>

**🎯 ผลลัพธ์ Phase 1**: I/Q data capture, spectrum analysis, network streaming

---

# 🔄 Lab 3 Phase 2: ETI Stream Processing

<div class="columns">
<div>

### **ETI-cmdline Integration**
**เรียนรู้**: การใช้ eti-cmdline แปลงสัญญาณ I/Q จาก RTL-SDR เป็น ETI frames ขนาด 6144 bytes ต่อ frame
```python
# lab3_2.py - DAB+ Signal → ETI Conversion
import subprocess
import threading
from queue import Queue

class ETIProcessor:
    def __init__(self):
        self.eti_cmdline_path = "/usr/local/bin/eti-cmdline"
        self.eti_queue = Queue()
        self.sync_status = False

    def start_eti_processing(self):
        # TODO: เริ่ม eti-cmdline subprocess
        # TODO: ส่ง I/Q data เข้า stdin
        # TODO: รับ ETI frames จาก stdout
        pass

    def parse_eti_frame(self, eti_data):
        # TODO: แยก ETI frame (6144 bytes)
        # TODO: ตรวจสอบ sync pattern
        # TODO: คำนวณ error rate
        pass
```
**ผลลัพธ์**: ได้ ETI stream ที่สามารถแยกเป็น FIC และ MSC data

</div>
<div>

### **Signal Quality Monitoring**
**เรียนรู้**: การติดตาม sync status และ error rate เพื่อประเมินคุณภาพสัญญาณ DAB+ แบบ real-time
```python
class SignalQualityMonitor:
    def __init__(self):
        self.sync_rate = 0.0
        self.error_count = 0
        self.frame_count = 0

    def update_quality_metrics(self, frame):
        # TODO: คำนวณ sync success rate
        # TODO: ติดตาม error statistics
        # TODO: แสดงผล real-time status
        pass

    def display_status(self):
        # TODO: แสดง sync status ทุก 1 วินาที
        # TODO: แสดง error rate percentage
        # TODO: แสดง signal strength
        pass
```
**ผลลัพธ์**: มี metrics แสดงคุณภาพสัญญาณและความเสถียรของการรับสัญญาณ

</div>
</div>

**🎯 ผลลัพธ์ Phase 2**: ETI stream generation, sync monitoring, error tracking

---

# 🔍 Lab 3 Phase 3: ETI Analysis & Service Discovery

<div class="columns">
<div>

### **FIC (Fast Information Channel) Parser**
**เรียนรู้**: การถอดรหัส FIC data จาก ETI เพื่อดึงข้อมูล ensemble, services และ subchannels ผ่าน FIG decoding
```python
# lab3_3.py - ETI Frame Analysis
class FICParser:
    def __init__(self):
        self.ensemble_info = {}
        self.services = {}
        self.subchannels = {}

    def parse_fic_data(self, fic_bytes):
        # TODO: แยก FIG (Fast Information Group)
        # TODO: ดึง ensemble information
        # TODO: แยก service list
        pass

    def decode_fig_types(self, fig_data):
        # TODO: FIG 0/0 - Basic ensemble info
        # TODO: FIG 0/1 - Basic subchannel info
        # TODO: FIG 0/2 - Basic service info
        # TODO: FIG 1/0 - Service labels
        pass
```
**ผลลัพธ์**: สามารถแยกข้อมูล ensemble และ service list จาก DAB+ multiplex

</div>
<div>

### **Service Information Extraction**
**เรียนรู้**: การจัดระเบียบข้อมูล services และ export เป็น JSON สำหรับใช้งานใน phases ต่อไป
```python
class ServiceExtractor:
    def extract_services(self, fic_data):
        # TODO: สร้าง service database
        # TODO: จับคู่ service กับ subchannel
        # TODO: ดึง audio parameters
        pass

    def export_service_list(self):
        # TODO: บันทึกเป็น JSON format
        # TODO: ใส่ข้อมูล service labels
        # TODO: ระบุ audio bit rates
        return {
            "ensemble": "Thailand DAB+",
            "services": [
                {
                    "name": "Service 1",
                    "id": "0x1001",
                    "bitrate": 128,
                    "subchannel": 1
                }
            ]
        }
```
**ผลลัพธ์**: ไฟล์ service_list.json และ subchannel_info.json สำหรับ audio decoding

</div>
</div>

**🎯 ผลลัพธ์ Phase 3**: service_list.json, subchannel_info.json, ensemble metadata

---

# 🎵 Lab 3 Phase 4: Audio Processing & Playback


<div class="columns">
<div>

### **AAC Audio Decoder**
**เรียนรู้**: การแยก AAC audio frames จาก MSC data และ decode ด้วย ffmpeg + PyAudio สำหรับเล่นเสียงผ่าน 3.5mm jack
```python
# lab3_4.py - DAB+ Audio Processing
import subprocess
import pyaudio
from queue import Queue
import threading

class DABAudioDecoder:
    def __init__(self):
        self.audio_queue = Queue()
        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream = None
        self.current_service = None

    def extract_audio_frames(self, msc_data):
        # TODO: แยก audio super frames
        # TODO: ส่งข้อมูลไป ffmpeg decode
        # TODO: ได้ raw PCM audio
        pass

    def setup_audio_output(self):
        # TODO: ตั้งค่า PyAudio stream
        # TODO: รองรับ 3.5mm jack output
        # TODO: ควบคุม volume level
        pass
```
**ผลลัพธ์**: เล่นเสียง DAB+ ได้ผ่านหูฟัง พร้อมควบคุม volume

</div>
<div>

### **Dynamic Label & Slideshow**
**เรียนรู้**: การถอดรหัส DLS (song/artist info) และ MOT slideshow จาก PAD data เพื่อแสดงข้อมูลเพลงและรูปภาพ
```python
class DABMetadataProcessor:
    def __init__(self):
        self.current_dls = ""
        self.slideshow_images = []

    def process_dls_data(self, dls_bytes):
        # TODO: แยก Dynamic Label Segment
        # TODO: รวม segments เป็น text
        # TODO: แสดง song title, artist
        pass

    def process_mot_slideshow(self, mot_data):
        # TODO: แยก MOT (Multimedia Object Transfer)
        # TODO: ประกอบ JPEG/PNG images
        # TODO: บันทึกรูปภาพ slideshow
        pass

    def display_now_playing(self):
        # TODO: แสดง current track info
        # TODO: แสดง slideshow image
        pass
```
**ผลลัพธ์**: แสดงชื่อเพลง, ศิลปิน และ slideshow images แบบ real-time

</div>
</div>

**🎯 ผลลัพธ์ Phase 4**: Working audio player, DLS text, slideshow images

---

# 🖥️ Lab 3 Phase 5: Complete GUI Application


<div class="columns">
<div>

### **Touch-Optimized GUI**
**เรียนรู้**: การสร้าง PyQt5 GUI สำหรับหน้าจอสัมผัส 7" พร้อม spectrum analyzer และ dark theme
```python
# lab3_5.py - PyQt5 Complete Application
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg

class DABPlusGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 480)  # 7" screen
        self.setup_dark_theme()
        self.setup_main_interface()

    def setup_main_interface(self):
        # TODO: สร้าง tabbed interface
        # TODO: Spectrum tab, Services tab, Player tab
        # TODO: Settings tab สำหรับ RTL-SDR
        pass

    def setup_spectrum_analyzer(self):
        # TODO: Real-time spectrum plot
        # TODO: Waterfall display
        # TODO: Signal quality indicators
        pass
```
**ผลลัพธ์**: GUI application ที่ใช้งานง่ายบนหน้าจอสัมผัส

</div>
<div>

### **Integrated DAB+ Player**
**เรียนรู้**: การรวม Phase 1-4 เข้าด้วยกันเป็น complete pipeline จาก I/Q → Audio พร้อม GUI controls
```python
class DABPlayerController:
    def __init__(self, parent):
        self.parent = parent
        self.current_phase = 1
        self.all_components = {}

    def integrate_all_phases(self):
        # TODO: รวม Phase 1-4 เข้าด้วยกัน
        # TODO: I/Q → ETI → Services → Audio
        # TODO: Real-time processing pipeline
        pass

    def create_player_ui(self):
        # TODO: Service selection list
        # TODO: Audio controls (play/stop/volume)
        # TODO: DLS text display
        # TODO: Slideshow viewer
        # TODO: Signal quality meters
        pass
```
**ผลลัพธ์**: DAB+ receiver application ที่ทำงานครบวงจรตั้งแต่ RF จนถึงเสียง

</div>
</div>

**🎯 ผลลัพธ์ Phase 5**: Complete DAB+ receiver GUI application

---

# 🎯 Lab 3 Trap Exercises (แต่ละ Phase)

<div class="columns">
<div>

## **Phase 1 Traps:**
### **Trap 1.1: I/Q Data Analysis**
วิเคราะห์ spectrum ที่ได้และระบุ DAB+ signal peaks

### **Trap 1.2: Network Protocol**
อธิบายความแตกต่างระหว่าง USB และ TCP streaming

### **Trap 1.3: Sample Rate Optimization**
ทดลองเปลี่ยน sample rate และประเมินผลกระทบ

</div>
<div>

## **Phase 2-3 Traps:**
### **Trap 2.1: ETI Frame Structure**
วิเคราะห์ ETI frame header และอธิบาย fields

### **Trap 3.1: FIG Decoding**
ถอดรหัส FIG manually และเปรียบเทียบกับ parser

### **Trap 3.2: Service Discovery**
อธิบายขั้นตอนการค้นหา services ใน ensemble

</div>
</div>

<div class="columns">
<div>

## **Phase 4-5 Traps:**
### **Trap 4.1: Audio Pipeline**
วิเคราะห์ audio processing chain และ latency

### **Trap 4.2: Metadata Parsing**
ถอดรหัส DLS และ MOT data manually

### **Trap 5.1: GUI Performance**
วัด CPU/Memory usage และเพิ่มประสิทธิภาพ

</div>
<div>

## **Integration Traps:**
### **Trap 5.2: End-to-End Testing**
ทดสอบ complete pipeline จาก RF → Audio

### **Trap 5.3: Error Recovery**
จำลองสถานการณ์ signal loss และการกู้คืน

### **Trap 5.4: Multi-Service Support**
ปรับปรุงให้รองรับหลาย services พร้อมกัน

</div>
</div>

---

## 🎯 Trap Exercises LAB 3:

### **Trap 3.1: Spectrum Data Analysis**
วิเคราะห์ CSV file จาก rtl_power และหา peak ที่แต่ละความถี่ DAB+

### **Trap 3.2: Raw Data Capture Understanding**
อธิบายขนาดไฟล์ที่ได้จาก rtl_sdr และความสัมพันธ์กับ sample rate

### **Trap 3.3: PPM Error Interpretation**
อธิบายความหมายของ PPM error และผลกระทบต่อการรับสัญญาณ

---

# 🔍 LAB 4: ETISnoop - การวิเคราะห์ DAB+ Stream (15 นาที)

<div class="columns">
<div>

## 🛠️ การติดตั้ง ETISnoop

### **1. ติดตั้ง Dependencies**
```bash
sudo apt install build-essential cmake libfftw3-dev librtlsdr-dev
```

### **2. ดาวน์โหลดและ Compile ETISnoop**
```bash
# Clone repository
git clone https://github.com/JvanKatwijk/eti-snoop
cd eti-snoop

# Build
mkdir build && cd build
cmake ..
make
```

</div>

<div>

### **3. การใช้งาน ETISnoop**
```bash
## รัน ETISnoop กับ RTL-SDR
./eti-snoop -D RTL_SDR -C 6C
```

---

<div class="columns">
<div>

## 🔍 สิ่งที่ตรวจสอบใน ETISnoop

### **1. Ensemble Information**
- [ ] Ensemble Label
- [ ] Country Code
- [ ] ECC (Extended Country Code)
- [ ] Ensemble ID

### **2. Service Information**
- [ ] Service Labels
- [ ] Service IDs
- [ ] Program Types
- [ ] Bit Rates

</div>
<div>

### **3. Technical Parameters**
- [ ] Frame Error Rate
- [ ] Signal Quality
- [ ] Frequency Offset
- [ ] Time/Date Information
</div>

</div>

---

## 🎯 Trap Exercises LAB 4:

### **Trap 4.1: Build Troubleshooting**
ถ้า make ล้มเหลว ให้วิเคราะห์ error message และแก้ไข

### **Trap 4.2: Log Data Interpretation**
จาก log ให้ระบุ Service ID, Bit Rate และ Audio Codec ของแต่ละ service

---

# 📋 LAB 5: การตรวจสอบและวิเคราะห์สัญญาณขั้นสูง (10 นาที)

<div class="columns">
<div>

## 📊 รายงานผลการทดสอบรวม

### ตาราง checklist รวม:
| ความถี่ (MHz) | welle.io | Command Line | ETISnoop | Signal Quality |
|---------------|----------|--------------|----------|----------------|
| 178.352 (5C)  |          |              |          |                |
| 185.360 (6C)  |          |              |          |                |
| 192.352 (7C)  |          |              |          |                |
| 199.360 (8C)  |          |              |          |                |

</div>
<div>


### การเปรียบเทียบ Tools
| เครื่องมือ | ข้อดี | ข้อเสีย | เหมาะสำหรับ |
|------------|-------|---------|--------------|
| welle.io | GUI ใช้ง่าย, Real-time | Limited analysis | การฟังทั่วไป |
| Command Line | Fast, Scriptable | ต้องมีความรู้ | การทดสอบเทคนิค |
| ETISnoop | Deep analysis | ซับซ้อน | การวิเคราะห์ขั้นสูง |

</div>

---

<div class="columns">
<div>

## 📈 ข้อมูลที่ได้จากการทดสอบ
- [ ] **Coverage Area**: พื้นที่ที่รับสัญญาณได้
- [ ] **Service Availability**: บริการที่มีในแต่ละ ensemble
- [ ] **Technical Quality**: คุณภาพทางเทคนิค
- [ ] **Comparison Data**: เปรียบเทียบระหว่าง tools

## 🛠️ Automation Scripts
```bash
#!/bin/bash
echo "=== DAB+ Automated Test ==="
echo "1. Testing Hardware..."
rtl_test -t

echo "2. Scanning Spectrum..."
rtl_power -f 174M:230M:8k -g 30 -i 5 scan_$(date +%Y%m%d_%H%M).csv

echo "3. Testing Each Channel..."
for freq in 178352000 185360000 192352000 199360000; do
    echo "Testing $freq Hz..."
    timeout 30 rtl_sdr -f $freq -s 2048000 -n 1024000 test_$freq.raw
done

echo "Test Complete!"
```

</div>
</div>

---

## 🎯 Trap Exercises LAB 5:

### **Trap 5.1: Tool Performance Comparison**
สร้างตารางเปรียบเทียบ CPU usage, Memory usage และ Accuracy ของแต่ละ tool

### **Trap 5.2: Automation Script Development**
ปรับปรุง automation script ให้เหมาะสมกับสภาพแวดล้อมของคุณ

---

# 🔧 การแก้ไขปัญหาและ Troubleshooting

<div class="columns">
<div>

## 🚫 ปัญหาที่พบบ่อยและการแก้ไข

### **1. RTL-SDR ไม่ทำงาน**
- [ ] ตรวจสอบ USB connection
- [ ] ใช้คำสั่ง `lsusb` ดู device
- [ ] รีบูทระบบ
- [ ] ตรวจสอบ driver installation

### **2. Command Line Tools Error**
- [ ] ตรวจสอบ PATH environment
- [ ] ใช้ `which rtl_test` หา location
- [ ] Re-install rtl-sdr package


</div>
<div>

### **3. ETISnoop ไม่ compile**
- [ ] ติดตั้ง missing dependencies
- [ ] ใช้ `sudo apt install build-essential`
- [ ] ตรวจสอบ CMake version

### **4. ไม่พบสัญญาณ DAB+**
- [ ] ตรวจสอบตำแหน่งเสาอากาศ (วางแนวตั้ง)
- [ ] ลองย้ายไปใกล้หน้าต่าง
- [ ] เปลี่ยน gain setting ใน tools ต่างๆ
- [ ] ทดสอบใน welle.io ก่อน
</div>
<div>

---
## 🚫 ปัญหาที่พบบ่อยและการแก้ไข
<div class="columns">
<div>

### **5. เสียงไม่ดี/กระตุก**
- [ ] ตรวจสอบ CPU usage (`top` command)
- [ ] ลด sample rate ถ้าจำเป็น
- [ ] ปิดโปรแกรมอื่นที่ไม่จำเป็น

## 💡 เคล็ดลับเพิ่มเติม
- **เสาอากาศ**: ใช้แบบ vertical polarization
- **Gain Control**: เริ่มจาก Auto แล้วปรับตามต้องการ
- **Location**: ทดสอบในพื้นที่ที่ระบุใน NBTC frequency plan

</div>
<div>

### 🎯 ผลลัพธ์ที่คาดหวังหลังจบ Labs 1-5:
- [ ] ติดตั้งและใช้งาน RTL-SDR V4 ได้
- [ ] รับฟังสัญญาณ DAB+ ในประเทศไทยได้
- [ ] ใช้ Command Line Tools สำหรับการทดสอบ
- [ ] วิเคราะห์ DAB+ stream ด้วย ETISnoop
- [ ] เข้าใจพารามิเตอร์คุณภาพสัญญาณ
- [ ] แก้ไขปัญหาเบื้องต้นได้
- [ ] เปรียบเทียบประสิทธิภาพของ tools ต่างๆ

</div>
</div>

---

# 📊 LAB 6: สร้าง DAB+ Signal Analyzer (Advanced)

<div class="columns">
<div>

## 🔬 Advanced Analysis
- **OFDM Structure** วิเคราะห์
- **SNR, MER, BER** คุณภาพสัญญาณ
- **Constellation Diagram** I/Q แสดงผล
- **Waterfall Plot** spectrum ตามเวลา

</div>
<div>

## 📈 Visualization & Reports
- **Real-time Metrics** LCD displays
- **Professional Reports** PDF generation
- **Data Export** CSV, JSON formats
- **Advanced Matplotlib** integration

</div>
</div>

### 🎯 ผลลัพธ์: Professional DAB+ Signal Analyzer

---

# 📡 เทคโนโลยี DAB+ เบื้องลึก

<div class="columns">
<div>

## 🏗️ DAB+ Signal Structure
```
DAB+ Frame (96ms)
├── Null Symbol (sync)
├── PRS (Phase Reference) 
├── FIC (Fast Info Channel)
└── MSC (Main Service Channel)
    ├── Audio Services
    └── Data Services
```

</div>
<div>

## 🔄 OFDM Technology
- **2048 Carriers** ใช้พร้อมกัน
- **Guard Interval** ป้องกัน multipath
- **DQPSK Modulation** ทนต่อ noise
- **Error Correction** Reed-Solomon

</div>
</div>

**🎯 ความเข้าใจ**: จากพื้นฐานไปถึงระดับ Professional RF Engineer

---

# 🛠️ การพัฒนาด้วย PyQt5

<div class="columns">
<div>

## 🖥️ Touch-Friendly GUI
```python
# ปุ่มขนาดใหญ่
button.setMinimumSize(120, 60)

# Font สำหรับหน้าจอ 7"
font = QFont()
font.setPointSize(14)

# CSS Styling
button.setStyleSheet("""
    QPushButton {
        border-radius: 8px;
        background: #3498db;
        color: white;
        font-weight: bold;
    }
""")
```

</div>
<div>

## 🔗 Signals & Slots
```python
# Built-in signals
button.clicked.connect(self.on_click)
slider.valueChanged.connect(self.update_value)

# Custom signals
class MyWidget(QThread):
    data_ready = pyqtSignal(dict)
    
    def emit_data(self):
        self.data_ready.emit({'value': 42})
```

</div>
</div>

---

# 📊 การประมวลผลสัญญาณ (DSP)

<div class="columns">
<div>

## 🔢 NumPy & SciPy
```python
import numpy as np
from scipy import signal

# FFT Analysis
fft_result = np.fft.fft(iq_samples)
frequencies = np.fft.fftfreq(len(samples), 1/sample_rate)

# Power Spectrum
power_db = 20 * np.log10(np.abs(fft_result))

# Signal Quality
snr = signal_power / noise_power
```

</div>
<div>

## 📈 Real-time Visualization
```python
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

class SpectrumPlot(FigureCanvasQTAgg):
    def update_spectrum(self, freq, power):
        self.axes.clear()
        self.axes.plot(freq/1e6, power)
        self.draw()
```

</div>
</div>

---

# 🔧 การแก้ไขปัญหาทั่วไป

<div class="columns">
<div>

## 🚫 RTL-SDR Issues
```bash
# ตรวจสอบการเชื่อมต่อ
lsusb | grep RTL

# แก้ driver conflicts  
sudo modprobe -r dvb_usb_rtl28xxu
lsmod | grep dvb

# Permissions
sudo usermod -a -G plugdev $USER
```

</div>
<div>

## 🔇 Audio Issues
```bash
# ตั้งค่าเสียงออก 3.5mm
sudo raspi-config
# Advanced Options > Audio > Force 3.5mm

# ทดสอบเสียง
speaker-test -t wav -c 2

# PulseAudio restart
pulseaudio -k
```

</div>
</div>

**💡 เคล็ดลับ**: อ่านคู่มือแต่ละ LAB ก่อนเริ่มโค้ด

---

# 📈 เส้นทางการเรียนรู้

<div class="columns">
<div>

## 🎯 ระดับเริ่มต้น (Tools-based)
1. **Lab 0**: PyQt5 พื้นฐาน
2. **Lab 1**: RTL-SDR เบื้องต้น (20 นาที)
3. **Lab 2**: DAB+ รับฟัง (25 นาที)
4. **Lab 3**: Command Line Tools (15 นาที)
5. **Lab 4**: ETISnoop Analysis (15 นาที)

**⏱️ เวลา**: ~2 ชั่วโมง
**🎯 เป้าหมาย**: เรียนรู้ DAB+ tools พื้นฐาน

</div>
<div>

## 🚀 หลักสูตรหลัก + การบ้าน
### หลักสูตรหลัก (ผู้สอน 14-15 ชั่วโมง)
1. **Lab 1**: RTL-SDR Setup (2-3 ชม.)
2. **Lab 2**: welle.io Integration (3-4 ชม.)
3. **Lab 3**: DAB+ RTL-SDR Pipeline (5 phases, 9-8 ชม.)

### การบ้าน (นักเรียนทำเอง 9-12 ชั่วโมง)
4. **Lab 4**: Station Scanner (3-4 ชม.)
5. **Lab 5**: Program Recorder (3-4 ชม.)
6. **Lab 6**: Signal Analyzer (3-4 ชม.)

**⏱️ เวลา**: ~23-27 ชั่วโมง
**🎯 เป้าหมาย**: Professional DAB+ Applications

</div>
</div>

---

# 🎉 ผลลัพธ์ที่ได้รับ

<div class="columns">
<div>

## 🛠️ แอปพลิเคชันที่สร้างได้
**เริ่มต้น (Tools-based):**
- Basic DAB+ Reception
- Command Line Analysis

**ขั้นสูง (Development-based):**
- **RTL-SDR Hardware Controller**
- **DAB+ Station Scanner**
- **Program Recorder with Scheduling**
- **Real-time Spectrum Analyzer**
- **Professional Signal Analyzer**

**🎯 Trap Exercises**: ทดสอบความเข้าใจลึก

</div>
<div>

## 📚 ความรู้ที่ได้รับ
**เริ่มต้น:**
- DAB+ Technology พื้นฐาน
- Command Line Tools

**ขั้นสูง:**
- **Python & PyQt5** GUI Development
- **RF & DSP** Signal Processing
- **Real-time Audio Processing**
- **Database & Threading**
- **OFDM & Machine Learning**
- **Professional RF Analysis**

</div>
</div>

**✨ พัฒนาจาก ผู้เริ่มต้น → RF Engineer**

---

# 🌐 แหล่งข้อมูลเพิ่มเติม

<div class="columns">
<div>

## 📖 Documentation
- [welle.io GitHub](https://github.com/AlbrechtL/welle.io)
- [RTL-SDR.com](https://rtl-sdr.com)
- [PyQt5 Docs](https://doc.qt.io/qtforpython/)
- [DAB+ Standard (ETSI)](https://www.etsi.org/standards)

</div>
<div>

## 🎓 Learning Resources
- **GNU Radio** สำหรับ SDR ขั้นสูง
- **DSP Course** Signal Processing
- **RF Engineering** คลื่นวิทยุ
- **Embedded Linux** สำหรับ IoT

</div>
</div>

---

# 💫 Next Steps - ขั้นต่อไป

<div class="columns">
<div>

## 🔧 พัฒนาเพิ่มเติม
- **Web Interface** ควบคุมผ่าน browser
- **Mobile App** Android/iOS remote
- **Cloud Integration** upload recordings  
- **AI/ML** automatic classification

</div>
<div>

## 🎯 Career Paths
- **RF Engineer** วิศวกรคลื่นวิทยุ
- **SDR Developer** Software Defined Radio
- **IoT Developer** Internet of Things
- **Embedded Systems** ระบบฝังตัว

</div>
</div>

**🚀 จาก Hobby Project → Professional Career**

---

# 🙏 ขอบคุณและสนับสนุน

<div class="columns">
<div>

## 🎉 ขอบคุณที่เรียนรู้กับเรา!

**DAB+ Labs** เป็นโครงการ Open Source  
สำหรับการศึกษาและพัฒนาเทคโนโลยี เพื่อให้ความรู้่เกี่ยวกับ ระบบวิทยุดิจิตอล DAB+ และการจัดทำเครื่องรับ DAB+ ด้วยตนเอง จัดการอบรมโดย กสทช.

**🌟 ขอให้สนุกกับการเรียนรู้!**

</div>
<div>

## 📞 ติดต่อและสนับสนุน

- **💬 Issues**: GitHub Issues
- **📧 Email**: project contact
- **📱 Community**: Forum discussion  
- **⭐ Star**: ถ้าชอบโครงการ

**MIT License** - ใช้ได้อย่างอิสระ

</div>
</div>

---

# 📝 สรุป: การเดินทาง DAB+ Learning

## 🎯 สิ่งที่เราได้เรียนรู้:
- **DAB+ Technology** จาก 0 ถึง Hero
- **Python & PyQt5** สำหรับ Professional GUI
- **RTL-SDR & RF Engineering** ด้วยมือ
- **Project Development** จาก Idea ถึง Working App

## 🏆 Achievement Unlocked:
**📻 DAB+ Expert | 🐍 Python GUI Master | 📡 RF Engineer | 🔧 Maker**

---

**🎊 พร้อมสำหรับการผจญภัยใหม่แล้ว! 🎊**