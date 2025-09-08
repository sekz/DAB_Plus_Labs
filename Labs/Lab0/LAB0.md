# LAB 0: Introduction to DAB+ และ PyQt5

## ส่วนที่ 1: Introduction to DAB+ (15 นาที)

### DAB+ คืออะไร?

**DAB+** (Digital Audio Broadcasting Plus) คือเทคโนโลยีการแพร่สัญญาณวิทยุแบบดิจิทัลที่พัฒนาต่อยอดจาก DAB เดิม โดยใช้ codec ที่ดีกว่าและมีประสิทธิภาพสูงกว่า

### ข้อดีของ DAB+ เมื่อเทียบกับ FM:

#### 🔊 **คุณภาพเสียง**
- **เสียงดิจิทัล** ไม่มี static หรือสัญญาณรบกวน
- **คุณภาพคงที่** ไม่ขึ้นกับระยะทางจากเครื่องส่ง
- **เสียง stereo** ชัดเจนตลอดช่วงรับสัญญาณ

#### 📊 **ข้อมูลเพิ่มเติม**
- **Program Information** แสดงชื่อสถานี รายการ
- **Dynamic Label Segment (DLS)** แสดงชื่อเพลง ศิลปิน แบบ real-time
- **MOT Slideshow** แสดงรูปภาพ album art หรือข้อมูลโฆษณา
- **Electronic Program Guide (EPG)** ตารางรายการ

#### 📡 **ประสิทธิภาพการใช้คลื่น**
- **Multiplexing** สถานีหลายสถานีใช้ความถี่เดียวกัน
- **SFN (Single Frequency Network)** เครื่องส่งหลายจุดใช้ความถี่เดียว
- **ประหยัดสเปกตรัม** ใช้คลื่นความถี่น้อยกว่า FM

### ความถี่ DAB+ ในประเทศไทย:

#### **ข้อมูลพื้นฐานที่ยืนยันแล้ว:**
- ✅ **ช่วงความถี่ที่อนุญาต**: 174-230 MHz (VHF Band III)
- ✅ **วัตถุประสงค์**: สำหรับการทดลองและทดสอบ DAB+
- ✅ **เทคโนโลยี**: DAB+ (MPEG-4 HE AAC v2)
- ✅ **แผนความถี่**: NBTC ผว. 104-2567

#### **การทดลองที่ได้รับอนุญาตปัจจุบัน (2025):**
- 📻 **Block 9A**: ความถี่ 202.928 MHz - กรุงเทพฯ และปริมณฑล (กลุ่มสถานีธรรมะ)
  - สถานีธรรมะเพื่อประชาชน
  - สถานีวิทยุสันติ
- 📻 **Block 6C**: ความถี่ 185.360 MHz - ขอนแก่น และมหาสารคาม (กลุ่มสถานีขอนแก่น)
  - สถานีวิทยุขอนแก่นมหานคร
  - สถานีวิทยุใสฟ้า
  - สถานีวิทยุไธย์ท้องถิ่น

### เทคโนโลยีที่เกี่ยวข้อง:

#### 🔧 **RTL-SDR (Software Defined Radio)**
- **Hardware**: ตัวรับสัญญาณ USB ราคาถูก (~500-1500 บาท)
- **Software**: ประมวลผลสัญญาณด้วยโปรแกรม
- **ความถี่**: รับได้ 24-1700 MHz (ครอบคลุม FM และ DAB+)
- **Bandwidth**: 2.4 MHz (เพียงพอสำหรับ DAB+ ensemble)

#### 💻 **welle.io**
- **DAB+ Decoder**: โปรแกรมถอดรหัส DAB+ แบบ open source
- **Cross-platform**: ทำงานบน Linux, Windows, macOS
- **Features**: รองรับ audio decoding, metadata, slideshow
- **API**: สามารถควบคุมผ่าน command line

### การทำงานของระบบ DAB+:

```
📡 เสาส่ง DAB+ 
    ⬇️
🌐 สัญญาณ RF (174-240 MHz)
    ⬇️
📻 RTL-SDR Dongle 
    ⬇️
💻 IQ Samples (Python)
    ⬇️
🔧 welle.io Decoder
    ⬇️
🎵 Audio + 📝 Metadata + 🖼️ Slideshow
```

---

## ส่วนที่ 2: Introduction to PyQt5 (45 นาที)

### PyQt5 คืออะไร?

**PyQt5** คือ Python binding สำหรับ Qt5 framework ที่ใช้สร้าง GUI applications ข้ามแพลตฟอร์ม

### ทำไมต้องใช้ PyQt5?

#### ✅ **ข้อดี**
- **Cross-platform** ทำงานบน Windows, Linux, macOS
- **Native look** UI ดูเหมือน native app ของแต่ละ OS
- **Rich widgets** มี widget ครบครัน
- **Professional** ใช้สร้างแอปเชิงพาณิชย์ได้
- **Touch support** รองรับหน้าจอสัมผัส

#### 📱 **เหมาะกับ Raspberry Pi เพราะ:**
- **Performance** เร็วกว่า Tkinter
- **Multimedia** รองรับเสียง วิดีโอ
- **Embedded** เหมาะกับระบบฝังตัว
- **Customizable** ปรับแต่ง UI ได้ดี

