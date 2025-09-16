# LAB 3: การควบคุม RTL-SDR โดยตรงด้วย pyrtlsdr

## วัตถุประสงค์
- เข้าถึงและควบคุม RTL-SDR โดยตรงผ่าน Python
- เรียนรู้การอ่านและประมวลผล IQ samples
- สร้างเครื่องมือวิเคราะห์สเปกตรัมความถี่แบบ real-time
- พัฒนา GUI สำหรับการควบคุมและแสดงผลด้วย matplotlib

## ความรู้พื้นฐานที่ต้องมี
- ความเข้าใจจาก Lab 1 และ Lab 2
- ความรู้พื้นฐานเกี่ยวกับ DSP (Digital Signal Processing)
- การใช้งาน NumPy และ matplotlib
- ความเข้าใจเกี่ยวกับ FFT และ spectrum analysis

## อุปกรณ์ที่ใช้
- **Raspberry Pi 4** พร้อม RTL-SDR V4 dongle
- **หน้าจอสัมผัส HDMI 7"** สำหรับควบคุม
- **เสาอากาศ wideband** สำหรับรับสัญญาณ
- **การเชื่อมต่อเน็ต** สำหรับติดตั้ง packages

## การเตรียมระบบ

### คำสั่งติดตั้ง Dependencies:

```bash
# ติดตั้ง Python scientific packages
sudo apt install -y python3-numpy python3-scipy python3-matplotlib
sudo apt install -y python3-pyqt5 python3-pyqt5.qtwidgets

# ติดตั้ง pyrtlsdr dependencies
sudo apt install -y librtlsdr0 librtlsdr-dev
sudo apt install -y python3-pip python3-dev

# ติดตั้ง pyrtlsdr
pip3 install pyrtlsdr

# ติดตั้ง matplotlib backend สำหรับ PyQt5
pip3 install matplotlib PyQt5
```

### ตรวจสอบการติดตั้ง:

```bash
# ทดสอบ pyrtlsdr
python3 -c "from rtlsdr import RtlSdr; print('pyrtlsdr OK')"

# ทดสอบ RTL-SDR hardware
rtl_test -t
```

## ขั้นตอนการทำงาน

### 1. ทำความเข้าใจ RTL-SDR โดยตรง

```python
from rtlsdr import RtlSdr

# เชื่อมต่อ RTL-SDR
sdr = RtlSdr()

# ตั้งค่าพื้นฐาน
sdr.sample_rate = 2.4e6    # 2.4 MHz
sdr.center_freq = 100e6    # 100 MHz  
sdr.gain = 'auto'

# อ่าน samples (complex numbers)
samples = sdr.read_samples(1024*1024)  # 1M samples

sdr.close()
```

### 2. เรียกใช้งาน Lab GUI

```bash
cd Labs/Lab3
python3 lab3.py
```

## การเขียนโค้ด

### ส่วนที่ต้องเติมใน `lab3.py`:

#### 1. RTLSDRController - การควบคุมโดยตรง:

```python
from rtlsdr import RtlSdr
import numpy as np

class RTLSDRController(QThread):
    spectrum_data = pyqtSignal(np.ndarray, np.ndarray)  # freq, power
    signal_info = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def connect_rtlsdr(self):
        try:
            self.sdr = RtlSdr()
            
            # ตั้งค่าเริ่มต้น
            self.sdr.sample_rate = self.sample_rate
            self.sdr.center_freq = self.center_freq
            self.sdr.gain = self.gain
            
            # ตรวจสอบการเชื่อมต่อ
            test_samples = self.sdr.read_samples(1024)
            if len(test_samples) > 0:
                return True
            else:
                return False
                
        except Exception as e:
            self.error_occurred.emit(f"เชื่อมต่อ RTL-SDR ไม่ได้: {str(e)}")
            return False
            
    def read_samples(self, num_samples=1024*1024):
        try:
            if self.sdr:
                return self.sdr.read_samples(num_samples)
            return None
        except Exception as e:
            self.error_occurred.emit(f"อ่าน samples ไม่ได้: {str(e)}")
            return None
```

#### 2. การคำนวณสเปกตรัม:

