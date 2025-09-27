# LAB 3: Learning DAB+ with Raspberry Pi and RTL-SDR

## วัตถุประสงค์
- เรียนรู้การรับสัญญาณ DAB+ ด้วย RTL-SDR
- ทำความเข้าใจ I/Q data processing และ ETI stream format
- พัฒนาแอปพลิเคชันสำหรับ decode และเล่น DAB+ services
- สร้าง GUI application สำหรับควบคุมและแสดงผล

## ความรู้พื้นฐานที่ต้องมี
- ความรู้พื้นฐาน Software Defined Radio (SDR)
- การเขียนโปรแกรม Python
- ความเข้าใจเกี่ยวกับ digital signal processing
- การใช้งาน Linux command line

## อุปกรณ์ที่ใช้
- Raspberry Pi 4 (4GB RAM)
- RTL-SDR Blog V4 dongle
- หน้าจอสัมผัส HDMI 7"
- หูฟัง 3.5mm
- เสาอากาศสำหรับรับสัญญาณ DAB+

## การติดตั้ง Dependencies

### Phase 1: RTL-SDR Data Acquisition
```bash
# ติดตั้ง RTL-SDR drivers และ libraries
sudo apt update
sudo apt install -y rtl-sdr librtlsdr-dev

# ติดตั้ง Python packages
pip install pyrtlsdr numpy scipy matplotlib

# ตั้งค่า udev rules สำหรับ RTL-SDR
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", GROUP="adm", MODE="0666", SYMLINK+="rtl_sdr"' | sudo tee /etc/udev/rules.d/20.rtlsdr.rules
sudo udevadm control --reload-rules

# ทดสอบ RTL-SDR
rtl_test -t
```

### Phase 2: DAB+ Signal Processing
```bash
# ติดตั้ง dependencies สำหรับ eti-cmdline
sudo apt install -y cmake build-essential libfftw3-dev librtlsdr-dev git

# ดาวน์โหลดและ compile eti-stuff
git clone https://github.com/JvanKatwijk/eti-stuff
cd eti-stuff
mkdir build && cd build
cmake .. -DRTLSDR=1
make -j4
sudo make install

# ตรวจสอบการติดตั้ง
eti-cmdline --help
```

### Phase 3: ETI Analysis
```bash
# ติดตั้ง Python packages สำหรับ parsing
pip install bitstring
```

### Phase 4: Audio Playback
```bash
# ติดตั้ง audio dependencies
sudo apt install -y ffmpeg alsa-utils pulseaudio
pip install ffmpeg-python pyaudio pillow

# ตั้งค่า audio output (3.5mm jack)
sudo raspi-config nonint do_audio 1

# ทดสอบ audio
speaker-test -c2 -t wav
```

### Phase 5: GUI Application
```bash
# ติดตั้ง PyQt5 และ dependencies
sudo apt install -y python3-pyqt5 python3-pyqt5-dev
pip install PyQt5 pyqtgraph

# ตั้งค่า touchscreen (สำหรับ 7" HDMI)
sudo apt install -y xinput-calibrator
```

## ขั้นตอนการทำงาน

### Phase 1: RTL-SDR Data Acquisition

#### ขั้นตอนที่ 1.1: ทดสอบ RTL-SDR พื้นฐาน (lab3_1a.py)
1. **เชื่อมต่อ RTL-SDR** กับ Raspberry Pi
2. **ตั้งค่าความถี่** DAB+ Thailand (185.360 MHz)
3. **รับ I/Q samples** และบันทึกเป็นไฟล์
4. **วิเคราะห์สเปกตรัม** เบื้องต้น

#### ขั้นตอนที่ 1.2: RTL-TCP Client (lab3_1b.py)
1. **เริ่มต้น rtl_tcp server**: `rtl_tcp -a localhost -p 1234`
2. **เชื่อมต่อผ่าน TCP** และควบคุม RTL-SDR
3. **รับ I/Q data** ผ่านเครือข่าย
4. **เปรียบเทียบ** กับการเชื่อมต่อโดยตรง

### Phase 2: DAB+ Signal Processing

#### ขั้นตอนที่ 2: ETI Stream Generation (lab3_2.py)
1. **ใช้ eti-cmdline** แปลง I/Q เป็น ETI stream
2. **ตั้งค่าความถี่** และพารามิเตอร์
3. **ติดตามสถานะ** การ sync และ error rate
4. **บันทึก ETI stream** สำหรับขั้นตอนถัดไป

