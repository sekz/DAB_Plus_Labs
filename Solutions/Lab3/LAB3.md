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

### Phase 2: DAB+ Signal Processing (eti-cmdline)
```bash
# ติดตั้ง dependencies สำหรับ eti-cmdline
sudo apt install -y cmake build-essential libfftw3-dev librtlsdr-dev git

# ดาวน์โหลดและ compile eti-stuff
cd ~
git clone https://github.com/JvanKatwijk/eti-stuff
cd eti-stuff
mkdir build && cd build
cmake .. -DRTLSDR=1
make -j4

# คัดลอก binary ไปยัง project directory
mkdir -p /home/pi/DAB_Plus_Labs/eti
cp eti-cmdline-rtlsdr /home/pi/DAB_Plus_Labs/eti/eti-cmdline

# ตรวจสอบการติดตั้ง
/home/pi/DAB_Plus_Labs/eti/eti-cmdline -h
```

### Phase 3: ETI Analysis & Audio Tools (ni2out)
```bash
# ติดตั้ง dependencies สำหรับ eti-tools
sudo apt install -y cmake build-essential libfftw3-dev icecast2

# ดาวน์โหลดและ compile eti-tools
cd ~
git clone https://github.com/piratfm/eti-tools
cd eti-tools
make

# คัดลอก binary ไปยัง project directory
cp ni2out /home/pi/DAB_Plus_Labs/eti/ni2out

# ตรวจสอบการติดตั้ง
/home/pi/DAB_Plus_Labs/eti/ni2out -h
```

### Phase 4: Audio Playback
```bash
# ติดตั้ง audio dependencies
sudo apt install -y ffmpeg alsa-utils pulseaudio
pip install ffmpeg-python pyaudio pillow numpy

# ตั้งค่า audio output (3.5mm jack)
sudo raspi-config nonint do_audio 1

# ทดสอบ audio
speaker-test -c2 -t wav
```

### Phase 5: GUI Application
```bash
# ติดตั้ง PyQt5 และ dependencies
sudo apt install -y python3-pyqt5 python3-pyqt5-dev
pip install PyQt5 pyqtgraph matplotlib

# ติดตั้ง DAB viewers (สำหรับดู MOT slideshow)
sudo apt install -y dablin welle-io

# ตั้งค่า touchscreen (สำหรับ 7" HDMI)
sudo apt install -y xinput-calibrator
```

## ขั้นตอนการทำงาน

### Phase 1: RTL-SDR Data Acquisition

#### ขั้นตอนที่ 1.1: ทดสอบ RTL-SDR พื้นฐาน (lab3_1a.py)
```bash
cd /home/pi/DAB_Plus_Labs/Labs/Lab3
python3 lab3_1a.py
```

**สิ่งที่เกิดขึ้น:**
1. เชื่อมต่อ RTL-SDR กับ Raspberry Pi
2. ตั้งค่าความถี่ DAB+ Thailand (185.360 MHz)
3. รับ I/Q samples และบันทึกเป็นไฟล์
4. วิเคราะห์สเปกตรัมเบื้องต้น

**Output:**
- `raw_iq_data.bin` - I/Q samples (complex64)
- `spectrum_analysis.png` - กราฟสเปกตรัม

#### ขั้นตอนที่ 1.2: RTL-TCP Client (lab3_1b.py)
```bash
# Terminal 1: เริ่ม rtl_tcp server
python3 lab3_1b.py --start-server

# Terminal 2: รับข้อมูลผ่าน network
python3 lab3_1b.py
```

**Output:**
- `networked_iq_data.bin` - I/Q samples จาก network
- `spectrum_analysis_rtltcp.png`

### Phase 2: DAB+ Signal Processing

#### ขั้นตอนที่ 2: ETI Stream Generation (lab3_2.py)
```bash
cd /home/pi/DAB_Plus_Labs/Labs/Lab3
python3 lab3_2.py
```

**Tool Used:** `/home/pi/DAB_Plus_Labs/eti/eti-cmdline`

**สิ่งที่เกิดขึ้น:**
1. ใช้ eti-cmdline แปลง I/Q เป็น ETI stream
2. รับสัญญาณ DAB+ จาก RTL-SDR โดยตรง
3. ติดตามสถานะ sync และ signal quality
4. บันทึก ETI stream และ JSON metadata

**Output:**
- `dab_ensemble.eti` - ETI stream (6144 bytes/frame, ~1052 frames, ~25 seconds)
- `ensemble-ch-6C.json` - Station list และ metadata

**คำสั่งที่สร้าง:**
```bash
/home/pi/DAB_Plus_Labs/eti/eti-cmdline \
  -C 6C \
  -B BAND_III \
  -O dab_ensemble.eti \
  -G 50 \
  -t 30 \
  -J
```