```python
def calculate_spectrum(self, samples):
    try:
        # คำนวณ FFT
        fft_data = np.fft.fft(samples)
        fft_shifted = np.fft.fftshift(fft_data)
        
        # คำนวณ power spectrum (dB)
        power = 20 * np.log10(np.abs(fft_shifted) + 1e-10)
        
        # คำนวณ frequencies
        frequencies = np.fft.fftfreq(len(samples), 1/self.sample_rate)
        frequencies = np.fft.fftshift(frequencies) + self.center_freq
        
        return frequencies, power
        
    except Exception as e:
        self.error_occurred.emit(f"คำนวณสเปกตรัม error: {str(e)}")
        return None, None
```

#### 3. SpectrumAnalyzer - การแสดงกราฟ:

```python
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class SpectrumAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_matplotlib()
        self.setup_ui()
        
    def setup_matplotlib(self):
        # สร้าง matplotlib figure
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        # ตั้งค่าแกน
        self.ax.set_xlabel('Frequency (MHz)')
        self.ax.set_ylabel('Power (dB)')
        self.ax.set_title('RF Spectrum Analyzer')
        self.ax.grid(True, alpha=0.3)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # เพิ่ม matplotlib canvas
        layout.addWidget(self.canvas)
        
        # ปุ่มควบคุม
        control_layout = QHBoxLayout()
        self.save_btn = QPushButton(" บันทึกกราฟ")
        self.clear_btn = QPushButton(" เคลียร์")
        self.freeze_btn = QPushButton("️ หยุดชั่วคราว")
        
        control_layout.addWidget(self.save_btn)
        control_layout.addWidget(self.clear_btn)
        control_layout.addWidget(self.freeze_btn)
        layout.addLayout(control_layout)
        
    def update_spectrum(self, frequencies, power):
        try:
            # เคลียร์กราฟเก่า
            self.ax.clear()
            
            # วาดกราฟใหม่
            self.ax.plot(frequencies / 1e6, power, 'b-', linewidth=0.8)
            
            # ตั้งค่าแกน
            self.ax.set_xlabel('Frequency (MHz)')
            self.ax.set_ylabel('Power (dB)')
            self.ax.set_title('RF Spectrum - Real Time')
            self.ax.grid(True, alpha=0.3)
            
            # อัพเดท canvas
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"อัพเดทกราฟ error: {str(e)}")
```

#### 4. RTLSDRControlPanel - การควบคุมพารามิเตอร์:

```python
class RTLSDRControlPanel(QWidget):
    frequency_changed = pyqtSignal(float)
    sample_rate_changed = pyqtSignal(float)
    gain_changed = pyqtSignal(str)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Frequency control
        freq_group = QGroupBox("ความถี่กลาง (MHz)")
        freq_layout = QVBoxLayout(freq_group)
        
        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setRange(24, 1700)  # 24-1700 MHz
        self.freq_slider.setValue(100)       # 100 MHz
        
        self.freq_spinbox = QSpinBox()
        self.freq_spinbox.setRange(24, 1700)
        self.freq_spinbox.setValue(100)
        self.freq_spinbox.setSuffix(" MHz")
        
        freq_layout.addWidget(self.freq_slider)
        freq_layout.addWidget(self.freq_spinbox)
        layout.addWidget(freq_group)
        
        # Sample rate control
        sr_group = QGroupBox("Sample Rate")
        sr_layout = QVBoxLayout(sr_group)
        
        self.sr_combo = QComboBox()
        self.sr_combo.addItems([
            "0.25 MHz", "0.5 MHz", "1.0 MHz", 
            "1.2 MHz", "2.0 MHz", "2.4 MHz"
        ])
        self.sr_combo.setCurrentText("2.4 MHz")
        
        sr_layout.addWidget(self.sr_combo)
        layout.addWidget(sr_group)
        
        # Gain control
        gain_group = QGroupBox("Gain")
        gain_layout = QVBoxLayout(gain_group)
        
        self.gain_combo = QComboBox()
        self.gain_combo.addItems([
            "auto", "0 dB", "9 dB", "14 dB", "27 dB", 
            "37 dB", "77 dB", "87 dB", "125 dB", 
            "144 dB", "157 dB", "166 dB", "197 dB"
        ])
        
        gain_layout.addWidget(self.gain_combo)
        layout.addWidget(gain_group)
        
        # เชื่อม signals
        self.freq_slider.valueChanged.connect(self.on_freq_changed)
        self.freq_spinbox.valueChanged.connect(self.on_freq_changed)
        self.sr_combo.currentTextChanged.connect(self.on_sr_changed)
        self.gain_combo.currentTextChanged.connect(self.gain_changed.emit)
        
    def on_freq_changed(self, value):
        # sync slider และ spinbox
        if self.sender() == self.freq_slider:
            self.freq_spinbox.setValue(value)
        else:
            self.freq_slider.setValue(value)
            
        self.frequency_changed.emit(value * 1e6)  # convert to Hz
        
    def on_sr_changed(self, text):
        # แปลง text เป็น sample rate
        sr_map = {
            "0.25 MHz": 0.25e6, "0.5 MHz": 0.5e6, "1.0 MHz": 1.0e6,
            "1.2 MHz": 1.2e6, "2.0 MHz": 2.0e6, "2.4 MHz": 2.4e6
        }
        self.sample_rate_changed.emit(sr_map.get(text, 2.4e6))
```

