# DAB+ Labs สำหรับ Raspberry Pi

โครงการแล็บการเรียนรู้ DAB+ (Digital Audio Broadcasting Plus) โดยใช้ Raspberry Pi และ RTL-SDR

## 📋 รายการแล็บทั้งหมด

### Lab 0: Introduction to DAB+ และ PyQt5 (เตรียมพร้อม)
- แนะนำเทคโนโลยี DAB+ และข้อดีเมื่อเทียบกับ FM
- เรียนรู้พื้นฐาน PyQt5 GUI programming ใน 1 ชั่วโมง
- การสร้าง Touch-Friendly UI สำหรับหน้าจอสัมผัส 7"
- ความรู้เบื้องต้นเกี่ยวกับ RTL-SDR และ welle.io

### Lab 1: การติดตั้งและทดสอบ RTL-SDR
- ทดสอบการเชื่อมต่อและการทำงานของ RTL-SDR dongle บน Raspberry Pi
- ตรวจสอบการรู้จำอุปกรณ์และแก้ไขปัญหาไดรเวอร์
- เขียนฟังก์ชัน Python ทดสอบพื้นฐาน

### Lab 2: การใช้งาน welle.io ผ่าน Python
- เรียนรู้การควบคุม welle.io เพื่อรับสัญญาณ DAB+
- สแกนหาสถานี DAB+ และเล่นเสียง
- จัดการข้อมูลเมทาดาต้าและสไลด์โชว์

### Lab 3: การควบคุม RTL-SDR โดยตรงด้วย pyrtlsdr
- เข้าถึงและควบคุม RTL-SDR โดยตรงผ่าน Python
- การอ่านและวิเคราะห์สัญญาณความถี่
- สร้างกราฟแสดงผลสเปกตรัม

### Lab 4: สร้าง DAB+ Station Scanner
- พัฒนาแอปพลิเคชันสแกนและติดตามสถานี DAB+
- ติดตามคุณภาพสัญญาณแบบเรียลไทม์
- สร้าง GUI ด้วย PyQt5 สำหรับหน้าจอสัมผัส

### Lab 5: สร้าง DAB+ Program Recorder
- พัฒนาระบบบันทึกรายการ DAB+ ตามตารางเวลา
- จัดการการบันทึกแบบแมนนวลและอัตโนมัติ
- จัดเก็บไฟล์เสียง สไลด์ และเมทาดาต้า

### Lab 6: สร้าง DAB+ Signal Analyzer
- พัฒนาเครื่องมือวิเคราะห์สัญญาณ DAB+ อย่างละเอียด
- วิเคราะห์คุณภาพสัญญาณ และสเปกตรัมความถี่
- สร้างกราฟและรายงานการวิเคราะห์

## 🔧 ข้อกำหนดระบบ

### Hardware ที่จำเป็น:
- **Raspberry Pi 4** (แนะนำ 4GB RAM ขึ้นไป)
- **RTL-SDR V4 dongle** หรือเทียบเท่า
- **หน้าจอสัมผัส HDMI 7 นิ้ว** (อุปกรณ์เสริม)
- **หูฟัง 3.5mm** สำหรับฟังเสียง
- **เสาอากาศ DAB/FM** สำหรับรับสัญญาณ

### Software ที่จำเป็น:
- **Raspberry Pi OS Bookworm** (64-bit แนะนำ)
- **Python 3.11+**
- **PyQt5** สำหรับ GUI
- **RTL-SDR drivers และ libraries**
- **welle.io** สำหรับ DAB+ decoding

## 🚀 การติดตั้ง

### วิธีที่ 1: ใช้สคริปต์อัตโนมัติ (แนะนำ)

```bash
# โคลนโครงการ
git clone <repository-url> DAB_Plus_Labs
cd DAB_Plus_Labs

# รันสคริปต์ติดตั้งอัตโนมัติ
chmod +x install_deps.sh
sudo ./install_deps.sh

# ติดตั้ง Python packages
pip install -r requirements.txt
```

### วิธีที่ 2: ติดตั้งแมนนวล

```bash
# อัพเดทระบบ
sudo apt update && sudo apt upgrade -y

# ติดตั้ง dependencies หลัก
sudo apt install -y python3-pyqt5 python3-pyqt5.qtmultimedia \
    rtl-sdr librtlsdr0 librtlsdr-dev \
    cmake build-essential git \
    python3-matplotlib python3-scipy python3-numpy

# ติดตั้ง welle.io
sudo apt install -y qt5-qmake qtbase5-dev qtchooser \
    qtmultimedia5-dev libqt5multimedia5-plugins \
    libfaad-dev libmpg123-dev libfftw3-dev
    
# คอมไพล์ welle.io จากซอร์ส (ถ้าไม่มีใน apt)
git clone https://github.com/AlbrechtL/welle.io.git
cd welle.io && mkdir build && cd build
cmake .. && make -j4
sudo make install
```

