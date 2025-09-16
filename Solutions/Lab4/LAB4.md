# LAB 4: สร้าง DAB+ Station Scanner

## วัตถุประสงค์
- พัฒนาแอปพลิเคชันสแกนและติดตามสถานี DAB+ อัตโนมัติ
- สร้างระบบติดตามคุณภาพสัญญาณแบบ real-time
- บันทึกประวัติการสแกนและสร้างฐานข้อมูลสถานี
- พัฒนา GUI แบบ touch-friendly สำหรับหน้าจอ 7"

## ความรู้พื้นฐานที่ต้องมี
- ความเข้าใจจาก Lab 1-3 (RTL-SDR, welle.io, pyrtlsdr)
- PyQt5 advanced GUI programming
- การทำงานของ SQLite database
- ความรู้เกี่ยวกับ DAB+ ensemble และ services

## อุปกรณ์ที่ใช้
- **Raspberry Pi 4** พร้อม RTL-SDR V4 dongle
- **หน้าจอสัมผัส HDMI 7"** สำหรับควบคุม
- **เสาอากาศ DAB/FM** ที่มีประสิทธิภาพสูง
- **การเชื่อมต่อเน็ต** สำหรับติดตั้ง dependencies

## การเตรียมระบบ

### คำสั่งติดตั้ง Dependencies:

```bash
# ติดตั้ง database และ data processing tools
sudo apt install -y sqlite3 python3-sqlite3
pip3 install pandas matplotlib seaborn

# ติดตั้ง GUI enhancements
pip3 install PyQt5 qtawesome

# ติดตั้ง async programming support
pip3 install asyncio aiohttp
```

## ขั้นตอนการทำงาน

### 1. ทำความเข้าใจ DAB+ Ensemble Structure

```
DAB+ Ensemble (Multiplex)
├── Service 1 (เช่น Thai PBS Radio)
│   ├── Primary Component (Audio)
│   └── Secondary Component (Data)
├── Service 2 (เช่น NBT Radio)
└── Service 3 (เช่น Voice TV Radio)
```

### 2. เรียกใช้งาน Lab GUI

```bash
cd Labs/Lab4
python3 lab4.py
```

## การเขียนโค้ด

### ส่วนที่ต้องเติมใน `lab4.py`:

#### 1. DatabaseManager - การจัดการฐานข้อมูล:

```python
import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="dab_stations.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """สร้างตารางฐานข้อมูล"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # ตาราง ensembles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ensembles (
                    id INTEGER PRIMARY KEY,
                    frequency REAL NOT NULL,
                    ensemble_id INTEGER,
                    ensemble_label TEXT,
                    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # ตาราง services
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY,
                    ensemble_id INTEGER,
                    service_id INTEGER,
                    service_label TEXT,
                    service_type TEXT,
                    bitrate INTEGER,
                    signal_quality REAL,
                    FOREIGN KEY (ensemble_id) REFERENCES ensembles (id)
                )
            """)
    
    def add_ensemble(self, frequency, ensemble_id, label):
        """เพิ่ม ensemble ใหม่"""
        # TODO: เติมโค้ดเพิ่ม ensemble ลงฐานข้อมูล
        pass
    
    def add_service(self, ensemble_id, service_id, label, service_type, bitrate, quality):
        """เพิ่ม service ใหม่"""
        # TODO: เติมโค้ดเพิ่ม service ลงฐานข้อมูล
        pass
```

#### 2. DABScanner - การสแกนสถานีอัตโนมัติ:

