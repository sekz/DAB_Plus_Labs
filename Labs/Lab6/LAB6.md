# LAB 6: สร้าง DAB+ Signal Analyzer

## วัตถุประสงค์
- พัฒนาเครื่องมือวิเคราะห์สัญญาณ DAB+ อย่างละเอียด
- วิเคราะห์คุณภาพสัญญาณ (SNR, RSSI, BER, MER) แบบ real-time
- สร้างกราฟและรายงานการวิเคราะห์ที่ครอบคลุม
- ส่งออกข้อมูลเป็น CSV, JSON และรูปภาพสำหรับรายงาน

## ความรู้พื้นฐานที่ต้องมี  
- ความเข้าใจจาก Lab 1-5 ทั้งหมด
- ความรู้ด้าน RF และ Digital Signal Processing ขั้นสูง
- การใช้งาน NumPy, SciPy และ Matplotlib ระดับสูง
- ความเข้าใจเกี่ยวกับ OFDM และ DAB+ protocol

## อุปกรณ์ที่ใช้
- **Raspberry Pi 4** พร้อม RTL-SDR V4 dongle
- **หน้าจอสัมผัส HDMI 7"** สำหรับแสดงผล
- **เสาอากาศ DAB+ คุณภาพสูง** พร้อม LNA (ถ้าจำเป็น)
- **การเชื่อมต่อเน็ต** สำหรับอัพเดท databases
- **USB Storage** สำหรับส่งออกรายงาน

## การเตรียมระบบ

### คำสั่งติดตั้ง Advanced Dependencies:

```bash
# ติดตั้ง scientific computing packages
sudo apt install -y python3-scipy python3-pandas
pip3 install scikit-learn seaborn plotly

# ติดตั้ง signal processing libraries
pip3 install scipy.signal librosa

# ติดตั้ง advanced visualization
pip3 install matplotlib seaborn plotly bokeh
pip3 install pillow reportlab

# ติดตั้ง data export tools
pip3 install openpyxl xlsxwriter h5py
```

### การเพิ่มเติม RTL-SDR Calibration:

```bash
# ติดตั้ง kalibrate-rtl สำหรับ frequency calibration
cd /tmp
git clone https://github.com/steve-m/kalibrate-rtl
cd kalibrate-rtl
./bootstrap && ./configure && make
sudo make install

# calibrate RTL-SDR (หา frequency offset)
kal -s GSM900 -g 40
```

## ขั้นตอนการทำงาน

### 1. ทำความเข้าใจ DAB+ Signal Structure

```
DAB+ Signal Structure:
├── OFDM Symbols (2048 carriers)
├── Transmission Frame (96 ms)
│   ├── Null Symbol (for synchronization)
│   ├── PRS (Phase Reference Symbol)
│   ├── FIC (Fast Information Channel)
│   └── MSC (Main Service Channel)
└── Ensemble Multiplex
```

### 2. เรียกใช้งาน Lab GUI

```bash
cd Labs/Lab6
python3 lab6.py
```

## การเขียนโค้ด

### ส่วนที่ต้องเติมใน `lab6.py`:

#### 1. AdvancedSignalAnalyzer - การวิเคราะห์ขั้นสูง:

