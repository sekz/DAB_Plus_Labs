# LAB 0: Introduction to DAB+, Python, FRP และ PyQt5

## ส่วนที่ 1: Introduction to DAB+ (15 นาที)

### DAB+ คืออะไร?

**DAB+** (Digital Audio Broadcasting Plus) คือเทคโนโลยีการแพร่สัญญาณวิทยุแบบดิจิทัลที่พัฒนาต่อยอดจาก DAB เดิม โดยใช้ codec ที่ดีกว่าและมีประสิทธิภาพสูงกว่า

### ข้อดีของ DAB+ เมื่อเทียบกับ FM:

####  **คุณภาพเสียง**
- **เสียงดิจิทัล** ไม่มี static หรือสัญญาณรบกวน
- **คุณภาพคงที่** ไม่ขึ้นกับระยะทางจากเครื่องส่ง
- **เสียง stereo** ชัดเจนตลอดช่วงรับสัญญาณ

####  **ข้อมูลเพิ่มเติม**
- **Program Information** แสดงชื่อสถานี รายการ
- **Dynamic Label Segment (DLS)** แสดงชื่อเพลง ศิลปิน แบบ real-time
- **MOT Slideshow** แสดงรูปภาพ album art หรือข้อมูลโฆษณา
- **Electronic Program Guide (EPG)** ตารางรายการ

####  **ประสิทธิภาพการใช้คลื่น**
- **Multiplexing** สถานีหลายสถานีใช้ความถี่เดียวกัน
- **SFN (Single Frequency Network)** เครื่องส่งหลายจุดใช้ความถี่เดียว
- **ประหยัดสเปกตรัม** ใช้คลื่นความถี่น้อยกว่า FM

### ความถี่ DAB+ ในประเทศไทย:

#### **ข้อมูลพื้นฐานที่ยืนยันแล้ว:**
-  **ช่วงความถี่ที่อนุญาต**: 174-230 MHz (VHF Band III)
-  **วัตถุประสงค์**: สำหรับการทดลองและทดสอบ DAB+
-  **เทคโนโลยี**: DAB+ (MPEG-4 HE AAC v2)
-  **แผนความถี่**: NBTC ผว. 104-2567

#### **การทดลองที่ได้รับอนุญาตปัจจุบัน (2025):**
-  **Block 9A**: ความถี่ 202.928 MHz - กรุงเทพฯ และปริมณฑล (กลุ่มสถานีธรรมะ)
  - สถานีธรรมะเพื่อประชาชน
  - สถานีวิทยุสันติ
-  **Block 6C**: ความถี่ 185.360 MHz - ขอนแก่น และมหาสารคาม (กลุ่มสถานีขอนแก่น)
  - สถานีวิทยุขอนแก่นมหานคร
  - สถานีวิทยุใสฟ้า
  - สถานีวิทยุไธย์ท้องถิ่น

### เทคโนโลยีที่เกี่ยวข้อง:

####  **RTL-SDR (Software Defined Radio)**
- **Hardware**: ตัวรับสัญญาณ USB ราคาถูก (~500-1500 บาท)
- **Software**: ประมวลผลสัญญาณด้วยโปรแกรม
- **ความถี่**: รับได้ 24-1700 MHz (ครอบคลุม FM และ DAB+)
- **Bandwidth**: 2.4 MHz (เพียงพอสำหรับ DAB+ ensemble)

####  **welle.io**
- **DAB+ Decoder**: โปรแกรมถอดรหัส DAB+ แบบ open source
- **Cross-platform**: ทำงานบน Linux, Windows, macOS
- **Features**: รองรับ audio decoding, metadata, slideshow
- **API**: สามารถควบคุมผ่าน command line

### การทำงานของระบบ DAB+:

```
 เสาส่ง DAB+
    ⬇️
 สัญญาণ RF (174-240 MHz)
    ⬇️
 RTL-SDR Dongle
    ⬇️
 IQ Samples (Python)
    ⬇️
 welle.io Decoder
    ⬇️
 Audio +  Metadata + ️ Slideshow
```

---

