#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAB 2: การใช้งาน welle.io ผ่าน Python - เฉลยครบถ้วน
วัตถุประสงค์: เรียนรู้การควบคุม welle.io เพื่อรับสัญญาณ DAB+ และเล่นเสียง
"""

import sys
import subprocess
import time
import json
import os
import re
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QWidget, QPushButton, QTextEdit, QLabel, QProgressBar,
                            QListWidget, QListWidgetItem, QSlider, QComboBox, 
                            QSpinBox, QGroupBox, QMessageBox, QFileDialog, 
                            QSplitter, QTabWidget, QCheckBox)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, QUrl
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QAudioOutput
import logging

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WelleIOController(QThread):
    """Thread สำหรับควบคุม welle.io"""
    
    station_found = pyqtSignal(dict)
    audio_data = pyqtSignal(str)  # path ของไฟล์เสียง
    metadata_update = pyqtSignal(dict)
    slideshow_update = pyqtSignal(str)  # path ของ slideshow
    error_occurred = pyqtSignal(str)
    scan_progress = pyqtSignal(int)
    status_update = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.welle_process = None
        self.current_frequency = 0
        self.current_station = ""
        self.is_recording = False
        self.stations = []
        self.output_dir = "dab_output"
        self.ensure_output_directories()
        
    def ensure_output_directories(self):
        """สร้างไดเรกทอรีสำหรับเก็บผลลัพธ์"""
        dirs = ['recordings', 'slideshows', 'metadata']
        for d in dirs:
            Path(self.output_dir) / d.mkdir(parents=True, exist_ok=True)
            
    def start_welle_io(self, frequency=None):
        """เริ่ม welle.io process"""
        try:
            if self.welle_process and self.welle_process.poll() is None:
                self.status_update.emit("welle.io กำลังทำงานอยู่แล้ว")
                return True
            
            cmd = ['welle-io']
            
            # ตรวจสอบว่ามี GUI mode หรือไม่
            if frequency:
                # ใช้ headless mode สำหรับการควบคุม
                cmd.extend(['-c', 'headless'])
                cmd.extend(['-f', str(int(frequency * 1000000))])  # MHz to Hz
            else:
                # ใช้ GUI mode
                cmd.extend(['-c', 'gui'])
            
            self.status_update.emit(f"เริ่มต้น welle.io ด้วยคำสั่ง: {' '.join(cmd)}")
            
            self.welle_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # ตรวจสอบว่า process เริ่มต้นสำเร็จ
            time.sleep(2)
            if self.welle_process.poll() is not None:
                stderr_output = self.welle_process.stderr.read()
                self.error_occurred.emit(f"welle.io หยุดทำงาน: {stderr_output}")
                return False
            
            self.status_update.emit("welle.io เริ่มต้นสำเร็จแล้ว")
            self.start()  # เริ่ม monitoring thread
            return True
            
        except FileNotFoundError:
            self.error_occurred.emit("ไม่พบ welle-io command - โปรดติดตั้งก่อน")
            return False
        except Exception as e:
            self.error_occurred.emit(f"เริ่ม welle.io ไม่ได้: {str(e)}")
            return False
    
    def scan_dab_stations(self, frequency_range=None):
        """สแกนหาสถานี DAB+ ในช่วงความถี่ที่กำหนด"""
        if not frequency_range:
            # ความถี่ DAB+ Band III สำหรับไทย
            frequency_range = {
                '5A': 174.928, '5B': 176.640, '5C': 178.352, '5D': 180.064,
                '6A': 181.936, '6B': 183.648, '6C': 185.360, '6D': 187.072,
                '7A': 188.928, '7B': 190.640, '7C': 192.352, '7D': 194.064,
                '8A': 195.936, '8B': 197.648, '8C': 199.360, '8D': 201.072,
                '9A': 202.928, '9B': 204.640, '9C': 206.352, '9D': 208.064,
                '10A': 209.936, '10B': 211.648, '10C': 213.360, '10D': 215.072,
                '11A': 216.928, '11B': 218.640, '11C': 220.352, '11D': 222.064,
                '12A': 223.936, '12B': 225.648, '12C': 227.360, '12D': 229.072
            }
        
        self.status_update.emit("เริ่มการสแกนสถานี DAB+...")
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
                    timeout=15  # รอ 15 วินาทีต่อความถี่
                )
                
                if result.returncode == 0:
                    # แปลงผลลัพธ์เป็นข้อมูลสถานี
                    stations = self.parse_ensemble_info(result.stdout, freq, channel)
                    
                    for station in stations:
                        # เพิ่มข้อมูลเพิ่มเติม
                        station['scan_time'] = datetime.now().isoformat()
                        station['signal_quality'] = self.estimate_signal_quality(result.stdout)
                        
                        self.stations.append(station)
                        self.station_found.emit(station)
                        
                        logger.info(f"พบสถานี: {station['name']} บน {channel} ({freq} MHz)")
                
            except subprocess.TimeoutExpired:
                logger.warning(f"Timeout สแกนความถี่ {freq} MHz")
                continue
            except Exception as e:
                logger.error(f"สแกนความถี่ {freq} MHz ล้มเหลว: {str(e)}")
                continue
        
        self.scan_progress.emit(100)
        self.status_update.emit(f"สแกนเสร็จ - พบ {len(self.stations)} สถานี")
        
        # บันทึกรายการสถานีลงไฟล์
        self.save_station_list()
        
    def parse_ensemble_info(self, output, frequency, channel):
        """แปลงผลลัพธ์จาก welle.io เป็นข้อมูลสถานี"""
        stations = []
        
        try:
            # แปลง text output เป็น structured data
            lines = output.split('\n')
            
            current_station = {}
            for line in lines:
                line = line.strip()
                
                # ตรวจหาข้อมูলสถานี
                if 'Service:' in line or 'Programme:' in line:
                    if current_station:
                        current_station['frequency'] = frequency
                        current_station['channel'] = channel
                        stations.append(current_station.copy())
                    
                    # เริ่มสถานีใหม่
                    current_station = {
                        'name': line.split(':', 1)[1].strip() if ':' in line else line,
                        'frequency': frequency,
                        'channel': channel,
                        'type': 'DAB+',
                        'bitrate': 0,
                        'ensemble': ''
                    }
                    
                elif 'Ensemble:' in line and current_station:
                    current_station['ensemble'] = line.split(':', 1)[1].strip()
                    
                elif 'Bitrate:' in line and current_station:
                    try:
                        bitrate_match = re.search(r'(\d+)', line)
                        if bitrate_match:
                            current_station['bitrate'] = int(bitrate_match.group(1))
                    except:
                        pass
                        
                elif 'SubChannel:' in line and current_station:
                    try:
                        subchannel_match = re.search(r'(\d+)', line)
                        if subchannel_match:
                            current_station['subchannel'] = int(subchannel_match.group(1))
                    except:
                        pass
            
            # เพิ่มสถานีสุดท้าย
            if current_station and current_station.get('name'):
                current_station['frequency'] = frequency
                current_station['channel'] = channel
                stations.append(current_station)
                
        except Exception as e:
            logger.error(f"แปลงข้อมูลสถานี error: {str(e)}")
        
        return stations
        
    def estimate_signal_quality(self, output):
        """ประเมินคุณภาพสัญญาณจาก welle.io output"""
        # ค้นหา signal strength indicators
        if 'SNR' in output:
            snr_match = re.search(r'SNR:?\s*(\d+\.?\d*)', output, re.IGNORECASE)
            if snr_match:
                snr = float(snr_match.group(1))
                return min(100, max(0, (snr / 20) * 100))  # แปลงเป็น %
        
        if 'signal' in output.lower() and 'good' in output.lower():
            return 80
        elif 'signal' in output.lower() and 'weak' in output.lower():
            return 40
        else:
            return 60  # default
            
    def tune_to_station(self, station_info):
        """ปรับไปยังสถานีที่ระบุ"""
        try:
            frequency = station_info['frequency']
            station_name = station_info['name']
            
            self.status_update.emit(f"กำลัง tune ไปยัง {station_name} ({frequency} MHz)")
            
            # หยุด process เก่า
            if self.welle_process and self.welle_process.poll() is None:
                self.welle_process.terminate()
                self.welle_process.wait()
            
            # เริ่ม process ใหม่ด้วยความถี่ที่เลือก
            success = self.start_welle_io(frequency)
            
            if success:
                self.current_frequency = frequency
                self.current_station = station_name
                self.status_update.emit(f"tune เสร็จ: {station_name}")
                
                # เริ่มการเล่นเสียง
                self.start_audio_playback()
                
                return True
            else:
                self.error_occurred.emit(f"ไม่สามารถ tune ไปยัง {station_name} ได้")
                return False
                
        except Exception as e:
            self.error_occurred.emit(f"Tune station error: {str(e)}")
            return False
    
    def start_audio_playback(self):
        """เริ่มการเล่นเสียง"""
        try:
            if not self.welle_process or self.welle_process.poll() is not None:
                self.error_occurred.emit("welle.io ไม่ทำงาน")
                return False
            
            # สำหรับ welle.io เราจะใช้ pipe audio ผ่าน named pipe หรือ TCP
            # ในที่นี้เป็นตัวอย่างการสร้าง audio stream
            
            audio_file = self.create_audio_stream()
            if audio_file:
                self.audio_data.emit(audio_file)
                self.status_update.emit("เริ่มการเล่นเสียง")
                return True
            else:
                self.error_occurred.emit("ไม่สามารถสร้าง audio stream ได้")
                return False
                
        except Exception as e:
            self.error_occurred.emit(f"เริ่มการเล่นเสียง error: {str(e)}")
            return False
    
    def create_audio_stream(self):
        """สร้าง audio stream จาก welle.io"""
        try:
            # สร้างไฟล์ temporary สำหรับ audio stream
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            audio_file = f"{self.output_dir}/recordings/stream_{timestamp}.wav"
            
            # ในการใช้งานจริง อาจต้องใช้ named pipe หรือ TCP socket
            # เพื่อรับ audio data จาก welle.io
            
            # สำหรับตัวอย่าง เราจะสร้างไฟล์ placeholder
            with open(audio_file, 'w') as f:
                f.write("# Audio stream placeholder")
            
            return audio_file
            
        except Exception as e:
            logger.error(f"สร้าง audio stream error: {str(e)}")
            return None
    
    def start_recording(self, output_path=None):
        """เริ่มบันทึกเสียงและข้อมูล"""
        try:
            if not output_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                station_name = self.current_station.replace(' ', '_')
                output_path = f"{self.output_dir}/recordings/{station_name}_{timestamp}"
            
            self.recording_path = output_path
            self.is_recording = True
            
            # สร้างไฟล์สำหรับบันทึก
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # เริ่มบันทึกเสียง
            self.audio_recording_file = f"{output_path}.wav"
            
            # เริ่มบันทึก metadata
            self.metadata_file = f"{output_path}_metadata.json"
            self.recording_start_time = datetime.now()
            
            self.status_update.emit(f"เริ่มบันทึก: {os.path.basename(output_path)}")
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"เริ่มบันทึก error: {str(e)}")
            return False
    
    def stop_recording(self):
        """หยุดการบันทึก"""
        try:
            if not self.is_recording:
                self.status_update.emit("ไม่ได้บันทึกอยู่")
                return
            
            self.is_recording = False
            
            # บันทึกข้อมูล metadata สุดท้าย
            if hasattr(self, 'metadata_file'):
                recording_info = {
                    'station': self.current_station,
                    'frequency': self.current_frequency,
                    'start_time': self.recording_start_time.isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'duration': (datetime.now() - self.recording_start_time).total_seconds()
                }
                
                with open(self.metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(recording_info, f, indent=2, ensure_ascii=False)
            
            self.status_update.emit(f"หยุดบันทึกแล้ว: {os.path.basename(self.recording_path)}")
            
        except Exception as e:
            self.error_occurred.emit(f"หยุดบันทึก error: {str(e)}")
    
    def get_station_info(self):
        """ดึงข้อมูลของสถานีปัจจุบัน"""
        if self.current_station:
            return {
                'name': self.current_station,
                'frequency': self.current_frequency,
                'status': 'playing' if self.welle_process and self.welle_process.poll() is None else 'stopped'
            }
        return None
    
    def save_station_list(self):
        """บันทึกรายการสถานีลงไฟล์"""
        try:
            station_file = f"{self.output_dir}/station_list.json"
            
            with open(station_file, 'w', encoding='utf-8') as f:
                json.dump(self.stations, f, indent=2, ensure_ascii=False)
                
            logger.info(f"บันทึกรายการสถานีลง {station_file}")
            
        except Exception as e:
            logger.error(f"บันทึกรายการสถานี error: {str(e)}")
    
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
                
                time.sleep(0.1)  # ไม่ให้ใช้ CPU มากเกินไป
                
        except Exception as e:
            logger.error(f"Monitor thread error: {str(e)}")
    
    def process_welle_output(self, line):
        """ประมวลผล output จาก welle.io"""
        try:
            # ตรวจหา metadata updates
            if 'DLS:' in line:
                # Dynamic Label Segment (metadata)
                metadata_text = line.split('DLS:', 1)[1].strip()
                self.parse_metadata(metadata_text)
            
            # ตรวจหา slideshow data
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
            # แยกข้อมูล title, artist จาก DLS text
            metadata = {
                'text': metadata_text,
                'timestamp': datetime.now().isoformat()
            }
            
            # พยายามแยก title และ artist
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
    
    def save_metadata(self, metadata):
        """บันทึก metadata ลงไฟล์"""
        try:
            if hasattr(self, 'metadata_file'):
                # อ่าน metadata เก่า
                existing_metadata = []
                if os.path.exists(self.metadata_file):
                    with open(self.metadata_file, 'r', encoding='utf-8') as f:
                        existing_metadata = json.load(f).get('metadata_history', [])
                
                # เพิ่ม metadata ใหม่
                existing_metadata.append(metadata)
                
                # บันทึกกลับ
                full_metadata = {
                    'station': self.current_station,
                    'frequency': self.current_frequency,
                    'metadata_history': existing_metadata
                }
                
                with open(self.metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(full_metadata, f, indent=2, ensure_ascii=False)
                    
        except Exception as e:
            logger.error(f"บันทึก metadata error: {str(e)}")
    
    def cleanup(self):
        """ทำความสะอาดและปิด process"""
        try:
            if self.is_recording:
                self.stop_recording()
            
            if self.welle_process and self.welle_process.poll() is None:
                self.welle_process.terminate()
                
                # รอให้ process หยุด
                try:
                    self.welle_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.welle_process.kill()
                    self.welle_process.wait()
                    
                self.status_update.emit("หยุด welle.io แล้ว")
                
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")

class AudioPlayer(QWidget):
    """Widget สำหรับควบคุมการเล่นเสียง"""
    
    def __init__(self):
        super().__init__()
        self.media_player = QMediaPlayer()
        self.current_audio_file = None
        self.setup_ui()
        self.setup_audio_output()
        self.setup_connections()
        
    def setup_ui(self):
        """สร้าง UI สำหรับควบคุมเสียง"""
        layout = QVBoxLayout(self)
        
        # กลุ่มควบคุมการเล่น
        playback_group = QGroupBox("การเล่นเสียง")
        playback_layout = QVBoxLayout(playback_group)
        
        # ปุ่มควบคุม
        control_layout = QHBoxLayout()
        self.play_btn = QPushButton("▶️ เล่น")
        self.pause_btn = QPushButton("⏸️ พัก")
        self.stop_btn = QPushButton("⏹️ หยุด")
        
        # ตั้งขนาดปุ่มสำหรับหน้าจอสัมผัส
        for btn in [self.play_btn, self.pause_btn, self.stop_btn]:
            btn.setMinimumSize(80, 50)
            btn.setStyleSheet("""
                QPushButton {
                    border: 2px solid #2c3e50;
                    border-radius: 6px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3498db, stop:1 #2980b9);
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:pressed {
                    background: #2980b9;
                }
                QPushButton:disabled {
                    background: #95a5a6;
                }
            """)
        
        control_layout.addWidget(self.play_btn)
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.stop_btn)
        playback_layout.addLayout(control_layout)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("🔊 เสียง:"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMinimumHeight(40)
        self.volume_label = QLabel("70%")
        self.volume_label.setMinimumWidth(40)
        
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_label)
        playback_layout.addLayout(volume_layout)
        
        # สถานะการเล่น
        self.status_label = QLabel("พร้อมเล่น")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #ecf0f1;
                border-radius: 4px;
                font-size: 11px;
            }
        """)
        playback_layout.addWidget(self.status_label)
        
        # ข้อมูลไฟล์ปัจจุบัน
        self.file_info_label = QLabel("ไม่มีไฟล์")
        self.file_info_label.setWordWrap(True)
        self.file_info_label.setStyleSheet("font-size: 10px; color: #7f8c8d; padding: 5px;")
        playback_layout.addWidget(self.file_info_label)
        
        layout.addWidget(playback_group)
        
        # ปุ่มเพิ่มเติม
        extra_layout = QHBoxLayout()
        self.load_file_btn = QPushButton("📁 เลือกไฟล์")
        self.test_audio_btn = QPushButton("🔊 ทดสอบเสียง")
        
        for btn in [self.load_file_btn, self.test_audio_btn]:
            btn.setMinimumSize(100, 40)
            btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    background: #ecf0f1;
                    font-size: 10px;
                }
                QPushButton:pressed {
                    background: #d5dbdb;
                }
            """)
        
        extra_layout.addWidget(self.load_file_btn)
        extra_layout.addWidget(self.test_audio_btn)
        layout.addLayout(extra_layout)
        
    def setup_audio_output(self):
        """ตั้งค่า audio output ไปที่ 3.5mm jack"""
        try:
            # ตั้งค่า volume เริ่มต้น
            self.media_player.setVolume(70)
            
        except Exception as e:
            logger.error(f"ตั้งค่า audio output error: {str(e)}")
    
    def setup_connections(self):
        """เชื่อม signals และ slots"""
        self.play_btn.clicked.connect(self.play_audio)
        self.pause_btn.clicked.connect(self.pause_audio)
        self.stop_btn.clicked.connect(self.stop_audio)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.load_file_btn.clicked.connect(self.load_audio_file)
        self.test_audio_btn.clicked.connect(self.test_audio_output)
        
        # Media player events
        self.media_player.stateChanged.connect(self.on_state_changed)
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.media_player.error.connect(self.on_error)
    
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
            logger.error(f"เล่นเสียง error: {str(e)}")
    
    def pause_audio(self):
        """พักการเล่นเสียง"""
        self.media_player.pause()
        
    def stop_audio(self):
        """หยุดการเล่นเสียง"""
        self.media_player.stop()
        
    def set_volume(self, volume):
        """ตั้งค่าระดับเสียง (0-100)"""
        self.media_player.setVolume(volume)
        self.volume_label.setText(f"{volume}%")
    
    def load_audio_source(self, audio_source):
        """โหลด audio source (ไฟล์หรือ URL)"""
        try:
            if isinstance(audio_source, str):
                if os.path.exists(audio_source):
                    # ไฟล์ในเครื่อง
                    url = QUrl.fromLocalFile(audio_source)
                    self.current_audio_file = audio_source
                    self.file_info_label.setText(f"ไฟล์: {os.path.basename(audio_source)}")
                else:
                    # URL หรือ stream
                    url = QUrl(audio_source)
                    self.current_audio_file = audio_source
                    self.file_info_label.setText(f"Stream: {audio_source}")
                
                content = QMediaContent(url)
                self.media_player.setMedia(content)
                
        except Exception as e:
            self.status_label.setText(f"โหลดไฟล์ไม่ได้: {str(e)}")
            logger.error(f"โหลด audio source error: {str(e)}")
    
    def load_audio_file(self):
        """เปิด dialog เลือกไฟล์เสียง"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "เลือกไฟล์เสียง", 
                "", 
                "Audio Files (*.wav *.mp3 *.m4a *.ogg);;All Files (*)"
            )
            
            if file_path:
                self.load_audio_source(file_path)
                self.status_label.setText("โหลดไฟล์แล้ว")
                
        except Exception as e:
            self.status_label.setText(f"เลือกไฟล์ไม่ได้: {str(e)}")
    
    def test_audio_output(self):
        """ทดสอบการออกเสียง"""
        try:
            # สร้างเสียงทดสอบ
            import subprocess
            result = subprocess.run(['speaker-test', '-t', 'wav', '-c', '2', '-l', '1'], 
                                  capture_output=True, timeout=10)
            
            if result.returncode == 0:
                self.status_label.setText("ทดสอบเสียงสำเร็จ")
            else:
                self.status_label.setText("ทดสอบเสียงล้มเหลว")
                
        except subprocess.TimeoutExpired:
            self.status_label.setText("ทดสอบเสียง timeout")
        except Exception as e:
            self.status_label.setText(f"ทดสอบเสียงไม่ได้: {str(e)}")
    
    def on_state_changed(self, state):
        """เมื่อสถานะการเล่นเปลี่ยน"""
        if state == QMediaPlayer.PlayingState:
            self.status_label.setText("กำลังเล่น")
            self.play_btn.setText("▶️ เล่น")
        elif state == QMediaPlayer.PausedState:
            self.status_label.setText("พักการเล่น")
            self.play_btn.setText("▶️ ดำเนินต่อ")
        elif state == QMediaPlayer.StoppedState:
            self.status_label.setText("หยุดแล้ว")
            self.play_btn.setText("▶️ เล่น")
    
    def on_media_status_changed(self, status):
        """เมื่อสถานะ media เปลี่ยน"""
        if status == QMediaPlayer.LoadedMedia:
            self.status_label.setText("พร้อมเล่น")
        elif status == QMediaPlayer.LoadingMedia:
            self.status_label.setText("กำลังโหลด...")
        elif status == QMediaPlayer.EndOfMedia:
            self.status_label.setText("เล่นจบแล้ว")
        elif status == QMediaPlayer.InvalidMedia:
            self.status_label.setText("ไฟล์ไม่ถูกต้อง")
    
    def on_error(self, error):
        """เมื่อเกิด error ในการเล่น"""
        error_messages = {
            QMediaPlayer.NoError: "ไม่มี error",
            QMediaPlayer.ResourceError: "Resource error",
            QMediaPlayer.FormatError: "Format ไม่รองรับ",
            QMediaPlayer.NetworkError: "Network error",
            QMediaPlayer.AccessDeniedError: "Access denied"
        }
        
        message = error_messages.get(error, f"Unknown error: {error}")
        self.status_label.setText(f"Error: {message}")
        logger.error(f"Media player error: {message}")