## 📱 การรองรับหน้าจอสัมผัส

โครงการนี้รองรับหน้าจอสัมผัส 7 นิ้วด้วย:
- ปุ่มขนาดใหญ่ที่เหมาะสำหรับการสัมผัส
- Font ขนาดใหญ่เพื่อการมองเห็นที่ชัดเจน
- การจัดเรียง UI ที่เหมาะกับหน้าจอเล็ก
- รองรับ touch events และ gestures

### การตั้งค่าหน้าจอสัมผัส:

```bash
# ตั้งค่าความละเอียดใน /boot/config.txt
echo "hdmi_group=2" | sudo tee -a /boot/config.txt
echo "hdmi_mode=87" | sudo tee -a /boot/config.txt
echo "hdmi_cvt 1024 600 60 6 0 0 0" | sudo tee -a /boot/config.txt

# รีสตาร์ทระบบ
sudo reboot
```

## 🔊 การตั้งค่าเสียง

```bash
# ตั้งให้เสียงออกทาง 3.5mm jack
sudo raspi-config nonint do_audio 1

# ทดสอบเสียง
speaker-test -t wav -c 2
```

## 📚 วิธีใช้งาน

### สำหรับผู้เรียน (ใช้โฟลเดอร์ Labs/):
1. เปิดไฟล์ `Labs/Lab[X]/lab[X].py`
2. อ่านคู่มือใน `Labs/Lab[X]/LAB[X].md`
3. เติมโค้ดในส่วนที่มี TODO comments
4. ทดสอบการทำงานตามคู่มือ

### สำหรับผู้สอน (ใช้โฟลเดอร์ Solutions/):
- ไฟล์ใน `Solutions/` เป็นเฉลยครบถ้วน
- สามารถใช้เป็นตัวอย่างหรือเฉลยให้ผู้เรียน

### การรันแล็บแต่ละตัว:

```bash
# Lab 0: PyQt5 Introduction (เริ่มต้นที่นี่)
cd Labs/Lab0
python3 lab0.py

# Lab 1: RTL-SDR Testing
cd Labs/Lab1
python3 lab1.py

# Lab 2: Welle.io Integration  
cd Labs/Lab2
python3 lab2.py

# ฯลฯ สำหรับแล็บอื่นๆ
```

## 🔍 การแก้ไขปัญหาเบื้องต้น

### ปัญหา RTL-SDR ไม่รู้จำอุปกรณ์:
```bash
# ตรวจสอบการเชื่อมต่อ USB
lsusb | grep RTL

# ตรวจสอบไดรเวอร์
rtl_test -t
```

### ปัญหา welle.io ไม่ทำงาน:
```bash
# ตรวจสอบการติดตั้ง
which welle-io

# ทดสอบการทำงาน
welle-io --help
```

### ปัญหา PyQt5 GUI ไม่แสดง:
```bash
# ตรวจสอบ X11 forwarding (ถ้าใช้ SSH)
echo $DISPLAY

# ตั้งค่า DISPLAY variable
export DISPLAY=:0.0
```

## 📈 การพัฒนาเพิ่มเติม

หลังจากทำแล็บทั้ง 6 แล็บแล้ว สามารถพัฒนาต่อได้ด้วย:
- การเชื่อมต่อกับ web API สำหรับข้อมูลสถานี
- การสร้าง mobile app ควบคุมผ่าน HTTP
- การบันทึกข้อมูลลง database
- การสร้าง streaming server

## 🤝 การสนับสนุน

หากพบปัญหาหรือต้องการความช่วยเหลือ:
1. ตรวจสอบไฟล์ LAB[X].md ในแต่ละแล็บ
2. ดู Solutions/ สำหรับตัวอย่างโค้ดที่ใช้งานได้
3. ตรวจสอบ logs และ error messages
4. ทดสอบ hardware connections

## 📄 License

โครงการนี้ใช้ MIT License - ดูรายละเอียดใน LICENSE file

---

**หมายเหตุ**: โครงการนี้พัฒนาขึ้นเพื่อการศึกษาเรียนรู้เท่านั้น ไม่ใช่เพื่อการใช้งานเชิงพาณิชย์