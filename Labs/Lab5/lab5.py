#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAB 5: สร้าง DAB+ Program Recorder (โจทย์ - ใช้ Lab 3 ETI approach)
- พัฒนาระบบบันทึกรายการ DAB+ ตามตารางเวลา ด้วย RTL-SDR + ETI processing
- จัดการตารางเวลาการบันทึกและการเล่นไฟล์
- รองรับหน้าจอสัมผัส 7" ด้วย PyQt5 และ QMediaPlayer
- ใช้ Lab 3 pipeline: RTL-SDR → ETI → Audio extraction → Recording
"""

import sys
import os
import json
import sqlite3
import logging
import subprocess
import shutil
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QProgressBar, QComboBox, QSpinBox,
    QGroupBox, QSplitter, QTextEdit, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QFileDialog, QMessageBox, QListWidget, QListWidgetItem, QHeaderView,
    QSlider, QCheckBox, QTimeEdit, QDateEdit, QScrollArea, QGridLayout
)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, QDateTime, QTime, QDate, QUrl
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# นำเข้า modules จาก Lab 3 (สำหรับใช้ในการแก้โจทย์)
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Lab3'))
    from lab3_1a import RTLSDRDataAcquisition
    from lab3_2 import ETIProcessor
    from lab3_3 import ETIFrameParser
    from lab3_4 import DABServicePlayer
except ImportError as e:
    print(f"Warning: Cannot import Lab 3 modules: {e}")
    print("Make sure Lab 3 solutions are available")

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Lab5")

# DAB+ Thailand frequencies และ services
DAB_FREQUENCIES = {
    '185.360': {'location': 'Bangkok/Phuket', 'block': '7A', 'freq': 185.360},
    '202.928': {'location': 'Bangkok', 'block': '9A', 'freq': 202.928},
    '195.936': {'location': 'Chiang Mai', 'block': '8C', 'freq': 195.936},
    '210.096': {'location': 'Northeast', 'block': '10B', 'freq': 210.096},
}

# ---------- Recording Database ----------
class RecordingDatabase:
    """ฐานข้อมูลสำหรับเก็บข้อมูลการบันทึก"""

    def __init__(self, db_path="dab_recordings.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """สร้างฐานข้อมูลและตาราง"""
        # TODO: สร้างตาราง recording_schedule (3 ฟิลด์หลัก: station_name, start_time, duration)
        # TODO: สร้างตาราง recording_history (บันทึกผลลัพธ์การบันทึก)
        pass

    def add_schedule(self, schedule_data):
        """เพิ่มตารางเวลาการบันทึก"""
        # TODO: เพิ่มข้อมูลลงฐานข้อมูล
        pass

    def get_all_schedules(self):
        """ดึงตารางเวลาทั้งหมด"""
        # TODO: SELECT * FROM recording_schedule
        return []

    def get_active_schedules(self):
        """ดึงตารางเวลาที่ active ในปัจจุบัน"""
        # TODO: ดึงเฉพาะตารางเวลาที่ is_active = True
        # TODO: กรองตามวันในสัปดาห์ปัจจุบัน
        return []

    def add_recording(self, recording_data):
        """เพิ่มบันทึกการบันทึก"""
        # TODO: เพิ่มบันทึกการบันทึกลงในฐานข้อมูล
        # TODO: บันทึกข้อมูล ETI และ service ที่เกี่ยวข้อง
        # TODO: return recording_id หากสำเร็จ หรือ None หากไม่สำเร็จ
        pass

    def add_recorded_file(self, recording_id, file_data):
        """เพิ่มข้อมูลไฟล์ที่บันทึก"""
        # TODO: เพิ่มข้อมูลไฟล์ (audio, slideshow, metadata) ลงฐานข้อมูล
        pass

    def get_recordings(self, limit=50):
        """ดึงประวัติการบันทึก"""
        # TODO: ดึงประวัติการบันทึกจากฐานข้อมูล
        # TODO: รวมข้อมูลไฟล์ที่เกี่ยวข้อง
        # TODO: เรียงลำดับตาม start_time (ล่าสุดก่อน)
        return []

    def update_recording_status(self, recording_id, status, error_message=None):
        """อัปเดตสถานะการบันทึก"""
        # TODO: อัปเดตสถานะการบันทึก (recording, completed, failed)
        pass

# ---------- DAB+ Recorder Engine (ใช้ Lab 3 approach) ----------
class DABRecorderEngine(QThread):
    """เครื่องมือบันทึก DAB+ ใช้ Lab 3 pipeline"""

    recording_started = pyqtSignal(dict)
    recording_progress = pyqtSignal(int, str)
    recording_completed = pyqtSignal(dict)
    recording_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.current_recording = None
        self._stop_flag = False
        self.output_dir = Path("recordings")

        # Lab 3 components
        self.rtl_sdr = None
        self.eti_processor = None
        self.eti_parser = None
        self.service_player = None

        # TODO: สร้างโฟลเดอร์ output ถ้ายังไม่มี
        # TODO: สร้างโฟลเดอร์ย่อยสำหรับ audio, metadata, slideshow

    def setup_lab3_pipeline(self):
        """ตั้งค่า Lab 3 pipeline สำหรับการบันทึก"""
        try:
            # TODO: เริ่มต้น RTLSDRDataAcquisition
            # TODO: เริ่มต้น ETIProcessor
            # TODO: เริ่มต้น ETIFrameParser
            # TODO: เริ่มต้น DABServicePlayer
            # TODO: return True หากสำเร็จ, False หากไม่สำเร็จ
            pass
        except Exception as e:
            logger.error(f"Lab 3 pipeline setup error: {e}")
            return False

    def start_recording(self, schedule_data):
        """เริ่มการบันทึก"""
        try:
            # TODO: ตั้งค่า current_recording และเริ่ม thread
            pass
        except Exception as e:
            self.recording_error.emit(f"Start recording error: {e}")
            return False

    def get_output_path(self, schedule_data):
        """สร้างเส้นทางไฟล์ output"""
        try:
            # TODO: สร้างชื่อไฟล์ที่เหมาะสมตาม timestamp, station name และ program name
            # TODO: format: recordings/YYYY-MM-DD/station_name/program_name_HHMMSS/
            # TODO: return Path object ของโฟลเดอร์หลัก
            pass
        except Exception as e:
            logger.error(f"Output path creation error: {e}")
            return None

    def run(self):
        """ทำการบันทึกจริงใช้ Lab 3 pipeline"""
        if not self.current_recording:
            return

        try:
            # TODO: ใช้ Lab 3 pipeline: RTL-SDR → ETI → extract audio
            # TODO: บันทึกไฟล์เสียงและส่ง signals

            # สำหรับการทดสอบ ใช้ mock recording
            self.record_with_lab3_mock()

        except Exception as e:
            self.recording_error.emit(f"Recording error: {e}")
        finally:
            self.cleanup()

    def record_with_lab3_mock(self):
        """จำลองการบันทึกด้วย Lab 3 approach (สำหรับการทดสอบ)"""
        try:
            recording_info = {
                'station_name': self.current_recording.get('station_name'),
                'program_name': self.current_recording.get('program_name'),
                'start_time': datetime.now()
            }
            self.recording_started.emit(recording_info)

            duration = self.current_recording.get('duration_minutes', 30)
            total_steps = duration * 60  # seconds

            for step in range(total_steps):
                if self._stop_flag:
                    break

                # TODO: จำลองการบันทึกและส่ง progress signal

                progress = int((step / total_steps) * 100)
                elapsed_time = step
                remaining_time = total_steps - step

                message = f"Recording: {elapsed_time//60:02d}:{elapsed_time%60:02d} / {total_steps//60:02d}:{total_steps%60:02d}"
                self.recording_progress.emit(progress, message)

                time.sleep(1)  # จำลองการบันทึก 1 วินาที

            # TODO: สร้างไฟล์ mock สำหรับทดสอบ
            output_path = self.get_output_path(self.current_recording)
            if output_path:
                self.create_mock_files(output_path)

            recording_result = {
                'status': 'completed',
                'output_path': str(output_path) if output_path else None,
                'duration': total_steps,
                'file_size': self.get_total_file_size(output_path) if output_path else 0
            }
            self.recording_completed.emit(recording_result)

        except Exception as e:
            self.recording_error.emit(f"Mock recording error: {e}")

    def create_mock_files(self, output_path):
        """สร้างไฟล์ mock สำหรับทดสอบ"""
        try:
            # TODO: สร้างไฟล์ audio mock (WAV หรือ MP3)
            # TODO: สร้างไฟล์ metadata JSON
            # TODO: สร้างไฟล์ slideshow images
            # TODO: สร้างไฟล์ ETI data (ถ้าต้องการ)
            pass
        except Exception as e:
            logger.error(f"Mock file creation error: {e}")

    def capture_and_process_eti(self, frequency, service_id, duration):
        """รับ I/Q data และประมวลผลเป็น ETI เพื่อหา service"""
        try:
            # TODO: ตั้งค่าความถี่ให้ RTL-SDR
            # TODO: รับ I/Q data ด้วย capture_samples()
            # TODO: ประมวลผล I/Q เป็น ETI ด้วย ETIProcessor
            # TODO: parse ETI เพื่อหา services ด้วย ETIFrameParser
            # TODO: หา service ที่ต้องการตาม service_id
            # TODO: extract audio data จาก service
            # TODO: return audio data, metadata, slideshow
            return None, None, None
        except Exception as e:
            logger.error(f"ETI capture and process error: {e}")
            return None, None, None

    def save_recording_files(self, output_path, audio_data, metadata, slideshow_data):
        """บันทึกไฟล์ต่างๆ ที่ได้จากการบันทึก"""
        try:
            # TODO: บันทึกไฟล์เสียง (WAV/MP3)
            # TODO: บันทึก metadata JSON
            # TODO: บันทึก slideshow images
            # TODO: สร้างไฟล์ข้อมูลสรุป (summary.json)
            pass
        except Exception as e:
            logger.error(f"Save recording files error: {e}")

    def get_total_file_size(self, output_path):
        """คำนวณขนาดไฟล์ทั้งหมดที่บันทึก"""
        try:
            # TODO: คำนวณขนาดไฟล์ทั้งหมดในโฟลเดอร์
            # TODO: return ขนาดเป็น bytes
            return 0
        except Exception as e:
            logger.error(f"File size calculation error: {e}")
            return 0

    def stop_recording(self):
        """หยุดการบันทึก"""
        # TODO: ตั้งค่า flags เพื่อหยุดการทำงาน
        self.is_recording = False
        self._stop_flag = True

    def cleanup(self):
        """ทำความสะอาด resources"""
        try:
            # TODO: ปิดการเชื่อมต่อ RTL-SDR
            # TODO: หยุดการทำงานของ ETI processor
            # TODO: ปิดไฟล์ที่เปิดอยู่
            pass
        except:
            pass

# ---------- Schedule Manager ----------
class ScheduleManager(QThread):
    """จัดการตารางเวลาการบันทึกอัตโนมัติ"""

    schedule_triggered = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.db = RecordingDatabase()
        self.running = False
        self._stop_flag = False

    def run(self):
        """ตรวจสอบตารางเวลาทุกนาที"""
        self.running = True
        self._stop_flag = False

        while self.running and not self._stop_flag:
            try:
                # TODO: เรียก check_schedules() เพื่อตรวจสอบตารางเวลา
                # TODO: รอ 60 วินาทีก่อนตรวจสอบครั้งต่อไป
                time.sleep(60)
            except Exception as e:
                self.error_occurred.emit(f"Schedule manager error: {e}")
                time.sleep(60)

    def check_schedules(self):
        """ตรวจสอบตารางเวลาว่าถึงเวลาบันทึกหรือไม่"""
        try:
            # TODO: ดึงตารางเวลาที่ active
            # TODO: ตรวจสอบเวลาปัจจุบันกับตารางเวลา
            # TODO: เช็ควันในสัปดาห์
            # TODO: ตรวจสอบว่าไม่ได้บันทึกซ้ำ
            # TODO: ส่ง signal schedule_triggered เมื่อถึงเวลา
            pass
        except Exception as e:
            logger.error(f"Schedule check error: {e}")

    def is_time_to_record(self, schedule):
        """ตรวจสอบว่าถึงเวลาบันทึกตามตารางเวลาหรือไม่"""
        try:
            # TODO: เปรียบเทียบเวลาปัจจุบันกับ start_time ในตารางเวลา
            # TODO: เช็ควันในสัปดาห์ตาม days_of_week
            # TODO: return True หากถึงเวลา
            return False
        except Exception as e:
            logger.error(f"Time check error: {e}")
            return False

    def stop_manager(self):
        """หยุดการทำงาน"""
        # TODO: หยุดการทำงานของ thread
        self.running = False
        self._stop_flag = True

# ---------- Schedule Widget ----------
class ScheduleWidget(QWidget):
    """Widget จัดการตารางเวลาการบันทึก"""

    schedule_added = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db = RecordingDatabase()
        self.setup_ui()
        # TODO: เรียก refresh_schedules()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # หัวข้อ
        title = QLabel("ตารางเวลาการบันทึก")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # ฟอร์มเพิ่มตารางเวลา
        form_group = QGroupBox("เพิ่มตารางเวลาใหม่")
        form_layout = QGridLayout(form_group)

        # TODO: สร้าง station combo, time edit, program name input
        # TODO: สร้างปุ่ม Add Schedule
        # TODO: สร้างตาราง schedule แสดงรายการ

        layout.addWidget(form_group)
        layout.addWidget(QTableWidget())  # placeholder

        # TODO: เชื่อมต่อ signals กับ add_schedule()

    def update_services(self, station_name):
        """อัปเดตรายการ services ตาม station ที่เลือก"""
        # TODO: ดึงรายการ services จาก station ที่เลือก
        # TODO: อัปเดต service_combo
        pass

    def add_schedule(self):
        """เพิ่มตารางเวลาใหม่"""
        try:
            # TODO: รวบรวมข้อมูลจากฟอร์มและบันทึกลงฐานข้อมูล
            pass
        except Exception as e:
            QMessageBox.critical(self, "Add Schedule Error", str(e))

    def clear_form(self):
        """เคลียร์ฟอร์ม"""
        # TODO: รีเซ็ตค่าในฟอร์มทั้งหมด
        # TODO: uncheck checkboxes ทั้งหมด
        # TODO: รีเซ็ต time edits เป็นเวลาปัจจุบัน
        pass

    def refresh_schedules(self):
        """รีเฟรชตารางเวลา"""
        try:
            # TODO: ดึงข้อมูลตารางเวลาจากฐานข้อมูล
            # TODO: แสดงผลในตาราง (clear table แล้วเพิ่มข้อมูลใหม่)
            # TODO: format ข้อมูลให้อ่านง่าย
            # TODO: แสดงสถานะ active/inactive ด้วยสีหรือไอคอน
            pass
        except Exception as e:
            QMessageBox.critical(self, "Refresh Error", str(e))

    def delete_schedule(self):
        """ลบตารางเวลาที่เลือก"""
        # TODO: เช็คว่าเลือกแถวหรือไม่
        # TODO: แสดง confirmation dialog
        # TODO: ลบจากฐานข้อมูล
        # TODO: รีเฟรชตาราง
        pass

    def toggle_schedule(self):
        """เปิด/ปิดตารางเวลาที่เลือก"""
        # TODO: เช็คว่าเลือกแถวหรือไม่
        # TODO: อัปเดตสถานะ is_active ในฐานข้อมูล
        # TODO: รีเฟรชตาราง
        pass

# ---------- Recording History Widget ----------
class RecordingHistoryWidget(QWidget):
    """Widget แสดงประวัติการบันทึกและเล่นไฟล์"""

    def __init__(self):
        super().__init__()
        self.db = RecordingDatabase()
        self.media_player = QMediaPlayer()
        self.setup_ui()
        # TODO: เรียก refresh_history()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # หัวข้อ
        title = QLabel("ประวัติการบันทึก")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # TODO: สร้างตารางแสดงประวัติการบันทึก
        # TODO: สร้าง QMediaPlayer สำหรับเล่นไฟล์
        # TODO: สร้างปุ่มควบคุม play/pause/stop

        self.history_table = QTableWidget()
        layout.addWidget(self.history_table)

        # TODO: เชื่อมต่อ signals ของ media player

    def refresh_history(self):
        """รีเฟรชประวัติการบันทึก"""
        try:
            # TODO: ดึงข้อมูลประวัติจากฐานข้อมูล
            # TODO: แสดงผลในตาราง (clear table แล้วเพิ่มข้อมูลใหม่)
            # TODO: format ข้อมูลให้อ่านง่าย (file size, duration, timestamp)
            # TODO: แสดงสถานะด้วยสีหรือไอคอน
            pass
        except Exception as e:
            QMessageBox.critical(self, "Refresh Error", str(e))

    def on_selection_changed(self):
        """เมื่อเลือกแถวในตาราง"""
        try:
            # TODO: รับข้อมูลการบันทึกที่เลือก
            # TODO: อัปเดตข้อมูลไฟล์ใน current_file_label
            # TODO: หาไฟล์เสียงที่เกี่ยวข้อง
            # TODO: เตรียมไฟล์สำหรับเล่น (แต่ยังไม่เล่น)
            pass
        except Exception as e:
            logger.error(f"Selection change error: {e}")

    def play_selected_recording(self):
        """เล่นไฟล์ที่เลือก"""
        try:
            # TODO: เช็คว่าเลือกแถวหรือไม่
            # TODO: หาไฟล์เสียงจากข้อมูลที่เลือก
            # TODO: ตั้งค่า QMediaContent และเล่นด้วย QMediaPlayer
            # TODO: อัปเดต UI สำหรับสถานะการเล่น
            pass
        except Exception as e:
            QMessageBox.critical(self, "Play Error", str(e))

    def play_media(self):
        """เล่นไฟล์"""
        # TODO: เล่นไฟล์ด้วย media player
        pass

    def pause_media(self):
        """หยุดชั่วคราว"""
        # TODO: หยุดชั่วคราวด้วย media player
        pass

    def stop_media(self):
        """หยุดการเล่น"""
        # TODO: หยุดการเล่นและรีเซ็ตตำแหน่ง
        pass

    def position_changed(self, position):
        """อัปเดตตำแหน่งการเล่น"""
        # TODO: อัปเดต position slider และ current time label
        pass

    def duration_changed(self, duration):
        """อัปเดตระยะเวลาทั้งหมด"""
        # TODO: ตั้งค่า range ของ position slider และ total time label
        pass

    def set_position(self, position):
        """ตั้งค่าตำแหน่งการเล่น"""
        # TODO: ตั้งค่าตำแหน่งการเล่นของ media player
        pass

    def set_volume(self, volume):
        """ตั้งค่าระดับเสียง"""
        # TODO: ตั้งค่าระดับเสียงของ media player
        pass

    def open_folder(self):
        """เปิดโฟลเดอร์ไฟล์ที่เลือก"""
        # TODO: เปิดโฟลเดอร์ที่มีไฟล์ที่เลือกด้วย file manager
        pass

    def delete_recording(self):
        """ลบไฟล์ที่เลือก"""
        # TODO: แสดง confirmation dialog
        # TODO: ลบไฟล์จริงและลบจากฐานข้อมูล
        # TODO: รีเฟรชตาราง
        pass

# ---------- Manual Recording Widget ----------
class ManualRecordingWidget(QWidget):
    """Widget สำหรับการบันทึกแมนนวล"""

    recording_requested = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # หัวข้อ
        title = QLabel("บันทึกแมนนวล")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # TODO: สร้างฟอร์มเลือกสถานี และระยะเวลา
        # TODO: สร้าง progress bar และปุ่ม Start/Stop
        # TODO: เชื่อมต่อ signals กับ start_recording()

    def update_services(self, station_name):
        """อัปเดตรายการ services ตาม station ที่เลือก"""
        # TODO: ดึงรายการ services จาก station ที่เลือก
        # TODO: อัปเดต service_combo
        pass

    def browse_folder(self):
        """เลือกโฟลเดอร์สำหรับบันทึก"""
        # TODO: เปิด folder dialog
        # TODO: อัปเดต folder_label
        pass

    def start_recording(self):
        """เริ่มการบันทึกแมนนวล"""
        try:
            # TODO: รวบรวมข้อมูลจากฟอร์ม
            # TODO: ตรวจสอบความถูกต้องของข้อมูล
            # TODO: สร้าง recording_data dict
            # TODO: ส่ง signal recording_requested
            # TODO: อัปเดตสถานะ UI (ปิด start_btn, เปิด stop_btn)
            pass
        except Exception as e:
            QMessageBox.critical(self, "Start Recording Error", str(e))

    def stop_recording(self):
        """หยุดการบันทึก"""
        # TODO: ส่ง signal หยุดการบันทึก
        # TODO: อัปเดตสถานะ UI
        pass

    def update_recording_progress(self, progress, message):
        """อัปเดตความก้าวหน้า"""
        # TODO: อัปเดต progress bar (0-100)
        # TODO: อัปเดต status label ด้วย message
        # TODO: คำนวณและแสดงเวลาที่เหลือ
        pass

    def recording_completed(self, result):
        """การบันทึกเสร็จสิ้น"""
        try:
            # TODO: อัปเดตสถานะ UI เมื่อบันทึกเสร็จ
            # TODO: แสดงผลลัพธ์ (สำเร็จ/ไม่สำเร็จ)
            # TODO: รีเซ็ต progress bar และ UI
            # TODO: เปิด start_btn, ปิด stop_btn
            pass
        except Exception as e:
            logger.error(f"Recording completion error: {e}")

# ---------- Main Window ----------
class Lab5MainWindow(QMainWindow):
    """หน้าต่างหลักของ Lab 5"""

    def __init__(self):
        super().__init__()
        self.db = RecordingDatabase()
        self.recorder = DABRecorderEngine()
        self.schedule_manager = ScheduleManager()

        self.setup_ui()
        self.setup_touch_interface()
        self.setup_connections()

        self.setWindowTitle("LAB 5: DAB+ Program Recorder (Lab 3 Pipeline)")
        self.resize(1200, 900)

        if '--fullscreen' in sys.argv:
            self.showFullScreen()

        # TODO: เริ่ม schedule manager

    def setup_ui(self):
        """สร้าง UI หลัก"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # หัวข้อ
        title_label = QLabel("LAB 5: DAB+ Program Recorder")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("""
            background-color: #2c3e50; color: white; padding: 15px;
            border-radius: 10px; margin: 5px;
        """)
        main_layout.addWidget(title_label)

        # Tab widget
        self.tab_widget = QTabWidget()

        # TODO: สร้าง 3 tabs: Manual Recording, Schedule, History

        main_layout.addWidget(self.tab_widget)

        # Status bar
        self.status_label = QLabel("พร้อมใช้งาน - เลือกสถานีและเริ่มบันทึก")
        self.status_label.setStyleSheet("background-color: #d5f4e6; padding: 8px; border-radius: 5px;")
        main_layout.addWidget(self.status_label)

    def setup_touch_interface(self):
        """ปรับการแสดงผลสำหรับหน้าจอสัมผัส"""
        # TODO: ตั้งค่า font ขนาดใหญ่สำหรับ application
        # TODO: ปรับขนาด tab widget ให้ใช้งานง่ายด้วยนิ้ว
        # TODO: ปรับขนาดปุ่มทั้งหมดให้เหมาะสำหรับ touch (ความสูงอย่างน้อย 48px)
        pass

    def setup_connections(self):
        """เชื่อมต่อ signals และ slots"""
        # TODO: เชื่อมต่อ signals ของ manual recording widget:
        #   - manual_widget.recording_requested.connect(self.start_manual_recording)

        # TODO: เชื่อมต่อ signals ของ recorder:
        #   - self.recorder.recording_started.connect(self.on_recording_started)
        #   - self.recorder.recording_progress.connect(self.on_recording_progress)
        #   - self.recorder.recording_completed.connect(self.on_recording_completed)
        #   - self.recorder.recording_error.connect(self.show_error)

        # TODO: เชื่อมต่อ signals ของ schedule manager:
        #   - self.schedule_manager.schedule_triggered.connect(self.on_schedule_triggered)
        #   - self.schedule_manager.error_occurred.connect(self.show_error)

        # TODO: เชื่อมต่อ signals ของ schedule widget:
        #   - schedule_widget.schedule_added.connect(self.on_schedule_added)
        pass

    def start_manual_recording(self, recording_data):
        """เริ่มการบันทึกแมนนวล"""
        try:
            # TODO: ตรวจสอบว่ากำลังบันทึกอยู่หรือไม่
            # TODO: เริ่มการบันทึกด้วย DABRecorderEngine
            # TODO: อัปเดตสถานะ UI
            self.status_label.setText(f"กำลังบันทึก: {recording_data.get('program_name', 'Unknown')}")
        except Exception as e:
            self.show_error(f"Start manual recording error: {e}")

    def on_recording_started(self, recording_info):
        """เมื่อเริ่มการบันทึก"""
        try:
            # TODO: อัปเดตสถานะใน UI ทุก tab ที่เกี่ยวข้อง
            # TODO: อัปเดต status bar
            # TODO: disable การบันทึกใหม่จนกว่าจะเสร็จ
            logger.info(f"Recording started: {recording_info}")
        except Exception as e:
            logger.error(f"Recording started processing error: {e}")

    def on_recording_progress(self, progress, message):
        """อัปเดตความก้าวหน้าการบันทึก"""
        try:
            # TODO: อัปเดต progress ใน manual recording widget
            # TODO: อัปเดต status bar ด้วย progress และ message
            pass
        except Exception as e:
            logger.error(f"Recording progress error: {e}")

    def on_recording_completed(self, result):
        """เมื่อการบันทึกเสร็จสิ้น"""
        try:
            # TODO: บันทึกผลลงฐานข้อมูล
            # TODO: อัปเดต UI ทุก tab ที่เกี่ยวข้อง
            # TODO: แสดงข้อความแจ้งเตือน (QMessageBox)
            # TODO: รีเฟรช recording history
            # TODO: enable การบันทึกใหม่

            status = result.get('status', 'unknown')
            if status == 'completed':
                self.status_label.setText("บันทึกเสร็จสิ้น")
                QMessageBox.information(self, "Recording Completed",
                                      f"การบันทึกเสร็จสิ้น\nไฟล์: {result.get('output_path', 'Unknown')}")
            else:
                self.status_label.setText("บันทึกไม่สำเร็จ")
                QMessageBox.warning(self, "Recording Failed", "การบันทึกไม่สำเร็จ")

        except Exception as e:
            logger.error(f"Recording completion processing error: {e}")

    def on_schedule_triggered(self, schedule_data):
        """เมื่อถึงเวลาตามตารางเวลา"""
        try:
            # TODO: ตรวจสอบว่ากำลังบันทึกอยู่หรือไม่
            # TODO: แสดงการแจ้งเตือนให้ผู้ใช้ทราบ
            # TODO: เริ่มการบันทึกอัตโนมัติ
            # TODO: อัปเดต UI ให้แสดงการบันทึกตามตารางเวลา

            program_name = schedule_data.get('program_name', 'Unknown')
            station_name = schedule_data.get('station_name', 'Unknown')

            reply = QMessageBox.question(self, "Scheduled Recording",
                                       f"ถึงเวลาบันทึก:\n{program_name} @ {station_name}\n\nเริ่มบันทึกหรือไม่?",
                                       QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.start_manual_recording(schedule_data)

        except Exception as e:
            logger.error(f"Schedule trigger processing error: {e}")

    def on_schedule_added(self):
        """เมื่อเพิ่มตารางเวลาใหม่"""
        # TODO: รีเฟรชข้อมูลตารางเวลาในทุก widget ที่เกี่ยวข้อง
        # TODO: อัปเดต status bar
        pass

    def show_error(self, error_message):
        """แสดงข้อความผิดพลาด"""
        QMessageBox.critical(self, "Error", error_message)
        self.status_label.setText(f"Error: {error_message}")
        logger.error(error_message)

    def closeEvent(self, event):
        """เมื่อปิดโปรแกรม"""
        try:
            # TODO: หยุดการทำงานของ recorder
            # TODO: หยุดการทำงานของ schedule manager
            # TODO: รอให้ threads หยุดทำงาน
            # TODO: ทำความสะอาด resources

            if self.recorder.is_recording:
                reply = QMessageBox.question(self, "Close Application",
                                           "กำลังบันทึกอยู่ ต้องการปิดโปรแกรมหรือไม่?",
                                           QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No:
                    event.ignore()
                    return

            self.recorder.stop_recording()
            self.schedule_manager.stop_manager()

            if self.recorder.isRunning():
                self.recorder.wait(3000)
            if self.schedule_manager.isRunning():
                self.schedule_manager.wait(3000)

            event.accept()

        except Exception as e:
            logger.error(f"Close event error: {e}")
            event.accept()

# ---------- Main Function ----------
def main():
    """ฟังก์ชันหลัก"""
    app = QApplication(sys.argv)

    # TODO: ตั้งค่า font สำหรับ touch interface
    font = QFont()
    font.setPointSize(12)
    app.setFont(font)

    # TODO: สร้างและแสดงหน้าต่างหลัก
    window = Lab5MainWindow()
    window.show()

    print("LAB 5: DAB+ Program Recorder")
    print("Based on Lab 3 RTL-SDR + ETI Pipeline")
    print("Features to implement:")
    print("- Scheduled DAB+ program recording")
    print("- Manual recording with real-time monitoring")
    print("- Audio file playback with QMediaPlayer")
    print("- ETI stream processing for service extraction")
    print("- Touch-friendly interface")

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()