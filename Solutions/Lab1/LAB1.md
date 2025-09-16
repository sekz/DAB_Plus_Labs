# LAB 1: การติดตั้งและทดสอบ RTL-SDR - เฉลย

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
cd Solutions/Lab1
python3 lab1.py
```

## อธิบายการเขียนโค้ด (เฉลย)

### 1. คลาส RTLSDRTestThread - Thread หลักสำหรับการทดสอบ:

```python
class RTLSDRTestThread(QThread):
    """Thread สำหรับทดสอบ RTL-SDR แบบครบถ้วน"""
    
    # Signals สำหรับสื่อสารกับ GUI
    test_result = pyqtSignal(str)      # ส่งข้อความผลการทดสอบ
    progress_update = pyqtSignal(int)   # อัพเดท progress bar
    error_occurred = pyqtSignal(str)    # แจ้งเตือนข้อผิดพลาด
    test_completed = pyqtSignal(bool)   # แจ้งเมื่อทดสอบเสร็จ (สำเร็จ/ล้มเหลว)
    
    def run(self):
        """เมธอดหลักที่ทำงานใน background thread"""
        # ทดสอบ 4 ขั้นตอนตามลำดับ:
        # 1. ตรวจสอบ USB connection (25%)
        # 2. ตรวจสอบไดรเวอร์ (50%) 
        # 3. ทดสอบการทำงาน (75%)
        # 4. ดึงข้อมูลอุปกรณ์ (100%)
```

### 2. การตรวจสอบ USB Device:

```python
def check_usb_device(self):
    """ตรวจสอบการเชื่อมต่อ USB ของ RTL-SDR"""
    try:
        # รัน lsusb command
        result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=5)
        
        # ตรวจหา Device IDs ที่รู้จัก
        known_devices = [
            ('0bda:2832', 'RTL2832U DVB-T'),
            ('0bda:2838', 'RTL2838 DVB-T'), 
            ('1d50:604b', 'RTL-SDR Blog V3'),
            ('1209:2832', 'Generic RTL2832U')
        ]
        
        # ค้นหาอุปกรณ์ใน output
        for device_id, device_name in known_devices:
            if device_id in result.stdout.lower():
                return True, f"พบ RTL-SDR device: {device_name} (ID: {device_id})"
        
        return False, "ไม่พบ RTL-SDR device"
        
    except Exception as e:
        return False, f"Error: {str(e)}"
```

### 3. การตรวจสอบไดรเวอร์:

```python
def check_drivers(self):
    """ตรวจสอบการตั้งค่าไดรเวอร์"""
    try:
        issues = []
        warnings = []
        
        # ตรวจสอบไดรเวอร์ที่โหลดอยู่
        result = subprocess.run(['lsmod'], capture_output=True, text=True)
        loaded_modules = result.stdout.lower()
        
        # ตรวจหาไดรเวอร์ที่ขัดแย้ง
        conflicting_drivers = ['dvb_usb_rtl28xxu', 'rtl2832', 'rtl2830']
        loaded_conflicts = [d for d in conflicting_drivers if d in loaded_modules]
        
        if loaded_conflicts:
            warnings.append(f"พบไดรเวอร์ที่อาจขัดแย้ง: {', '.join(loaded_conflicts)}")
        
        # ตรวจสอบ blacklist files
        blacklist_files = ['/etc/modprobe.d/blacklist-rtl.conf']
        if not any(os.path.exists(f) for f in blacklist_files) and loaded_conflicts:
            issues.append("ควรสร้างไฟล์ blacklist สำหรับไดรเวอร์ DVB-T")
        
        # ตรวจสอบ udev rules
        udev_files = ['/etc/udev/rules.d/20-rtlsdr.rules']
        if not any(os.path.exists(f) for f in udev_files):
            issues.append("ไม่พบ udev rules สำหรับ RTL-SDR")
        
        return len(issues) == 0, "; ".join(issues + warnings)
        
    except Exception as e:
        return False, f"Error: {str(e)}"