## ส่วนที่ 2: Introduction to Python สำหรับมือใหม่ (30 นาที)

### Python คืออะไร?

**Python** คือภาษาโปรแกรมมิ่งที่ออกแบบมาให้เรียนรู้ง่าย อ่านง่าย และเขียนง่าย เหมาะสำหรับผู้เริ่มต้น

#### ทำไมต้องใช้ Python?
- **ง่ายต่อการเรียนรู้**: syntax ใกล้เคียงภาษาอังกฤษ
- **ไลบรารีมากมาย**: มีโมดูลสำเร็จรูปเยอะ
- **Cross-platform**: ทำงานได้ทุก OS
- **Community ใหญ่**: หาความช่วยเหลือได้ง่าย
- **เหมาะกับ Raspberry Pi**: ติดตั้งมาให้แล้ว

### การติดตั้งและเรียกใช้ Python

#### ตรวจสอบ Python บน Raspberry Pi:
```bash
# ตรวจสอบเวอร์ชัน Python
python3 --version

# เข้าสู่ Python interactive mode
python3

# ออกจาก Python interactive mode
>>> exit()
```

### Python Basics - ทีละขั้นตอน

#### 1. Variables (ตัวแปร)
```python
# ตัวแปรประเภทต่างๆ
name = "สวัสดี"           # String (ข้อความ)
age = 25                  # Integer (จำนวนเต็ม)
height = 175.5            # Float (จำนวนทศนิยม)
is_student = True         # Boolean (จริง/เท็จ)

# แสดงผล
print(name)               # แสดง: สวัสดี
print("อายุ:", age)        # แสดง: อายุ: 25
```

#### 2. Lists (รายการ)
```python
# สร้าง list
fruits = ["แอปเปิ้ล", "กล้วย", "ส้ม"]
numbers = [1, 2, 3, 4, 5]

# เข้าถึงข้อมูลใน list
print(fruits[0])          # แสดง: แอปเปิ้ล (อันแรก)
print(fruits[-1])         # แสดง: ส้ม (อันสุดท้าย)

# เพิ่มข้อมูล
fruits.append("มะม่วง")    # เพิ่มท้าย list
print(fruits)             # แสดง: ['แอปเปิ้ล', 'กล้วย', 'ส้ม', 'มะม่วง']

# นับจำนวน
print(len(fruits))        # แสดง: 4
```

#### 3. Loops (การวนซ้ำ)
```python
# for loop - วนทุกตัวใน list
fruits = ["แอปเปิ้ล", "กล้วย", "ส้ม"]
for fruit in fruits:
    print("ผลไม้:", fruit)

# for loop - วนตามจำนวน
for i in range(5):        # วน 0, 1, 2, 3, 4
    print("รอบที่", i)

# while loop - วนจนกว่าเงื่อนไขจะเป็นเท็จ
count = 0
while count < 3:
    print("นับ:", count)
    count = count + 1     # เพิ่มค่า count
```

#### 4. Conditions (เงื่อนไข)
```python
# if-elif-else
age = 18

if age >= 18:
    print("เป็นผู้ใหญ่แล้ว")
elif age >= 13:
    print("เป็นวัยรุ่น")
else:
    print("เป็นเด็ก")

# การเปรียบเทียบ
x = 10
y = 20

if x > y:
    print("x มากกว่า y")
elif x < y:
    print("x น้อยกว่า y")    # จะแสดงบรรทัดนี้
else:
    print("x เท่ากับ y")
```

#### 5. Functions (ฟังก์ชัน)
```python
# สร้างฟังก์ชัน
def say_hello(name):
    return "สวัสดี " + name

# เรียกใช้ฟังก์ชัน
message = say_hello("สมชาย")
print(message)            # แสดง: สวัสดี สมชาย

# ฟังก์ชันคำนวณ
def add_numbers(a, b):
    result = a + b
    return result

sum_result = add_numbers(5, 3)
print("ผลรวม:", sum_result)   # แสดง: ผลรวม: 8

# ฟังก์ชันไม่ return ค่า
def print_info(name, age):
    print(f"ชื่อ: {name}")
    print(f"อายุ: {age} ปี")

print_info("สมศรี", 25)
```