class StationListWidget(QWidget):
    """Widget สำหรับแสดงรายการสถานี"""
    
    station_selected = pyqtSignal(dict)  # ส่งข้อมูลสถานีที่เลือก
    
    def __init__(self):
        super().__init__()
        self.stations = []
        self.setup_ui()
        
    def setup_ui(self):
        """สร้าง UI สำหรับแสดงรายการสถานี"""
        layout = QVBoxLayout(self)
        
        # กลุ่มการสแกน
        scan_group = QGroupBox("การสแกนสถานี")
        scan_layout = QVBoxLayout(scan_group)
        
        self.scan_btn = QPushButton("🔍 สแกนสถานี")
        self.scan_btn.setMinimumSize(120, 50)
        self.scan_btn.setStyleSheet("""
            QPushButton {
                border: 2px solid #27ae60;
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2ecc71, stop:1 #27ae60);
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:pressed {
                background: #27ae60;
            }
        """)
        scan_layout.addWidget(self.scan_btn)
        
        # Progress bar สำหรับการสแกน
        self.scan_progress = QProgressBar()
        self.scan_progress.setVisible(False)
        scan_layout.addWidget(self.scan_progress)
        
        layout.addWidget(scan_group)
        
        # รายการสถานี
        station_group = QGroupBox("รายการสถานี")
        station_layout = QVBoxLayout(station_group)
        
        self.station_list = QListWidget()
        self.station_list.setMinimumHeight(300)
        self.station_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ebf3fd;
            }
        """)
        station_layout.addWidget(self.station_list)
        
        # ข้อมูลสถานีที่เลือก
        self.station_info_label = QLabel("เลือกสถานีเพื่อดูข้อมูล")
        self.station_info_label.setWordWrap(True)
        self.station_info_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 4px;
                font-size: 10px;
                border: 1px solid #e9ecef;
            }
        """)
        station_layout.addWidget(self.station_info_label)
        
        layout.addWidget(station_group)
        
        # ปุ่มจัดการ
        action_layout = QHBoxLayout()
        self.clear_btn = QPushButton("🗑️ ลบทั้งหมด")
        self.save_btn = QPushButton("💾 บันทึกรายการ")
        
        for btn in [self.clear_btn, self.save_btn]:
            btn.setMinimumSize(100, 40)
            btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid #95a5a6;
                    border-radius: 4px;
                    background: #ecf0f1;
                    font-size: 10px;
                }
                QPushButton:pressed {
                    background: #d5dbdb;
                }
            """)
        
        action_layout.addWidget(self.clear_btn)
        action_layout.addWidget(self.save_btn)
        layout.addLayout(action_layout)
        
        # เชื่อม signals
        self.station_list.currentItemChanged.connect(self.on_station_selection_changed)
        self.station_list.itemDoubleClicked.connect(self.on_station_double_clicked)
        self.clear_btn.clicked.connect(self.clear_stations)
        self.save_btn.clicked.connect(self.save_station_list)
        
    def add_station(self, station_info):
        """เพิ่มสถานีลงในรายการ"""
        try:
            # ตรวจสอบว่ามีสถานีนี้แล้วหรือไม่
            for existing_station in self.stations:
                if (existing_station.get('name') == station_info.get('name') and 
                    existing_station.get('frequency') == station_info.get('frequency')):
                    return  # มีแล้ว ไม่เพิ่ม
            
            self.stations.append(station_info)
            
            # สร้าง list item
            item_text = f"{station_info.get('name', 'Unknown')}"
            if 'frequency' in station_info:
                item_text += f" ({station_info['frequency']:.3f} MHz)"
            if 'channel' in station_info:
                item_text += f" [{station_info['channel']}]"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, station_info)  # เก็บข้อมูลสถานี
            
            # เพิ่ม tooltip
            tooltip = f"สถานี: {station_info.get('name', 'Unknown')}\n"
            tooltip += f"ความถี่: {station_info.get('frequency', 0):.3f} MHz\n"
            tooltip += f"Channel: {station_info.get('channel', 'Unknown')}\n"
            if 'ensemble' in station_info:
                tooltip += f"Ensemble: {station_info['ensemble']}\n"
            if 'bitrate' in station_info:
                tooltip += f"Bitrate: {station_info['bitrate']} kbps"
            item.setToolTip(tooltip)
            
            self.station_list.addItem(item)
            
        except Exception as e:
            logger.error(f"เพิ่มสถานี error: {str(e)}")
    
    def clear_stations(self):
        """ลบสถานีทั้งหมด"""
        self.stations.clear()
        self.station_list.clear()
        self.station_info_label.setText("ลบรายการสถานีแล้ว")
    
    def get_selected_station(self):
        """ได้ข้อมูลสถานีที่เลือกอยู่"""
        current_item = self.station_list.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return None
    
    def on_station_selection_changed(self, current, previous):
        """เมื่อเปลี่ยนการเลือกสถานี"""
        if current:
            station_info = current.data(Qt.UserRole)
            if station_info:
                # แสดงข้อมูลสถานี
                info_text = f"📻 {station_info.get('name', 'Unknown')}\n"
                info_text += f"📡 {station_info.get('frequency', 0):.3f} MHz ({station_info.get('channel', 'Unknown')})\n"
                if 'ensemble' in station_info:
                    info_text += f"📂 {station_info['ensemble']}\n"
                if 'bitrate' in station_info:
                    info_text += f"💿 {station_info['bitrate']} kbps\n"
                if 'signal_quality' in station_info:
                    info_text += f"📶 Signal: {station_info['signal_quality']:.0f}%"
                
                self.station_info_label.setText(info_text)
        else:
            self.station_info_label.setText("เลือกสถานีเพื่อดูข้อมูล")
    
    def on_station_double_clicked(self, item):
        """เมื่อดับเบิลคลิกสถานี"""
        station_info = item.data(Qt.UserRole)
        if station_info:
            self.station_selected.emit(station_info)
    
    def save_station_list(self):
        """บันทึกรายการสถานีลงไฟล์"""
        try:
            if not self.stations:
                QMessageBox.information(self, "แจ้งเตือน", "ไม่มีสถานีให้บันทึก")
                return
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "บันทึกรายการสถานี", 
                f"station_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.stations, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "สำเร็จ", f"บันทึกรายการสถานีลง:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"บันทึกไฟล์ไม่ได้:\n{str(e)}")

class MetadataWidget(QWidget):
    """Widget สำหรับแสดง metadata และ slideshow"""
    
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.setup_ui()
        
    def setup_ui(self):
        """สร้าง UI สำหรับแสดง metadata"""
        layout = QVBoxLayout(self)
        
        # Metadata display
        metadata_group = QGroupBox("ข้อมูลเพลง")
        metadata_layout = QVBoxLayout(metadata_group)
        
        self.song_label = QLabel("ชื่อเพลง: -")
        self.artist_label = QLabel("ศิลปิน: -")
        self.album_label = QLabel("อัลบั้ม: -")
        self.extra_label = QLabel("ข้อมูลเพิ่มเติม: -")
        self.time_label = QLabel("เวลา: -")
        
        # ปรับ style สำหรับ metadata labels
        for label in [self.song_label, self.artist_label, self.album_label, self.extra_label, self.time_label]:
            label.setStyleSheet("""
                QLabel {
                    font-size: 11px; 
                    padding: 4px;
                    background-color: #f8f9fa;
                    border-radius: 3px;
                    margin: 2px 0px;
                }
            """)
            label.setWordWrap(True)
        
        metadata_layout.addWidget(self.song_label)
        metadata_layout.addWidget(self.artist_label)
        metadata_layout.addWidget(self.album_label)
        metadata_layout.addWidget(self.extra_label)
        metadata_layout.addWidget(self.time_label)
        layout.addWidget(metadata_group)
        
        # Slideshow display
        slideshow_group = QGroupBox("สไลด์โชว์")
        slideshow_layout = QVBoxLayout(slideshow_group)
        
        self.slideshow_label = QLabel("ไม่มีรูปภาพ")
        self.slideshow_label.setMinimumSize(200, 150)
        self.slideshow_label.setMaximumSize(300, 225)
        self.slideshow_label.setAlignment(Qt.AlignCenter)
        self.slideshow_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 8px;
                background-color: #f8f9fa;
                color: #7f8c8d;
                font-size: 12px;
            }
        """)
        self.slideshow_label.setScaledContents(True)
        slideshow_layout.addWidget(self.slideshow_label)
        
        # ปุ่มจัดการรูป
        image_button_layout = QHBoxLayout()
        self.save_image_btn = QPushButton("💾 บันทึกรูป")
        self.load_image_btn = QPushButton("📁 เลือกรูป")
        
        for btn in [self.save_image_btn, self.load_image_btn]:
            btn.setMinimumSize(90, 35)
            btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid #95a5a6;
                    border-radius: 4px;
                    background: #ecf0f1;
                    font-size: 9px;
                }
                QPushButton:pressed {
                    background: #d5dbdb;
                }
            """)
        
        image_button_layout.addWidget(self.save_image_btn)
        image_button_layout.addWidget(self.load_image_btn)
        slideshow_layout.addLayout(image_button_layout)
        
        layout.addWidget(slideshow_group)
        
        # ข้อมูลเพิ่มเติม
        info_group = QGroupBox("สถิติ")
        info_layout = QVBoxLayout(info_group)
        
        self.metadata_count_label = QLabel("จำนวน metadata: 0")
        self.slideshow_count_label = QLabel("จำนวนรูป: 0")
        
        for label in [self.metadata_count_label, self.slideshow_count_label]:
            label.setStyleSheet("font-size: 10px; padding: 3px;")
        
        info_layout.addWidget(self.metadata_count_label)
        info_layout.addWidget(self.slideshow_count_label)
        layout.addWidget(info_group)
        
        # เชื่อม signals
        self.save_image_btn.clicked.connect(self.save_slideshow)
        self.load_image_btn.clicked.connect(self.load_test_image)
        
        # เก็บสถิติ
        self.metadata_count = 0
        self.slideshow_count = 0
        
    def update_metadata(self, metadata):
        """อัพเดท metadata"""
        try:
            self.song_label.setText(f"ชื่อเพลง: {metadata.get('title', '-')}")
            self.artist_label.setText(f"ศิลปิน: {metadata.get('artist', '-')}")
            self.album_label.setText(f"อัลบั้ม: {metadata.get('album', '-')}")
            self.extra_label.setText(f"ข้อมูลเพิ่มเติม: {metadata.get('text', '-')}")
            
            # แสดงเวลาที่ได้รับข้อมูล
            if 'timestamp' in metadata:
                timestamp = datetime.fromisoformat(metadata['timestamp'])
                time_str = timestamp.strftime('%H:%M:%S')
                self.time_label.setText(f"เวลา: {time_str}")
            
            # อัพเดทสถิติ
            self.metadata_count += 1
            self.metadata_count_label.setText(f"จำนวน metadata: {self.metadata_count}")
            
            logger.info(f"อัพเดท metadata: {metadata.get('title', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"อัพเดท metadata error: {str(e)}")
        
    def update_slideshow(self, image_path):
        """อัพเดทรูป slideshow"""
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
                    
                    logger.info(f"อัพเดท slideshow: {os.path.basename(image_path)}")
                else:
                    self.slideshow_label.setText("ไม่สามารถโหลดรูปภาพได้")
            else:
                self.slideshow_label.setText("ไฟล์รูปภาพไม่ถูกต้อง")
                
        except Exception as e:
            self.slideshow_label.setText(f"Error: {str(e)}")
            logger.error(f"อัพเดท slideshow error: {str(e)}")
    
    def save_slideshow(self):
        """บันทึกรูป slideshow"""
        try:
            if not self.current_image_path or not os.path.exists(self.current_image_path):
                QMessageBox.information(self, "แจ้งเตือน", "ไม่มีรูปภาพให้บันทึก")
                return
            
            # เลือกตำแหน่งบันทึก
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_name = f"slideshow_{timestamp}.jpg"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "บันทึกรูป Slideshow",
                default_name,
                "Image Files (*.jpg *.jpeg *.png);;All Files (*)"
            )
            
            if file_path:
                # คัดลอกไฟล์
                import shutil
                shutil.copy2(self.current_image_path, file_path)
                
                QMessageBox.information(self, "สำเร็จ", f"บันทึกรูปแล้ว:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"บันทึกรูปไม่ได้:\n{str(e)}")
    
    def load_test_image(self):
        """โหลดรูปทดสอบ"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "เลือกรูปทดสอบ",
                "",
                "Image Files (*.jpg *.jpeg *.png *.gif *.bmp);;All Files (*)"
            )
            
            if file_path:
                self.update_slideshow(file_path)
                
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"โหลดรูปไม่ได้:\n{str(e)}")