```python
import numpy as np
from scipy import signal
from scipy.fftpack import fft, fftfreq
import pandas as pd

class AdvancedSignalAnalyzer(QThread):
    analysis_result = pyqtSignal(dict)
    spectrum_data = pyqtSignal(np.ndarray, np.ndarray, dict)
    constellation_data = pyqtSignal(np.ndarray)  # I/Q constellation
    error_data = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.sample_rate = 2.048e6  # DAB+ sample rate
        self.center_freq = 174.928e6  # default frequency
        self.fft_size = 2048
        
    def analyze_dab_signal(self, iq_samples):
        """วิเคราะห์สัญญาณ DAB+ ครอบคลุม"""
        analysis = {}
        
        try:
            # 1. Basic signal parameters
            analysis.update(self.calculate_basic_params(iq_samples))
            
            # 2. OFDM-specific analysis
            analysis.update(self.analyze_ofdm_structure(iq_samples))
            
            # 3. Quality metrics
            analysis.update(self.calculate_quality_metrics(iq_samples))
            
            # 4. Frequency domain analysis
            analysis.update(self.analyze_frequency_domain(iq_samples))
            
            # 5. Time domain analysis
            analysis.update(self.analyze_time_domain(iq_samples))
            
            return analysis
            
        except Exception as e:
            logger.error(f"Signal analysis error: {str(e)}")
            return {}
    
    def calculate_basic_params(self, iq_samples):
        """คำนวณพารามิเตอร์พื้นฐาน"""
        # TODO: เติมโค้ดคำนวณ
        # 1. Signal power (RMS, Peak, Average)
        # 2. Dynamic range
        # 3. DC offset
        # 4. I/Q imbalance
        
        rms_power = np.sqrt(np.mean(np.abs(iq_samples)**2))
        peak_power = np.max(np.abs(iq_samples))
        avg_power = np.mean(np.abs(iq_samples))
        
        return {
            'rms_power_dbm': 20 * np.log10(rms_power + 1e-12),
            'peak_power_dbm': 20 * np.log10(peak_power + 1e-12),
            'crest_factor_db': 20 * np.log10(peak_power / rms_power),
            'dc_offset_i': np.mean(iq_samples.real),
            'dc_offset_q': np.mean(iq_samples.imag)
        }
        
    def analyze_ofdm_structure(self, iq_samples):
        """วิเคราะห์โครงสร้าง OFDM ของ DAB+"""
        # TODO: เติมโค้ดวิเคราะห์ OFDM
        # 1. หา Null Symbol (synchronization)
        # 2. ตรวจจับ PRS (Phase Reference Symbol)  
        # 3. วิเคราะห์ Carrier spacing
        # 4. ตรวจสอบ Guard interval
        
        # หา correlation peaks สำหรับ frame sync
        autocorr = np.correlate(iq_samples, iq_samples, mode='full')
        sync_peaks = signal.find_peaks(np.abs(autocorr), height=0.7*np.max(np.abs(autocorr)))
        
        return {
            'frame_sync_detected': len(sync_peaks[0]) > 0,
            'frame_sync_strength': np.max(np.abs(autocorr)) if len(sync_peaks[0]) > 0 else 0,
            'estimated_symbol_rate': self.sample_rate / 2048,  # DAB+ symbol rate
            'carriers_detected': self.count_active_carriers(iq_samples)
        }
        
    def calculate_quality_metrics(self, iq_samples):
        """คำนวณค่าคุณภาพสัญญาณ"""
        # TODO: เติมโค้ดคำนวณคุณภาพ
        # 1. SNR (Signal-to-Noise Ratio)
        # 2. MER (Modulation Error Ratio)  
        # 3. BER estimation
        # 4. Carrier-to-Noise Ratio (CNR)
        
        # คำนวณ SNR แบบง่าย
        signal_power = np.mean(np.abs(iq_samples)**2)
        
        # ประมาณ noise จาก high frequency components
        fft_data = np.fft.fft(iq_samples[:4096])  
        noise_floor = np.mean(np.abs(fft_data[-512:])**2)  # assume high freq = noise
        
        snr_linear = signal_power / (noise_floor + 1e-12)
        snr_db = 10 * np.log10(snr_linear)
        
        return {
            'snr_db': snr_db,
            'signal_power_dbm': 10 * np.log10(signal_power + 1e-12),
            'noise_floor_dbm': 10 * np.log10(noise_floor + 1e-12),
            'estimated_ber': self.estimate_ber(snr_db)
        }
        
    def estimate_ber(self, snr_db):
        """ประมาณ BER จาก SNR สำหรับ DAB+"""
        # Simplified BER estimation for QPSK (DAB+ uses DQPSK)
        if snr_db > 20:
            return 1e-6
        elif snr_db > 10:
            return 1e-4 * np.exp(-(snr_db - 10) / 3)
        else:
            return 0.01 * np.exp(-(snr_db) / 2)
```

#### 2. SpectrumWaterfall - การแสดงผล Waterfall:

