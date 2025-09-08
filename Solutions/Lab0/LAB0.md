# LAB 0: Introduction to DAB+ และ PyQt5 - เฉลย

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

| Channel | Frequency | การใช้งาน |
|---------|-----------|----------|
| 5A | 174.928 MHz | Thai PBS, NBT |
| 5B | 176.640 MHz | Voice TV, Spring News |
| 5C | 178.352 MHz | MCOT Network |
| 6A | 181.936 MHz | Private Networks |
| 7A | 188.928 MHz | Community Radio |

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

## ส่วนที่ 2: Introduction to PyQt5 - เฉลยครบถ้วน (45 นาที)

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

### หลักการพื้นฐาน PyQt5 (เฉลย):

#### 1. **Application และ Window**
```python
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

# สร้าง Application - จัดการ event loop และ system
app = QApplication(sys.argv)
app.setApplicationName("My App")       # ตั้งชื่อแอป
app.setApplicationVersion("1.0")       # ตั้งเวอร์ชัน

# สร้าง Window หลัก
window = QMainWindow()
window.setWindowTitle("My Window")     # ตั้งชื่อหน้าต่าง
window.setGeometry(100, 100, 800, 600)  # x, y, width, height
window.show()                          # แสดงหน้าต่าง

# รัน Event Loop - รอรับ events จากผู้ใช้
sys.exit(app.exec_())
```

#### 2. **Widgets (ส่วนประกอบ UI) - เฉลยการใช้งาน**

```python
# Label - ป้ายข้อความ
label = QLabel("Hello World")
label.setAlignment(Qt.AlignCenter)     # จัดตำแหน่งกลาง
label.setStyleSheet("color: blue; font-size: 16px;")

# Button - ปุ่มกด
button = QPushButton("Click Me")
button.clicked.connect(my_function)    # เชื่อมกับฟังก์ชัน
button.setMinimumSize(100, 50)        # ขนาดขั้นต่ำ

# LineEdit - ช่องใส่ข้อความ 1 บรรทัด
line_edit = QLineEdit()
line_edit.setPlaceholderText("Enter text...")
line_edit.textChanged.connect(on_text_change)  # เมื่อข้อความเปลี่ยน

# TextEdit - ช่องใส่ข้อความหลายบรรทัด
text_edit = QTextEdit()
text_edit.append("New line")           # เพิ่มบรรทัดใหม่
content = text_edit.toPlainText()      # อ่านข้อความทั้งหมด

# Slider - แถบเลื่อน
slider = QSlider(Qt.Horizontal)        # แนวนอน
slider.setRange(0, 100)                # ช่วงค่า 0-100
slider.setValue(50)                    # ค่าเริ่มต้น
slider.valueChanged.connect(on_value_changed)

# ProgressBar - แถบความคืบหน้า
progress = QProgressBar()
progress.setRange(0, 100)
progress.setValue(75)                  # 75%
```

#### 3. **Layouts (การจัดเรียง) - เฉลย**

```python
# VBoxLayout - จัดเรียงแนวตั้ง
v_layout = QVBoxLayout()
v_layout.addWidget(QLabel("Top"))
v_layout.addWidget(QLabel("Middle"))
v_layout.addWidget(QLabel("Bottom"))

# HBoxLayout - จัดเรียงแนวนอน
h_layout = QHBoxLayout()
h_layout.addWidget(QLabel("Left"))
h_layout.addWidget(QLabel("Center"))
h_layout.addWidget(QLabel("Right"))

# Mixed Layout - ผสมกัน
main_layout = QVBoxLayout()
main_layout.addLayout(h_layout)        # เพิ่ม layout ย่อย
main_layout.addWidget(QLabel("Bottom row"))

# ใช้ Layout กับ Widget
widget = QWidget()
widget.setLayout(main_layout)
```

#### 4. **Signals และ Slots (การสื่อสาร) - เฉลยครบถ้วน**

```python
from PyQt5.QtCore import pyqtSignal

class MyWidget(QWidget):
    # สร้าง Custom Signal
    custom_signal = pyqtSignal(str)    # ส่งข้อความ
    value_changed = pyqtSignal(int)    # ส่งตัวเลข
    
    def __init__(self):
        super().__init__()
        
        # Built-in Signals
        button = QPushButton("Click")
        button.clicked.connect(self.on_button_click)  # เชื่อม signal กับ slot
        
        slider = QSlider(Qt.Horizontal)
        slider.valueChanged.connect(self.on_slider_change)
        
        # เชื่อม Custom Signal
        self.custom_signal.connect(self.handle_custom_signal)
        
    def on_button_click(self):
        """Slot function สำหรับ button"""
        print("Button clicked!")
        
        # ส่ง custom signal
        self.custom_signal.emit("Button was clicked")
        
    def on_slider_change(self, value):
        """Slot function สำหรับ slider"""
        print(f"Slider value: {value}")
        self.value_changed.emit(value)
        
    def handle_custom_signal(self, message):
        """รับ custom signal"""
        print(f"Received: {message}")
```