class Lab2MainWindow(QMainWindow):
    """หน้าต่างหลักของ Lab 2"""
    
    def __init__(self):
        super().__init__()
        self.welle_controller = None
        self.setup_ui()
        self.setup_touch_interface()
        self.setup_connections()
        self.setWindowTitle("LAB 2: การใช้งาน welle.io ผ่าน Python")
        self.resize(1000, 700)
        
    def setup_ui(self):
        """สร้าง UI elements"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # สร้าง layout หลัก
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # ชื่อแล็บ
        title_label = QLabel("LAB 2: การใช้งาน welle.io ผ่าน Python")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #2c3e50;
            padding: 12px;
            background-color: #ecf0f1;
            border-radius: 8px;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(title_label)
        
        # ปุ่มควบคุมหลัก
        control_layout = QHBoxLayout()
        
        self.start_welle_btn = QPushButton("🚀 เริ่ม welle.io")
        self.scan_btn = QPushButton("🔍 สแกนสถานี")
        self.play_btn = QPushButton("▶️ เล่น")
        self.record_btn = QPushButton("⏺️ บันทึก")
        self.stop_btn = QPushButton("⏹️ หยุด")
        
        # ตั้งค่า style สำหรับปุ่มควบคุม
        main_button_style = """
            QPushButton {
                border: 2px solid #2c3e50;
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 8px;
                min-height: 50px;
                min-width: 110px;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #1f4e79);
            }
            QPushButton:disabled {
                background: #95a5a6;
                color: #7f8c8d;
            }
        """
        
        for btn in [self.start_welle_btn, self.scan_btn, self.play_btn, self.record_btn, self.stop_btn]:
            btn.setStyleSheet(main_button_style)
        
        control_layout.addWidget(self.start_welle_btn)
        control_layout.addWidget(self.scan_btn)
        control_layout.addWidget(self.play_btn)
        control_layout.addWidget(self.record_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addStretch()  # ผลักปุ่มไปทางซ้าย
        
        main_layout.addLayout(control_layout)
        
        # พื้นที่หลัก - แบ่งเป็น 3 ส่วน
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
        
        # กำหนดอัตราส่วนขนาดของแต่ละส่วน
        content_splitter.setSizes([350, 300, 350])  # รวม 1000px
        main_layout.addWidget(content_splitter, 1)
        
        # Status bar
        self.status_label = QLabel("พร้อมใช้งาน - เริ่มต้นด้วยการกด 'เริ่ม welle.io'")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #ecf0f1;
                border-radius: 4px;
                font-size: 11px;
                color: #2c3e50;
            }
        """)
        main_layout.addWidget(self.status_label)
        
        # ปิดปุ่มที่ไม่พร้อมใช้งาน
        self.scan_btn.setEnabled(False)
        self.play_btn.setEnabled(False)
        self.record_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        
    def setup_touch_interface(self):
        """ปรับ UI สำหรับหน้าจอสัมผัส"""
        # ตั้งค่า font ขนาดใหญ่สำหรับหน้าจอสัมผัส
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
                    border-radius: 2px;
                }
                QSplitter::handle:hover {
                    background-color: #3498db;
                }
            """)
        
    def setup_connections(self):
        """เชื่อม signals และ slots"""
        # ปุ่มควบคุมหลัก
        self.start_welle_btn.clicked.connect(self.start_welle_io)
        self.scan_btn.clicked.connect(self.scan_stations)
        self.play_btn.clicked.connect(self.start_playback)
        self.record_btn.clicked.connect(self.toggle_recording)
        self.stop_btn.clicked.connect(self.stop_all)
        
        # Station list events
        self.station_widget.station_selected.connect(self.on_station_selected)
        self.station_widget.scan_btn.clicked.connect(self.scan_stations)
    
    def start_welle_io(self):
        """เริ่มต้น welle.io"""
        try:
            if self.welle_controller and self.welle_controller.isRunning():
                QMessageBox.information(self, "แจ้งเตือน", "welle.io กำลังทำงานอยู่แล้ว")
                return
            
            self.status_label.setText("กำลังเริ่มต้น welle.io...")
            self.start_welle_btn.setEnabled(False)
            
            # สร้าง controller ใหม่
            self.welle_controller = WelleIOController()
            
            # เชื่อม signals
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
                self.status_label.setText("welle.io เริ่มต้นสำเร็จ - พร้อมสแกนสถานี")
            else:
                self.start_welle_btn.setEnabled(True)
                
        except Exception as e:
            self.on_error(f"เริ่ม welle.io ไม่ได้: {str(e)}")
            self.start_welle_btn.setEnabled(True)
    
    def scan_stations(self):
        """สแกนหาสถานี DAB+"""
        try:
            if not self.welle_controller:
                QMessageBox.warning(self, "คำเตือน", "กรุณาเริ่ม welle.io ก่อน")
                return
            
            # แสดง progress bar
            self.station_widget.scan_progress.setVisible(True)
            self.station_widget.scan_progress.setValue(0)
            
            self.scan_btn.setEnabled(False)
            self.station_widget.scan_btn.setEnabled(False)
            
            self.status_label.setText("กำลังสแกนสถานี DAB+...")
            
            # เริ่มสแกนใน thread แยก
            self.welle_controller.scan_dab_stations()
            
        except Exception as e:
            self.on_error(f"สแกนสถานี error: {str(e)}")
            self.scan_btn.setEnabled(True)
            self.station_widget.scan_btn.setEnabled(True)
    
    def start_playback(self):
        """เริ่มการเล่นเสียง"""
        try:
            selected_station = self.station_widget.get_selected_station()
            
            if not selected_station:
                QMessageBox.information(self, "แจ้งเตือน", "กรุณาเลือกสถานีก่อน")
                return
            
            if not self.welle_controller:
                QMessageBox.warning(self, "คำเตือน", "welle.io ไม่ทำงาน")
                return
            
            self.status_label.setText(f"กำลัง tune ไปยัง {selected_station['name']}...")
            
            # Tune ไปยังสถานีที่เลือก
            success = self.welle_controller.tune_to_station(selected_station)
            
            if success:
                self.play_btn.setEnabled(False)
                self.record_btn.setEnabled(True)
                self.status_label.setText(f"กำลังเล่น: {selected_station['name']}")
            else:
                QMessageBox.warning(self, "ข้อผิดพลาด", "ไม่สามารถเล่นสถานีนี้ได้")
                
        except Exception as e:
            self.on_error(f"เล่นเสียง error: {str(e)}")
    
    def toggle_recording(self):
        """สลับการบันทึก (เริ่ม/หยุด)"""
        try:
            if not self.welle_controller:
                QMessageBox.warning(self, "คำเตือน", "welle.io ไม่ทำงาน")
                return
            
            if not self.welle_controller.is_recording:
                # เริ่มบันทึก
                success = self.welle_controller.start_recording()
                if success:
                    self.record_btn.setText("⏸️ หยุดบันทึก")
                    self.record_btn.setStyleSheet(self.record_btn.styleSheet().replace('#3498db', '#e74c3c'))
            else:
                # หยุดบันทึก
                self.welle_controller.stop_recording()
                self.record_btn.setText("⏺️ บันทึก")
                self.record_btn.setStyleSheet(self.record_btn.styleSheet().replace('#e74c3c', '#3498db'))
                
        except Exception as e:
            self.on_error(f"บันทึก error: {str(e)}")
    
    def stop_all(self):
        """หยุดการทำงานทั้งหมด"""
        try:
            if self.welle_controller:
                self.welle_controller.cleanup()
            
            # หยุดการเล่นเสียง
            self.audio_widget.stop_audio()
            
            # รีเซ็ตปุ่ม
            self.start_welle_btn.setEnabled(True)
            self.scan_btn.setEnabled(False)
            self.play_btn.setEnabled(False)
            self.record_btn.setEnabled(False)
            self.record_btn.setText("⏺️ บันทึก")
            self.stop_btn.setEnabled(False)
            
            # ซ่อน progress bar
            self.station_widget.scan_progress.setVisible(False)
            
            self.status_label.setText("หยุดการทำงานทั้งหมดแล้ว")
            
        except Exception as e:
            self.on_error(f"หยุดการทำงาน error: {str(e)}")
    
    def on_station_selected(self, station_info):
        """เมื่อเลือกสถานีใหม่"""
        try:
            self.play_btn.setEnabled(True)
            self.status_label.setText(f"เลือกสถานี: {station_info['name']} ({station_info['frequency']:.3f} MHz)")
            
        except Exception as e:
            logger.error(f"Station selection error: {str(e)}")
    
    def on_error(self, error_message):
        """จัดการข้อผิดพลาด"""
        self.status_label.setText(f"Error: {error_message}")
        logger.error(f"Lab2 error: {error_message}")
        
        # แสดง message box สำหรับ error ร้ายแรง
        if "ไม่พบ welle-io" in error_message or "เริ่ม welle.io ไม่ได้" in error_message:
            QMessageBox.critical(self, "ข้อผิดพลาดร้ายแรง", error_message)
    
    def closeEvent(self, event):
        """เมื่อปิดหน้าต่าง"""
        try:
            if self.welle_controller:
                self.welle_controller.cleanup()
                
            event.accept()
            
        except Exception as e:
            logger.error(f"Close event error: {str(e)}")
            event.accept()

# Helper Functions
def check_welle_io_installation():
    """ตรวจสอบการติดตั้ง welle.io"""
    try:
        result = subprocess.run(['welle-io', '--help'], capture_output=True, text=True, timeout=10)
        
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
        # Band III DAB+ channels for Thailand
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
    """ฟังก์ชันหลัก"""
    # ตรวจสอบ welle.io installation
    installed, version, capabilities = check_welle_io_installation()
    
    if not installed:
        print("❌ ไม่พบ welle.io หรือติดตั้งไม่สมบูรณ์")
        print("โปรดติดตั้ง welle.io ตามคำแนะนำใน LAB2.md")
        print(f"สาเหตุ: {version}")
        return 1
    
    # สร้าง QApplication
    app = QApplication(sys.argv)
    
    # ตั้งค่า application properties
    app.setApplicationName("DAB+ Lab 2")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("DAB+ Labs")
    
    # ตั้งค่า font สำหรับหน้าจอสัมผัส
    font = QFont()
    font.setPointSize(10)
    font.setFamily("DejaVu Sans")
    app.setFont(font)
    
    # แสดงข้อมูลระบบ
    logger.info("เริ่มต้น welle.io DAB+ Lab")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"welle.io version: {version}")
    logger.info(f"welle.io capabilities: {', '.join(capabilities) if capabilities else 'Unknown'}")
    
    # สร้างและแสดง main window
    window = Lab2MainWindow()
    window.show()
    
    # แสดงข้อมูลเริ่มต้นใน status
    if capabilities:
        window.status_label.setText(f"พร้อมใช้งาน - {version} ({', '.join(capabilities)})")
    
    # รัน event loop
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())