#### 6. Dictionaries (พจนานุกรม)
```python
# สร้าง dictionary
student = {
    "name": "สมชาย",
    "age": 20,
    "grade": "A"
}

# เข้าถึงข้อมูล
print(student["name"])    # แสดง: สมชาย
print(student.get("age")) # แสดง: 20

# เพิ่ม/แก้ไขข้อมูล
student["city"] = "กรุงเทพ"
student["age"] = 21

print(student)
```

#### 7. Working with Files (การทำงานกับไฟล์)
```python
# เขียนไฟล์
with open("test.txt", "w", encoding="utf-8") as file:
    file.write("สวัสดีชาวโลก\n")
    file.write("นี่คือไฟล์ทดสอบ")

# อ่านไฟล์
with open("test.txt", "r", encoding="utf-8") as file:
    content = file.read()
    print(content)

# อ่านไฟล์ทีละบรรทัด
with open("test.txt", "r", encoding="utf-8") as file:
    for line in file:
        print("บรรทัด:", line.strip())
```

#### 8. Classes (คลาส) - พื้นฐาน
```python
# สร้างคลาส
class Person:
    def __init__(self, name, age):  # Constructor
        self.name = name
        self.age = age

    def introduce(self):           # Method
        return f"ชื่อ {self.name} อายุ {self.age} ปี"

    def have_birthday(self):
        self.age += 1
        print(f"{self.name} อายุขึ้น 1 ปี")

# ใช้งานคลาส
person1 = Person("สมชาย", 25)
print(person1.introduce())        # แสดง: ชื่อ สมชาย อายุ 25 ปี

person1.have_birthday()           # แสดง: สมชาย อายุขึ้น 1 ปี
print(person1.introduce())        # แสดง: ชื่อ สมชาย อายุ 26 ปี
```

#### 9. Modules (โมดูล)
```python
# import โมดูล
import math
import datetime
import random

# ใช้งานฟังก์ชันใน math
print(math.sqrt(16))              # แสดง: 4.0
print(math.pi)                    # แสดง: 3.141592653589793

# ใช้งาน datetime
now = datetime.datetime.now()
print("วันเวลาปัจจุบัน:", now)

# ใช้งาน random
number = random.randint(1, 10)    # สุ่มเลข 1-10
print("เลขสุ่ม:", number)

# import เฉพาะฟังก์ชันที่ต้องการ
from math import sqrt, pow
print(sqrt(25))                   # แสดง: 5.0
print(pow(2, 3))                  # แสดง: 8.0
```

#### 10. Error Handling (จัดการข้อผิดพลาด)
```python
# try-except
try:
    number = int(input("ใส่ตัวเลข: "))
    result = 10 / number
    print("ผลลัพธ์:", result)
except ValueError:
    print("ผิดพลาด: กรุณาใส่ตัวเลข")
except ZeroDivisionError:
    print("ผิดพลาด: ไม่สามารถหารด้วย 0")
except Exception as e:
    print("ผิดพลาดอื่นๆ:", str(e))
finally:
    print("จบการทำงาน")
```

### การเชื่อมต่อกับ Hardware (Raspberry Pi)

#### การใช้งาน GPIO (ตัวอย่าง)
```python
# ตัวอย่างการควบคุม LED (ต้องติดตั้ง RPi.GPIO)
try:
    import RPi.GPIO as GPIO
    import time

    # ตั้งค่า GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)  # Pin 18 เป็น output

    # กะพริบ LED
    for i in range(5):
        GPIO.output(18, GPIO.HIGH)  # เปิด LED
        time.sleep(1)               # รอ 1 วินาที
        GPIO.output(18, GPIO.LOW)   # ปิด LED
        time.sleep(1)

    GPIO.cleanup()                  # ทำความสะอาด GPIO

except ImportError:
    print("RPi.GPIO ไม่พร้อมใช้งาน (ทำงานบนคอมพิวเตอร์ทั่วไป)")
```

### การติดตั้ง Python Packages