#### 5. **QTimer - จัดการเวลา (เฉลย)**

```python
class TimerExample(QWidget):
    def __init__(self):
        super().__init__()
        
        # สร้าง Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)  # เมื่อหมดเวลา
        
        self.count = 0
        self.label = QLabel("Count: 0")
        
        # ปุ่มควบคุม
        start_btn = QPushButton("Start")
        stop_btn = QPushButton("Stop")
        
        start_btn.clicked.connect(self.start_timer)
        stop_btn.clicked.connect(self.stop_timer)
        
    def start_timer(self):
        self.timer.start(1000)  # ทุก 1000ms (1 วินาที)
        
    def stop_timer(self):
        self.timer.stop()
        self.count = 0
        self.label.setText("Count: 0")
        
    def update_time(self):
        self.count += 1
        self.label.setText(f"Count: {self.count}")
```

### การติดตั้งและเรียกใช้:

#### ติดตั้ง PyQt5:
```bash
# บน Raspberry Pi OS
sudo apt install python3-pyqt5 python3-pyqt5.qtwidgets python3-pyqt5.qtmultimedia

# หรือใช้ pip (อาจใช้เวลานาน)
pip3 install PyQt5
```

#### เรียกใช้ Lab 0:
```bash
cd Solutions/Lab0    # เวอร์ชันเฉลย
python3 lab0.py
```

### อธิบายโค้ดเฉลย:

#### 1. **BasicWidgetsDemo Class**
```python
def say_hello(self):
    """Slot function เมื่อกดปุ่มสวัสดี"""
    name = self.name_input.text()           # อ่านข้อความจาก LineEdit
    if name:                                # ถ้ามีข้อความ
        message = f"สวัสดี {name}! ยินดีต้อนรับสู่ PyQt5"
        self.output_text.append(message)    # เพิ่มข้อความใน TextEdit
    else:                                   # ถ้าไม่มีข้อความ
        QMessageBox.information(self, "แจ้งเตือน", "กรุณาใส่ชื่อก่อนครับ")

def update_progress(self, value):
    """อัพเดท Progress Bar เมื่อ Slider เปลี่ยน"""
    self.progress_bar.setValue(value)       # ตั้งค่า progress bar
```

#### 2. **SignalsAndSlotsDemo Class**
```python
# สร้าง Custom Signal
custom_signal = pyqtSignal(str)

def emit_custom_signal(self):
    """ส่ง custom signal พร้อมข้อความ"""
    from PyQt5.QtCore import QTime
    message = f"Custom Signal ส่งเมื่อ {QTime.currentTime().toString()}"
    self.custom_signal.emit(message)        # ส่ง signal

def handle_custom_signal(self, message):
    """รับ custom signal"""
    self.signal_output.append(f"📡 รับ Signal: {message}")
```

#### 3. **Timer Implementation**
```python
def toggle_timer(self):
    """เปิด/ปิด Timer"""
    if self.timer.isActive():              # ถ้า timer ทำงานอยู่
        self.timer.stop()                  # หยุด timer
        self.timer_btn.setText("เริ่ม Timer")
        self.timer_count = 0               # รีเซ็ตตัวนับ
    else:                                  # ถ้า timer หยุดอยู่
        self.timer.start(1000)             # เริ่ม timer (1000ms = 1วินาที)
        self.timer_btn.setText("หยุด Timer")

def update_timer(self):
    """ฟังก์ชันที่ถูกเรียกทุกวินาที"""
    self.timer_count += 1                  # เพิ่มตัวนับ
    self.timer_label.setText(f"Timer: {self.timer_count} วินาที")
```

