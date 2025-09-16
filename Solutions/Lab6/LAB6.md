# LAB 6: สร้าง DAB+ Signal Analyzer

## วัตถุประสงค์
- พัฒนาเครื่องมือวิเคราะห์สัญญาณ DAB+ อย่างละเอียด
- วิเคราะห์คุณภาพสัญญาณ (SNR, RSSI, BER)
- วิเคราะห์สเปกตรัมความถี่และโครงสร้าง OFDM
- สร้างกราฟและรายงานการวิเคราะห์
- ส่งออกข้อมูลเป็น CSV, PNG, JSON

## ความรู้พื้นฐานที่ต้องมี
- ความเข้าใจจาก Lab 1-5
- Digital Signal Processing (DSP) ขั้นสูง
- การใช้งาน NumPy, matplotlib, pandas
- ความเข้าใจ OFDM, BER, SNR, RSSI
- การใช้งาน PyQt5 GUI และ matplotlib integration

## อุปกรณ์ที่ใช้
- **Raspberry Pi 4** พร้อม RTL-SDR V4 dongle
- **หน้าจอสัมผัส HDMI 7"** สำหรับควบคุม
- **เสาอากาศ wideband** สำหรับรับสัญญาณ
- **การเชื่อมต่อเน็ต** สำหรับติดตั้ง packages

## การเตรียมระบบ

### คำสั่งติดตั้ง Advanced Dependencies:

```bash
# ติดตั้ง scientific packages
sudo apt install -y python3-numpy python3-scipy python3-matplotlib python3-pandas
sudo apt install -y python3-pyqt5 python3-pyqt5.qtwidgets

# ติดตั้ง pyrtlsdr และ matplotlib backend
sudo apt install -y librtlsdr0 librtlsdr-dev
sudo apt install -y python3-pip python3-dev
pip3 install pyrtlsdr matplotlib PyQt5

# ติดตั้ง seaborn, scikit-learn สำหรับ visualization/analysis
pip3 install seaborn scikit-learn
```

### การเตรียมไฟล์และโฟลเดอร์

```bash
mkdir -p Solutions/Lab6/analysis_reports
mkdir -p Solutions/Lab6/spectrum_data
```

### การ calibrate RTL-SDR (optional)

```bash
# ตรวจสอบ hardware
rtl_test -t

# ตรวจสอบค่า gain, sample rate, center frequency
python3 -c "from rtlsdr import RtlSdr; s=RtlSdr(); print(s.get_gains())"
```

## ขั้นตอนการทำงาน

### 1. ทำความเข้าใจ DAB+ Signal Structure

- DAB+ ใช้ OFDM (Orthogonal Frequency Division Multiplexing)
- มี subcarriers หลายร้อยตัวในแต่ละ ensemble
- คุณภาพสัญญาณวัดจาก SNR, RSSI, BER

### 2. เรียกใช้งาน Lab GUI

```bash
cd Solutions/Lab6
python3 lab6.py
```

## การเขียนโค้ด

### ส่วนที่ต้องเติมใน `lab6.py`:

#### 1. AdvancedSignalAnalyzer - การวิเคราะห์ขั้นสูง:

```python
class AdvancedSignalAnalyzer(QThread):
    analysis_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def analyze_dab_signal(self, samples, sample_rate, center_freq):
        # TODO: วิเคราะห์โครงสร้าง OFDM, SNR, RSSI, BER
        # ส่งผลลัพธ์ผ่าน analysis_ready
        pass

    def calculate_basic_params(self, samples):
        # TODO: คำนวณ RSSI, SNR
        pass

    def analyze_ofdm_structure(self, samples):
        # TODO: วิเคราะห์ OFDM subcarriers
        pass

    def calculate_quality_metrics(self, samples):
        # TODO: คำนวณ BER, SNR, RSSI
        pass

    def estimate_ber(self, samples):
        # TODO: ประมาณ BER
        pass
```

#### 2. SpectrumWaterfall - การแสดงผล Waterfall:

```python
class SpectrumWaterfall(QWidget):
    def setup_matplotlib(self):
        # TODO: สร้าง waterfall plot ด้วย matplotlib
        pass

    def update_spectrum(self, spectrum):
        # TODO: อัพเดท waterfall plot
        pass
```

#### 3. ConstellationPlot - การแสดง I/Q Constellation:

```python
class ConstellationPlot(QWidget):
    def setup_matplotlib(self):
        # TODO: สร้าง constellation plot
        pass

    def update_constellation(self, samples):
        # TODO: อัพเดทจุด I/Q
        pass
```

#### 4. ReportGenerator - การสร้างรายงาน:

```python
class ReportGenerator:
    def generate_analysis_report(self, analysis_data):
        # TODO: สร้างรายงานวิเคราะห์ (text/HTML)
        pass

    def export_csv_data(self, data, filename):
        # TODO: ส่งออกข้อมูลเป็น CSV
        pass

    def export_json_data(self, data, filename):
        # TODO: ส่งออกข้อมูลเป็น JSON
        pass
```

#### 5. RealTimeAnalysisWidget - การแสดงผลแบบ Real-time:

```python
class RealTimeAnalysisWidget(QWidget):
    def setup_ui(self):
        # TODO: สร้าง UI สำหรับแสดง metrics real-time
        pass

    def create_indicator(self, label, min_val, max_val, unit):
        # TODO: สร้าง progress bar/indicator
        pass

    def update_metrics(self, metrics):
        # TODO: อัพเดทค่า SNR, RSSI, BER
        pass
```

### คำแนะนำการเขียน:

1. **ใช้ numpy/scipy** สำหรับ DSP และการวิเคราะห์
2. **ใช้ matplotlib** สำหรับกราฟ spectrum, waterfall, constellation
3. **ใช้ QThread** สำหรับงานวิเคราะห์หนัก
4. **รองรับการ export ข้อมูลเป็น CSV, PNG, JSON**
5. **มี error handling และ logging**

## ผลลัพธ์ที่คาดหวัง

### 1. GUI Application ที่ครบถ้วน:
- หน้าต่างแบ่งเป็น 4 ส่วน: spectrum, waterfall, constellation, metrics
- วิเคราะห์คุณภาพสัญญาณแบบ real-time
- บันทึกและส่งออกข้อมูลได้หลายรูปแบบ

### 2. การทำงานของระบบ:
```
 เริ่มวิเคราะห์สัญญาณ DAB+...
 SNR: 18.7 dB
 RSSI: -52 dBm
 BER: 2.1%
 Waterfall: อัพเดทต่อเนื่อง
 Constellation: จุดกระจายดี
 บันทึกข้อมูลแล้ว: analysis_20241208.json, spectrum_20241208.csv
```

### 3. ไฟล์ที่สร้างขึ้น:
- `analysis_reports/analysis_*.json`: รายงานวิเคราะห์
- `spectrum_data/spectrum_*.csv`: ข้อมูลสเปกตรัม
- `spectrum_data/waterfall_*.png`: ภาพ waterfall
- `spectrum_data/constellation_*.png`: ภาพ constellation

## การแก้ไขปัญหา

### ปัญหา 1: การวิเคราะห์ช้า/ค้าง

**วิธีแก้**:
- ใช้ QThread สำหรับงานหนัก
- จำกัดขนาด samples ที่วิเคราะห์

### ปัญหา 2: Memory overflow

**วิธีแก้**:
- จำกัดจำนวน rows ใน waterfall plot
- ใช้ in-place numpy operations

### ปัญหา 3: ค่าคุณภาพผิดปกติ

**วิธีแก้**:
- ตรวจสอบการ calibrate hardware
- ตรวจสอบ sample rate/gain

## คำถามทบทวน

1. **BER คืออะไร?**
   - ตอบ: Bit Error Rate คืออัตราส่วนบิตผิดพลาดต่อบิตทั้งหมด

2. **SNR มีผลต่ออะไร?**
   - ตอบ: มีผลต่อความชัดเจนของสัญญาณและการ demodulate

3. **Waterfall plot ใช้ดูอะไร?**
   - ตอบ: ดูการเปลี่ยนแปลงของสเปกตรัมตามเวลา

4. **Constellation plot คืออะไร?**
   - ตอบ: กราฟแสดงการกระจายของจุด I/Q สำหรับวิเคราะห์ modulation

---

**หมายเหตุ**: Lab นี้เหมาะสำหรับผู้ที่ต้องการเข้าใจการวิเคราะห์สัญญาณ DAB+ เชิงลึกและการประยุกต์ DSP บน Raspberry Pi