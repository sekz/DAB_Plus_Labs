# LAB 1: การติดตั้งและทดสอบ RTL-SDR

## วัตถุประสงค์
- ทดสอบการเชื่อมต่อและการทำงานของ RTL-SDR dongle บน Raspberry Pi
- ตรวจสอบการรู้จำอุปกรณ์และแก้ไขปัญหาไดรเวอร์ DVB-T
- เขียนฟังก์ชัน Python ทดสอบพื้นฐานผ่าน PyQt5 GUI
- เรียนรู้การใช้งาน RTL-SDR command line tools

## ความรู้พื้นฐานที่ต้องมี
- การใช้งาน Linux command line พื้นฐาน
- Python programming และ PyQt5 GUI
- ความเข้าใจเบื้องต้นเกี่ยวกับ Software Defined Radio (SDR)
- การแก้ไขปัญหา USB devices บน Linux

## อุปกรณ์ที่ใช้
- **Raspberry Pi 4** (4GB RAM ขึ้นไป แนะนำ)
- **RTL-SDR V4 dongle** หรือ compatible device
- **หน้าจอสัมผัส HDMI 7"** (อุปกรณ์เสริม)
- **หูฟัง 3.5mm** สำหรับฟังเสียง
- **เสาอากาศ** ที่เหมาะกับความถี่ DAB/FM
- **สายแปลง USB extension** (แนะนำเพื่อลดสัญญาณรบกวน)

## การเตรียมระบบ

### คำสั่งติดตั้ง Dependencies ทั้งหมด:

```bash
# อัพเดทระบบก่อน
sudo apt update && sudo apt upgrade -y

# ติดตั้ง Python และ PyQt5
sudo apt install -y python3 python3-pip python3-dev
sudo apt install -y python3-pyqt5 python3-pyqt5.qtwidgets python3-pyqt5.qtcore python3-pyqt5.qtgui

# ติดตั้ง RTL-SDR tools และ libraries
sudo apt install -y rtl-sdr librtlsdr0 librtlsdr-dev

# ติดตั้ง utilities ที่จำเป็น
sudo apt install -y usbutils cmake build-essential git

# ติดตั้ง Python packages เพิ่มเติม
pip3 install pyrtlsdr
```

### ตั้งค่า RTL-SDR udev rules:

```bash
# สร้างไฟล์ udev rules
sudo nano /etc/udev/rules.d/20-rtlsdr.rules
```

เพิ่มเนื้อหาในไฟล์:
```
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2832", GROUP="adm", MODE="0666", SYMLINK+="rtl_sdr"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", GROUP="adm", MODE="0666", SYMLINK+="rtl_sdr"
SUBSYSTEM=="usb", ATTRS{idVendor}=="1d50", ATTRS{idProduct}=="604b", GROUP="adm", MODE="0666", SYMLINK+="rtl_sdr"
SUBSYSTEM=="usb", ATTRS{idVendor}=="1209", ATTRS{idProduct}=="2832", GROUP="adm", MODE="0666", SYMLINK+="rtl_sdr"
```

### Blacklist ไดรเวอร์ DVB-T ที่ขัดแย้ง:

```bash
# สร้างไฟล์ blacklist
sudo nano /etc/modprobe.d/blacklist-rtl.conf
```

เพิ่มเนื้อหา:
```
blacklist dvb_usb_rtl28xxu
blacklist rtl2832
blacklist rtl2830
blacklist dvb_usb_rtl2832u
```

### เพิ่ม user ใน group ที่จำเป็น:

```bash
sudo usermod -a -G plugdev,dialout $USER
```

### Reload udev rules และรีสตาร์ท:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
sudo reboot
```

## ขั้นตอนการทำงาน

### 1. ตรวจสอบการเชื่อมต่อ USB

เสียบ RTL-SDR dongle แล้วตรวจสอบ:

```bash
# ตรวจสอบการรู้จำอุปกรณ์
lsusb | grep -i rtl

# ตัวอย่างผลลัพธ์ที่ถูกต้อง:
# Bus 001 Device 004: ID 0bda:2832 Realtek Semiconductor Corp. RTL2832U DVB-T
```

### 2. ทดสอบการทำงานพื้นฐาน

```bash
# ทดสอบ RTL-SDR
rtl_test -t

