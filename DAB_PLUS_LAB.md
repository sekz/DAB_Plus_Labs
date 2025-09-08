# คู่มือแล็บ DAB+ สำหรับ Raspberry Pi

<div align="center">

# 📻 DAB+ Labs สำหรับ Raspberry Pi
## คู่มือการเรียนรู้ Digital Audio Broadcasting Plus
### พร้อม RTL-SDR และ PyQt5

---

**เวอร์ชัน**: 1.0  
**วันที่**: ธันวาคม 2024  
**ผู้เขียน**: DAB+ Learning Project  
**เป้าหมาย**: Raspberry Pi OS Bookworm + RTL-SDR V4

---

</div>

## 📋 สารบัญ

### [📖 ภาพรวมโครงการ](#overview)
### [🔧 ข้อกำหนดระบบ](#requirements)  
### [🚀 การติดตั้ง](#installation)
### [📚 รายการแล็บทั้งหมด](#labs)
### [🔍 การแก้ไขปัญหา](#troubleshooting)
### [📞 การสนับสนุน](#support)

---

<a name="overview"></a>
## 📖 ภาพรวมโครงการ

โครงการ DAB+ Labs เป็นชุดแล็บการเรียนรู้ที่ครอบคลุมเทคโนโลยี **Digital Audio Broadcasting Plus (DAB+)** โดยใช้:

- 🐧 **Raspberry Pi 4** เป็นแพลตฟอร์มหลัก
- 📻 **RTL-SDR V4** สำหรับรับสัญญาณ RF
- 🖥️ **PyQt5** สำหรับสร้าง GUI ที่เหมาะกับหน้าจอสัมผัส
- 🔧 **welle.io** สำหรับถอดรหัส DAB+

### 🎯 วัตถุประสงค์:
1. เรียนรู้เทคโนโลยี DAB+ จากพื้นฐานจนถึงขั้นสูง
2. ฝึกทักษะการเขียนโปรแกรม Python และ GUI
3. เข้าใจการทำงานของ Software Defined Radio (SDR)
4. สร้างแอปพลิเคชันที่ใช้งานได้จริงบน Raspberry Pi

---

<a name="requirements"></a>
## 🔧 ข้อกำหนดระบบ

### Hardware ที่จำเป็น:
- **Raspberry Pi 4** (4GB RAM ขึ้นไป แนะนำ)
- **RTL-SDR V4 dongle** หรือเทียบเท่า
- **MicroSD Card** 32GB+ (Class 10)
- **หน้าจอสัมผัส HDMI 7"** (อุปกรณ์เสริม)
- **หูฟัง 3.5mm** สำหรับฟังเสียง
- **เสาอากาศ DAB/FM** สำหรับรับสัญญาณ

### Software ที่จำเป็น:
- **Raspberry Pi OS Bookworm** (64-bit แนะนำ)
- **Python 3.11+**
- **PyQt5** สำหรับ GUI
- **RTL-SDR drivers และ libraries**
- **welle.io** สำหรับ DAB+ decoding

---

<a name="installation"></a>
## 🚀 การติดตั้ง

### วิธีที่ 1: ใช้สคริปต์อัตโนมัติ (แนะนำ)

```bash
# โคลนโครงการ
git clone https://github.com/your-repo/DAB_Plus_Labs.git
cd DAB_Plus_Labs

# รันสคริปต์ติดตั้งอัตโนมัติ
chmod +x install_deps.sh
sudo ./install_deps.sh

# ติดตั้ง Python packages
pip install -r requirements.txt
```

### วิธีที่ 2: ติดตั้งแมนนวล

ดูรายละเอียดใน [README.md](README.md)

---

<a name="labs"></a>
## 📚 รายการแล็บทั้งหมด

<div align="center">

| Lab | หัวข้อ | ระยะเวลา | ความยาก | ไฟล์คู่มือ |
|-----|--------|----------|----------|------------|
| **0** | **Introduction to DAB+ และ PyQt5** | 60 นาที | ⭐ | [LAB0.md](Labs/Lab0/LAB0.md) |
| **1** | **การติดตั้งและทดสอบ RTL-SDR** | 90 นาที | ⭐⭐ | [LAB1.md](Labs/Lab1/LAB1.md) |
| **2** | **การใช้งาน welle.io ผ่าน Python** | 120 นาที | ⭐⭐⭐ | [LAB2.md](Labs/Lab2/LAB2.md) |
| **3** | **การควบคุม RTL-SDR โดยตรงด้วย pyrtlsdr** | 120 นาที | ⭐⭐⭐ | [LAB3.md](Labs/Lab3/LAB3.md) |
| **4** | **สร้าง DAB+ Station Scanner** | 150 นาที | ⭐⭐⭐⭐ | [LAB4.md](Labs/Lab4/LAB4.md) |
| **5** | **สร้าง DAB+ Program Recorder** | 150 นาที | ⭐⭐⭐⭐ | [LAB5.md](Labs/Lab5/LAB5.md) |
| **6** | **สร้าง DAB+ Signal Analyzer** | 180 นาที | ⭐⭐⭐⭐⭐ | [LAB6.md](Labs/Lab6/LAB6.md) |