```python
class SpectrumWaterfall(QWidget):
    def __init__(self, max_history=500):
        super().__init__()
        self.max_history = max_history
        self.spectrum_history = []
        self.setup_matplotlib()
        self.setup_ui()
        
    def setup_matplotlib(self):
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        
        # สร้าง subplots
        self.ax_spectrum = self.figure.add_subplot(211)
        self.ax_waterfall = self.figure.add_subplot(212)
        
        # ตั้งค่า spectrum plot
        self.ax_spectrum.set_xlabel('Frequency (MHz)')
        self.ax_spectrum.set_ylabel('Power (dB)')
        self.ax_spectrum.set_title('Real-time Spectrum')
        self.ax_spectrum.grid(True, alpha=0.3)
        
        # ตั้งค่า waterfall plot
        self.ax_waterfall.set_xlabel('Frequency (MHz)')
        self.ax_waterfall.set_ylabel('Time (s)')
        self.ax_waterfall.set_title('Spectrum Waterfall')
        
    def update_spectrum(self, frequencies, power_spectrum):
        """อัพเดทกราฟสเปกตรัมและ waterfall"""
        try:
            # เก็บข้อมูลใน history
            self.spectrum_history.append(power_spectrum.copy())
            if len(self.spectrum_history) > self.max_history:
                self.spectrum_history.pop(0)
                
            # Clear และวาดกราฟ spectrum ใหม่
            self.ax_spectrum.clear()
            self.ax_spectrum.plot(frequencies/1e6, power_spectrum, 'b-', linewidth=0.8)
            self.ax_spectrum.set_xlabel('Frequency (MHz)')
            self.ax_spectrum.set_ylabel('Power (dB)')
            self.ax_spectrum.grid(True, alpha=0.3)
            
            # วาด waterfall
            if len(self.spectrum_history) > 10:
                waterfall_data = np.array(self.spectrum_history[-100:])  # last 100 samples
                
                self.ax_waterfall.clear()
                im = self.ax_waterfall.imshow(
                    waterfall_data, 
                    aspect='auto',
                    extent=[frequencies[0]/1e6, frequencies[-1]/1e6, 0, len(waterfall_data)],
                    cmap='plasma',
                    origin='lower'
                )
                self.ax_waterfall.set_xlabel('Frequency (MHz)')
                self.ax_waterfall.set_ylabel('Time (samples)')
                
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Waterfall update error: {str(e)}")
```

#### 3. ConstellationPlot - การแสดง I/Q Constellation:

```python
class ConstellationPlot(QWidget):
    def setup_matplotlib(self):
        self.figure = Figure(figsize=(6, 6))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        self.ax.set_xlabel('I (In-phase)')
        self.ax.set_ylabel('Q (Quadrature)')
        self.ax.set_title('I/Q Constellation')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_aspect('equal')
        
    def update_constellation(self, iq_samples, decimation=100):
        """อัพเดท constellation diagram"""
        try:
            # ลด samples เพื่อแสดงผลได้เร็วขึ้น
            samples_decimated = iq_samples[::decimation]
            
            self.ax.clear()
            
            # วาด constellation points
            self.ax.scatter(
                samples_decimated.real, 
                samples_decimated.imag, 
                alpha=0.6, 
                s=1,
                c='blue'
            )
            
            # TODO: เติมการวิเคราะห์ constellation
            # 1. หา decision boundaries
            # 2. คำนวณ EVM (Error Vector Magnitude)
            # 3. ตรวจจับ modulation scheme
            
            self.ax.set_xlabel('I (In-phase)')
            self.ax.set_ylabel('Q (Quadrature)')
            self.ax.set_title(f'I/Q Constellation ({len(samples_decimated)} samples)')
            self.ax.grid(True, alpha=0.3)
            self.ax.set_aspect('equal')
            
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Constellation update error: {str(e)}")
```

#### 4. ReportGenerator - การสร้างรายงาน:

```python
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
    def generate_analysis_report(self, analysis_data, output_path):
        """สร้างรายงานการวิเคราะห์"""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Title
        title = Paragraph("DAB+ Signal Analysis Report", self.styles['Title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # TODO: เติมเนื้อหารายงาน
        # 1. Executive Summary
        # 2. Signal Parameters Table
        # 3. Quality Metrics
        # 4. Spectrum plots
        # 5. Recommendations
        
        # Signal Parameters
        story.append(Paragraph("Signal Parameters", self.styles['Heading2']))
        
        params_data = [
            ['Parameter', 'Value', 'Unit'],
            ['Center Frequency', f"{analysis_data.get('center_freq', 0)/1e6:.3f}", 'MHz'],
            ['Sample Rate', f"{analysis_data.get('sample_rate', 0)/1e6:.2f}", 'MSps'],
            ['SNR', f"{analysis_data.get('snr_db', 0):.1f}", 'dB'],
            ['Signal Power', f"{analysis_data.get('signal_power_dbm', 0):.1f}", 'dBm'],
            ['Estimated BER', f"{analysis_data.get('estimated_ber', 0):.2e}", '']
        ]
        
        params_table = Table(params_data)
        story.append(params_table)
        
        doc.build(story)
        
    def export_csv_data(self, spectrum_data, analysis_data, output_path):
        """ส่งออกข้อมูลเป็น CSV"""
        # TODO: เติมโค้ดส่งออก CSV
        # 1. สร้าง DataFrame จาก spectrum data
        # 2. เพิ่มคอลัมน์ analysis results
        # 3. บันทึกเป็น CSV
        pass
        
    def export_json_data(self, analysis_data, output_path):
        """ส่งออกข้อมูลเป็น JSON"""
        import json
        
        # TODO: เติมโค้ดส่งออก JSON
        # 1. เตรียมข้อมูลให้เป็น serializable
        # 2. เพิ่ม timestamp และ metadata
        # 3. บันทึกเป็น JSON
        pass
```

#### 5. RealTimeAnalysisWidget - การแสดงผลแบบ Real-time:

```python
class RealTimeAnalysisWidget(QWidget):
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Status indicators
        status_layout = QGridLayout()
        
        self.sync_indicator = self.create_indicator("🔄 Sync", "red")
        self.signal_indicator = self.create_indicator("📶 Signal", "yellow")
        self.quality_indicator = self.create_indicator("✓ Quality", "green")
        
        status_layout.addWidget(self.sync_indicator, 0, 0)
        status_layout.addWidget(self.signal_indicator, 0, 1)
        status_layout.addWidget(self.quality_indicator, 0, 2)
        
        layout.addLayout(status_layout)
        
        # Real-time metrics
        metrics_group = QGroupBox("Real-time Metrics")
        metrics_layout = QGridLayout(metrics_group)
        
        # Create LCD displays for key metrics
        self.snr_lcd = QLCDNumber(5)
        self.snr_lcd.display("--.-")
        self.rssi_lcd = QLCDNumber(6)
        self.rssi_lcd.display("---.-")
        self.ber_lcd = QLCDNumber(8)
        self.ber_lcd.display("-.--E-0")
        
        metrics_layout.addWidget(QLabel("SNR (dB):"), 0, 0)
        metrics_layout.addWidget(self.snr_lcd, 0, 1)
        metrics_layout.addWidget(QLabel("RSSI (dBm):"), 1, 0)
        metrics_layout.addWidget(self.rssi_lcd, 1, 1)
        metrics_layout.addWidget(QLabel("BER:"), 2, 0)
        metrics_layout.addWidget(self.ber_lcd, 2, 1)
        
        layout.addWidget(metrics_group)
        
    def create_indicator(self, text, initial_color):
        """สร้าง status indicator"""
        indicator = QPushButton(text)
        indicator.setEnabled(False)
        indicator.setMinimumSize(100, 40)
        indicator.setStyleSheet(f"""
            QPushButton {{
                background: {initial_color};
                color: white;
                border: 2px solid black;
                border-radius: 8px;
                font-weight: bold;
            }}
        """)
        return indicator
        
    def update_metrics(self, analysis_data):
        """อัพเดทค่าต่างๆ แบบ real-time"""
        # TODO: เติมโค้ดอัพเดท metrics
        # 1. อัพเดท LCD displays
        # 2. เปลี่ยนสี indicators
        # 3. ตรวจสอบ thresholds
        pass
```

### คำแนะนำการเขียน:

1. **ใช้ NumPy/SciPy** สำหรับการประมวลผลสัญญาณขั้นสูง
2. **จัดการ Memory** อย่างระมัดระวังเนื่องจากข้อมูลมาก
3. **ใช้ Threading** เพื่อแยกการประมวลผลออกจาก GUI
4. **เพิ่ม Progress Indicators** สำหรับการประมวลผลที่ใช้เวลานาน

