# LAB 5: สร้าง DAB+ Program Recorder

## วัตถุประสงค์
- พัฒนาระบบบันทึกรายการ DAB+ ตามตารางเวลา
- สร้างระบบจัดการการบันทึกแบบแมนนวลและอัตโนมัติ  
- จัดเก็บไฟล์เสียง สไลด์โชว์ และเมทาดาต้าอย่างเป็นระบบ
- พัฒนา GUI สำหรับจัดการตารางการบันทึก

## ความรู้พื้นฐานที่ต้องมี
- ความเข้าใจจาก Lab 1-4 (RTL-SDR, welle.io, GUI, Database)
- การทำงานของ QTimer และ scheduling
- การจัดการไฟล์และ directory structure
- ความเข้าใจ audio file formats

## อุปกรณ์ที่ใช้
- **Raspberry Pi 4** พร้อม RTL-SDR V4 dongle
- **หน้าจอสัมผัส HDMI 7"** สำหรับจัดการ
- **MicroSD Card ขนาดใหญ่** สำหรับเก็บบันทึก
- **USB Storage** (เสริม) สำหรับ backup
- **เสาอากาศ DAB/FM** คุณภาพสูง

## การเตรียมระบบ

### คำสั่งติดตั้ง Dependencies:

```bash
# ติดตั้ง audio processing tools
sudo apt install -y ffmpeg sox libsox-fmt-all
pip3 install pydub mutagen

# ติดตั้ง datetime และ scheduling
pip3 install schedule python-crontab

# ติดตั้ง file management tools  
sudo apt install -y tree rsync
pip3 install watchdog send2trash
```

### ตั้งค่า Storage Directories:

```bash
# สร้าง directory structure สำหรับบันทึก
mkdir -p ~/DAB_Recordings/{audio,slideshow,metadata,logs}
mkdir -p ~/DAB_Recordings/schedules

# ตั้งค่า permissions
chmod 755 ~/DAB_Recordings
chmod 755 ~/DAB_Recordings/*
```

## ขั้นตอนการทำงาน

### 1. ทำความเข้าใจ Recording Workflow

```
 Schedule Management
    ↓
 Target Selection (Station + Time)
    ↓  
 Recording Process (Audio + Metadata + Slideshow)
    ↓
 File Organization & Storage
    ↓
 Playback & Export
```

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
from datetime import datetime, timedelta
import json

class RecordingScheduler(QThread):
    recording_started = pyqtSignal(dict)
    recording_stopped = pyqtSignal(dict)
    schedule_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.schedules = []
        self.active_recordings = {}
        self.schedule_file = "schedules/recording_schedule.json"
        
    def add_schedule(self, station, start_time, duration, repeat=None):
        """เพิ่มตารางการบันทึกใหม่"""
        schedule_item = {
            'id': len(self.schedules) + 1,
            'station': station,
            'start_time': start_time.isoformat(),
            'duration': duration,  # minutes
            'repeat': repeat,  # 'daily', 'weekly', 'once'
            'enabled': True,
            'created': datetime.now().isoformat()
        }
        
        # TODO: เติมโค้ดเพิ่ม schedule
        # 1. เพิ่มใน self.schedules list
        # 2. บันทึกลงไฟล์
        # 3. ตั้ง timer สำหรับการบันทึก
        pass
        
    def check_pending_recordings(self):
        """ตรวจสอบการบันทึกที่รอ"""
        current_time = datetime.now()
        
        for schedule_item in self.schedules:
            if not schedule_item['enabled']:
                continue
                
            start_time = datetime.fromisoformat(schedule_item['start_time'])
            
            # TODO: เติมโค้ดตรวจสอบเวลา
            # 1. เปรียบเทียบเวลาปัจจุบันกับเวลาที่กำหนด
            # 2. เริ่มการบันทึกหากถึงเวลา
            # 3. จัดการ repeat schedule
            pass