</div>

### 📖 รายละเอียดแต่ละแล็บ:

---

#### 🎯 **LAB 0: Introduction to DAB+ และ PyQt5** 
**📁 [คู่มือเต็ม →](Labs/Lab0/LAB0.md)**

**เวลา**: 60 นาที | **ระดับ**: เริ่มต้น ⭐

**เนื้อหาย่อ**:
- พื้นฐาน DAB+ vs FM (15 นาที)
- PyQt5 GUI สำหรับผู้เริ่มต้น (45 นาที)  
- 5 demos: Widgets, Signals/Slots, Layouts, Input, Touch UI
- **TODO**: 4 จุดง่ายๆ ให้เติมโค้ด

**เรียนรู้**:
- เข้าใจความแตกต่าง DAB+ และ FM
- สร้าง PyQt5 application พื้นฐาน
- จัดการ signals/slots และ layouts
- UI สำหรับหน้าจอสัมผัส

**ไฟล์**: `lab0.py`, `LAB0.md`

---

#### 🔌 **LAB 1: การติดตั้งและทดสอบ RTL-SDR**
**📁 [คู่มือเต็ม →](Labs/Lab1/LAB1.md)**

**เวลา**: 90 นาที | **ระดับ**: พื้นฐาน ⭐⭐

**เนื้อหาย่อ**:
- ติดตั้งและกำหนดค่า RTL-SDR drivers
- แก้ปัญหา DVB-T driver conflicts  
- สร้าง GUI ทดสอบการทำงาน
- ตรวจสอบอุปกรณ์และคุณภาพสัญญาณ

**เรียนรู้**:
- การติดตั้ง udev rules และ blacklist drivers
- ใช้ subprocess เรียก command line tools
- PyQt5 threading กับ QThread
- การจัดการ errors และ logging

**ผลลัพธ์**: GUI app ทดสอบ RTL-SDR พร้อมรายงานสถานะ

---

#### 📻 **LAB 2: การใช้งาน welle.io ผ่าน Python**
**📁 [คู่มือเต็ม →](Labs/Lab2/LAB2.md)**

**เวลา**: 120 นาที | **ระดับ**: ปานกลาง ⭐⭐⭐

**เนื้อหาย่อ**:
- คอมไพล์และติดตั้ง welle.io จาก source
- สแกนหาสถานี DAB+ และเล่นเสียง
- จัดการ metadata และ slideshow
- สร้าง audio player ด้วย QMediaPlayer

**เรียนรู้**:
- การควบคุม external processes แบบ interactive  
- QMediaPlayer สำหรับเล่นเสียง
- การจัดการ audio routing บน Raspberry Pi
- Parser สำหรับ DAB+ metadata

**ผลลัพธ์**: DAB+ receiver app ที่ใช้งานได้จริง

---

#### 🔬 **LAB 3: การควบคุม RTL-SDR โดยตรงด้วย pyrtlsdr**
**📁 [คู่มือเต็ม →](Labs/Lab3/LAB3.md)**

**เวลา**: 120 นาที | **ระดับ**: ปานกลาง ⭐⭐⭐

**เนื้อหาย่อ**:
- เข้าถึง RTL-SDR โดยตรงด้วย Python
- ประมวลผล IQ samples และคำนวณ FFT
- สร้าง spectrum analyzer แบบ real-time
- matplotlib integration กับ PyQt5

**เรียนรู้**:
- Digital Signal Processing ขั้นพื้นฐาน
- NumPy/SciPy สำหรับการประมวลผลสัญญาณ  
- matplotlib backends สำหรับ PyQt5
- การจัดการ memory สำหรับข้อมูลขนาดใหญ่

**ผลลัพธ์**: RF spectrum analyzer แบบ real-time

---

#### 🔍 **LAB 4: สร้าง DAB+ Station Scanner**
**📁 [คู่มือเต็ม →](Labs/Lab4/LAB4.md)**

**เวลา**: 150 นาที | **ระดับ**: สูง ⭐⭐⭐⭐

**เนื้อหาย่อ**:
- พัฒนาระบบสแกนสถานี DAB+ อัตโนมัติ
- สร้างฐานข้อมูล SQLite เก็บข้อมูลสถานี  
- ติดตามคุณภาพสัญญาณแบบ real-time
- สร้าง advanced GUI ด้วย PyQt5

**เรียนรู้**:
- SQLite database design และ operations
- Advanced PyQt5 widgets (QTreeWidget, QTableWidget)
- Threading สำหรับ background scanning
- Data visualization และ reporting