```python
class DABScanner(QThread):
    ensemble_found = pyqtSignal(dict)
    service_found = pyqtSignal(dict)
    scan_progress = pyqtSignal(int, str)
    scan_completed = pyqtSignal(int, int)  # ensembles, services
    
    def __init__(self):
        super().__init__()
        self.frequencies = [
            174.928, 176.640, 178.352, 180.064, 181.936,
            183.648, 185.360, 187.072, 188.928, 190.640
        ]
        self.is_scanning = False
        
    def scan_all_frequencies(self):
        """สแกนทุกความถี่ DAB+"""
        total_freqs = len(self.frequencies)
        ensemble_count = 0
        service_count = 0
        
        for i, frequency in enumerate(self.frequencies):
            if not self.is_scanning:
                break
                
            self.scan_progress.emit(
                int((i / total_freqs) * 100),
                f"กำลังสแกน {frequency} MHz..."
            )
            
            # TODO: เติมโค้ดสแกนความถี่
            # 1. รัน welle-io หรือใช้ pyrtlsdr
            # 2. ตรวจหา ensemble
            # 3. แปลง service information
            # 4. ส่ง signals
            
        self.scan_completed.emit(ensemble_count, service_count)
```

#### 3. StationListWidget - แสดงรายการสถานี:

```python
class StationListWidget(QWidget):
    station_selected = pyqtSignal(dict)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Search box
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(" ค้นหาสถานี...")
        self.search_input.setMinimumHeight(40)
        self.search_btn = QPushButton("ค้นหา")
        self.search_btn.setMinimumSize(80, 40)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)
        
        # Station tree
        self.station_tree = QTreeWidget()
        self.station_tree.setHeaderLabels([
            "สถานี", "ความถี่", "คุณภาพ", "Bitrate", "ประเภท"
        ])
        
        # ปรับขนาดสำหรับหน้าจอสัมผัส
        self.station_tree.setMinimumHeight(300)
        header = self.station_tree.header()
        header.setDefaultSectionSize(120)
        
        layout.addWidget(self.station_tree)
        
        # Filter buttons
        filter_layout = QHBoxLayout()
        self.all_btn = QPushButton("ทั้งหมด")
        self.audio_btn = QPushButton(" เสียง")
        self.data_btn = QPushButton(" ข้อมูล")
        
        for btn in [self.all_btn, self.audio_btn, self.data_btn]:
            btn.setMinimumSize(100, 40)
            filter_layout.addWidget(btn)
            
        layout.addLayout(filter_layout)
```

#### 4. SignalQualityMonitor - ติดตามคุณภาพสัญญาณ:

```python
class SignalQualityMonitor(QWidget):
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Signal meters
        self.rssi_meter = QProgressBar()
        self.rssi_meter.setOrientation(Qt.Horizontal)
        self.rssi_meter.setRange(-100, -20)
        self.rssi_meter.setValue(-60)
        self.rssi_meter.setFormat("RSSI: %v dBm")
        
        self.snr_meter = QProgressBar()
        self.snr_meter.setRange(0, 30)
        self.snr_meter.setValue(15)
        self.snr_meter.setFormat("SNR: %v dB")
        
        self.ber_meter = QProgressBar()
        self.ber_meter.setRange(0, 100)
        self.ber_meter.setValue(5)
        self.ber_meter.setFormat("BER: %v%")
        
        # Labels
        layout.addWidget(QLabel(" ความแรงสัญญาณ (RSSI):"))
        layout.addWidget(self.rssi_meter)
        layout.addWidget(QLabel(" อัตราส่วนสัญญาณต่อสัญญาณรบกวน (SNR):"))
        layout.addWidget(self.snr_meter)
        layout.addWidget(QLabel(" อัตราข้อผิดพลาด (BER):"))
        layout.addWidget(self.ber_meter)
        
    def update_quality(self, rssi, snr, ber):
        """อัพเดทค่าคุณภาพสัญญาณ"""
        # TODO: เติมโค้ดอัพเดทค่าต่างๆ
        pass
```

#### 5. ScanHistoryWidget - ประวัติการสแกน:

