# LAB 5: สร้าง DAB+ Program Recorder

## วัตถุประสงค์
- พัฒนาระบบบันทึกรายการ DAB+ ตามตารางเวลา
- สร้าง GUI สำหรับจัดการการบันทึกและไฟล์เสียง
- จัดเก็บไฟล์เสียง, สไลด์, และเมทาดาต้าอย่างเป็นระบบ

## ความรู้พื้นฐานที่ต้องมี
- ความเข้าใจจาก Lab 1-4 (RTL-SDR, welle.io, pyrtlsdr, DAB+ scanning)
- การใช้งาน PyQt5 และ QMediaPlayer
- การจัดการไฟล์และโฟลเดอร์ใน Python
- การใช้งาน threading และ scheduling

## อุปกรณ์ที่ใช้
- **Raspberry Pi 4** พร้อม RTL-SDR V4 dongle
- **หน้าจอสัมผัส HDMI 7"** สำหรับควบคุม
- **เสาอากาศ DAB/FM** ที่มีประสิทธิภาพสูง
- **พื้นที่เก็บข้อมูลเพียงพอ** สำหรับไฟล์เสียง

## การเตรียมระบบ

### คำสั่งติดตั้ง Dependencies:

```bash
# ติดตั้ง QMediaPlayer และ PyQt5
sudo apt install -y python3-pyqt5 python3-pyqt5.qtmultimedia

# ติดตั้ง audio tools
sudo apt install -y sox lame ffmpeg

# ติดตั้ง Python packages
pip3 install PyQt5 matplotlib schedule
```

### ตั้งค่า Storage Directories:

```bash
mkdir -p ~/dab_recordings/audio
mkdir -p ~/dab_recordings/metadata
mkdir -p ~/dab_recordings/slides
```

## ขั้นตอนการทำงาน

### 1. ทำความเข้าใจ Recording Workflow

- ผู้ใช้เลือกสถานีและตั้งเวลาบันทึก
- ระบบเริ่มบันทึกเสียงและ metadata ตามเวลาที่กำหนด
- ไฟล์เสียงและข้อมูลถูกจัดเก็บแยกโฟลเดอร์
- สามารถเล่นไฟล์เสียงย้อนหลังผ่าน GUI

### 2. เรียกใช้งาน Lab GUI

```bash
cd Labs/Lab5
python3 lab5.py
```

## การเขียนโค้ด

### ส่วนที่ต้องเติมใน `lab5.py`:

#### 1. RecordingScheduler - การจัดการตารางบันทึก:

```python
import schedule
import threading
from datetime import datetime

class RecordingScheduler:
    def __init__(self):
        self.schedules = []
        self.running = False

    def add_schedule(self, station, start_time, duration):
        """เพิ่มตารางบันทึกใหม่"""
        # TODO: เพิ่มข้อมูลตารางบันทึก
        pass

    def check_pending_recordings(self):
        """ตรวจสอบและเริ่มบันทึกเมื่อถึงเวลา"""
        # TODO: ตรวจสอบเวลาปัจจุบันกับตาราง
        pass
```

#### 2. DABRecorder - การบันทึกสัญญาณ:

```python
from PyQt5.QtMultimedia import QMediaRecorder

class DABRecorder:
    def __init__(self, output_path):
        self.output_path = output_path
        # TODO: เตรียม QMediaRecorder หรือ subprocess สำหรับบันทึก

    def start_recording(self, station, duration):
        """เริ่มบันทึกเสียง"""
        # TODO: เรียกใช้งาน QMediaRecorder หรือ ffmpeg
        pass

    def stop_recording(self):
        """หยุดบันทึกเสียง"""
        # TODO: หยุดการบันทึก
        pass
```

#### 3. RecordingManager - การจัดการไฟล์:

```python
import os

class RecordingManager:
    def __init__(self, base_dir="~/dab_recordings"):
        self.base_dir = os.path.expanduser(base_dir)
        self.create_directories()

    def create_directories(self):
        """สร้างโฟลเดอร์สำหรับเก็บไฟล์"""
        # TODO: สร้างโฟลเดอร์ audio, metadata, slides
        pass

    def organize_recording(self, station, start_time):
        """จัดเก็บไฟล์เสียงและข้อมูล"""
        # TODO: จัดเก็บไฟล์ในโฟลเดอร์ที่เหมาะสม
        pass

    def get_recording_info(self):
        """ดึงข้อมูลไฟล์บันทึกทั้งหมด"""
        # TODO: คืนรายการไฟล์เสียงและ metadata
        pass
```

