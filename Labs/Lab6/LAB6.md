# LAB 6: สร้าง DAB+ Signal Analyzer (การบ้าน)

## วัตถุประสงค์
- สร้างเครื่องมือวิเคราะห์สัญญาณ DAB+ อย่างง่าย
- ใช้ Lab 3 pipeline สำหรับวิเคราะห์สัญญาณ
- แสดงค่า SNR, RSSI, BER แบบ real-time
- สร้างกราฟสเปกตรัมพื้นฐาน

## ความรู้พื้นฐานที่ต้องมี
- Lab 3 (RTL-SDR + ETI pipeline)
- PyQt5 และ matplotlib พื้นฐาน
- NumPy การประมวลผลสัญญาณ

## อุปกรณ์ที่ใช้
- **Raspberry Pi 4** พร้อม RTL-SDR V4 dongle
- **หน้าจอสัมผัส HDMI 7"** สำหรับแสดงผล
- **เสาอากาศ DAB/FM** ที่มีประสิทธิภาพสูง
- **การเชื่อมต่อเน็ต** สำหรับข้อมูลเพิ่มเติม

## การเตรียมระบบ

### คำสั่งติดตั้ง:

```bash
sudo apt install -y python3-numpy python3-matplotlib
pip3 install PyQt5 scipy
```

## ขั้นตอนการทำงาน

### 1. ทำความเข้าใจ Signal Analysis Pipeline

```
Lab 3 ETI Pipeline → I/Q Analysis → Signal Quality Metrics
        ↓
FFT Analysis → Spectrum Display → Real-time Updates
```

### 2. เรียกใช้งาน Lab GUI

```bash
cd Labs/Lab6
python3 lab6.py
```

## งานที่ต้องทำ (ประมาณ 3-4 ชั่วโมง)

### 1. ปรับแต่ง Database (30 นาที):

```python
def init_database(self):
    # TODO: สร้างตาราง signal_measurements (เก็บ SNR, RSSI, BER)
    # TODO: สร้างตาราง spectrum_data (เก็บข้อมูลสเปกตรัม)
    pass
```

### 2. Signal Analyzer ใช้ Lab 3 (1.5 ชั่วโมง):

```python
def run(self):
    # TODO: ใช้ Lab 3 pipeline วิเคราะห์และส่ง signals
    pass

def capture_iq_data(self):
    # TODO: ใช้ Lab 3 RTL-SDR capture หรือ mock data
    pass

def analyze_spectrum(self, iq_data):
    # TODO: คำนวณ FFT และ power spectrum
    pass
```

### 3. Real-time Display (1 ชั่วโมง):

```python
def setup_ui(self):
    # TODO: สร้าง control panel (เลือกความถี่, ระยะเวลา, ปุ่ม Start/Stop)
    # TODO: สร้าง LCD displays สำหรับ SNR, RSSI, BER
    # TODO: สร้าง matplotlib graphs สำหรับสเปกตรัม
    # TODO: เชื่อมต่อ signals กับ start_analysis()
    pass
```

### 4. Analysis Functions (1 ชั่วโมง):

```python
def start_analysis(self):
    # TODO: รับค่าจาก combo boxes และเริ่มการวิเคราะห์
    # TODO: อัปเดต UI status และเริ่ม timer
    pass
```

## เป้าหมายของการบ้าน
- เข้าใจการใช้ Lab 3 pipeline สำหรับวิเคราะห์
- เรียนรู้ matplotlib การแสดงกราฟ
- แสดงค่าสัญญาณแบบ real-time
- วิเคราะห์ได้อย่างน้อย 1 ความถี่

## ผลลัพธ์ที่คาดหวัง

### การทำงานพื้นฐาน:
```
DAB+ Signal Analyzer เริ่มต้น...
เลือกความถี่: 185.360 MHz
เริ่มวิเคราะห์...
SNR: 12.5 dB, RSSI: -45.2 dBm, BER: 0.001%
แสดงกราฟสเปกตรัมแบบ real-time
```

### ไฟล์ที่สร้าง:
- `signal_analysis.db`: ฐานข้อมูลการวิเคราะห์
- `spectrum_*.png`: กราฟสเปกตรัมที่บันทึก
- Screenshot ของ GUI ที่ทำงานได้

## หัวข้อขยาย (ถ้าเหลือเวลา)

1. **เพิ่มการวิเคราะห์หลายความถี่**
2. **บันทึกข้อมูลลง CSV**
3. **Constellation diagram**
4. **สัญญาณเตือนคุณภาพต่ำ**

## Tips การทำงาน

1. **เริ่มจาก Database** สร้างตารางก่อน
2. **ทดสอบ Lab 3** ให้ทำงานได้ก่อน
3. **matplotlib พื้นฐาน** เริ่มจากกราฟง่ายๆ
4. **Mock Data** ถ้า RTL-SDR ไม่มี

## การส่งงาน

1. **ไฟล์ที่ต้องส่ง:**
   - `lab6.py` (โค้ดที่แก้แล้ว)
   - `signal_analysis.db` (ฐานข้อมูล)
   - Screenshot ของ GUI

2. **เกณฑ์การให้คะแนน:**
   - แสดงค่า SNR, RSSI, BER ได้ (30%)
   - สร้างกราฟสเปกตรัมได้ (30%)
   - GUI ทำงานแบบ real-time (40%)

---
**หมายเหตุ**: การบ้านนี้ใช้เวลาประมาณ 3-4 ชั่วโมง