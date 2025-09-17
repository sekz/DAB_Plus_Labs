# LAB 2: การใช้งาน welle.io ผ่าน Python

## วัตถุประสงค์
- เรียนรู้การควบคุม welle.io เพื่อรับสัญญาณ DAB+
- สแกนหาสถานี DAB+ และเล่นเสียงผ่าน PyQt5 GUI
- จัดการข้อมูลเมทาดาต้า (ชื่อเพลง, ศิลปิน) และสไลด์โชว์
- พัฒนาระบบควบคุมเสียงสำหรับหน้าจอสัมผัส

## ความรู้พื้นฐานที่ต้องมี
- ความเข้าใจจาก Lab 1 (RTL-SDR พื้นฐาน)
- PyQt5 GUI programming และ QMediaPlayer
- ความรู้เกี่ยวกับ DAB+ protocol เบื้องต้น
- การทำงานของ subprocess และ threading

## อุปกรณ์ที่ใช้
- **Raspberry Pi 4** พร้อม RTL-SDR V4 dongle (จาก Lab 1)
- **หน้าจอสัมผัส HDMI 7"** สำหรับควบคุม GUI
- **หูฟัง 3.5mm** สำหรับฟังเสียง DAB+
- **เสาอากาศ DAB/FM** ที่มีประสิทธิภาพดี
- **การเชื่อมต่อเน็ต** สำหรับดาวน์โหลด welle.io

## การเตรียมระบบ

### คำสั่งติดตั้ง welle.io และ Dependencies:

```bash
# อัพเดทระบบก่อน (ถ้ายังไม่ทำ)
sudo apt update && sudo apt upgrade -y

# ติดตั้ง Qt5 development packages สำหรับ welle.io
sudo apt install -y qt5-qmake qtbase5-dev qtchooser
sudo apt install -y qtmultimedia5-dev libqt5multimedia5-plugins
sudo apt install -y qttools5-dev-tools

# ติดตั้ง audio codecs และ libraries
sudo apt install -y libfaad-dev libmpg123-dev libfftw3-dev
sudo apt install -y libasound2-dev pulseaudio pavucontrol

# ติดตั้ง build tools (ถ้ายังไม่มี)
sudo apt install -y cmake build-essential git pkg-config

# ติดตั้ง Python multimedia packages
sudo apt install -y python3-pyqt5.qtmultimedia
pip3 install pydub soundfile
```

### คอมไพล์และติดตั้ง welle.io จากซอร์ส:

```bash
# สร้างไดเรกทอรีสำหรับ compile
cd /tmp

# ดาวน์โหลด welle.io source code
git clone https://github.com/AlbrechtL/welle.io.git
cd welle.io

# สร้าง build directory
mkdir build && cd build

# Configure build ด้วย CMAKE
cmake .. -DRTLSDR=ON -DCLI=ON -DGUI=ON -DPROFILING=OFF

# คอมไพล์ (อาจใช้เวลา 15-30 นาที)
make -j$(nproc)

# ติดตั้ง
sudo make install

# อัพเดท library cache
sudo ldconfig

# ทดสอบการติดตั้ง
which welle-io
welle-io --help
```

### ตั้งค่า Audio Output สำหรับ 3.5mm Jack:

```bash
# ตั้งค่าให้เสียงออกทาง 3.5mm jack
sudo raspi-config nonint do_audio 1

# ตั้งค่า ALSA default device
cat > ~/.asoundrc << 'EOF'
pcm.!default {
    type hw
    card 0
    device 0
}
ctl.!default {
    type hw
    card 0
}
EOF

# รีสตาร์ท audio service
sudo systemctl restart alsa-state
pulseaudio -k  # รีสตาร์ท PulseAudio

# ทดสอบเสียง
speaker-test -t wav -c 2 -l 1
```

### ตั้งค่า permissions สำหรับ Audio:

```bash
# เพิ่ม user ใน audio group
sudo usermod -a -G audio $USER

# ตั้งค่า PulseAudio สำหรับ system mode (ถ้าจำเป็น)
sudo systemctl --global disable pulseaudio.service pulseaudio.socket
sudo systemctl enable pulseaudio.service

# logout และ login ใหม่
```

## ขั้นตอนการทำงาน

### 1. ทดสอบ welle.io Command Line

```bash
# ทดสอบการทำงานพื้นฐาน
welle-io --help

# ลองรันแบบ headless (ไม่มี GUI)
welle-io -c headless_mode

# ทดสอบ scan ความถี่ (ตัวอย่าง 5A = 174.928 MHz)
welle-io -c headless_mode -f 174928000
```

### 2. ทำความเข้าใจความถี่ DAB+ ในประเทศไทย

| Channel | Frequency (MHz) | Block |
|---------|-----------------|-------|
| 5A      | 174.928        | III   |
| 5B      | 176.640        | III   |
| 5C      | 178.352        | III   |
| 5D      | 180.064        | III   |
| 6A      | 181.936        | III   |
| 6B      | 183.648        | III   |
| 6C      | 185.360        | III   |
| 6D      | 187.072        | III   |
| 7A      | 188.928        | III   |
| 7B      | 190.640        | III   |
| 7C      | 192.352        | III   |
| 7D      | 194.064        | III   |

### 3. เรียกใช้งาน Lab GUI

```bash
cd Labs/Lab2
python3 lab2.py
```

## การเขียนโค้ด

### ส่วนที่ต้องเติมใน `lab2.py`:

#### 1. คลาส WelleIOController:

```python
class WelleIOController(QThread):
    station_found = pyqtSignal(dict)
    audio_data = pyqtSignal(str)  # audio file path
    metadata_update = pyqtSignal(dict)
    slideshow_update = pyqtSignal(str)  # image path
    error_occurred = pyqtSignal(str)
    
    def start_welle_io(self, frequency=None):
        try:
            cmd = ['welle-io', '-c', 'headless_mode']
            if frequency:
                cmd.extend(['-f', str(int(frequency * 1000000))])  # MHz -> Hz
            
            self.welle_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # ติดตาม output ใน thread แยก
            self.start()  # เริ่ม run() method
            
        except Exception as e:
            self.error_occurred.emit(f"เริ่ม welle.io ไม่ได้: {str(e)}")
```

#### 2. การสแกนหาสถานี:

```python
def scan_dab_stations(self, frequency_range=None):
    """สแกนหาสถานี DAB+ ในช่วงความถี่ที่กำหนด"""
    if not frequency_range:
        # ความถี่ DAB+ Band III สำหรับไทย
        frequency_range = [174.928, 176.640, 178.352, 180.064, 181.936, 
                          183.648, 185.360, 187.072, 188.928, 190.640]
    
    for freq in frequency_range:
        try:
            # รัน welle-io สำหรับแต่ละความถี่
            result = subprocess.run(
                ['welle-io', '-c', 'headless_mode', '-f', str(int(freq * 1000000))],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # แปลงผลลัพธ์เป็นข้อมูลสถานี
            stations = self.parse_ensemble_info(result.stdout, freq)
            
            for station in stations:
                self.station_found.emit(station)
                
        except subprocess.TimeoutExpired:
            continue
        except Exception as e:
            self.error_occurred.emit(f"สแกนความถี่ {freq} MHz ล้มเหลว: {str(e)}")
```

#### 3. การเล่นเสียง:

```python
class AudioPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.media_player = QMediaPlayer()
        self.setup_ui()
        self.setup_audio_connections()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # ปุ่มควบคุม
        control_layout = QHBoxLayout()
        self.play_btn = QPushButton(" เล่น")
        self.stop_btn = QPushButton(" หยุด")
        self.play_btn.setMinimumSize(80, 50)
        self.stop_btn.setMinimumSize(80, 50)
        
        control_layout.addWidget(self.play_btn)
        control_layout.addWidget(self.stop_btn)
        layout.addLayout(control_layout)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel(" เสียง:"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMinimumHeight(40)
        volume_layout.addWidget(self.volume_slider)
        layout.addLayout(volume_layout)
        
        # สถานะ
        self.status_label = QLabel("พร้อมเล่น")
        layout.addWidget(self.status_label)
        
    def setup_audio_connections(self):
        self.play_btn.clicked.connect(self.play_audio)
        self.stop_btn.clicked.connect(self.stop_audio)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.media_player.stateChanged.connect(self.on_state_changed)
        
    def play_audio(self, audio_source=None):
        if audio_source:
            # เล่นจากไฟล์หรือ stream
            if os.path.exists(audio_source):
                url = QUrl.fromLocalFile(audio_source)
                self.media_player.setMedia(QMediaContent(url))
            else:
                # Stream URL
                url = QUrl(audio_source)
                self.media_player.setMedia(QMediaContent(url))
        
        self.media_player.play()
        
    def stop_audio(self):
        self.media_player.stop()
        
    def set_volume(self, volume):
        self.media_player.setVolume(volume)
```

#### 4. การจัดการ Metadata และ Slideshow:

```python
class MetadataWidget(QWidget):
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Metadata display
        metadata_group = QGroupBox("ข้อมูลเพลง")
        metadata_layout = QVBoxLayout(metadata_group)
        
        self.song_label = QLabel("ชื่อเพลง: -")
        self.artist_label = QLabel("ศิลปิน: -")
        self.album_label = QLabel("อัลบั้ม: -")
        self.extra_label = QLabel("ข้อมูลเพิ่มเติม: -")
        
        # ปรับ font size สำหรับหน้าจอสัมผัส
        for label in [self.song_label, self.artist_label, self.album_label]:
            label.setStyleSheet("font-size: 12px; padding: 5px;")
            label.setWordWrap(True)
        
        metadata_layout.addWidget(self.song_label)
        metadata_layout.addWidget(self.artist_label)
        metadata_layout.addWidget(self.album_label)
        metadata_layout.addWidget(self.extra_label)
        layout.addWidget(metadata_group)
        
        # Slideshow display
        slideshow_group = QGroupBox("สライด์โชว์")
        slideshow_layout = QVBoxLayout(slideshow_group)
        
        self.slideshow_label = QLabel("ไม่มีรูปภาพ")
        self.slideshow_label.setMinimumSize(200, 150)
        self.slideshow_label.setAlignment(Qt.AlignCenter)
        self.slideshow_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)
        slideshow_layout.addWidget(self.slideshow_label)
        
        # ปุ่มบันทึกรูป
        self.save_image_btn = QPushButton(" บันทึกรูป")
        self.save_image_btn.setMinimumSize(120, 40)
        slideshow_layout.addWidget(self.save_image_btn)
        
        layout.addWidget(slideshow_group)
        
    def update_metadata(self, metadata):
        """อัพเดท metadata"""
        self.song_label.setText(f"ชื่อเพลง: {metadata.get('title', '-')}")
        self.artist_label.setText(f"ศิลปิน: {metadata.get('artist', '-')}")
        self.album_label.setText(f"อัลบั้ม: {metadata.get('album', '-')}")
        self.extra_label.setText(f"ข้อมูลเพิ่มเติม: {metadata.get('extra', '-')}")
        
    def update_slideshow(self, image_path):
        """อัพเดทรูป slideshow"""
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            # ปรับขนาดให้พอดีกับ label
            scaled_pixmap = pixmap.scaled(
                self.slideshow_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.slideshow_label.setPixmap(scaled_pixmap)
            self.current_image_path = image_path
        else:
            self.slideshow_label.setText("ไม่สามารถโหลดรูปภาพได้")
```

#### 5. การจัดการ Main Window:

```python
def setup_ui(self):
    central_widget = QWidget()
    self.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)
    
    # Title
    title_label = QLabel("LAB 2: การใช้งาน welle.io ผ่าน Python")
    title_label.setAlignment(Qt.AlignCenter)
    title_label.setStyleSheet("""
        font-size: 18px; font-weight: bold; color: #2c3e50;
        padding: 10px; background-color: #ecf0f1; border-radius: 8px;
    """)
    main_layout.addWidget(title_label)
    
    # ปุ่มควบคุม
    button_layout = QHBoxLayout()
    self.start_btn = QPushButton(" เริ่ม welle.io")
    self.scan_btn = QPushButton(" สแกนสถานี")
    self.play_btn = QPushButton(" เล่น")
    self.record_btn = QPushButton(" บันทึก")
    
    # ตั้งขนาดปุ่มสำหรับหน้าจอสัมผัส
    for btn in [self.start_btn, self.scan_btn, self.play_btn, self.record_btn]:
        btn.setMinimumSize(120, 50)
        btn.setStyleSheet("""
            QPushButton {
                border: 2px solid #34495e;
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:pressed {
                background: #2980b9;
            }
        """)
    
    button_layout.addWidget(self.start_btn)
    button_layout.addWidget(self.scan_btn)
    button_layout.addWidget(self.play_btn)
    button_layout.addWidget(self.record_btn)
    main_layout.addLayout(button_layout)
    
    # พื้นที่หลัก - 3 คอลัมน์
    content_splitter = QSplitter(Qt.Horizontal)
    
    # 1. Station List (ซ้าย)
    self.station_widget = StationListWidget()
    content_splitter.addWidget(self.station_widget)
    
    # 2. Audio Player (กลาง)
    self.audio_widget = AudioPlayer()
    content_splitter.addWidget(self.audio_widget)
    
    # 3. Metadata & Slideshow (ขวา)
    self.metadata_widget = MetadataWidget()
    content_splitter.addWidget(self.metadata_widget)
    
    # กำหนดอัตราส่วนขนาด
    content_splitter.setSizes([300, 300, 300])
    main_layout.addWidget(content_splitter, 1)
    
    # Status bar
    self.status_label = QLabel("พร้อมใช้งาน - เริ่มต้นด้วยการกด 'เริ่ม welle.io'")
    self.status_label.setStyleSheet("padding: 5px; background-color: #ecf0f1;")
    main_layout.addWidget(self.status_label)
```

### คำแนะนำการเขียน:

1. **ใช้ subprocess.Popen()** สำหรับควบคุม welle.io แบบ interactive
2. **ใช้ QThread** สำหรับการประมวลผลที่ใช้เวลานาน
3. **ใช้ QMediaPlayer** สำหรับเล่นเสียงผ่าน Qt framework
4. **จัดการ metadata** ด้วย JSON หรือ text parsing
5. **ใช้ QPixmap** สำหรับแสดงรูป slideshow

## ผลลัพธ์ที่คาดหวัง

### 1. GUI Application ที่สมบูรณ์:
- หน้าต่างแบ่งเป็น 3 ส่วน: สถานี, เครื่องเล่น, metadata
- ปุ่มควบคุมขนาดใหญ่เหมาะกับหน้าจอสัมผัส
- การแสดงข้อมูลแบบ real-time
- Volume control พร้อม slider

### 2. การทำงานของระบบ:
```
 เริ่ม welle.io...
 welle.io เริ่มต้นสำเร็จ

 กำลังสแกนสถานี DAB+...
 พบสถานี: Thai PBS Radio (174.928 MHz)
 พบสถานี: NBT Radio (176.640 MHz)
 พบสถานี: Voice TV Radio (178.352 MHz)

 เริ่มเล่นเสียง: Thai PBS Radio
 กำลังเล่น: เพลงไทย - ศิลปินไทย
️ รับ slideshow: โลโก้ Thai PBS

 เริ่มบันทึก...
 บันทึกลง: recordings/thai_pbs_20241208_143000.wav
```