```

#### 2. DABRecorder - การบันทึกสัญญาณ:

```python
class DABRecorder(QThread):
    recording_progress = pyqtSignal(int, str)
    metadata_received = pyqtSignal(dict)
    slideshow_received = pyqtSignal(str)
    recording_complete = pyqtSignal(str)  # output file path
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.output_dir = "~/DAB_Recordings"
        self.current_station = None
        
    def start_recording(self, station_info, duration_minutes):
        """เริ่มการบันทึก"""
        self.station_info = station_info
        self.duration = duration_minutes
        
        # สร้างชื่อไฟล์
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        station_name = station_info['name'].replace(' ', '_')
        self.output_file = f"{station_name}_{timestamp}"
        
        # TODO: เติมโค้ดการบันทึก
        # 1. เริ่ม welle-io process
        # 2. ตั้ง timer สำหรับหยุดบันทึก
        # 3. เริ่ม monitoring metadata และ slideshow
        pass
        
    def record_audio_stream(self):
        """บันทึกเสียงจาก welle.io"""
        try:
            # เรียก welle-io แบบ headless และบันทึกเสียง
            cmd = [
                'welle-io', '-c', 'headless_mode',
                '-f', str(int(self.station_info['frequency'] * 1000000)),
                '--audio-output', f"{self.output_dir}/audio/{self.output_file}.wav"
            ]
            
            self.welle_process = subprocess.Popen(cmd)
            
            # TODO: เติมโค้ด monitoring การบันทึก
            # 1. ตรวจสอบสถานะ process
            # 2. อัพเดท progress
            # 3. จัดการ errors
            
        except Exception as e:
            logger.error(f"Recording error: {str(e)}")
            
    def stop_recording(self):
        """หยุดการบันทึก"""
        self.is_recording = False
        
        # TODO: เติมโค้ดหยุดบันทึก
        # 1. หยุด welle-io process
        # 2. บันทึก metadata สุดท้าย
        # 3. ปิดไฟล์ทั้งหมด
        pass
```

#### 3. RecordingManager - การจัดการไฟล์:

```python
import shutil
from pathlib import Path

