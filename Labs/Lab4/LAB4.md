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
- **การเชื่อมต่อเน็ต** สำหรับข้อมูลสถานี

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

#### 2. DABScanner - การสแกนอัตโนมัติ:

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

#### 4. SignalQualityMonitor - ติดตามคุณภาพ:

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
        # TODO: เติมโค้ดโหลดจากฐานข้อมูล
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
- การสแกนอัตโนมัติพร้อม progress indicator
- รายการสถานีที่สามารถกรอง filter ได้
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
- `scan_export_*.csv`: ไฟล์ส่งออกข้อมูล
- `quality_log_*.json`: บันทึกคุณภาพสัญญาณ

## 🎯 Trap Exercises

### Trap 4.1: Database Design และ Optimization Challenge
**เป้าหมาย**: ออกแบบและปรับแต่งฐานข้อมูลสำหรับเก็บข้อมูลสถานี DAB+

**โจทย์**:
1. ออกแบบ database schema ที่มีประสิทธิภาพสำหรับเก็บ ensemble, service, และ scan history
2. สร้าง indexes ที่เหมาะสมเพื่อเพิ่มความเร็วในการ query
3. Implement database migration system สำหรับการอัพเดท schema
4. สร้าง backup และ restore functionality

**Hints**:
- ใช้ foreign key เพื่อเชื่อมโยง ensembles กับ services
- Index frequency, timestamp สำหรับ scan history
- ใช้ PRAGMA commands เพื่อปรับแต่ง SQLite
- WAL mode เพื่อการเขียนที่เร็วขึ้น

### Trap 4.2: Advanced Scanning Algorithm
**เป้าหมาย**: พัฒนาอัลกอริทึมการสแกนที่ชาญฉลาดและมีประสิทธิภาพ

**โจทย์**:
1. สร้าง adaptive scanning ที่ปรับ scan time ตามความแรงสัญญาณ
2. Implement priority-based scanning (สแกนความถี่ที่เคยพบสถานีก่อน)
3. สร้าง background monitoring สำหรับสถานีที่รู้จักแล้ว
4. ใช้ machine learning เพื่อทำนายความน่าจะเป็นที่จะพบสถานี

**Hints**:
- Strong signal = สแกนเร็ว, Weak signal = สแกนช้า
- เก็บ success rate ของแต่ละความถี่
- ใช้ threading สำหรับ background monitoring
- Simple ML: ใช้ historical data ทำนาย probability

### Trap 4.3: Signal Quality Analysis และ Visualization
**เป้าหมาย**: วิเคราะห์และแสดงผลคุณภาพสัญญาณแบบละเอียด

**โจทย์**:
1. สร้าง real-time signal quality dashboard
2. Implement signal quality trending และ alerting system
3. สร้าง coverage map visualization
4. วิเคราะห์ correlation ระหว่าง เวลา/สภาพอากาศ กับคุณภาพสัญญาณ

**Hints**:
- ใช้ matplotlib หรือ pyqtgraph สำหรับ real-time plotting
- Moving average สำหรับ signal trending
- GPS coordinates สำหรับ coverage mapping
- เก็บ timestamp และ weather data สำหรับ correlation

### Trap 4.4: Touch-Optimized GUI Design
**เป้าหมาย**: สร้าง GUI ที่เหมาะสมสำหรับหน้าจอสัมผัส 7"

**โจทย์**:
1. ออกแบบ responsive layout ที่ใช้งานง่ายด้วยนิ้ว
2. สร้าง gesture support (swipe, pinch-to-zoom)
3. Implement custom widgets สำหรับการแสดงผลข้อมูลสถานี
4. เพิ่ม accessibility features (ขนาดตัวอักษร, contrast)

**Hints**:
- Touch targets ต้องมีขนาดอย่างน้อย 44x44 pixels
- ใช้ QScroller สำหรับ smooth scrolling
- Custom QWidget สำหรับ station display cards
- QSettings เพื่อเก็บ user preferences

## การแก้ไขปัญหา

### ปัญหา 1: สแกนช้า
**วิธีแก้**:
```python
# ปรับ timeout สำหรับแต่ละความถี่
scan_timeout = 5  # วินาที แทน 10 วินาที

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
   - ตอบ: RSSI = ความแรงสัญญาณ, SNR = สัญญาณต่อสัญญาณรบกวน, BER = อัตราข้อผิดพลาด

---

**หมายเหตุ**: Lab นี้ต้องการเสาอากาศที่ดีและสถานี DAB+ ในพื้นที่เพื่อให้การสแกนได้ผลลัพธ์ที่ดี