### 3. ไฟล์ที่สร้างขึ้น:
- `recordings/*.wav`: ไฟล์เสียงที่บันทึก
- `slideshows/*.jpg`: รูปภาพ slideshow
- `metadata/*.json`: ข้อมูล metadata
- `station_list.json`: รายการสถานีที่พบ

## การแก้ไขปัญหา

### ปัญหา 1: welle.io ไม่ทำงาน

**อาการ**: `welle-io` command ไม่พบหรือ error

**วิธีแก้**:
```bash
# ตรวจสอบการติดตั้ง
which welle-io
ldd $(which welle-io)  # ตรวจสอบ libraries

# ติดตั้งใหม่จาก source
cd /tmp/welle.io/build
sudo make uninstall
sudo make install
sudo ldconfig
```

### ปัญหา 2: ไม่มีเสียง

**อาการ**: GUI ทำงานแต่ไม่ได้ยินเสียง

**วิธีแก้**:
```bash
# ตรวจสอบ audio devices
aplay -l
amixer scontrols

# ตั้งค่า default audio output
sudo raspi-config  # เลือก Advanced Options > Audio > Force 3.5mm

# ทดสอบเสียง
speaker-test -t wav -c 2
```

### ปัญหา 3: ไม่พบสถานี DAB+

**อาการ**: สแกนแล้วไม่เจอสถานี

**วิธีแก้**:
```bash
# ตรวจสอบ RTL-SDR
rtl_test -t

# ตรวจสอบเสาอากาศ
# - ใช้เสา DAB/FM ที่มีประสิทธิภาพ
# - วางเสาในตำแหน่งที่เปิดโล่ง
# - หลีกเลี่ยงสัญญาณรบกวน

# ลองความถี่อื่น
welle-io -c headless_mode -f 181936000  # 6A channel
```

### ปัญหา 4: GUI ช้าหรือค้าง

**วิธีแก้**:
```python
# ตรวจสอบ threading ใน code
# ให้แน่ใจว่า long-running operations อยู่ใน QThread
# ใช้ signals/slots สำหรับการสื่อสาร

# เพิ่ม progress indicators
self.progress_bar.setValue(progress_value)
QApplication.processEvents()  # อัพเดท GUI ระหว่างประมวลผล
```

### ปัญหา 5: Slideshow ไม่แสดง

**วิธีแก้**:
```python
# ตรวจสอบการ decode รูปภาพ
def update_slideshow(self, image_path):
    if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(200, 150, Qt.KeepAspectRatio)
                self.slideshow_label.setPixmap(scaled_pixmap)
            else:
                self.slideshow_label.setText("ไม่สามารถโหลดรูปได้")
        except Exception as e:
            logger.error(f"Slideshow error: {str(e)}")
```

## 🎯 Trap Exercises LAB 2

### **Trap 2.1: DAB+ Frequency Planning**
ก่อนการ scan ให้นักเรียน:
- ศึกษาความถี่ DAB+ ในประเทศไทย (Band III: 174-240 MHz)
- เลือก 2-3 frequencies ที่น่าจะมี signal ในพื้นที่
- อธิบายความแตกต่างระหว่าง ensemble และ service
- คำนวณว่า RTL-SDR สามารถรับความถี่ไหนได้บ้าง

**ข้อมูลความถี่:**
```
DAB+ ในไทย (ตาม NBTC):
- Channel 5C: 178.352 MHz
- Channel 6C: 185.360 MHz
- Channel 7C: 192.352 MHz
- Channel 8C: 199.360 MHz
```

### **Trap 2.2: welle.io Integration Challenge**
หลังติดตั้ง welle.io ให้วิเคราะห์:
- ความแตกต่างระหว่าง command line และ GUI mode
- การ parse output จาก welle.io subprocess
- วิธีการส่งคำสั่งควบคุมไปยัง welle.io
- การ handle errors เมื่อ welle.io crash