### คำแนะนำการเขียน:

1. **ใช้ numpy** สำหรับการประมวลผลสัญญาณ
2. **ใช้ matplotlib** สำหรับแสดงกราฟแบบ real-time
3. **ใช้ QThread** เพื่อไม่ให้ GUI ค้าง
4. **จัดการ memory** เพื่อไม่ให้ระบบหน่วง

## ผลลัพธ์ที่คาดหวัง

### 1. GUI Application ที่สมบูรณ์:
- หน้าต่างแบ่งเป็น 3 ส่วน: controls, spectrum, analysis
- การควบคุมความถี่และพารามิเตอร์แบบ real-time
- กราฟสเปกตรัมที่อัพเดทต่อเนื่อง
- การแสดงข้อมูลการวิเคราะห์สัญญาณ

### 2. การทำงานของระบบ:
```
 เชื่อมต่อ RTL-SDR สำเร็จ
 Tuner: Rafael Micro R820T2
 ตั้งค่า: 100 MHz, 2.4 MHz, auto gain

 เริ่มการวิเคราะห์สเปกตรัม...
 พบสัญญาณที่ 88.5 MHz (-45 dBm) - FM Radio
 พบสัญญาณที่  174.9 MHz (-52 dBm) - DAB+
 พบสัญญาณที่ 462.7 MHz (-38 dBm) - PMR

 SNR: 15.2 dB
 Peak count: 12 signals
 บันทึกข้อมูลแล้ว: spectrum_100MHz_20241208.csv
```

### 3. ไฟล์ที่สร้างขึ้น:
- `spectrum_data_*.csv`: ข้อมูลสเปกตรัม
- `spectrum_plot_*.png`: กราฟที่บันทึก
- `signal_analysis_*.json`: ผลการวิเคราะห์

## การแก้ไขปัญหา

### ปัญหา 1: pyrtlsdr import ไม่ได้

**วิธีแก้**:
```bash
# ติดตั้งใหม่
sudo apt remove python3-rtlsdr
pip3 uninstall pyrtlsdr
pip3 install pyrtlsdr

# ตรวจสอบ
python3 -c "from rtlsdr import RtlSdr; print('OK')"
```

### ปัญหา 2: matplotlib ช้าบนหน้าจอสัมผัส

**วิธีแก้**:
```python
# ลดการอัพเดทกราฟ
self.update_timer.setInterval(200)  # 5 FPS แทน 30 FPS

# ใช้ blit สำหรับการวาดที่เร็วขึ้น
self.line, = self.ax.plot([], [])
self.line.set_data(frequencies, power)
self.canvas.draw_idle()
```

### ปัญหา 3: Memory leak

**วิธีแก้**:
```python
def calculate_spectrum(self, samples):
    # จำกัดขนาด samples
    if len(samples) > 1024*1024:
        samples = samples[:1024*1024]
    
    # ใช้ in-place operations
    np.fft.fft(samples, overwrite_x=True)
    
    # ล้าง memory
    del samples
```

## คำถามทบทวน

1. **IQ samples คืออะไร?**
   - ตอบ: Complex numbers แทน amplitude และ phase ของสัญญาณ

2. **FFT ใช้ทำอะไรใน spectrum analysis?**
   - ตอบ: แปลงสัญญาณจาก time domain เป็น frequency domain

3. **ทำไมต้องใช้ fftshift?**
   - ตอบ: เพื่อจัดเรียงความถี่ให้ถูกต้อง (negative ไปซ้าย, positive ไปขวา)

4. **Sample rate มีผลต่ออะไร?**
   - ตอบ: ช่วงความถี่ที่วิเคราะห์ได้และความละเอียดของสเปกตรัม

---

**หมายเหตุ**: Lab นี้ต้องการความรู้ DSP พื้นฐาน สำหรับการทำความเข้าใจการทำงานของ RTL-SDR ระดับต่ำ