#### 4. **Touch-Friendly Styling**
```python
def apply_touch_styles(self):
    """ใช้ CSS styles ที่เหมาะกับการสัมผัส"""
    
    big_button_style = """
    QPushButton {
        border: 2px solid #3498db;         /* ขอบสีฟ้า */
        border-radius: 8px;                /* มุมโค้ง */
        background: qlineargradient(       /* ไล่สีจากบนลงล่าง */
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #5dade2, stop:1 #3498db);
        color: white;                      /* ข้อความสีขาว */
        font-weight: bold;                 /* ตัวหนา */
        font-size: 14px;                   /* ขนาดตัวอักษร */
        padding: 15px;                     /* ระยะห่างภายใน */
        min-height: 50px;                  /* ความสูงขั้นต่ำ */
        min-width: 120px;                  /* ความกว้างขั้นต่ำ */
    }
    QPushButton:pressed {                  /* เมื่อกดปุ่ม */
        background: #2980b9;               /* สีเข้มขึ้น */
    }
    """
    
    # ใช้ style กับปุ่มทั้งหมด
    for btn in [self.big_btn1, self.big_btn2, self.big_btn3]:
        btn.setStyleSheet(big_button_style)
```

#### 5. **Navigation System**
```python
def show_current_demo(self):
    """แสดง demo ปัจจุบัน"""
    # เคลียร์ demo area เก่า
    if self.demo_area.layout():
        for i in reversed(range(self.demo_area.layout().count())):
            child = self.demo_area.layout().itemAt(i).widget()
            if child:
                child.setParent(None)      # ลบ widget เก่า
    
    # สร้าง demo ใหม่
    demo_name, demo_class = self.demos[self.current_demo]
    demo_widget = demo_class()             # สร้าง instance ใหม่
    
    self.demo_area.layout().addWidget(demo_widget)
    
    # อัพเดท navigation buttons
    self.prev_btn.setEnabled(self.current_demo > 0)
    self.next_btn.setEnabled(self.current_demo < len(self.demos) - 1)
```

### คุณสมบัติครบถ้วนของเฉลย:

#### ✅ **Functional Features:**
- **ทุก Widget ทำงานได้** - Button, Slider, Input fields
- **Signals/Slots ครบ** - Built-in และ Custom signals
- **Timer ใช้งานได้** - นับเวลาแบบ real-time
- **Navigation System** - เปลี่ยน demo ได้
- **Touch-optimized** - ขนาดและ spacing เหมาะสม

#### 💎 **Professional Touches:**
- **CSS Styling** - ปุ่มสวย gradient effects
- **Error Handling** - ตรวจสอบ input ที่ว่าง
- **Visual Feedback** - สี hover และ pressed states
- **Responsive Layout** - ปรับขนาดตามหน้าต่าง
- **Status Updates** - แสดงสถานะที่ชัดเจน

#### 🎯 **Educational Value:**
- **Progressive Learning** - จากง่ายไปยาก
- **Real Examples** - โค้ดที่ใช้จริงได้
- **Best Practices** - รูปแบบการเขียนที่ดี
- **Touch-Ready** - เตรียมพร้อมสำหรับ Raspberry Pi

### การเตรียมพร้อมสำหรับ Labs ถัดไป:

หลังจากจบ Lab 0 เฉลยนี้ คุณจะเข้าใจ:

#### 🎓 **PyQt5 Core Concepts:**
- ✅ Application lifecycle และ event loop
- ✅ Widget hierarchy และ parent-child relationships
- ✅ Layout management ที่มีประสิทธิภาพ
- ✅ Signal-slot mechanism ที่ powerful
- ✅ CSS styling ที่ professional

#### 🔧 **Practical Skills:**
- ✅ การสร้าง responsive UI
- ✅ การจัดการ user input validation
- ✅ การใช้ Timer สำหรับ real-time updates
- ✅ การทำ touch-friendly interface
- ✅ การ debug และ troubleshoot PyQt5 apps

#### 🚀 **Ready for Advanced Labs:**
- **Lab 1**: RTL-SDR Testing (subprocess + PyQt5)
- **Lab 2**: welle.io Integration (QMediaPlayer + threading)
- **Lab 3**: Spectrum Analysis (matplotlib + PyQt5 integration)
- **Lab 4-6**: Complex DAB+ applications

---

**🎉 เฉลยครบถ้วน!** 

คุณได้เรียนรู้:
- 📚 **15 นาที**: DAB+ technology overview
- 🔧 **45 นาที**: PyQt5 hands-on กับเฉลยที่ทำงานได้จริง
- 💡 **Best practices** สำหรับ Raspberry Pi touch applications
- 🎯 **Foundation** ที่แข็งแกร่งสำหรับ Labs ถัดไป

**พร้อมไปต่อ Lab 1 แล้ว!**