### Phase 3: ETI Analysis

#### ขั้นตอนที่ 3: Service Discovery (lab3_3.py)
1. **Parse ETI frames** (6144 bytes แต่ละ frame)
2. **แยก FIC data** (Fast Information Channel)
3. **ค้นหา DAB+ services** และ subchannels
4. **สร้างรายการ services** และบันทึกเป็น JSON

### Phase 4: Audio Playback

#### ขั้นตอนที่ 4: Service Player (lab3_4.py)
1. **เลือก service** จากรายการ
2. **แยกเสียง AAC** จาก ETI stream
3. **เล่นเสียงผ่าน 3.5mm jack**
4. **แสดง Dynamic Label** และ MOT slideshow

### Phase 5: Complete GUI

#### ขั้นตอนที่ 5: GUI Application (lab3_5.py)
1. **สร้าง main window** ด้วย PyQt5
2. **แสดงรายการ services** แบบ touch-friendly
3. **ควบคุมการเล่นเสียง** และปรับระดับเสียง
4. **แสดง spectrum analyzer** และ signal quality
5. **แสดง slideshow** และ real-time information

## การเขียนโค้ด

### ส่วนที่ต้องเติมใน lab3_1a.py:
- `setup_rtlsdr()`: เชื่อมต่อและตั้งค่า RTL-SDR
- `capture_samples()`: รับ I/Q samples และบันทึกไฟล์
- `analyze_spectrum()`: วิเคราะห์สเปกตรัม FFT

### ส่วนที่ต้องเติมใน lab3_1b.py:
- `connect()`: เชื่อมต่อ TCP กับ rtl_tcp server
- `set_frequency()`, `set_sample_rate()`, `set_gain()`: ส่งคำสั่งควบคุม
- `receive_samples()`: รับ I/Q data ผ่าน network

### ส่วนที่ต้องเติมใน lab3_2.py:
- `check_eti_cmdline()`: ตรวจสอบการติดตั้ง eti-cmdline
- `run_eti_cmdline()`: เรียกใช้และติดตาม eti-cmdline process
- `analyze_eti_output()`: วิเคราะห์ไฟล์ ETI ที่ได้

### ส่วนที่ต้องเติมใน lab3_3.py:
- `parse_eti_header()`: แยก ETI frame header
- `extract_fic_data()`: แยก Fast Information Channel
- `parse_service_information()`: แยกข้อมูล services และ subchannels

### ส่วนที่ต้องเติมใน lab3_4.py:
- `load_service_list()`: โหลดรายการ services จาก JSON
- `extract_audio_data()`: แยกเสียง AAC จาก ETI
- `play_audio()`: เล่นเสียงผ่าน PyAudio
- `extract_slideshow_images()`: แยก MOT slideshow

### ส่วนที่ต้องเติมใน lab3_5.py:
- `setup_ui()`: สร้าง GUI หลักด้วย PyQt5
- `DABSignalThread.run()`: ประมวลผลสัญญาณใน background
- `SpectrumWidget`: แสดง spectrum analyzer
- `ServiceListWidget`: แสดงรายการ services
- `AudioControlWidget`: ควบคุมการเล่นเสียง

## ผลลัพธ์ที่คาดหวัง

### Phase 1:
- ไฟล์ `raw_iq_data.bin` และ `networked_iq_data.bin`
- กราฟสเปกตรัมความถี่
- ข้อมูล signal strength และ quality

### Phase 2:
- ไฟล์ `dab_ensemble.eti` ขนาดประมาณ 6144 * จำนวน frames
- สถานะ sync และ error rate จาก eti-cmdline
- ETI frames ที่สามารถ parse ได้

### Phase 3:
- ไฟล์ `service_list.json` และ `subchannel_info.json`
- รายการ DAB+ services ที่พบ
- ข้อมูล bitrate และ codec type ของแต่ละ service

### Phase 4:
- ไฟล์ `decoded_audio.wav`
- โฟลเดอร์ `slideshow_images/` พร้อมภาพ
- การเล่นเสียงผ่าน 3.5mm jack
- แสดง Dynamic Label Segment (DLS)

### Phase 5:
- GUI application ที่ทำงานบน 7" touchscreen
- Real-time spectrum analyzer
- Touch-friendly service selection
- Audio player controls
- Slideshow viewer
- Signal quality indicators

