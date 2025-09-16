# LAB 2: การใช้งาน welle.io ผ่าน Python - เฉลย

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
cd Solutions/Lab2
python3 lab2.py
```

## อธิบายการเขียนโค้ด (เฉลย)

### 1. คลาส WelleIOController - การควบคุม welle.io process:

```python
class WelleIOController(QThread):
    """Thread หลักสำหรับควบคุม welle.io"""
    
    # Signals สำหรับสื่อสาร
    station_found = pyqtSignal(dict)        # พบสถานีใหม่
    audio_data = pyqtSignal(str)            # ข้อมูลเสียง
    metadata_update = pyqtSignal(dict)       # อัพเดท metadata
    slideshow_update = pyqtSignal(str)       # รูป slideshow
    error_occurred = pyqtSignal(str)         # แจ้งเตือน error
    
    def start_welle_io(self, frequency=None):
        """เริ่ม welle.io process"""
        try:
            cmd = ['welle-io']
            
            if frequency:
                # ใช้ headless mode พร้อม frequency
                cmd.extend(['-c', 'headless', '-f', str(int(frequency * 1000000))])
            else:
                # ใช้ GUI mode
                cmd.extend(['-c', 'gui'])
            
            # สร้าง subprocess
            self.welle_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # ตรวจสอบว่า process เริ่มสำเร็จ
            time.sleep(2)
            if self.welle_process.poll() is not None:
                stderr = self.welle_process.stderr.read()
                self.error_occurred.emit(f"welle.io หยุดทำงาน: {stderr}")
                return False
            
            self.start()  # เริ่ม monitoring thread
            return True
            
        except FileNotFoundError:
            self.error_occurred.emit("ไม่พบ welle-io command")
            return False