class RecordingManager:
    def __init__(self, base_dir="~/DAB_Recordings"):
        self.base_dir = Path(base_dir).expanduser()
        self.audio_dir = self.base_dir / "audio"
        self.slideshow_dir = self.base_dir / "slideshow"
        self.metadata_dir = self.base_dir / "metadata"
        self.create_directories()
        
    def create_directories(self):
        """สร้าง directory structure"""
        for directory in [self.audio_dir, self.slideshow_dir, self.metadata_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
    def organize_recording(self, recording_id, station_name, date):
        """จัดเรียงไฟล์บันทึก"""
        # สร้าง subdirectory ตามวันที่
        date_dir = self.base_dir / date.strftime("%Y-%m-%d")
        date_dir.mkdir(exist_ok=True)
        
        station_dir = date_dir / station_name.replace(' ', '_')
        station_dir.mkdir(exist_ok=True)
        
        # TODO: เติมโค้ดย้ายไฟล์
        # 1. ย้ายไฟล์เสียงไปยัง station_dir
        # 2. ย้าย slideshow images
        # 3. ย้าย metadata files
        # 4. สร้าง index file
        pass
        
    def get_recording_info(self, recording_path):
        """ดึงข้อมูลการบันทึก"""
        info = {
            'file_size': 0,
            'duration': 0,
            'bitrate': 0,
            'sample_rate': 0,
            'metadata_count': 0,
            'slideshow_count': 0
        }
        
        # TODO: เติมโค้ดวิเคราะห์ไฟล์
        # 1. ใช้ mutagen อ่านข้อมูล audio
        # 2. นับจำนวน slideshow images
        # 3. นับ metadata entries
        pass
        
        return info
```

#### 4. ScheduleWidget - GUI จัดการตารางเวลา:

```python
class ScheduleWidget(QWidget):
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Schedule table
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(6)
        self.schedule_table.setHorizontalHeaderLabels([
            "สถานี", "เวลาเริ่ม", "ระยะเวลา", "ทำซ้ำ", "สถานะ", "การจัดการ"
        ])
        
        # ปรับขนาดตาราง
        self.schedule_table.setMinimumHeight(250)
        header = self.schedule_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        layout.addWidget(self.schedule_table)
        
        # Add new schedule
        add_group = QGroupBox("เพิ่มตารางการบันทึกใหม่")
        add_layout = QGridLayout(add_group)
        
        # Station selection
        add_layout.addWidget(QLabel("สถานี:"), 0, 0)
        self.station_combo = QComboBox()
        self.station_combo.setMinimumHeight(40)
        add_layout.addWidget(self.station_combo, 0, 1)
        
        # Time selection
        add_layout.addWidget(QLabel("วันที่:"), 1, 0)
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setMinimumHeight(40)
        add_layout.addWidget(self.date_edit, 1, 1)
        
        add_layout.addWidget(QLabel("เวลา:"), 1, 2)
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setMinimumHeight(40)
        add_layout.addWidget(self.time_edit, 1, 3)
        
        # Duration
        add_layout.addWidget(QLabel("ระยะเวลา (นาที):"), 2, 0)
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 480)  # 1 minute to 8 hours
        self.duration_spin.setValue(60)
        self.duration_spin.setMinimumHeight(40)
        add_layout.addWidget(self.duration_spin, 2, 1)
        
        # Repeat options
        add_layout.addWidget(QLabel("ทำซ้ำ:"), 2, 2)
        self.repeat_combo = QComboBox()
        self.repeat_combo.addItems(["ครั้งเดียว", "ทุกวัน", "ทุกสัปดาห์"])
        self.repeat_combo.setMinimumHeight(40)
        add_layout.addWidget(self.repeat_combo, 2, 3)
        
        # Add button
        self.add_schedule_btn = QPushButton(" เพิ่มตารางการบันทึก")
        self.add_schedule_btn.setMinimumSize(200, 50)
        self.add_schedule_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:pressed {
                background: #219a52;
            }
        """)
        add_layout.addWidget(self.add_schedule_btn, 3, 0, 1, 4)
        
        layout.addWidget(add_group)
```

#### 5. RecordingListWidget - รายการบันทึก:

```python
class RecordingListWidget(QWidget):
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        self.date_filter = QDateEdit()
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.setMinimumHeight(40)
        
        self.station_filter = QComboBox()
        self.station_filter.addItem("ทุกสถานี")
        self.station_filter.setMinimumHeight(40)
        
        self.refresh_btn = QPushButton(" รีเฟรช")
        self.refresh_btn.setMinimumSize(100, 40)
        
        filter_layout.addWidget(QLabel("วันที่:"))
        filter_layout.addWidget(self.date_filter)
        filter_layout.addWidget(QLabel("สถานี:"))
        filter_layout.addWidget(self.station_filter)
        filter_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(filter_layout)
        
        # Recording list
        self.recording_list = QListWidget()
        self.recording_list.setMinimumHeight(300)
        
        layout.addWidget(self.recording_list)
        
        # Playback controls
        playback_layout = QHBoxLayout()
        
        self.play_btn = QPushButton(" เล่น")
        self.stop_btn = QPushButton(" หยุด")
        self.export_btn = QPushButton(" ส่งออก")
        self.delete_btn = QPushButton(" ลบ")
        
        for btn in [self.play_btn, self.stop_btn, self.export_btn, self.delete_btn]:
            btn.setMinimumSize(100, 50)
            
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
            }
        """)
        
        playback_layout.addWidget(self.play_btn)
        playback_layout.addWidget(self.stop_btn)  
        playback_layout.addWidget(self.export_btn)
        playback_layout.addWidget(self.delete_btn)
        
        layout.addLayout(playback_layout)