**แบบฝึกหัด:**
```bash
# ทดสอบ welle.io command line
welle-io -h  # ดู help options
welle-io -c -D rtl_sdr -C 6C  # ทดสอบ channel 6C

# Monitor output การทำงาน
welle-io -v 2>&1 | tee welle_output.log
```

### **Trap 2.3: Audio Routing Investigation**
เมื่อได้เสียงจาก DAB+ แล้ว ให้ตรวจสอบ:
- การทำงานของ ALSA vs PulseAudio บน Pi
- คุณภาพเสียง (sample rate, bit depth) ของ DAB+
- การจัดการ audio buffer และ latency
- ความแตกต่างระหว่าง หูฟัง 3.5mm และ HDMI audio

**การทดลอง:**
```bash
# ตรวจสอบ audio devices
aplay -l
pacmd list-sinks

# ทดสอบ audio routing
pactl set-default-sink alsa_output.platform-soc_audio.analog-stereo

# Monitor audio levels
pavucontrol &  # GUI volume control
alsamixer      # Command line mixer
```

### **Trap 2.4: Metadata และ Slideshow Analysis**
ในส่วน metadata handling ให้อธิบาย:
- โครงสร้างของ PAD (Programme Associated Data)
- การ decode Dynamic Label Segment (DLS)
- รูปแบบของ MOT Slideshow (JPEG encoding)
- การ sync ระหว่าง audio และ visual data

**การทดลอง:**
```python
# ตัวอย่าง metadata structure
metadata_example = {
    'dls_text': 'ชื่อเพลง - ศิลปิน',
    'mot_image': '/tmp/slideshow.jpg',
    'program_type': 'Music',
    'bitrate': '128 kbps'
}

# วิเคราะห์ image file
from PIL import Image
img = Image.open('/tmp/slideshow.jpg')
print(f"Image size: {img.size}")
print(f"Image format: {img.format}")
```

### **Trap 2.5: GUI Threading และ Performance**
ในการเขียน GUI ให้วิเคราะห์:
- ทำไม audio processing ต้องอยู่ใน separate thread
- การใช้ QTimer vs QThread สำหรับ periodic updates
- Memory management สำหรับ slideshow images
- การ optimize GUI สำหรับ Raspberry Pi performance

**Performance Testing:**
```python
import psutil
import time

# Monitor resource usage
def monitor_performance():
    process = psutil.Process()
    cpu_percent = process.cpu_percent()
    memory_info = process.memory_info()
    print(f"CPU: {cpu_percent}%, Memory: {memory_info.rss / 1024 / 1024:.1f} MB")

# ทดสอบระหว่าง audio playback
timer = QTimer()
timer.timeout.connect(monitor_performance)
timer.start(5000)  # ทุก 5 วินาที
```

## คำถามทบทวน

1. **DAB+ แตกต่างจาก FM อย่างไร?**
   - ตอบ: DAB+ ใช้เทคโนโลยีดิจิทัล, คุณภาพเสียงดีกว่า, มี metadata และ slideshow

2. **ทำไมต้องใช้ QThread สำหรับ welle.io?**
   - ตอบ: welle.io ใช้เวลานานในการประมวลผล หาก run ใน main thread จะทำให้ GUI ค้าง

3. **QMediaPlayer vs กการเล่นเสียงแบบอื่น?**
   - ตอบ: QMediaPlayer integrate ดีกับ Qt, รองรับ audio routing และ volume control

4. **Slideshow ใน DAB+ ทำงานอย่างไร?**
   - ตอบ: ข้อมูลรูปภาพส่งผ่าน PAD (Programme Associated Data) ใน JPEG format

5. **การ tuning ไปยังสถานีต่างๆ ทำอย่างไร?**
   - ตอบ: ส่งคำสั่ง frequency และ service ID ไปยัง welle.io process

---

**หมายเหตุ**: Lab นี้ต้องการเสาอากาศที่ดีและสถานี DAB+ ในพื้นที่เพื่อให้ได้ผลลัพธ์ที่ชัดเจน