```

### 2. การสแกนสถานี DAB+:

```python
def scan_dab_stations(self, frequency_range=None):
    """สแกนหาสถานี DAB+ ในช่วงความถี่ที่กำหนด"""
    if not frequency_range:
        # ความถี่ DAB+ Band III สำหรับไทย
        frequency_range = {
            '5A': 174.928, '5B': 176.640, '5C': 178.352, '5D': 180.064,
            '6A': 181.936, '6B': 183.648, '6C': 185.360, '6D': 187.072,
            '7A': 188.928, '7B': 190.640, '7C': 192.352, '7D': 194.064,
            # ... ความถี่เพิ่มเติม
        }
    
    total_freq = len(frequency_range)
    
    for i, (channel, freq) in enumerate(frequency_range.items()):
        try:
            self.status_update.emit(f"สแกน Channel {channel} ({freq} MHz)...")
            self.scan_progress.emit(int((i / total_freq) * 100))
            
            # รัน welle-io สำหรับแต่ละความถี่
            result = subprocess.run(
                ['welle-io', '-c', 'headless', '-f', str(int(freq * 1000000))],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                # แปลงผลลัพธ์เป็นข้อมูลสถานี
                stations = self.parse_ensemble_info(result.stdout, freq, channel)
                
                for station in stations:
                    station['scan_time'] = datetime.now().isoformat()
                    station['signal_quality'] = self.estimate_signal_quality(result.stdout)
                    
                    self.stations.append(station)
                    self.station_found.emit(station)
                    
        except subprocess.TimeoutExpired:
            continue
        except Exception as e:
            continue
    
    self.scan_progress.emit(100)
    self.save_station_list()  # บันทึกรายการสถานี
```

### 3. การแปลงข้อมูลจาก welle.io output:

```python
def parse_ensemble_info(self, output, frequency, channel):
    """แปลงผลลัพธ์จาก welle.io เป็นข้อมูลสถานี"""
    stations = []
    
    try:
        lines = output.split('\n')
        current_station = {}
        
        for line in lines:
            line = line.strip()
            
            # ตรวจหาข้อมูลสถานี
            if 'Service:' in line or 'Programme:' in line:
                if current_station:
                    # บันทึกสถานีก่อนหน้า
                    current_station['frequency'] = frequency
                    current_station['channel'] = channel
                    stations.append(current_station.copy())
                
                # เริ่มสถานีใหม่
                station_name = line.split(':', 1)[1].strip() if ':' in line else line
                current_station = {
                    'name': station_name,
                    'frequency': frequency,
                    'channel': channel,
                    'type': 'DAB+',
                    'bitrate': 0,
                    'ensemble': ''
                }
                
            elif 'Ensemble:' in line and current_station:
                current_station['ensemble'] = line.split(':', 1)[1].strip()
                
            elif 'Bitrate:' in line and current_station:
                # แยก bitrate จาก text
                bitrate_match = re.search(r'(\d+)', line)
                if bitrate_match:
                    current_station['bitrate'] = int(bitrate_match.group(1))
        
        # เพิ่มสถานีสุดท้าย
        if current_station and current_station.get('name'):
            current_station['frequency'] = frequency
            current_station['channel'] = channel
            stations.append(current_station)
            
    except Exception as e:
        logger.error(f"แปลงข้อมูลสถานี error: {str(e)}")
    
    return stations
```

### 4. การจัดการเสียงด้วย QMediaPlayer:

```python
class AudioPlayer(QWidget):
    """Widget สำหรับควบคุมการเล่นเสียง"""
    
    def __init__(self):
        super().__init__()
        self.media_player = QMediaPlayer()
        self.current_audio_file = None
        self.setup_ui()
        self.setup_connections()
        
    def play_audio(self, audio_source=None):
        """เล่นเสียงจาก source ที่กำหนด"""
        try:
            if audio_source:
                self.load_audio_source(audio_source)
            
            if self.media_player.state() == QMediaPlayer.PausedState:
                # Resume จาก pause
                self.media_player.play()
            elif self.current_audio_file:
                # เล่นไฟล์ที่โหลดแล้ว
                self.media_player.play()
            else:
                self.status_label.setText("ไม่มีไฟล์สำหรับเล่น")
                return
            
            self.status_label.setText("กำลังเล่น...")
            
        except Exception as e:
            self.status_label.setText(f"เล่นไม่ได้: {str(e)}")
    
    def load_audio_source(self, audio_source):
        """โหลด audio source (ไฟล์หรือ stream)"""
        try:
            if os.path.exists(audio_source):
                # ไฟล์ในเครื่อง
                url = QUrl.fromLocalFile(audio_source)
                self.file_info_label.setText(f"ไฟล์: {os.path.basename(audio_source)}")
            else:
                # URL หรือ stream
                url = QUrl(audio_source)
                self.file_info_label.setText(f"Stream: {audio_source}")
            
            content = QMediaContent(url)
            self.media_player.setMedia(content)
            self.current_audio_file = audio_source
            
        except Exception as e:
            self.status_label.setText(f"โหลดไฟล์ไม่ได้: {str(e)}")
    
    def set_volume(self, volume):
        """ตั้งค่าระดับเสียง (0-100)"""
        self.media_player.setVolume(volume)
        self.volume_label.setText(f"{volume}%")
    
    def on_state_changed(self, state):
        """เมื่อสถานะการเล่นเปลี่ยน"""
        if state == QMediaPlayer.PlayingState:
            self.status_label.setText("กำลังเล่น")
        elif state == QMediaPlayer.PausedState:
            self.status_label.setText("พักการเล่น")
        elif state == QMediaPlayer.StoppedState:
            self.status_label.setText("หยุดแล้ว")
```

### 5. การจัดการ Metadata และ Slideshow:

```python
class MetadataWidget(QWidget):
    """Widget สำหรับแสดง metadata และ slideshow"""
    
    def update_metadata(self, metadata):
        """อัพเดท metadata จาก DAB+ DLS"""
        try:
            self.song_label.setText(f"ชื่อเพลง: {metadata.get('title', '-')}")
            self.artist_label.setText(f"ศิลปิน: {metadata.get('artist', '-')}")
            self.extra_label.setText(f"ข้อมูลเพิ่มเติม: {metadata.get('text', '-')}")
            
            # แสดงเวลาที่ได้รับข้อมูล
            if 'timestamp' in metadata:
                timestamp = datetime.fromisoformat(metadata['timestamp'])
                time_str = timestamp.strftime('%H:%M:%S')
                self.time_label.setText(f"เวลา: {time_str}")
            
            # อัพเดทสถิติ
            self.metadata_count += 1
            self.metadata_count_label.setText(f"จำนวน metadata: {self.metadata_count}")
            
        except Exception as e:
            logger.error(f"อัพเดท metadata error: {str(e)}")
    
    def update_slideshow(self, image_path):
        """อัพเดทรูป slideshow จาก DAB+ MOT"""
        try:
            if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
                pixmap = QPixmap(image_path)
                
                if not pixmap.isNull():
                    # ปรับขนาดให้พอดีกับ label โดยรักษาอัตราส่วน
                    scaled_pixmap = pixmap.scaled(
                        self.slideshow_label.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    
                    self.slideshow_label.setPixmap(scaled_pixmap)
                    self.current_image_path = image_path
                    
                    # อัพเดทสถิติ
                    self.slideshow_count += 1
                    self.slideshow_count_label.setText(f"จำนวนรูป: {self.slideshow_count}")
                else:
                    self.slideshow_label.setText("ไม่สามารถโหลดรูปภาพได้")
            else:
                self.slideshow_label.setText("ไฟล์รูปภาพไม่ถูกต้อง")
                
        except Exception as e:
            self.slideshow_label.setText(f"Error: {str(e)}")
```

### 6. การประมวลผล welle.io output แบบ real-time:

```python
def run(self):
    """Monitor welle.io process และ handle output"""
    if not self.welle_process:
        return
    
    try:
        while self.welle_process and self.welle_process.poll() is None:
            # อ่าน output จาก welle.io
            if self.welle_process.stdout:
                line = self.welle_process.stdout.readline()
                if line:
                    self.process_welle_output(line.strip())
            
            time.sleep(0.1)  # ป้องกันใช้ CPU มากเกินไป
            
    except Exception as e:
        logger.error(f"Monitor thread error: {str(e)}")

def process_welle_output(self, line):
    """ประมวลผล output จาก welle.io"""
    try:
        # ตรวจหา metadata updates (DLS - Dynamic Label Segment)
        if 'DLS:' in line:
            metadata_text = line.split('DLS:', 1)[1].strip()
            self.parse_metadata(metadata_text)
        
        # ตรวจหา slideshow data (MOT - Multimedia Object Transfer)
        elif 'Slideshow:' in line or 'MOT:' in line:
            self.process_slideshow_data(line)
        
        # ตรวจหา signal quality info
        elif 'SNR:' in line or 'Signal:' in line:
            self.process_signal_info(line)
            
    except Exception as e:
        logger.error(f"ประมวลผล welle output error: {str(e)}")

def parse_metadata(self, metadata_text):
    """แปลง metadata text เป็น structured data"""
    try:
        metadata = {
            'text': metadata_text,
            'timestamp': datetime.now().isoformat()
        }
        
        # พยายามแยก title และ artist จาก format "Artist - Title"
        if ' - ' in metadata_text:
            parts = metadata_text.split(' - ', 1)
            metadata['artist'] = parts[0].strip()
            metadata['title'] = parts[1].strip()
        else:
            metadata['title'] = metadata_text
            metadata['artist'] = ''
        
        self.metadata_update.emit(metadata)
        
        # บันทึก metadata ถ้ากำลังบันทึกอยู่
        if self.is_recording:
            self.save_metadata(metadata)
            
    except Exception as e:
        logger.error(f"แปลง metadata error: {str(e)}")
```

### 7. การจัดการ Main Window และ Touch Interface:

```python
def setup_touch_interface(self):
    """ปรับ UI สำหรับหน้าจอสัมผัส 7 นิ้ว"""
    # ตั้งค่า font ขนาดใหญ่
    font = QFont()
    font.setPointSize(11)
    font.setFamily("DejaVu Sans")
    self.setFont(font)
    
    # ปรับขนาด splitter handles ให้ใหญ่ขึ้น
    content_splitter = self.findChild(QSplitter)
    if content_splitter:
        content_splitter.setHandleWidth(8)
        content_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #bdc3c7;
                border: 1px solid #95a5a6;
            }
            QSplitter::handle:hover {
                background-color: #3498db;
            }
        """)

def setup_connections(self):
    """เชื่อม signals และ slots ทั้งหมด"""
    # ปุ่มควบคุมหลัก
    self.start_welle_btn.clicked.connect(self.start_welle_io)
    self.scan_btn.clicked.connect(self.scan_stations)
    self.play_btn.clicked.connect(self.start_playback)
    self.record_btn.clicked.connect(self.toggle_recording)
    self.stop_btn.clicked.connect(self.stop_all)
    
    # Station list events
    self.station_widget.station_selected.connect(self.on_station_selected)

def start_welle_io(self):
    """เริ่มต้น welle.io process"""
    try:
        if self.welle_controller and self.welle_controller.isRunning():
            QMessageBox.information(self, "แจ้งเตือน", "welle.io กำลังทำงานอยู่แล้ว")
            return
        
        self.start_welle_btn.setEnabled(False)
        
        # สร้าง controller ใหม่
        self.welle_controller = WelleIOController()
        
        # เชื่อม signals ทั้งหมด
        self.welle_controller.station_found.connect(self.station_widget.add_station)
        self.welle_controller.audio_data.connect(self.audio_widget.play_audio)
        self.welle_controller.metadata_update.connect(self.metadata_widget.update_metadata)
        self.welle_controller.slideshow_update.connect(self.metadata_widget.update_slideshow)
        self.welle_controller.error_occurred.connect(self.on_error)
        self.welle_controller.scan_progress.connect(self.station_widget.scan_progress.setValue)
        self.welle_controller.status_update.connect(self.status_label.setText)
        
        # เริ่ม welle.io
        success = self.welle_controller.start_welle_io()
        
        if success:
            self.scan_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
        else:
            self.start_welle_btn.setEnabled(True)
            
    except Exception as e:
        self.on_error(f"เริ่ม welle.io ไม่ได้: {str(e)}")
```

### 8. Helper Functions และ System Checks:

```python
def check_welle_io_installation():
    """ตรวจสอบการติดตั้ง welle.io"""
    try:
        result = subprocess.run(['welle-io', '--help'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            # แปลงข้อมูลเวอร์ชันจาก help output
            version = "Unknown"
            capabilities = []
            
            for line in result.stdout.split('\n'):
                if 'version' in line.lower():
                    version = line.strip()
                elif 'rtl' in line.lower():
                    capabilities.append('RTL-SDR')
                elif 'airspy' in line.lower():
                    capabilities.append('AirSpy')
            
            return True, version, capabilities
        else:
            return False, "Command failed", []
            
    except FileNotFoundError:
        return False, "welle-io not found", []
    except subprocess.TimeoutExpired:
        return False, "Command timeout", []
    except Exception as e:
        return False, str(e), []

def get_dab_frequencies():
    """ได้รายการความถี่ DAB+ สำหรับประเทศไทย"""
    return {
        # Band III DAB+ channels
        '5A': 174.928, '5B': 176.640, '5C': 178.352, '5D': 180.064,
        '6A': 181.936, '6B': 183.648, '6C': 185.360, '6D': 187.072,
        '7A': 188.928, '7B': 190.640, '7C': 192.352, '7D': 194.064,
        '8A': 195.936, '8B': 197.648, '8C': 199.360, '8D': 201.072,
        '9A': 202.928, '9B': 204.640, '9C': 206.352, '9D': 208.064,
        '10A': 209.936, '10B': 211.648, '10C': 213.360, '10D': 215.072,
        '11A': 216.928, '11B': 218.640, '11C': 220.352, '11D': 222.064,
        '12A': 223.936, '12B': 225.648, '12C': 227.360, '12D': 229.072
    }

def main():
    """ฟังก์ชันหลัก พร้อม system validation"""
    # ตรวจสอบ welle.io installation ก่อน
    installed, version, capabilities = check_welle_io_installation()
    
    if not installed:
        print(" ไม่พบ welle.io หรือติดตั้งไม่สมบูรณ์")
        print("โปรดติดตั้ง welle.io ตามคำแนะนำใน LAB2.md")
        print(f"สาเหตุ: {version}")
        return 1
    
    # สร้าง QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("DAB+ Lab 2")
    app.setApplicationVersion("1.0")
    
    # ตั้งค่า font สำหรับหน้าจอสัมผัส
    font = QFont()
    font.setPointSize(10)
    app.setFont(font)
    
    # สร้างและแสดง main window
    window = Lab2MainWindow()
    window.show()
    
    # แสดงข้อมูลการติดตั้ง
    if capabilities:
        window.status_label.setText(f"พร้อมใช้งาน - welle.io ({', '.join(capabilities)})")
    
    return app.exec_()
```

## ผลลัพธ์ที่คาดหวัง

### 1. GUI Application ที่สมบูรณ์:
- หน้าต่างขนาด 1000x700 แบ่งเป็น 3 คอลัมน์
- ปุ่มควบคุมขนาดใหญ่เหมาะกับหน้าจอสัมผัส
- การแสดงข้อมูลแบบ real-time
- ระบบจัดการเสียงครบถ้วน

### 2. การทำงานของระบบ (ตัวอย่าง):
```
 เริ่ม welle.io...
 welle.io เริ่มต้นสำเร็จ (RTL-SDR support)

 กำลังสแกนสถานี DAB+...
 สแกน Channel 5A (174.928 MHz)...
 พบสถานี: Thai PBS Radio
 พบสถานี: Thai PBS News

 สแกน Channel 5B (176.640 MHz)...
 พบสถานี: NBT Radio
 พบสถานี: NBT News

 สแกน Channel 5C (178.352 MHz)...
 พบสถานี: Voice TV Radio

สแกนเสร็จ - พบ 5 สถานี

 เลือกสถานี: Thai PBS Radio (174.928 MHz)
 เริ่มเล่นเสียง: Thai PBS Radio
 กำลังเล่น: เพลงไทยสมัยใหม่ - ศิลปินไทย
️ รับ slideshow: โลโก้ Thai PBS Radio
 Signal: 85%

 เริ่มบันทึก...
 บันทึกลง: dab_output/recordings/Thai_PBS_Radio_20241208_145030.wav
 บันทึก metadata: 25 รายการ
️ บันทึก slideshow: 3 รูป
```

### 3. ไฟล์ที่สร้างขึ้น:
```
dab_output/
├── recordings/
│   ├── Thai_PBS_Radio_20241208_145030.wav
│   ├── Thai_PBS_Radio_20241208_145030_metadata.json
│   └── stream_20241208_145030.wav
├── slideshows/
│   ├── slideshow_20241208_145045.jpg
│   ├── slideshow_20241208_145123.jpg
│   └── slideshow_20241208_145201.jpg
├── metadata/
│   └── Thai_PBS_Radio_metadata_history.json
└── station_list.json
```

### 4. ตัวอย่างไฟล์ station_list.json:
```json
[
  {
    "name": "Thai PBS Radio",
    "frequency": 174.928,
    "channel": "5A",
    "type": "DAB+",
    "bitrate": 128,
    "ensemble": "Thai Digital Radio",
    "scan_time": "2024-12-08T14:50:30",
    "signal_quality": 85.5
  },
  {
    "name": "NBT Radio",
    "frequency": 176.640,
    "channel": "5B", 
    "type": "DAB+",
    "bitrate": 96,
    "ensemble": "Government Broadcasting",
    "scan_time": "2024-12-08T14:50:45",
    "signal_quality": 72.3
  }
]
```

### 5. คุณสมบัติพิเศษของเฉลย:

#### **Threading และ Real-time Processing:**
- welle.io ทำงานใน background thread
- การสแกนไม่บล็อก GUI
- การประมวลผล metadata และ slideshow แบบ real-time
- การจัดการ signals/slots อย่างปลอดภัย

#### **Touch-Friendly Interface:**
- ปุ่มขนาดใหญ่ (minimum 50x110px)
- Font ขนาดเหมาะสม (10-12pt)
- Splitter handles ขนาด 8px
- Hover effects สำหรับ feedback

#### **Robust Error Handling:**
- ตรวจสอบการติดตั้ง welle.io ก่อนเริ่ม
- จัดการ subprocess timeouts
- Recovery จาก process crashes
- การแสดง error messages ที่เข้าใจง่าย

#### **Audio Management:**
- รองรับทั้งไฟล์และ stream
- Volume control พร้อม visual feedback
- State management (playing/paused/stopped)
- Audio format support (WAV, MP3, M4A, OGG)

#### **Data Persistence:**
- บันทึกรายการสถานีอัตโนมัติ
- Export ข้อมูลเป็น JSON
- การจัดเก็บ slideshow images
- Metadata history tracking

## การแก้ไขปัญหา (เพิ่มเติม)

### ปัญหา welle.io Process Management:

```python
# ตรวจสอบว่า process ยังทำงานอยู่หรือไม่
def is_welle_running(self):
    return (self.welle_process and 
            self.welle_process.poll() is None)

# จัดการกับ zombie processes
def cleanup_welle_process(self):
    if self.welle_process:
        try:
            self.welle_process.terminate()
            self.welle_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.welle_process.kill()
            self.welle_process.wait()
```

### ปัญหา Audio Latency และ Buffer:

```bash
# ปรับ ALSA buffer settings
echo "pcm.!default {
    type hw
    card 0
    device 0
    format S16_LE
    rate 48000
    channels 2
    period_size 1024
    buffer_size 4096
}" > ~/.asoundrc
```

### ปัญหา Threading และ GUI Updates:

```python
# ใช้ QTimer สำหรับ GUI updates ที่ปลอดภัย
def setup_gui_timer(self):
    self.gui_timer = QTimer()
    self.gui_timer.timeout.connect(self.update_gui_periodically)
    self.gui_timer.start(1000)  # อัพเดททุกวินาที

def update_gui_periodically(self):
    """อัพเดท GUI elements ที่ไม่ได้มาจาก signals"""
    if self.welle_controller:
        station_info = self.welle_controller.get_station_info()
        if station_info:
            self.status_label.setText(f"เล่น: {station_info['name']}")
```

### ปัญหา Memory Management:

```python
# จำกัดจำนวน metadata ใน memory
MAX_METADATA_HISTORY = 100

def add_metadata(self, metadata):
    self.metadata_history.append(metadata)
    
    # จำกัดขนาด history
    if len(self.metadata_history) > self.MAX_METADATA_HISTORY:
        self.metadata_history.pop(0)  # ลบตัวเก่าสุด

# ล้าง pixmap cache
def update_slideshow(self, image_path):
    # ล้าง pixmap เก่าก่อน
    self.slideshow_label.clear()
    
    # โหลดรูปใหม่
    pixmap = QPixmap(image_path)
    if not pixmap.isNull():
        scaled_pixmap = pixmap.scaled(...)
        self.slideshow_label.setPixmap(scaled_pixmap)
```

## คำถามทบทวน (พร้อมเฉลย)

1. **ทำไม welle.io ต้องรันใน subprocess แยก?**
   - **เฉลย**: welle.io เป็น external application ที่มี GUI และ I/O operations ของตัวเอง ไม่สามารถ integrate เป็น library ใน Python ได้โดยตรง

2. **การจัดการ DAB+ metadata (DLS) ทำงานอย่างไร?**
   - **เฉลย**: DLS (Dynamic Label Segment) ส่งข้อมูล text พร้อมกับ audio stream, เราจับจาก stdout ของ welle.io และแปลงเป็น structured data

3. **MOT Slideshow ใน DAB+ คืออะไร?**
   - **เฉลย**: MOT (Multimedia Object Transfer) เป็นกลไกส่งรูปภาพ (JPEG) พร้อมกับ audio, ใช้แสดงโลโก้ สถานี หรือ album art

4. **ทำไมต้องใช้ QMediaPlayer แทน direct audio handling?**
   - **เฉลย**: QMediaPlayer จัดการ audio formats, buffering, และ Qt integration ได้ดี รองรับหลาย platform และมี built-in error handling

5. **การ tuning ไปยังสถานีต่างๆ มีข้อจำกัดอะไร?**
   - **เฉลย**: RTL-SDR ต้องปรับความถี่ใหม่ทั้ง hardware, ใช้เวลา 2-3 วินาที, และต้องมี signal strength เพียงพอ

6. **วิธีการ optimize performance สำหรับ Raspberry Pi?**
   - **เฉลย**: ใช้ threading ถูกต้อง, จำกัด GUI updates, ปรับ audio buffer size, และ compile welle.io ด้วย optimization flags

---

**หมายเหตุ**: เฉลยนี้เป็นโค้ดที่ครบถ้วนและพร้อมใช้งานจริง รองรับการทำงานบน Raspberry Pi พร้อม RTL-SDR และหน้าจอสัมผัส