### หลักการพื้นฐาน PyQt5:

#### 1. **Application และ Window**
```python
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

app = QApplication(sys.argv)          # สร้าง Application
window = QMainWindow()                # สร้าง Window
window.show()                         # แสดงหน้าต่าง
sys.exit(app.exec_())                # รัน Event Loop
```

#### 2. **Widgets (ส่วนประกอบ UI)**
- **QLabel**: ป้ายข้อความ
- **QPushButton**: ปุ่มกด
- **QLineEdit**: ช่องใส่ข้อความ 1 บรรทัด
- **QTextEdit**: ช่องใส่ข้อความหลายบรรทัด
- **QSlider**: แถบเลื่อน
- **QProgressBar**: แถบความคืบหน้า

#### 3. **Layouts (การจัดเรียง)**
- **QVBoxLayout**: จัดเรียงแนวตั้ง
- **QHBoxLayout**: จัดเรียงแนวนอน
- **QGridLayout**: จัดเรียงแบบตาราง

#### 4. **Signals และ Slots (การสื่อสาร)**
```python
button.clicked.connect(self.on_button_click)  # เชื่อม signal กับ slot

def on_button_click(self):                    # slot function
    print("Button clicked!")
```

### การติดตั้งและเรียกใช้:

#### ติดตั้ง PyQt5:
```bash
# บน Raspberry Pi OS
sudo apt install python3-pyqt5 python3-pyqt5.qtwidgets

# หรือใช้ pip (อาจใช้เวลานาน)
pip3 install PyQt5
```

#### เรียกใช้ Lab 0:
```bash
cd Labs/Lab0
python3 lab0.py
```

### โครงสร้างโปรแกรม PyQt5:

```python
#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()           # สร้าง UI
        self.setup_connections()  # เชื่อม signals
        
    def setup_ui(self):
        # สร้าง widgets และ layouts
        pass
        
    def setup_connections(self):
        # เชื่อม signals กับ slots
        pass

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
```

### Demos ใน Lab 0:

#### 🧩 **Demo 1: Basic Widgets**
- การใช้ QLabel, QPushButton, QLineEdit
- การแสดง QMessageBox
- QSlider และ QProgressBar

#### 🔌 **Demo 2: Signals & Slots**
- Built-in signals (clicked, valueChanged)
- Custom signals (pyqtSignal)
- QTimer และ periodic updates

#### 📐 **Demo 3: Layouts**
- QVBoxLayout (แนวตั้ง)
- QHBoxLayout (แนวนอน)  
- Nested layouts

#### ⌨️ **Demo 4: Input Widgets**
- QCheckBox และ QRadioButton
- QComboBox และ QSpinBox
- การอ่านค่าจาก widgets

#### 📱 **Demo 5: Touch-Friendly UI**
- ปุ่มขนาดใหญ่ (min 60x40px)
- Slider ที่เหมาะกับนิ้ว
- Visual feedback
- Font sizes สำหรับหน้าจอ 7"

### Tips สำหรับ Touch Screen:

#### 🎯 **ขนาดที่เหมาะสม:**
- **Buttons**: อย่างน้อย 60x40 pixels
- **Fonts**: 12-16pt สำหรับหน้าจอ 7"
- **Spacing**: เว้นระยะระหว่าง elements

#### 🎨 **Visual Feedback:**
- **Hover effects**: เปลี่ยนสีเมื่อ hover
- **Press effects**: เปลี่ยนสีเมื่อกด
- **Disabled states**: สีเทาเมื่อปิดใช้งาน

#### 🔧 **CSS Styling:**
```python
button.setStyleSheet("""
    QPushButton {
        border: 2px solid #3498db;
        border-radius: 8px;
        background: #5dade2;
        color: white;
        font-size: 14px;
        min-height: 50px;
        min-width: 120px;
    }
    QPushButton:pressed {
        background: #2980b9;
    }
""")
```

### การเตรียมพร้อมสำหรับ Labs ถัดไป:

หลังจากจบ Lab 0 คุณจะรู้:
- ✅ การสร้าง PyQt5 application พื้นฐาน
- ✅ การใช้ widgets หลัก
- ✅ Signals และ Slots
- ✅ การจัดเรียง layouts
- ✅ การทำ touch-friendly UI
- ✅ ความรู้พื้นฐานเกี่ยวกับ DAB+

**เวลาที่ใช้**: ประมาณ 1 ชั่วโمง
- **DAB+ Introduction**: 15 นาที
- **PyQt5 Hands-on**: 45 นาที

### ขั้นตอนต่อไป:
- **Lab 1**: RTL-SDR Testing (ใช้ PyQt5 + subprocess)
- **Lab 2**: welle.io Integration (ใช้ QMediaPlayer)
- **Lab 3**: Direct RTL-SDR (ใช้ matplotlib + PyQt5)
- **Lab 4**: DAB+ Scanner (ใช้ advanced PyQt5)
- **Lab 5**: Program Recorder (ใช้ QTimer + file handling)  
- **Lab 6**: Signal Analyzer (ใช้ data visualization)

---

**🎉 พร้อมแล้ว!** ตอนนี้คุณมีพื้นฐานที่จำเป็นสำหรับ DAB+ Labs แล้ว ไปเริ่ม Lab 1 กันเถอะ!