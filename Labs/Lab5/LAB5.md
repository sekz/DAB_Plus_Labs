# LAB 5: สร้าง DAB+ Program Recorder (การบ้าน)

## วัตถุประสงค์
- สร้างระบบบันทึกรายการ DAB+ อย่างง่าย
- ใช้ Lab 3 pipeline สำหรับบันทึกเสียง
- จัดการตารางเวลาการบันทึกพื้นฐาน
- เล่นไฟล์ที่บันทึกด้วย QMediaPlayer

## ความรู้พื้นฐานที่ต้องมี
- Lab 3 (RTL-SDR + ETI pipeline)
- PyQt5 และ QMediaPlayer พื้นฐาน
- SQLite การจัดการตารางเวลา

## อุปกรณ์ที่ใช้
- **Raspberry Pi 4** พร้อม RTL-SDR V4 dongle
- **หน้าจอสัมผัส HDMI 7"** สำหรับควบคุม
- **เสาอากาศ DAB/FM** ที่มีประสิทธิภาพสูง
- **MicroSD Card** ขนาดใหญ่สำหรับเก็บบันทึก

## การเตรียมระบบ

### คำสั่งติดตั้ง:

```bash
sudo apt install -y sqlite3 python3-sqlite3 ffmpeg
pip3 install PyQt5 schedule
```

## ขั้นตอนการทำงาน

### 1. ทำความเข้าใจ Recording Pipeline

```
Lab 3 ETI Pipeline → Audio Extraction → File Storage
       ↓
Schedule Manager → Recording Trigger → QMediaPlayer
```

### 2. เรียกใช้งาน Lab GUI

```bash
cd Labs/Lab5
python3 lab5.py
```

## งานที่ต้องทำ (ประมาณ 3-4 ชั่วโมง)

### 1. ปรับแต่ง Database (30 นาที):

```python
def init_database(self):
    # TODO: สร้างตาราง recording_schedule (3 ฟิลด์หลัก: station_name, start_time, duration)
    # TODO: สร้างตาราง recording_history (บันทึกผลลัพธ์การบันทึก)
    pass
```

### 2. Recording Engine ใช้ Lab 3 (1.5 ชั่วโมง):

```python
def run(self):
    # TODO: ใช้ Lab 3 pipeline: RTL-SDR → ETI → extract audio
    # TODO: บันทึกไฟล์เสียงและส่ง signals
    pass

def record_with_lab3_mock(self):
    # TODO: จำลองการบันทึกและส่ง progress signal
    pass
```

### 3. Schedule Management (1 ชั่วโมง):

```python
def setup_ui(self):
    # TODO: สร้าง station combo, time edit, program name input
    # TODO: สร้างปุ่ม Add Schedule
    # TODO: สร้างตาราง schedule แสดงรายการ
    pass

def add_schedule(self):
    # TODO: รวบรวมข้อมูลจากฟอร์มและบันทึกลงฐานข้อมูล
    pass
```

### 4. Media Player (1 ชั่วโมง):

```python
def setup_ui(self):
    # TODO: สร้างตารางแสดงประวัติการบันทึก
    # TODO: สร้าง QMediaPlayer สำหรับเล่นไฟล์
    # TODO: สร้างปุ่มควบคุม play/pause/stop
    pass

# TODO: เชื่อมต่อ signals ของ media player
```

### 5. Main Interface (30 นาที):

```python
def setup_ui(self):
    # TODO: สร้าง 3 tabs: Manual Recording, Schedule, History
    pass
```

## เป้าหมายของการบ้าน
- เข้าใจการใช้ Lab 3 pipeline สำหรับบันทึก
- เรียนรู้ QMediaPlayer พื้นฐาน
- จัดการตารางเวลาอย่างง่าย
- บันทึกได้อย่างน้อย 1 รายการ

## ผลลัพธ์ที่คาดหวัง

### การทำงานพื้นฐาน:
```
DAB+ Recorder เริ่มต้น...
เพิ่มตารางเวลา: Thai PBS @ 09:00 (30 นาที)
เริ่มบันทึก...
บันทึกเสร็จสิ้น: Thai_PBS_20241208_090000.wav
```

### ไฟล์ที่สร้าง:
- `dab_recordings.db`: ฐานข้อมูลตารางเวลา
- `recordings/*.wav`: ไฟล์เสียงที่บันทึก
- Screenshot ของ GUI ที่ทำงานได้

## หัวข้อขยาย (ถ้าเหลือเวลา)

1. **เพิ่มการบันทึกหลายสถานี**
2. **ตั้งเวลาบันทึกล่วงหน้า**
3. **Export เป็น MP3**
4. **Progress indicator แสดงเวลาที่เหลือ**

## Tips การทำงาน

1. **เริ่มจาก Database** สร้างตารางก่อน
2. **ทดสอบ Lab 3** ให้ทำงานได้ก่อน
3. **GUI พื้นฐาน** ไม่ต้องสวย แค่ใช้งานได้
4. **Mock Data** ถ้า RTL-SDR ไม่มี

## การส่งงาน

1. **ไฟล์ที่ต้องส่ง:**
   - `lab5.py` (โค้ดที่แก้แล้ว)
   - `dab_recordings.db` (ฐานข้อมูล)
   - Screenshot ของ GUI

2. **เกณฑ์การให้คะแนน:**
   - บันทึกได้อย่างน้อย 1 ไฟล์ (30%)
   - จัดการตารางเวลาได้ (30%)
   - เล่นไฟล์ด้วย QMediaPlayer (40%)

---
**หมายเหตุ**: การบ้านนี้ใช้เวลาประมาณ 3-4 ชั่วโมง