### Phase 3: ETI Analysis

#### ขั้นตอนที่ 3: Service Discovery (lab3_3.py)
```bash
cd /home/pi/DAB_Plus_Labs/Labs/Lab3
python3 lab3_3.py
```

**สิ่งที่เกิดขึ้น:**
1. อ่าน `ensemble-ch-6C.json` จาก lab3_2
2. แปลง station list เป็น service format
3. สร้าง service_list.json และ subchannel_info.json

**Output:**
- `service_list.json` - รายการ 18 DAB+ services
- `subchannel_info.json` - ข้อมูล subchannels

**Services พบ:**
- BOONMA TV (0xA001)
- JKP TEST04-18 (0xA004-0xA018)
- KKN MAHA NAKHON (0xA003)
- SMARTRadio KK (0xA002)

### Phase 4: Audio Playback

#### ขั้นตอนที่ 4: Service Player (lab3_4.py)
```bash
cd /home/pi/DAB_Plus_Labs/Labs/Lab3

# แสดงรายการ services
python3 lab3_4.py -l

# เล่น service ที่เลือก
python3 lab3_4.py -s 0xa001

# แสดงข้อมูลการ extract MOT slideshow
python3 lab3_4.py --mot-info
```

**Tool Used:** `/home/pi/DAB_Plus_Labs/eti/ni2out`

**สิ่งที่เกิดขึ้น:**
1. โหลด service list จาก `service_list.json`
2. ใช้ ni2out แยกเสียง AAC จาก ETI stream
3. ใช้ ffmpeg decode AAC → PCM WAV
4. เล่นเสียงผ่าน PyAudio (3.5mm jack)

**Output:**
- `extracted_audio/service_0xA001_*.aac` - AAC audio (178 KB, ~10 seconds)
- `extracted_audio/service_0xA001_*_pcm.wav` - PCM audio (4.8 MB, 48kHz stereo)
- `slideshow_images/*.png` - Mock slideshow images (demo)

**คำสั่งที่ใช้ภายใน:**
```bash
# Extract audio
/home/pi/DAB_Plus_Labs/eti/ni2out -i dab_ensemble.eti -s 0xa001 > output.aac

# Decode to PCM
ffmpeg -i output.aac -f wav -acodec pcm_s16le -ar 48000 -ac 2 output.wav
```

**หมายเหตุสำคัญ - MOT Slideshow Extraction:**

⚠️ **ni2out ไม่รองรับ MOT extraction** - ni2out เป็นเครื่องมือสำหรับแยกเสียงเท่านั้น

**วิธีดู MOT slideshow จริง:**
1. **dablin_gtk** (แนะนำ):
   ```bash
   dablin_gtk -i dab_ensemble.eti
   ```
   - แสดง MOT slideshow ใน GUI
   - ไม่มี CLI export option

2. **XPADxpert** (Java tool):
   ```bash
   java -jar XPADxpert.jar dab_ensemble.eti
   ```
   - วิเคราะห์ ETI และ MOT data
   - บันทึก slides ผ่าน GUI (double-click)
   - ดาวน์โหลด: https://www.basicmaster.de/xpadxpert/

3. **welle-io**:
   ```bash
   welle-io
   ```
   - GUI application สำหรับ DAB reception
   - รองรับ MOT slideshow display

**สำหรับ lab นี้:**
- ใช้ **mock/demo images** เพื่อแสดง concept
- นักศึกษาสามารถใช้ dablin_gtk/XPADxpert ดู MOT จริง

### Phase 5: Complete GUI

#### ขั้นตอนที่ 5: GUI Application (lab3_5.py)
```bash
cd /home/pi/DAB_Plus_Labs/Labs/Lab3

# Run GUI application
python3 lab3_5.py

# Run fullscreen (สำหรับ 7" touchscreen)
python3 lab3_5.py --fullscreen
```

**Features:**
1. **Service List Widget**: โหลดจาก service_list.json
2. **Audio Control**: Real extraction ด้วย ni2out + PyAudio
3. **Spectrum Analyzer**: Real-time visualization (pyqtgraph)
4. **Signal Quality**: SNR, BER, signal strength indicators
5. **Slideshow Viewer**: MOT images (mock/demo)
6. **Settings Panel**: RTL-SDR configuration

**Integration:**
- Import `DABServicePlayer` จาก lab3_4.py
- Real audio extraction ด้วย ni2out
- QMediaPlayer สำหรับ playback
- PyQt5 GUI framework

## Data Flow Pipeline