## ผลลัพธ์ที่คาดหวัง

### 1. GUI Application ที่ครบถ้วน:
- หน้าต่างแบ่งเป็น 6 ส่วน: spectrum, waterfall, constellation, analysis, real-time, reports
- การวิเคราะห์สัญญาณขั้นสูงพร้อมกราฟแบบ real-time
- การส่งออกรายงานในรูปแบบต่างๆ
- การติดตาม quality metrics แบบต่อเนื่อง

### 2. การทำงานของระบบ:
```
🔬 DAB+ Signal Analyzer เริ่มต้นแล้ว
📡 ความถี่: 174.928 MHz (Thai PBS)
📊 Sample Rate: 2.048 MSps

📈 การวิเคราะห์เริ่มต้น...
🔄 ตรวจจับ Frame Sync... ✅ พบแล้ว
📶 RSSI: -51.2 dBm
📊 SNR: 22.8 dB (ยอดเยี่ยม)
❌ BER: 1.2e-5 (ต่ำมาก)
📡 MER: 18.5 dB
🎯 I/Q Imbalance: 0.3 dB

🔍 OFDM Structure:
   - Carriers Active: 1536/2048
   - Guard Interval: 246 μs
   - Symbol Rate: 2000 Hz
   - Frame Sync: Strong (95%)

📊 Ensemble Analysis:
   - Services Found: 3
   - Total Bitrate: 576 kbps
   - Audio Quality: Excellent
   
💾 รายงานส่งออกแล้ว:
   - signal_analysis_20241208.pdf
   - spectrum_data_20241208.csv
   - analysis_results_20241208.json
```

### 3. ไฟล์รายงานที่สร้างขึ้น:
```
Reports/
├── signal_analysis_20241208_143022.pdf
├── spectrum_data_20241208_143022.csv
├── analysis_results_20241208_143022.json
├── waterfall_plot_20241208_143022.png
├── constellation_plot_20241208_143022.png
└── quality_trending_20241208.xlsx
```

## การแก้ไขปัญหา

### ปัญหา 1: การวิเคราะห์ช้าเกินไป
**วิธีแก้**:
```python
# ใช้ multiprocessing สำหรับการประมวลผลหนัก
from multiprocessing import Pool

def parallel_fft_analysis(data_chunks):
    with Pool(processes=4) as pool:
        results = pool.map(np.fft.fft, data_chunks)
    return results

# ลด resolution ของการวิเคราะห์
decimation_factor = 4
samples_reduced = iq_samples[::decimation_factor]
```

### ปัญหา 2: Memory overflow
**วิธีแก้**:
```python
# จำกัดขนาด history
MAX_HISTORY_SIZE = 1000
if len(self.spectrum_history) > MAX_HISTORY_SIZE:
    self.spectrum_history = self.spectrum_history[-MAX_HISTORY_SIZE//2:]

# ใช้ memory mapping สำหรับข้อมูลขนาดใหญ่
import numpy as np
large_data = np.memmap('temp_data.dat', dtype='complex64', mode='w+', shape=(1000000,))
```

## คำถามทบทวน

1. **OFDM ในบริบท DAB+ หมายถึงอะไร?**
   - ตอบ: Orthogonal Frequency Division Multiplexing - เทคนิคการส่งข้อมูลหลายความถี่พร้อมกัน

2. **ความแตกต่างระหว่าง SNR และ MER คืออะไร?**
   - ตอบ: SNR วัดสัญญาณต่อ noise, MER วัดความผิดพลาดของ modulation

3. **Constellation diagram บอกอะไรเราได้บ้าง?**
   - ตอบ: คุณภาพการ modulation, noise level, และการบิดเบือนของสัญญาณ

4. **ทำไม DAB+ ใช้ DQPSK แทน QPSK?**
   - ตอบ: DQPSK ต้องการ phase reference น้อยกว่า ทำให้ทนต่อ phase noise ได้ดีกว่า

---

**หมายเหตุ**: Lab นี้เป็นการรวมความรู้ทั้งหมดจาก Lab 1-5 และต้องการความเข้าใจ RF Engineering ขั้นสูง