## การแก้ไขปัญหา

### ปัญหา RTL-SDR ไม่ work:
```bash
# ตรวจสอบ USB connection
lsusb | grep Realtek

# ตรวจสอบ driver conflict
sudo rmmod dvb_usb_rtl28xxu rtl2832 rtl2830

# รีสตาร์ท udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### ปัญหา eti-cmdline build failures:
```bash
# ติดตั้ง missing dependencies
sudo apt install -y libfftw3-dev libsndfile1-dev pkg-config

# ใช้ cmake version ใหม่
sudo apt install -y cmake

# ตรวจสอบ compiler
gcc --version
```

### ปัญหา Audio dropouts:
```bash
# ปรับ CPU performance
echo 'performance' | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# เพิ่ม audio buffer
echo 'snd-usb-audio index=0' | sudo tee -a /etc/modprobe.d/alsa-base.conf

# ตรวจสอบ audio devices
aplay -l
```

### ปัญหา GUI performance:
```bash
# เพิ่ม GPU memory
echo 'gpu_mem=128' | sudo tee -a /boot/config.txt

# ปิด unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable wifi-powersave@wlan0.service

# ตั้งค่า Qt scaling
export QT_SCALE_FACTOR=1.2
```

### ปัญหา Touchscreen calibration:
```bash
# Calibrate touchscreen
sudo apt install xinput-calibrator
xinput_calibrator

# ตั้งค่า rotation หากจำเป็น
echo 'display_rotate=2' | sudo tee -a /boot/config.txt
```

## คำถามทบทวน

1. **I/Q Data Processing**: อธิบายความแตกต่างระหว่างการรับข้อมูลจาก pyrtlsdr และ rtl_tcp client
2. **ETI Stream Format**: ETI frame มีขนาดกี่ bytes และแต่ละ frame มี logical time เท่าไหร่?
3. **DAB+ vs DAB**: ความแตกต่างหลักระหว่าง DAB และ DAB+ คืออะไร?
4. **Signal Quality**: ปัจจัยใดบ้างที่ส่งผลต่อคุณภาพสัญญาณ DAB+?
5. **Audio Codec**: DAB+ ใช้ audio codec อะไร และมี bitrate เท่าไหร่?
6. **MOT Slideshow**: MOT ย่อมาจากอะไร และมีวัตถุประสงค์อย่างไร?
7. **FIC vs MSC**: อธิบายหน้าที่ของ Fast Information Channel และ Main Service Channel
8. **GUI Design**: ออกแบบ GUI ให้เหมาะกับ touchscreen ต้องคำนึงถึงอะไรบ้าง?

## ข้อมูลเพิ่มเติม

### DAB+ Frequencies ในประเทศไทย:
- **Bangkok/Central**: 185.360 MHz (Block 7A)
- **Phuket/South**: 185.360 MHz (Block 7A)
- **Chiang Mai/North**: 195.936 MHz (Block 8C)

### ETI Frame Structure:
```
ETI Frame (6144 bytes total):
├── ERR (4 bytes) - Error information
├── FSYNC (3 bytes) - Frame synchronization
├── LIDATA (1 byte) - Length indicator
├── FC (4 bytes) - Frame characterization
├── NST (1 byte) - Number of streams
├── FIC (32 bytes × 3) - Fast Information Channel
└── MSC (remaining bytes) - Main Service Channel
```

### Performance Optimization สำหรับ Pi 4:
```bash
# CPU Performance Mode
echo 'performance' | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# GPU Memory สำหรับ GUI
echo 'gpu_mem=128' >> /boot/config.txt

# USB Buffer สำหรับ RTL-SDR
echo 'usbcore.usbfs_memory_mb=1000' >> /boot/cmdline.txt

# Network Buffer
echo 'net.core.rmem_max = 134217728' >> /etc/sysctl.conf
echo 'net.core.rmem_default = 134217728' >> /etc/sysctl.conf
```

### การเชื่อมต่อ Hardware:
```
RTL-SDR V4 → USB 3.0 → Raspberry Pi 4
           ↓
      DAB+ Antenna (VHF Band III: 174-240 MHz)

Pi 4 → HDMI → 7" Touchscreen (800×480)
     → 3.5mm → Headphones/Speaker
```