#### ใช้ pip (Python Package Manager):
```bash
# ติดตั้ง package ใหม่
pip3 install requests
pip3 install numpy
pip3 install matplotlib

# ดู package ที่ติดตั้งแล้ว
pip3 list

# อัปเดต package
pip3 install --upgrade package_name

# ติดตั้งจาก requirements.txt
pip3 install -r requirements.txt
```

### ตัวอย่างโปรแกรมสำหรับ DAB+ Lab

#### การอ่านข้อมูลจากไฟล์ CSV:
```python
import csv

# อ่านข้อมูลสถานี DAB+
def read_dab_stations(filename):
    stations = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                station = {
                    'name': row['name'],
                    'frequency': float(row['frequency']),
                    'location': row['location']
                }
                stations.append(station)
    except FileNotFoundError:
        print(f"ไม่พบไฟล์ {filename}")

    return stations

# ใช้งาน
stations = read_dab_stations("dab_stations.csv")
for station in stations:
    print(f"สถานี: {station['name']} - {station['frequency']} MHz")
```

#### การทำงานกับเวลา:
```python
import time
from datetime import datetime, timedelta

# แสดงเวลาปัจจุบัน
now = datetime.now()
print("เวลาปัจจุบัน:", now.strftime("%Y-%m-%d %H:%M:%S"))

# คำนวณเวลา
future_time = now + timedelta(hours=1)
print("1 ชั่วโมงข้างหน้า:", future_time.strftime("%H:%M:%S"))

# วัดเวลาที่ใช้ในการทำงาน
start_time = time.time()
time.sleep(2)  # จำลองการทำงาน 2 วินาที
end_time = time.time()
duration = end_time - start_time
print(f"ใช้เวลา: {duration:.2f} วินาที")
```

### เตรียมความพร้อมสำหรับ PyQt5

#### แนวคิดสำคัญที่ต้องเข้าใจ:
1. **Class และ Inheritance**: PyQt5 ใช้ OOP อย่างหนัก
2. **Event-driven Programming**: โปรแกรมตอบสนองต่อ events
3. **Callback Functions**: ฟังก์ชันที่เรียกเมื่อมี event
4. **Threading**: การทำงานพร้อมกันหลาย thread

#### ตัวอย่าง Class สำหรับ GUI:
```python
class DABStation:
    def __init__(self, name, frequency):
        self.name = name
        self.frequency = frequency
        self.is_playing = False

    def start_playing(self):
        self.is_playing = True
        print(f"เริ่มเล่น {self.name}")

    def stop_playing(self):
        self.is_playing = False
        print(f"หยุดเล่น {self.name}")

# ตัวอย่าง Event handling (แนวคิด)
def on_button_click():
    print("ปุ่มถูกกด!")

def on_slider_change(value):
    print(f"Slider เปลี่ยนเป็น: {value}")
```

### แหล่งเรียนรู้เพิ่มเติม

#### Online Resources:
- **Python.org Tutorial**: https://docs.python.org/3/tutorial/
- **Python for Beginners**: https://www.python.org/about/gettingstarted/
- **Raspberry Pi Python**: https://www.raspberrypi.org/documentation/usage/python/

#### Books ที่แนะนำ:
- "Python Crash Course" by Eric Matthes
- "Learn Python the Hard Way" by Zed Shaw
- "Python Programming for Raspberry Pi"

### Quick Reference Card

#### สิ่งที่ต้องจำ:
```python
# ตัวแปรและ Data Types
name = "text"        # String
number = 42          # Integer
decimal = 3.14       # Float
is_true = True       # Boolean
items = [1, 2, 3]    # List
info = {"key": "value"}  # Dictionary

# การควบคุมการไหล
if condition:
    # do something
elif other_condition:
    # do something else
else:
    # default action

for item in items:
    # process each item

while condition:
    # repeat until condition is false

# ฟังก์ชัน
def function_name(parameter):
    return result

# Class
class ClassName:
    def __init__(self, parameter):
        self.attribute = parameter

    def method(self):
        return self.attribute

# Error handling
try:
    # risky code
except SpecificError:
    # handle specific error
except Exception as e:
    # handle any other error
```