```
RTL-SDR Hardware
     ↓
[Lab 3-1a/1b] I/Q Data Acquisition
     ↓ raw_iq_data.bin
     ↓
[Lab 3-2] ETI Stream Creation (eti-cmdline)
     ↓ dab_ensemble.eti + ensemble-ch-6C.json
     ↓
[Lab 3-3] ETI Analysis
     ↓ service_list.json + subchannel_info.json
     ↓
[Lab 3-4] Audio Extraction (ni2out) & Playback
     ↓ extracted_audio/*.aac + *.wav
     ↓
[Lab 3-5] Complete GUI Application (PyQt5)
     └─→ Integrated player
```

## Tool Paths Summary

| Tool | Path | Purpose |
|------|------|---------|
| eti-cmdline | `/home/pi/DAB_Plus_Labs/eti/eti-cmdline` | I/Q → ETI conversion |
| ni2out | `/home/pi/DAB_Plus_Labs/eti/ni2out` | ETI → Audio extraction |
| dablin | `/usr/bin/dablin` | ETI playback (CLI) |
| dablin_gtk | `/usr/bin/dablin_gtk` | ETI playback + MOT viewer (GUI) |
| welle-io | `/usr/bin/welle-io` | DAB+ receiver (GUI) |

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

### ปัญหา eti-cmdline not found:
```bash
# ตรวจสอบว่า binary อยู่ที่ไหน
ls -la /home/pi/DAB_Plus_Labs/eti/eti-cmdline

# ถ้าไม่มี ให้ compile ใหม่
cd ~/eti-stuff/build
make
cp eti-cmdline-rtlsdr /home/pi/DAB_Plus_Labs/eti/eti-cmdline
chmod +x /home/pi/DAB_Plus_Labs/eti/eti-cmdline
```

### ปัญหา ni2out not found:
```bash
# ตรวจสอบว่า binary อยู่ที่ไหน
ls -la /home/pi/DAB_Plus_Labs/eti/ni2out

# ถ้าไม่มี ให้ compile ใหม่
cd ~/eti-tools
make
cp ni2out /home/pi/DAB_Plus_Labs/eti/ni2out
chmod +x /home/pi/DAB_Plus_Labs/eti/ni2out
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

# ตั้งค่า Qt scaling
export QT_SCALE_FACTOR=1.0
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
3. **Tool Chain**: อธิบาย workflow จาก RTL-SDR → eti-cmdline → ni2out → audio output
4. **Signal Quality**: ปัจจัยใดบ้างที่ส่งผลต่อคุณภาพสัญญาณ DAB+?
5. **Audio Codec**: DAB+ ใช้ audio codec อะไร และมี bitrate ทั่วไปเท่าไหร่?
6. **MOT Slideshow**: ni2out สามารถ extract MOT slideshow ได้หรือไม่? ใช้เครื่องมือใดแทน?
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

### Audio Extraction Process:
```
ETI File (dab_ensemble.eti)
     ↓ ni2out -i input.eti -s 0xa001
AAC Audio Stream (HE-AAC, 48kHz)
     ↓ ffmpeg -i input.aac -f wav -acodec pcm_s16le
PCM WAV (48kHz, 16-bit, stereo)
     ↓ PyAudio
Audio Output (3.5mm jack)
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

## สรุป Workflow ทั้งหมด

```bash
# Step 1: Capture I/Q data
cd /home/pi/DAB_Plus_Labs/Labs/Lab3
python3 lab3_1a.py                    # → raw_iq_data.bin

# Step 2: Create ETI stream
python3 lab3_2.py                     # → dab_ensemble.eti + ensemble-ch-6C.json

# Step 3: Analyze ETI
python3 lab3_3.py                     # → service_list.json

# Step 4: Extract & play audio
python3 lab3_4.py -l                  # List services
python3 lab3_4.py -s 0xa001          # Play service
python3 lab3_4.py --mot-info         # MOT extraction info

# Step 5: Run GUI application
python3 lab3_5.py                     # Complete GUI receiver
```

## ข้อควรระวัง

1. **eti-cmdline path**: ต้องใช้ `/home/pi/DAB_Plus_Labs/eti/eti-cmdline` (ไม่ใช่ system-wide install)
2. **ni2out path**: ต้องใช้ `/home/pi/DAB_Plus_Labs/eti/ni2out`
3. **MOT extraction**: ni2out **ไม่รองรับ** MOT - ใช้ dablin_gtk หรือ XPADxpert แทน
4. **Audio format**: ni2out output เป็น AAC (HE-AAC) ต้อง decode ด้วย ffmpeg ก่อนเล่น
5. **Service ID format**: รองรับทั้ง hex (0xa001) และ decimal (40961)