#### 4. ScheduleWidget - GUI จัดการตารางเวลา:

```python
class ScheduleWidget(QWidget):
    def setup_ui(self):
        layout = QVBoxLayout(self)
        # TODO: เพิ่มตารางแสดง schedule, ปุ่มเพิ่ม/ลบ/แก้ไข
        pass
```

#### 5. RecordingListWidget - รายการบันทึก:

```python
class RecordingListWidget(QWidget):
    def setup_ui(self):
        layout = QVBoxLayout(self)
        # TODO: แสดงรายการไฟล์เสียง, ปุ่มเล่น/ลบ/เปิดโฟลเดอร์
        pass
```

### คำแนะนำการเขียน:

1. **ใช้ QMediaPlayer** สำหรับเล่นไฟล์เสียงย้อนหลัง
2. **ใช้ QThread** สำหรับบันทึกเสียงแบบ background
3. **ใช้ QTimer** สำหรับอัพเดทสถานะ GUI
4. **จัดการ error และ logging** ทุกขั้นตอน

## ผลลัพธ์ที่คาดหวัง

### 1. GUI Application ที่สมบูรณ์:
- หน้าต่างแบ่งเป็น 3 ส่วน: schedule, recording, playback
- สามารถเพิ่ม/ลบ/แก้ไขตารางบันทึก
- แสดงสถานะการบันทึกแบบ real-time
- เล่นไฟล์เสียงย้อนหลังได้

### 2. การทำงานของระบบ:
```
️ ตารางบันทึก: 3 รายการ
 กำลังบันทึก: สถานี Thai PBS Radio (09:00-10:00)
 บันทึกสำเร็จ:  dab_recordings/audio/ThaiPBS_20241208_0900.wav
 เล่นไฟล์: ThaiPBS_20241208_0900.wav
```

### 3. ไฟล์ที่สร้างขึ้น:
- `audio/ThaiPBS_20241208_0900.wav`: ไฟล์เสียงที่บันทึก
- `metadata/ThaiPBS_20241208_0900.json`: ข้อมูลสถานีและเวลา
- `slides/ThaiPBS_20241208_0900.jpg`: สไลด์โชว์ (ถ้ามี)

## การแก้ไขปัญหา

### ปัญหา 1: พื้นที่เก็บข้อมูลไม่พอ

**วิธีแก้**:
- ตรวจสอบพื้นที่ว่างด้วย `df -h`
- ลบไฟล์เก่าอัตโนมัติเมื่อพื้นที่เหลือน้อย

### ปัญหา 2: การบันทึกหยุดกะทันหัน

**วิธีแก้**:
- ตรวจสอบ log ว่ามี error อะไร
- ใช้ QThread/Process แยกกับ GUI

### ปัญหา 3: การบันทึกหยุดทันทีหลังเริ่ม

**วิธีแก้**:
- ตรวจสอบว่า station/stream URL ถูกต้อง
- ตรวจสอบสิทธิ์การเขียนไฟล์

## คำถามทบทวน

1. **QMediaPlayer/QMediaRecorder ต่างกันอย่างไร?**
   - ตอบ: QMediaPlayer สำหรับเล่นไฟล์, QMediaRecorder สำหรับบันทึกไฟล์

2. **จะจัดการตารางเวลาบันทึกอัตโนมัติได้อย่างไร?**
   - ตอบ: ใช้ schedule/QTimer/QThread ตรวจสอบเวลาปัจจุบันกับตาราง

3. **ควรจัดเก็บ metadata อย่างไร?**
   - ตอบ: เก็บเป็นไฟล์ JSON แยกตามไฟล์เสียง

---

**หมายเหตุ**: Lab นี้เน้นการจัดการไฟล์และตารางเวลาในระบบจริง ต้องทดสอบกับสถานี DAB+ ที่รับได้จริง