---

## ส่วนที่ 3: การใช้งาน FRP Client (30 นาที)

### FRP คืออะไร?

**FRP (Fast Reverse Proxy)** เป็นเครื่องมือที่ช่วยให้เข้าถึง service บน Raspberry Pi ที่อยู่หลัง router/NAT ได้จากอินเทอร์เน็ต โดยไม่ต้องเปิด port ที่ router

#### การทำงานของ FRP:

```
[RPI Service:1234] ---> [FRP Client] ---> Internet ---> [FRP Server:600x] <--- [Client ภายนอก]
```

**ทำไมต้องใช้ FRP?**
- RPI อยู่หลัง NAT/router ไม่มี public IP
- IP บ้านเปลี่ยนบ่อย
- ไม่สามารถเข้าถึง router เพื่อเปิด port
- ต้องการเข้าถึง DAB+ streaming จาก Google Colab

### การติดตั้ง FRP Client

#### 1. ตรวจสอบ CPU Architecture:
```bash
uname -m
# aarch64 → ใช้ ARM64
# armv7l → ใช้ ARM
```

#### 2. ดาวน์โหลดและติดตั้ง (ARM64):
```bash
# ดาวน์โหลด
wget https://github.com/fatedier/frp/releases/download/v0.61.0/frp_0.61.0_linux_arm64.tar.gz

# แตกไฟล์
tar -xzf frp_0.61.0_linux_arm64.tar.gz
cd frp_0.61.0_linux_arm64

# ติดตั้ง
sudo cp frpc /usr/local/bin/
sudo chmod +x /usr/local/bin/frpc

# ตรวจสอบ
frpc --version
```

#### 3. สร้างไฟล์ Config:
```bash
sudo mkdir -p /etc/frp
sudo nano /etc/frp/frpc.toml
```

**เนื้อหาไฟล์ (เปลี่ยน XX เป็นเลขที่นั่งของคุณ)**:
```toml
# FRP Server Information
serverAddr = "xxx.xxx.xxx.xxx"
serverPort = 7000
auth.method = "token"
auth.token = "YourTokenFromInstructor"

# Proxy Configuration
[[proxies]]
name = "piXX-tcp-1234"          # เช่น pi01, pi02
type = "tcp"
localIP = "127.0.0.1"
localPort = 1234
remotePort = 60XX               # เช่น 6001, 6002
```

#### 4. ทดสอบรัน:
```bash
# รันแบบ manual
frpc -c /etc/frp/frpc.toml

# ต้องเห็น: "start proxy success"
# กด Ctrl+C เพื่อหยุด
```

#### 5. ตั้งค่า Systemd Service:
```bash
# สร้างไฟล์ service
sudo nano /etc/systemd/system/frpc.service
```

**เนื้อหาไฟล์**:
```ini
[Unit]
Description=FRP Client Service
After=network.target

[Service]
Type=simple
User=pi
Restart=on-failure
RestartSec=10
ExecStart=/usr/local/bin/frpc -c /etc/frp/frpc.toml

[Install]
WantedBy=multi-user.target
```

**เปิดใช้งาน**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable frpc
sudo systemctl start frpc
sudo systemctl status frpc
```

### การทดสอบ FRP

#### จาก Google Colab:
```python
import socket

FRP_SERVER = "xxx.xxx.xxx.xxx"
FRP_PORT = 60XX  # remote port ของคุณ

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
result = sock.connect_ex((FRP_SERVER, FRP_PORT))

if result == 0:
    print(f"✅ เชื่อมต่อสำเร็จ Port {FRP_PORT}")
else:
    print(f"❌ ไม่สามารถเชื่อมต่อ Port {FRP_PORT}")
sock.close()
```

### คำสั่งที่มีประโยชน์:
```bash
# ดูสถานะ
sudo systemctl status frpc

# ดู log
sudo journalctl -u frpc -f

# รีสตาร์ท
sudo systemctl restart frpc