```

### 4. การทดสอบการทำงาน:

```python
def test_rtlsdr_functionality(self):
    """ทดสอบด้วย rtl_test command"""
    try:
        # รัน rtl_test -t (test mode) 
        result = subprocess.run(['rtl_test', '-t'], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            # ตรวจสอบ output สำหรับ indicators ของความสำเร็จ
            success_indicators = ['found', 'success', 'supported', 'ok']
            error_indicators = ['error', 'failed', 'not found']
            
            output_lower = result.stdout.lower()
            has_success = any(indicator in output_lower for indicator in success_indicators)
            has_error = any(indicator in output_lower for indicator in error_indicators)
            
            if has_success and not has_error:
                return True, f"RTL-SDR ทำงานปกติ\n{result.stdout[:300]}"
            else:
                return False, f"RTL-SDR มีปัญหา:\n{result.stdout[:300]}"
        else:
            return False, f"rtl_test failed: {result.stderr[:300]}"
            
    except subprocess.TimeoutExpired:
        return False, "Timeout: rtl_test ใช้เวลานานเกินไป"
    except FileNotFoundError:
        return False, "ไม่พบ rtl_test - โปรดติดตั้ง rtl-sdr packages"
    except Exception as e:
        return False, f"Error: {str(e)}"
```

### 5. GUI Main Window - การตั้งค่าสำหรับหน้าจอสัมผัส:

```python
def setup_touch_interface(self):
    """ปรับ UI สำหรับหน้าจอสัมผัส 7 นิ้ว"""
    
    # ตั้งค่า font ขนาดใหญ่
    font = QFont()
    font.setPointSize(12)
    self.setFont(font)
    
    # CSS สำหรับปุ่มที่เหมาะกับการสัมผัส
    button_style = """
        QPushButton {
            border: 2px solid #34495e;
            border-radius: 8px;
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #3498db, stop: 1 #2980b9);
            color: white;
            font-weight: bold;
            font-size: 14px;
            padding: 8px;
            min-height: 50px;    /* ปุ่มสูงพอสำหรับนิ้ว */
            min-width: 120px;    /* ปุ่มกว้างพอสำหรับข้อความ */
        }
        QPushButton:pressed {
            background-color: #2980b9;  /* สีเข้มขึ้นเมื่อกด */
        }
        QPushButton:disabled {
            background-color: #95a5a6;  /* สีเทาเมื่อปิดใช้งาน */
        }
    """
    
    # ใช้ style กับปุ่มทั้งหมด
    for button in self.findChildren(QPushButton):
        button.setStyleSheet(button_style)
        button.setMinimumSize(120, 60)
```

### 6. การจัดการ Threading และ Signals:

```python
def setup_connections(self):
    """เชื่อม signals และ slots"""
    # ปุ่มต่างๆ
    self.check_device_btn.clicked.connect(self.start_device_check)
    self.run_all_btn.clicked.connect(self.run_all_tests)
    
    # เมื่อสร้าง thread แล้วเชื่อม signals:
    self.test_thread.test_result.connect(self.update_test_results)
    self.test_thread.progress_update.connect(self.update_progress)
    self.test_thread.error_occurred.connect(self.handle_test_error)
    self.test_thread.test_completed.connect(self.on_test_completed)

def run_all_tests(self):
    """รันการทดสอบทั้งหมด"""
    if self.test_thread and self.test_thread.isRunning():
        QMessageBox.warning(self, "คำเตือน", "การทดสอบกำลังดำเนินการอยู่")
        return
    
    # ปิดปุ่มระหว่างทดสอบ
    self.set_buttons_enabled(False)
    
    # สร้างและเริ่ม thread
    self.test_thread = RTLSDRTestThread()
    self.setup_thread_connections()  # เชื่อม signals
    self.test_thread.start()
```

### 7. Helper Functions:

```python
def run_command(command, timeout=10):
    """รันคำสั่ง shell อย่างปลอดภัย"""
    try:
        result = subprocess.run(
            command if isinstance(command, list) else command.split(),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False  # ไม่ raise exception เมื่อ returncode != 0
        )
        return result.returncode, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        return -1, "", f"Timeout after {timeout} seconds"
    except FileNotFoundError:
        return -1, "", f"Command not found: {command[0]}"
    except Exception as e:
        return -1, "", f"Error: {str(e)}"

def check_system_requirements():
    """ตรวจสอบความต้องการของระบบก่อนเริ่ม"""
    issues = []
    
    # ตรวจสอบ Python version
    if sys.version_info < (3, 7):
        issues.append("Python version ต่ำเกินไป")
    
    # ตรวจสอบ PyQt5
    try:
        from PyQt5.QtCore import QT_VERSION_STR
    except ImportError:
        issues.append("PyQt5 ไม่ได้ติดตั้ง")
    
    # ตรวจสอบ rtl_test
    if run_command(['which', 'rtl_test'])[0] != 0:
        issues.append("rtl_test ไม่พบ - ติดตั้ง rtl-sdr packages")
    
    return len(issues) == 0, issues
```

### 8. การจัดการข้อผิดพลาดและ Logging:

```python
import logging

# ตั้งค่า logging ที่จุดเริ่มต้น
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def handle_test_error(self, error_message):
    """จัดการข้อผิดพลาด"""
    self.results_text.append(f" Error: {error_message}")
    logger.error(f"Test error: {error_message}")
    self.set_buttons_enabled(True)  # เปิดปุ่มกลับมา
    QApplication.beep()  # เสียงแจ้งเตือน

def save_results(self):
    """บันทึกผลการทดสอบ"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"rtlsdr_test_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("RTL-SDR Test Results\n")
            f.write("=" * 50 + "\n")
            f.write(f"Date: {datetime.now()}\n\n")
            f.write(self.results_text.toPlainText())
        
        QMessageBox.information(self, "สำเร็จ", f"บันทึกแล้ว: {filename}")
        
    except Exception as e:
        QMessageBox.critical(self, "ข้อผิดพลาด", f"ไม่สามารถบันทึก: {str(e)}")
```

## ผลลัพธ์ที่คาดหวัง

เมื่อรันเฉลยแล้วจะได้:

### 1. GUI Application ที่สมบูรณ์:
- หน้าต่างขนาด 800x600 เหมาะกับหน้าจอ 7 นิ้ว
- ปุ่มขนาดใหญ่ (120x60px) เหมาะกับการสัมผัส
- การแสดงผลแบบ real-time ใน text area
- Progress bar แสดงความคืบหน้า 0-100%
- ระบบ threading ที่ไม่ทำให้ GUI ค้าง

### 2. การทดสอบครบถ้วน:
```
 เริ่มการทดสอบครบชุด - 14:30:45
============================================================

 ตรวจสอบการเชื่อมต่อ USB...
 พบ RTL-SDR device: RTL2832U DVB-T (ID: 0bda:2832)

 ตรวจสอบไดรเวอร์...
️ พบไดรเวอร์ที่อาจขัดแย้ง: dvb_usb_rtl28xxu

 ทดสอบการทำงานพื้นฐาน...
 RTL-SDR ทำงานปกติ
ข้อมูล tuner:
  Tuner type: Rafael Micro R820T2

 ดึงข้อมูลอุปกรณ์...
 ข้อมูล RTL-SDR device:
  Vendor: Realtek
  Product: RTL2832U
  Tuner Type: Rafael Micro R820T2

=== สรุปผลการทดสอบ ===
ผ่าน: 4/4 ข้อ
 RTL-SDR พร้อมใช้งานแล้ว!
```

### 3. ไฟล์ที่สร้างขึ้น:
- `rtlsdr_test_20241208_143045.txt`: รายงานผลการทดสอบ
- Console logs ใน terminal
- Error logs (ถ้ามี) ใน system log

### 4. คุณสมบัติพิเศษ:
- **Threading**: การทดสอบทำงานใน background ไม่บล็อก GUI
- **Error Handling**: จัดการข้อผิดพลาดครบถ้วน พร้อมข้อความภาษาไทย
- **Touch-Friendly**: ปุ่มและ font ขนาดใหญ่เหมาะกับหน้าจอสัมผัส
- **Progress Tracking**: แสดงความคืบหน้าแบบ real-time
- **Result Export**: บันทึกผลลงไฟล์พร้อม timestamp
- **System Validation**: ตรวจสอบระบบก่อนเริ่มแล็บ

## การแก้ไขปัญหา (เพิ่มเติม)

### ปัญหา Threading และ GUI:

```bash
# ถ้า GUI ค้างขณะทดสอบ
# ตรวจสอบใน code ว่าใช้ QThread ถูกต้อง
# และมี proper signal/slot connections

# ถ้า progress bar ไม่อัพเดท
# ตรวจสอบ emit progress_update signal ใน thread
```

### ปัญหาการบันทึกไฟล์:

```bash
# ตรวจสอบ permissions ในโฟลเดอร์ที่บันทึก
ls -la ./

# เปลี่ยน directory สำหรับบันทึก
cd /tmp
python3 lab1.py
```

### การปรับแต่งสำหรับหน้าจอขนาดต่าง:

```python
# ใน setup_touch_interface() ปรับค่า:
font.setPointSize(10)  # ลดลงสำหรับหน้าจอเล็ก
button.setMinimumSize(100, 50)  # ลดขนาดปุ่ม

# หรือเพิ่มสำหรับหน้าจอใหญ่:
font.setPointSize(16)
button.setMinimumSize(150, 80)
```

## คำถามทบทวน (พร้อมเฉลย)

1. **เหตุใดต้องใช้ QThread สำหรับการทดสอบ RTL-SDR?**
   - **เฉลย**: เพราะคำสั่ง rtl_test ใช้เวลา 10-15 วินาที หาก run ใน main thread จะทำให้ GUI ค้าง ผู้ใช้กดปุ่มไม่ได้

2. **Signal และ Slot ใน PyQt5 ทำงานอย่างไร?**
   - **เฉลย**: Signal คือการแจ้งเตือน, Slot คือฟังก์ชันที่รับ เช่น test_result.emit("ข้อความ") จะไปเรียก update_test_results("ข้อความ")

3. **subprocess.run() มีข้อดีกว่า os.system() อย่างไร?**
   - **เฉลย**: ควบคุม timeout ได้, จับ output แยก stdout/stderr, ปลอดภัยกว่า (ไม่ผ่าน shell), จัดการ error ได้ดี

4. **การ blacklist DVB-T drivers ทำงานอย่างไร?**
   - **เฉลย**: ไฟล์ใน /etc/modprobe.d/ จะป้องกันการโหลด kernel modules ที่ระบุ, ทำให้ RTL-SDR ใช้ generic drivers แทน

5. **udev rules ช่วยอะไรในการใช้ RTL-SDR?**
   - **เฉลย**: กำหนด permissions ให้ user ปกติเข้าถึง RTL-SDR device ได้ โดยไม่ต้องใช้ sudo

6. **วิธีการ debug เมื่อ rtl_test ไม่ทำงาน?**
   - **เฉลย**: ตรวจสอบตามลำดับ: lsusb (device มีไหม) → lsmod (driver ขัดแย้งไหม) → dmesg (kernel message) → strace rtl_test (system calls)

---

**หมายเหตุ**: เฉลยนี้เป็นโค้ดที่พร้อมใช้งานได้ทันที และอธิบายหลักการครบถ้วน เหมาะสำหรับการเรียนรู้และเป็นตัวอย่างสำหรับ Labs ถัดไป