# LAB 4: สร้าง DAB+ Station Scanner (การบ้าน)

## วัตถุประสงค์
- สร้างแอปพลิเคชันสแกนสถานี DAB+ อย่างง่าย
- ใช้ Lab 3 pipeline สำหรับหาสถานี
- เก็บข้อมูลสถานีในฐานข้อมูล SQLite
- สร้าง GUI พื้นฐานสำหรับแสดงผล

## ความรู้พื้นฐานที่ต้องมี
- Lab 3 (RTL-SDR + ETI pipeline)
- PyQt5 พื้นฐาน
- SQLite พื้นฐาน

## อุปกรณ์ที่ใช้
- **Raspberry Pi 4** พร้อม RTL-SDR V4 dongle
- **หน้าจอสัมผัส HDMI 7"** สำหรับควบคุม
- **เสาอากาศ DAB/FM** ที่มีประสิทธิภาพสูง
- **การเชื่อมต่อเน็ต** สำหรับข้อมูลสถานี

## การเตรียมระบบ

### คำสั่งติดตั้ง:

```bash
sudo apt install -y sqlite3 python3-sqlite3
pip3 install PyQt5 matplotlib
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

## งานที่ต้องทำ (ประมาณ 3-4 ชั่วโมง)

### 1. ปรับแต่ง Database (30 นาที):

```python
def init_database(self):
    # TODO: สร้างตาราง stations พื้นฐาน
    # แค่ id, frequency, station_name, last_seen
    pass

def add_station(self, station_data):
    # TODO: เพิ่มสถานีลงฐานข้อมูล
    pass
```

### 2. Scanner ใช้ Lab 3 (1.5 ชั่วโมง):

```python
def scan_frequency(self, frequency):
    # TODO: ใช้ Lab 3 RTL-SDR + ETI parser
    # TODO: หาสถานี DAB+ ในความถี่นี้
    # TODO: return รายการสถานีที่พบ
    pass

def run(self):
    # TODO: สแกนความถี่ 185.360 MHz และ 202.928 MHz
    # TODO: ส่ง progress signals
    pass
```

### 3. แสดงรายการสถานี (1 ชั่วโมง):

```python
def setup_ui(self):
    # TODO: สร้าง QTableWidget แสดงสถานี
    # คอลัมน์: ชื่อ, ความถี่, เวลาที่พบ
    # TODO: ปุ่ม Refresh และ Clear
    pass

def refresh_stations(self):
    # TODO: โหลดข้อมูลจากฐานข้อมูล
    # TODO: แสดงในตาราง
    pass
```

### 4. Main Window (1 ชั่วโมง):

```python
def setup_ui(self):
    # TODO: สร้าง Tab Widget
    # Tab 1: Scanner (ปุ่ม Start/Stop + Progress)
    # Tab 2: Station List
    pass

def start_scan(self):
    # TODO: เริ่มการสแกน
    pass
```

### 5. เชื่อมต่อ Signals (30 นาที):

```python
def setup_connections(self):
    # TODO: เชื่อมต่อ scanner signals กับ UI
    # TODO: station_found → update database
    # TODO: scan_completed → refresh list
    pass
```

## เป้าหมายของการบ้าน
- เข้าใจการใช้ Lab 3 pipeline
- เรียนรู้ SQLite พื้นฐาน
- สร้าง GUI ด้วย QThread
- สแกนได้อย่างน้อย 2 ความถี่

## ผลลัพธ์ที่คาดหวัง

### การทำงานพื้นฐาน:
```
DAB+ Scanner เริ่มต้น...
สแกน 185.360 MHz: พบ 3 สถานี
สแกน 202.928 MHz: พบ 2 สถานี
บันทึกลงฐานข้อมูลแล้ว
```

### ไฟล์ที่สร้าง:
- `dab_stations.db`: ฐานข้อมูลสถานี
- Screenshot ของ GUI ที่ทำงานได้

## หัวข้อขยาย (ถ้าเหลือเวลา)

1. **เพิ่มความถี่ให้ครบ** สำหรับ Thailand DAB+
2. **Export เป็น CSV**
3. **Progress bar แสดงการสแกน**
4. **Signal strength indicator**

## Tips การทำงาน

1. **เริ่มจาก Database** สร้างตารางก่อน
2. **ทดสอบ Lab 3** ให้ทำงานได้ก่อน
3. **GUI พื้นฐาน** ไม่ต้องสวย แค่ใช้งานได้
4. **Mock Data** ถ้า RTL-SDR ไม่มี

## การส่งงาน

1. **ไฟล์ที่ต้องส่ง:**
   - `lab4.py` (โค้ดที่แก้แล้ว)
   - `dab_stations.db` (ฐานข้อมูล)
   - Screenshot ของ GUI

2. **เกณฑ์การให้คะแนน:**
   - สแกนได้อย่างน้อย 1 ความถี่ (30%)
   - บันทึกลงฐานข้อมูลได้ (30%)
   - GUI แสดงผลได้ (40%)

---
**หมายเหตุ**: การบ้านนี้ใช้เวลาประมาณ 3-4 ชั่วโมง