# แก้ไข config
sudo nano /etc/frp/frpc.toml
sudo systemctl restart frpc
```

### Troubleshooting:

**ปัญหา: login failed**
```bash
# ตรวจสอบ config
cat /etc/frp/frpc.toml | grep -E "serverAddr|serverPort|token"

# ทดสอบ connection
ping -c 4 [SERVER_IP]
```

**ปัญหา: port already used**
```bash
# แก้ไข config ใช้ port อื่น
sudo nano /etc/frp/frpc.toml
# เปลี่ยน remotePort และ name
sudo systemctl restart frpc
```

---

## ส่วนที่ 4: Introduction to PyQt5 (30 นาที)

### PyQt5 คืออะไร?

**PyQt5** คือ Python binding สำหรับ Qt5 framework ที่ใช้สร้าง GUI applications ข้ามแพลตฟอร์ม

### ทำไมต้องใช้ PyQt5?

####  **ข้อดี**
- **Cross-platform** ทำงานบน Windows, Linux, macOS
- **Native look** UI ดูเหมือน native app ของแต่ละ OS
- **Rich widgets** มี widget ครบครัน
- **Professional** ใช้สร้างแอปเชิงพาณิชย์ได้
- **Touch support** รองรับหน้าจอสัมผัส

####  **เหมาะกับ Raspberry Pi เพราะ:**
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

####  **Demo 1: Basic Widgets**
- การใช้ QLabel, QPushButton, QLineEdit
- การแสดง QMessageBox
- QSlider และ QProgressBar

####  **Demo 2: Signals & Slots**
- Built-in signals (clicked, valueChanged)
- Custom signals (pyqtSignal)
- QTimer และ periodic updates

####  **Demo 3: Layouts**
- QVBoxLayout (แนวตั้ง)
- QHBoxLayout (แนวนอน)  
- Nested layouts

####  **Demo 4: Input Widgets**
- QCheckBox และ QRadioButton
- QComboBox และ QSpinBox
- การอ่านค่าจาก widgets

####  **Demo 5: Touch-Friendly UI**
- ปุ่มขนาดใหญ่ (min 60x40px)
- Slider ที่เหมาะกับนิ้ว
- Visual feedback
- Font sizes สำหรับหน้าจอ 7"

### Tips สำหรับ Touch Screen:

####  **ขนาดที่เหมาะสม:**
- **Buttons**: อย่างน้อย 60x40 pixels
- **Fonts**: 12-16pt สำหรับหน้าจอ 7"
- **Spacing**: เว้นระยะระหว่าง elements

####  **Visual Feedback:**
- **Hover effects**: เปลี่ยนสีเมื่อ hover
- **Press effects**: เปลี่ยนสีเมื่อกด
- **Disabled states**: สีเทาเมื่อปิดใช้งาน

####  **CSS Styling:**
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
-  การสร้าง PyQt5 application พื้นฐาน
-  การใช้ widgets หลัก
-  Signals และ Slots
-  การจัดเรียง layouts
-  การทำ touch-friendly UI
-  ความรู้พื้นฐานเกี่ยวกับ DAB+

**เวลาที่ใช้**: ประมาณ 1 ชั่วโمง
- **Python Introduction**: 30 นาที (ทฤษฎี + hands-on)
- **DAB+ Introduction**: 15 นาที (ทฤษฎี)
- **PyQt5 Hands-on**: 30 นาที (practical coding)

### ขั้นตอนต่อไป:
- **Lab 1**: RTL-SDR Testing (ใช้ PyQt5 + subprocess)
- **Lab 2**: welle.io Integration (ใช้ QMediaPlayer)
- **Lab 3**: Direct RTL-SDR (ใช้ matplotlib + PyQt5)
- **Lab 4**: DAB+ Scanner (ใช้ advanced PyQt5)
- **Lab 5**: Program Recorder (ใช้ QTimer + file handling)  
- **Lab 6**: Signal Analyzer (ใช้ data visualization)

---

## สรุปการเรียนรู้

### ความรู้ที่ได้รับหลังจบ Lab 0:

#### Python Programming:
- **ตัวแปรและข้อมูลพื้นฐาน**: String, Integer, Float, Boolean, List, Dictionary
- **การควบคุมการไหล**: if-elif-else, for loop, while loop
- **ฟังก์ชัน**: การสร้างและเรียกใช้ฟังก์ชัน, parameters และ return values
- **การจัดการไฟล์**: อ่าน-เขียนไฟล์ด้วย encoding UTF-8
- **Object-Oriented Programming**: Class, Object, Method, Constructor
- **โมดูล**: การ import และใช้งานโมดูลต่างๆ
- **Error Handling**: try-except-finally สำหรับจัดการข้อผิดพลาด
- **Hardware Integration**: การเชื่อมต่อกับ GPIO บน Raspberry Pi

#### DAB+ Technology:
- **ความรู้พื้นฐาน**: DAB+ vs FM, ข้อดีและข้อจำกัด
- **ข้อมูลเทคนิค**: ความถี่ในประเทศไทย, Ensemble และ Service
- **เทคโนโลยีที่เกี่ยวข้อง**: RTL-SDR, welle.io, Software Defined Radio
- **การประยุกต์ใช้**: การรับสัญญาณ, การถอดรหัส, การแสดงผล

#### FRP Client:
- **การติดตั้ง**: ดาวน์โหลดและติดตั้ง FRP Client บน ARM architecture
- **การตั้งค่า**: สร้างและจัดการ configuration file
- **Systemd Service**: ตั้งค่า service สำหรับรันอัตโนมัติ
- **การทดสอบ**: ทดสอบ connection และ troubleshooting
- **Remote Access**: เข้าถึง RPI จากภายนอกผ่าน FRP tunnel

#### PyQt5 GUI Programming:
- **พื้นฐาน**: Application, Window, Widget concepts
- **Widgets หลัก**: Label, Button, TextEdit, Slider, ProgressBar
- **Layout Management**: VBox, HBox, Grid layouts
- **Event System**: Signals และ Slots, การตอบสนอง events
- **Touch Interface**: การออกแบบสำหรับหน้าจอสัมผัส
- **Styling**: CSS-like styling สำหรับ Qt widgets

### เครื่องมือและ Skills ที่พร้อมใช้:

#### Development Environment:
- **Python 3** บน Raspberry Pi OS Bookworm
- **PyQt5** สำหรับสร้าง GUI applications
- **pip package management** สำหรับติดตั้ง libraries
- **File handling** และ data processing
- **FRP Client** สำหรับ remote access และ tunneling

#### Network & Remote Access:
- **FRP Tunneling** เข้าถึง RPI จากภายนอก
- **Systemd Service Management** จัดการ background services
- **Network Troubleshooting** debug connection issues
- **Remote Streaming** เชื่อมต่อจาก Google Colab

#### Hardware Integration:
- **Raspberry Pi GPIO** การควบคุม hardware
- **Touch screen support** สำหรับ UI interaction
- **Audio output** ผ่าน 3.5mm jack
- **USB devices** เช่น RTL-SDR dongle

#### Programming Concepts:
- **Object-Oriented Design** สำหรับโครงสร้างโปรแกรม
- **Event-driven Programming** สำหรับ GUI applications
- **Error handling** และ debugging techniques
- **Code organization** และ module management

### เตรียมพร้อมสำหรับ Labs ขั้นสูง:

คุณพร้อมแล้วสำหรับ:
- **Lab 1**: ทำงานกับ RTL-SDR hardware และ subprocess
- **Lab 2**: ใช้ welle.io สำหรับ DAB+ decoding
- **Lab 3**: การประมวลผลสัญญาณและ spectrum analysis
- **Lab 4**: สร้าง advanced GUI applications ด้วย database
- **Lab 5**: การจัดการเวลาและ multimedia playback
- **Lab 6**: การวิเคราะห์สัญญาณขั้นสูงและ data visualization

---

** พร้อมแล้ว!** ตอนนี้คุณมีพื้นฐานที่จำเป็นสำหรับ DAB+ Labs แล้ว ไปเริ่ม Lab 1 กันเถอะ!