```

### คำแนะนำการเขียน:

1. **ใช้ QTimer** สำหรับ scheduling และ monitoring
2. **จัดการไฟล์อย่างเป็นระบบ** ด้วย directory structure ที่ชัดเจน
3. **ใช้ metadata** เก็บข้อมูลการบันทึกทุกไฟล์
4. **เพิ่ม error handling** สำหรับกรณีพื้นที่เก็บข้อมูลไม่พอ

## ผลลัพธ์ที่คาดหวัง

### 1. GUI Application ที่สมบูรณ์:
- หน้าต่างแบ่งเป็น 3 ส่วน: schedule, recording, playback
- การตั้งตารางเวลาการบันทึกแบบ drag & drop
- การติดตามสถานะการบันทึกแบบ real-time
- การจัดการและเล่นไฟล์บันทึก

### 2. การทำงานของระบบ:
```
 ตารางการบันทึกวันนี้:
   09:00-10:00: Thai PBS Morning News
   12:00-13:00: NBT Lunch Hour
   18:00-19:00: Voice TV Evening Report

 09:00 - เริ่มบันทึก Thai PBS Morning News
 สถานะ: กำลังบันทึก... (15:32 / 60:00)
 เพลงปัจจุบัน: เพลงไทย - ศิลปินไทย
️ รับ slideshow: ข่าวเช้า (3/12 images)

 10:00 - บันทึกเสร็จสิ้น
 ไฟล์: Thai_PBS_20241208_090000.wav (142 MB)
 คุณภาพ: 192 kbps, 48 kHz, Stereo
️ Slideshow: 12 images บันทึกแล้ว
 Metadata: 45 entries บันทึกแล้ว
```

### 3. ไฟล์ที่สร้างขึ้น:
```
DAB_Recordings/
├── 2024-12-08/
│   ├── Thai_PBS/
│   │   ├── Thai_PBS_20241208_090000.wav
│   │   ├── slideshow_20241208_090000/
│   │   └── metadata_20241208_090000.json
│   └── NBT/
│       └── NBT_20241208_120000.wav
├── schedules/
│   └── recording_schedule.json
└── logs/
    └── recording_log_20241208.txt
```

## การแก้ไขปัญหา

### ปัญหา 1: พื้นที่เก็บข้อมูลไม่พอ
**วิธีแก้**:
```bash
# ตรวจสอบพื้นที่
df -h ~/DAB_Recordings

# ตั้งค่า auto cleanup เก่าไฟล์เก่า
find ~/DAB_Recordings -name "*.wav" -mtime +7 -delete

# ใช้ compression สำหรับไฟล์เก่า
find ~/DAB_Recordings -name "*.wav" -mtime +1 -exec gzip {} \;
```

### ปัญหา 2: การบันทึกหยุดกะทันหัน
**วิธีแก้**:
```python
# เพิ่ม watchdog สำหรับ monitor processes
def monitor_recording_process(self):
    if self.welle_process and self.welle_process.poll() is None:
        return True
    else:
        self.restart_recording()
        return False
```

## คำถามทบทวน

1. **ทำไมต้องจัดเรียงไฟล์บันทึกตามวันที่และสถานี?**
   - ตอบ: เพื่อง่ายต่อการค้นหาและการจัดการไฟล์ในอนาคต

2. **การใช้ QTimer vs schedule library ต่างกันอย่างไร?**  
   - ตอบ: QTimer เหมาะกับ GUI events, schedule library เหมาะกับ background tasks

3. **ทำไมต้องเก็บ metadata แยกจากไฟล์เสียง?**
   - ตอบ: เพื่อให้สามารถค้นหาและวิเคราะห์ได้โดยไม่ต้องเปิดไฟล์เสียง

---

**หมายเหตุ**: Lab นี้ต้องการพื้นที่เก็บข้อมูลมาก ควรใช้ MicroSD card ขนาดใหญ่หรือ external storage