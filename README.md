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
- **Jupyter Notebook**: `lab1_rtlsdr_connect.ipynb` - ทดสอบการเชื่อมต่อ RTL-SDR ผ่าน rtl_tcp

### Lab 2: การใช้งาน welle.io ผ่าน Python
- เรียนรู้การควบคุม welle.io เพื่อรับสัญญาณ DAB+
- สแกนหาสถานี DAB+ และเล่นเสียง
- จัดการข้อมูลเมทาดาต้าและสไลด์โชว์

### Lab 3: Learning DAB+ with RTL-SDR (Progressive Development) ✅ COMPLETED
- **Progressive Development**: เรียนรู้ DAB+ แบบ step-by-step ใน 5 phases
- **Phase 1a**: lab3_1a.py - RTL-SDR I/Q data acquisition (pyrtlsdr)
- **Phase 1b**: lab3_1b.py - Network RTL-SDR client (rtl_tcp)
- **Phase 2**: lab3_2.py - ETI stream processing (eti-cmdline)
- **Phase 3**: lab3_3.py - ETI parser และ service extraction
- **Phase 4**: lab3_4.py - Audio playback และ slideshow
- **Phase 5**: lab3_5.py - Complete PyQt5 GUI application
- **Google Colab Notebooks** 📓:
  - `Lab3_Phase1_IQ_Acquisition_Colab.ipynb` - I/Q data acquisition และ spectrum analysis
  - `Lab3_Phase2_ETI_Processing_Colab.ipynb` - ETI stream processing และ parsing
  - ดูคู่มือใน `README_Colab_Notebooks.md`
- **เอกสารเปรียบเทียบ**: `Lab3_SDR_vs_SI4684.md` - เปรียบเทียบ RTL-SDR กับ SI4684 chip

### Lab 4: สร้าง DAB+ Station Scanner (การบ้าน - 3-4 ชั่วโมง)
- สร้างแอปพลิเคชันสแกนสถานี DAB+ อย่างง่าย
- ใช้ Lab 3 pipeline สำหรับหาสถานี
- เก็บข้อมูลสถานีในฐานข้อมูล SQLite พื้นฐาน

### Lab 5: สร้าง DAB+ Program Recorder (การบ้าน - 3-4 ชั่วโมง)
- สร้างระบบบันทึกรายการ DAB+ อย่างง่าย
- ใช้ Lab 3 pipeline สำหรับบันทึกเสียง
- จัดการตารางเวลาการบันทึกพื้นฐาน

### Lab 6: สร้าง DAB+ Signal Analyzer (การบ้าน - 3-4 ชั่วโมง)
- สร้างเครื่องมือวิเคราะห์สัญญาณ DAB+ อย่างง่าย
- ใช้ Lab 3 pipeline สำหรับวิเคราะห์สัญญาณ
- แสดงค่า SNR, RSSI, BER แบบ real-time

## 📓 รองรับ Google Colab

Lab 1 และ Lab 3 มี Jupyter Notebooks ที่สามารถรันบน Google Colab ได้:
- เชื่อมต่อกับ RTL-SDR บน Raspberry Pi ผ่าน rtl_tcp และ FRP tunnel
- ไม่ต้องติดตั้ง software บนเครื่องตัวเอง
- เหมาะสำหรับการเรียนรู้และทดลอง
- ดูคู่มือใน `Labs/Lab3/README_Colab_Notebooks.md`

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