# ทดสอบการอ่านข้อมูล (กด Ctrl+C เพื่อหยุด)
rtl_test -s 2048000 -d 0
```

### 3. เรียกใช้งาน Lab GUI

```bash
cd Labs/Lab1
python3 lab1.py
```

## การเขียนโค้ด

### ส่วนที่ต้องเติมใน `lab1.py`:

#### 1. คลาส RTLSDRTestThread:

```python
class RTLSDRTestThread(QThread):
    test_result = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    error_occurred = pyqtSignal(str)
    
    def run(self):
        # เติมโค้ดการทดสอบตามลำดับ:
        # 1. ตรวจสอบ USB connection
        # 2. ทดสอบ rtl_test -t
        # 3. ตรวจสอบไดรเวอร์
        pass
```

#### 2. การตรวจสอบอุปกรณ์ USB:

```python
def check_usb_device(self):
    try:
        # ใช้ subprocess เรียก lsusb
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        if 'RTL' in result.stdout or '0bda:2832' in result.stdout:
            return True, "RTL-SDR device พบแล้ว"
        else:
            return False, "ไม่พบ RTL-SDR device"
    except Exception as e:
        return False, f"Error: {str(e)}"
```

#### 3. การทดสอบการทำงาน:

```python
def test_rtlsdr_functionality(self):
    try:
        # รัน rtl_test -t และจับผลลัพธ์
        result = subprocess.run(['rtl_test', '-t'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return True, f"RTL-SDR ทำงานปกติ\\n{result.stdout}"
        else:
            return False, f"RTL-SDR มีปัญหา\\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "Timeout: การทดสอบใช้เวลานานเกินไป"
    except Exception as e:
        return False, f"Error: {str(e)}"
```

#### 4. UI Setup สำหรับหน้าจอสัมผัส:

```python
def setup_touch_interface(self):
    # ตั้งค่า font ขนาดใหญ่
    font = QFont()
    font.setPointSize(14)
    self.setFont(font)
    
    # ตั้งค่าขนาดปุ่มให้เหมาะกับการสัมผัส
    for button in self.findChildren(QPushButton):
        button.setMinimumSize(120, 60)
        button.setStyleSheet("""
            QPushButton {
                border: 2px solid #8f8f91;
                border-radius: 6px;
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #f6f7fa, stop: 1 #dadbde);
            }
            QPushButton:pressed {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #dadbde, stop: 1 #f6f7fa);
            }
        """)
```

#### 5. Main Window Setup:

```python
def setup_ui(self):
    central_widget = QWidget()
    self.setCentralWidget(central_widget)
    
    # สร้าง layout หลัก
    main_layout = QVBoxLayout(central_widget)
    
    # ชื่อแล็บ
    title_label = QLabel("LAB 1: การติดตั้งและทดสอบ RTL-SDR")
    title_label.setAlignment(Qt.AlignCenter)
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
    main_layout.addWidget(title_label)
    
    # ปุ่มทดสอบ
    button_layout = QHBoxLayout()
    self.check_device_btn = QPushButton("ตรวจสอบอุปกรณ์")
    self.test_function_btn = QPushButton("ทดสอบการทำงาน")
    self.check_driver_btn = QPushButton("ตรวจสอบไดรเวอร์")
    self.run_all_btn = QPushButton("รันทดสอบทั้งหมด")
    
    # เพิ่มปุ่มลง layout...
    
    # พื้นที่แสดงผล
    self.results_text = QTextEdit()
    self.results_text.setReadOnly(True)
    main_layout.addWidget(self.results_text)
    
    # Progress bar
    self.progress_bar = QProgressBar()
    main_layout.addWidget(self.progress_bar)
```

### คำแนะนำการเขียน:

1. **ใช้ subprocess** สำหรับเรียก command line tools
2. **ใช้ QThread** เพื่อไม่ให้ GUI ค้าง
3. **จัดการ errors** ด้วย try-except
4. **ใช้ signals/slots** สำหรับสื่อสารระหว่าง threads
5. **เพิ่ม logging** เพื่อติดตาม debugging

## ผลลัพธ์ที่คาดหวัง

เมื่อรันแล็บแล้วจะได้:

### 1. GUI Application ที่มี:
- ปุ่มทดสอบอุปกรณ์ต่างๆ ขนาดใหญ่เหมาะกับหน้าจอสัมผัส
- พื้นที่แสดงผลการทดสอบแบบ real-time
- Progress bar แสดงความคืบหน้า
- การทำงานแบบ multi-threading

### 2. ผลการทดสอบที่แสดง:
```
=== ผลการทดสอบ RTL-SDR ===
✓ พบ RTL-SDR device (ID: 0bda:2832)
✓ ไดรเวอร์โหลดสำเร็จ
✓ การทดสอบ rtl_test ผ่าน
✓ การอ่านข้อมูลสัญญาณปกติ
✓ ระบบพร้อมใช้งาน DAB+
```

### 3. ไฟล์ log และรายงาน:
- `test_results.txt`: ผลการทดสอบละเอียด
- `rtlsdr_info.txt`: ข้อมูลอุปกรณ์
- Console logs สำหรับ debugging

## การแก้ไขปัญหา

### ปัญหา 1: ไม่พบ RTL-SDR device

**อาการ**: `lsusb` ไม่แสดง RTL-SDR

**วิธีแก้**:
```bash
# ตรวจสอบการเสียบ USB
lsusb

# ลองเสียบ port อื่น
# ตรวจสอบสายแปลง USB

# ตรวจสอบ power supply ของ Pi
vcgencmd get_throttled
```

### ปัญหา 2: rtl_test ไม่ทำงาน

**อาการ**: `rtl_test -t` error

**วิธีแก้**:
```bash
# ตรวจสอบไดรเวอร์ที่โหลด
lsmod | grep dvb

# ถ้ามี DVB drivers โหลดอยู่ ให้ unload:
sudo modprobe -r dvb_usb_rtl28xxu
sudo modprobe -r rtl2832
sudo modprobe -r rtl2830

# ลอง rtl_test อีกครั้ง
rtl_test -t
```

### ปัญหา 3: Permission denied

**อาการ**: Access denied เมื่อใช้ RTL-SDR

**วิธีแก้**:
```bash
# ตรวจสอบ group membership
groups $USER

# เพิ่ม user ใน plugdev group
sudo usermod -a -G plugdev $USER

# ตรวจสอบ udev rules
ls -la /etc/udev/rules.d/*rtl*

# Restart udev
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### ปัญหา 4: GUI ไม่แสดงบนหน้าจอสัมผัส

**อาการ**: PyQt5 app ไม่ปรากฏ

**วิธีแก้**:
```bash
# ตั้งค่า DISPLAY
export DISPLAY=:0

# ตรวจสอบ X11
echo $DISPLAY
xrandr

# รัน GUI ด้วย
DISPLAY=:0 python3 lab1.py
```

### ปัญหา 5: หน้าจอสัมผัสไม่ตอบสนอง

**วิธีแก้**:
```bash
# ตรวจสอบ touchscreen driver
dmesg | grep -i touch

# ตั้งค่าใน /boot/config.txt:
# hdmi_group=2
# hdmi_mode=87
# hdmi_cvt 1024 600 60 6 0 0 0

# Calibrate touchscreen
sudo apt install xinput-calibrator
xinput_calibrator
```

## คำถามทบทวน

1. **RTL-SDR คืออะไร และทำงานอย่างไร?**
   - ตอบ: Software Defined Radio ที่แปลงสัญญาณ RF เป็นดิจิทัล

2. **ทำไมต้อง blacklist DVB-T drivers?**
   - ตอบ: เพื่อป้องกันความขัดแย้งกับ RTL-SDR generic drivers

3. **การใช้ QThread มีประโยชน์อย่างไร?**
   - ตอบ: ป้องกันการค้าง GUI ระหว่างประมวลผลที่ใช้เวลานาน

4. **udev rules ทำหน้าที่อะไร?**
   - ตอบ: กำหนด permissions และ device nodes เมื่อเสียบ USB

5. **วิธีการดีบัก RTL-SDR ปัญหาเบื้องต้น?**
   - ตอบ: ตรวจสอบ lsusb, lsmod, dmesg และ rtl_test

---

**หมายเหตุ**: Lab นี้เป็นพื้นฐานสำหรับ Labs ถัดไป ต้องทำให้สำเร็จก่อนไปต่อ