**ผลลัพธ์**: DAB+ station scanner พร้อมฐานข้อมูล

---

#### ⏺️ **LAB 5: สร้าง DAB+ Program Recorder**
**📁 [คู่มือเต็ม →](Labs/Lab5/LAB5.md)**

**เวลา**: 150 นาที | **ระดับ**: สูง ⭐⭐⭐⭐

**เนื้อหาย่อ**:
- ระบบบันทึกรายการตามตารางเวลา
- จัดการไฟล์เสียง metadata และ slideshow
- สร้าง scheduler ด้วย QTimer
- ระบบจัดเก็บแฟ้มแบบมีระบบ

**เรียนรู้**:
- การจัดการไฟล์และ directory structures
- QTimer สำหรับ scheduling tasks
- Audio file processing ด้วย pydub
- File system monitoring

**ผลลัพธ์**: DAB+ program recorder พร้อม scheduler

---

#### 📊 **LAB 6: สร้าง DAB+ Signal Analyzer**
**📁 [คู่มือเต็ม →](Labs/Lab6/LAB6.md)**

**เวลา**: 180 นาที | **ระดับ**: ขั้นสูง ⭐⭐⭐⭐⭐

**เนื้อหาย่อ**:
- เครื่องมือวิเคราะห์สัญญาณ DAB+ ขั้นสูง
- วิเคราะห์ OFDM structure และ constellation
- สร้างกราฟ waterfall และ quality metrics
- ส่งออกรายงานเป็น PDF/CSV/JSON

**เรียนรู้**:
- Advanced DSP และ RF analysis
- OFDM signal processing
- Advanced matplotlib visualization
- Report generation ด้วย reportlab

**ผลลัพธ์**: Professional DAB+ signal analyzer

---

<a name="troubleshooting"></a>
## 🔍 การแก้ไขปัญหาทั่วไป

### 🚫 **RTL-SDR ไม่ทำงาน**
```bash
# ตรวจสอบการเชื่อมต่อ
lsusb | grep RTL

# ตรวจสอบ driver conflicts
lsmod | grep dvb

# แก้ไข permissions
sudo usermod -a -G plugdev $USER
```

### 🔇 **ไม่มีเสียง**  
```bash
# ตั้งค่าเสียงออก 3.5mm
sudo raspi-config # Advanced Options > Audio > Force 3.5mm

# ทดสอบเสียง
speaker-test -t wav -c 2
```

### 🖥️ **GUI ไม่แสดง**
```bash
# ตั้งค่า DISPLAY variable
export DISPLAY=:0

# ตรวจสอบ X11
echo $DISPLAY
```

### 📱 **หน้าจอสัมผัสไม่ตอบสนอง**
```bash
# เช็ค touchscreen driver
dmesg | grep -i touch

# Calibrate touchscreen  
sudo apt install xinput-calibrator
xinput_calibrator
```

**รายละเอียดเพิ่มเติม**: ดูในไฟล์ LAB*.md แต่ละไฟล์

---

<a name="support"></a>
## 📞 การสนับสนุน

### 📚 **แหล่งข้อมูลเพิ่มเติม**:
- [welle.io GitHub](https://github.com/AlbrechtL/welle.io)
- [RTL-SDR Documentation](https://rtl-sdr.com)
- [PyQt5 Documentation](https://doc.qt.io/qtforpython/)
- [DAB+ Standard](https://www.etsi.org/standards)

### 🐛 **รายงานปัญหา**:
1. ตรวจสอบไฟล์ LAB*.md ในแต่ละแล็บก่อน
2. ดู Solutions/ สำหรับโค้ดที่ทำงานได้
3. ตรวจสอบ hardware connections
4. เก็บ logs และ screenshots เพื่อ debugging

### 💡 **เคล็ดลับการเรียนรู้**:
- ✅ ทำ Lab 0 ให้เสร็จก่อนไปต่อ  
- ✅ อ่านคู่มือทั้งหมดก่อนเริ่มเขียนโค้ด
- ✅ ทดสอบ hardware ใน Lab 1 ให้ผ่านก่อน
- ✅ เก็บไฟล์ที่สร้างขึ้นในแต่ละ Lab ไว้
- ✅ ลองดัดแปลงโค้ดเพื่อทำความเข้าใจ

---

## 📄 ลิขสิทธิ์และการใช้งาน

โครงการนี้ใช้ **MIT License** - ใช้เพื่อการศึกษาได้อย่างอิสระ

**พัฒนาโดย**: DAB+ Learning Community  
**สำหรับ**: นักเรียน นักศึกษา และผู้สนใจ RF/SDR Technology

---

<div align="center">

**🎉 ขอให้สนุกกับการเรียนรู้ DAB+ Technology! 🎉**

*หากมีคำถามหรือข้อเสนอแนะ กรุณาติดต่อผ่าน Issues ใน GitHub*

</div>