```python
class ScanHistoryWidget(QWidget):
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "วันที่", "จำนวน Ensemble", "จำนวน Service", 
            "คุณภาพเฉลี่ย", "หมายเหตุ"
        ])
        
        # ปรับขนาดตาราง
        self.history_table.setMinimumHeight(200)
        header = self.history_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        layout.addWidget(self.history_table)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.export_btn = QPushButton(" ส่งออก CSV")
        self.clear_btn = QPushButton(" ล้างประวัติ")
        self.refresh_btn = QPushButton(" รีเฟรช")
        
        for btn in [self.export_btn, self.clear_btn, self.refresh_btn]:
            btn.setMinimumSize(120, 40)
            button_layout.addWidget(btn)
            
        layout.addLayout(button_layout)
    
    def load_history(self):
        """โหลดประวัติการสแกน"""
        # TODO: เติมโค้ดโหลดข้อมูลจากฐานข้อมูล
        pass
```

### คำแนะนำการเขียน:

1. **ใช้ SQLite** สำหรับเก็บข้อมูลสถานี
2. **ใช้ QThread** สำหรับการสแกนแบบไม่บล็อก GUI
3. **ใช้ QTimer** สำหรับ real-time monitoring
4. **ออกแบบ UI ให้เหมาะกับการสัมผัส**

## ผลลัพธ์ที่คาดหวัง

### 1. GUI Application ที่สมบูรณ์:
- หน้าต่างแบ่งเป็น 4 ส่วน: scanner, stations, quality, history
- การสแกนสถานีแบบ progress indicator
- รายการสถานีที่สามารถ filter ได้
- การติดตามคุณภาพสัญญาณแบบ real-time

### 2. การทำงานของระบบ:
```
 เริ่มต้น DAB+ Scanner...
 เชื่อมต่อ RTL-SDR สำเร็จ
 เชื่อมต่อฐานข้อมูล สำเร็จ

 กำลังสแกน DAB+ Band III...
 174.928 MHz: พบ Thai PBS Ensemble (3 services)
 176.640 MHz: พบ Voice TV Ensemble (2 services)  
 178.352 MHz: ไม่พบสัญญาณ
 181.936 MHz: พบ Private Network (4 services)

 สแกนเสร็จสิ้น: 3 ensembles, 9 services
 บันทึกลงฐานข้อมูลแล้ว

 สถิติคุณภาพเฉลี่ย:
   RSSI: -52 dBm
   SNR: 18.3 dB  
   BER: 2.1%
```

### 3. ไฟล์ที่สร้างขึ้น:
- `dab_stations.db`: ฐานข้อมูล SQLite
- `scan_export_*.csv`: ไฟล์ส่งออกข้อมูลสถานี
- `quality_log_*.json`: บันทึกคุณภาพสัญญาณ

## การแก้ไขปัญหา

### ปัญหา 1: สแกนช้า
**วิธีแก้**:
```python
# ปรับ timeout สำหรับแต่ละความถี่
scan_timeout = 5  # วินาที (แทน 10 วินาที)

# ใช้ threading pool
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(scan_frequency, freq) for freq in frequencies]
```

### ปัญหา 2: Database locked
**วิธีแก้**:
```python
# ใช้ context manager
with sqlite3.connect(self.db_path, timeout=30.0) as conn:
    cursor = conn.cursor()
    # database operations

# หรือใช้ WAL mode
conn.execute("PRAGMA journal_mode=WAL")
```

## คำถามทบทวน

1. **DAB+ Ensemble และ Service ต่างกันอย่างไร?**
   - ตอบ: Ensemble คือ multiplex ที่มี Service หลายตัว, Service คือสถานีแต่ละสถานี

2. **ทำไมต้องใช้ Database สำหรับเก็บข้อมูลสถานี?**
   - ตอบ: เพื่อเก็บประวัติและสามารถค้นหา filter ได้อย่างมีประสิทธิภาพ

3. **Signal Quality Parameters มีความหมายอย่างไร?**
   - ตอบ: RSSI = ความแรงสัญญาณ, SNR = สัดส่วนสัญญาณต่อสัญญาณรบกวน, BER = อัตราข้อผิดพลาด

---

**หมายเหตุ**: Lab นี้ต้องการการสื่อสารกับอุปกรณ์และสถานี DAB+ ในพื้นที่เพื่อให้ผลลัพธ์ที่ดี