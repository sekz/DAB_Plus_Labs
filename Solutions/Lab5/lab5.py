#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAB 5: สร้าง DAB+ Program Recorder (เฉลย)
- พัฒนาระบบบันทึกรายการ DAB+ ตามตารางเวลา
- จัดการตารางเวลาการบันทึกและการเล่นไฟล์
- รองรับหน้าจอสัมผัส 7" ด้วย PyQt5 และ QMediaPlayer
- บันทึกไฟล์เสียง, สไลด์โชว์, และเมทาดาต้า
"""

import sys
import os
import json
import sqlite3
import logging
import subprocess
import shutil
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

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Lab5")

# ---------- Recording Database ----------
class RecordingDatabase:
    def __init__(self, db_path="dab_recordings.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """สร้างฐานข้อมูลและตาราง"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # ตารางตารางเวลาการบันทึก
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recording_schedule (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    station_name TEXT NOT NULL,
                    frequency_mhz REAL NOT NULL,
                    program_name TEXT,
                    start_time TIME,
                    end_time TIME,
                    days_of_week TEXT,  -- JSON array of weekdays
                    is_active BOOLEAN DEFAULT 1,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            ''')

            # ตารางประวัติการบันทึก
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recording_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    schedule_id INTEGER,
                    station_name TEXT,
                    program_name TEXT,
                    start_time DATETIME,
                    end_time DATETIME,
                    file_path TEXT,
                    file_size INTEGER,
                    status TEXT,  -- success, error, cancelled
                    error_message TEXT,
                    FOREIGN KEY (schedule_id) REFERENCES recording_schedule (id)
                )
            ''')

            # ตารางไฟล์ที่บันทึก
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recorded_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recording_id INTEGER,
                    file_type TEXT,  -- audio, metadata, slideshow
                    file_path TEXT,
                    file_name TEXT,
                    file_size INTEGER,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (recording_id) REFERENCES recording_history (id)
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("ฐานข้อมูลการบันทึกพร้อมใช้งาน")
        except Exception as e:
            logger.error(f"สร้างฐานข้อมูลผิดพลาด: {str(e)}")

    def add_schedule(self, schedule_data):
        """เพิ่มตารางเวลาการบันทึก"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO recording_schedule
                (station_name, frequency_mhz, program_name, start_time, end_time, days_of_week, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                schedule_data['station_name'],
                schedule_data['frequency_mhz'],
                schedule_data['program_name'],
                schedule_data['start_time'],
                schedule_data['end_time'],
                json.dumps(schedule_data['days_of_week']),
                schedule_data.get('notes', '')
            ))

            schedule_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return schedule_id
        except Exception as e:
            logger.error(f"เพิ่มตารางเวลาผิดพลาด: {str(e)}")
            return None

    def get_all_schedules(self):
        """ดึงตารางเวลาทั้งหมด"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM recording_schedule WHERE is_active = 1 ORDER BY start_time')
            schedules = cursor.fetchall()
            conn.close()
            return schedules
        except Exception as e:
            logger.error(f"ดึงตารางเวลาผิดพลาด: {str(e)}")
            return []

    def add_recording(self, recording_data):
        """เพิ่มบันทึกการบันทึก"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO recording_history
                (schedule_id, station_name, program_name, start_time, end_time,
                 file_path, file_size, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                recording_data.get('schedule_id'),
                recording_data['station_name'],
                recording_data['program_name'],
                recording_data['start_time'],
                recording_data['end_time'],
                recording_data.get('file_path'),
                recording_data.get('file_size', 0),
                recording_data['status'],
                recording_data.get('error_message')
            ))

            recording_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return recording_id
        except Exception as e:
            logger.error(f"เพิ่มบันทึกการบันทึกผิดพลาด: {str(e)}")
            return None

    def get_recordings(self, limit=50):
        """ดึงประวัติการบันทึก"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM recording_history
                ORDER BY start_time DESC LIMIT ?
            ''', (limit,))
            recordings = cursor.fetchall()
            conn.close()
            return recordings
        except Exception as e:
            logger.error(f"ดึงประวัติการบันทึกผิดพลาด: {str(e)}")
            return []

# ---------- DAB+ Recorder Thread ----------
class DABRecorder(QThread):
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
        self.output_dir.mkdir(exist_ok=True)

    def start_recording(self, schedule_data):
        """เริ่มการบันทึก"""
        try:
            if self.is_recording:
                self.recording_error.emit("กำลังบันทึกอยู่แล้ว")
                return

            self.current_recording = {
                'station_name': schedule_data['station_name'],
                'frequency_mhz': schedule_data['frequency_mhz'],
                'program_name': schedule_data.get('program_name', 'Unknown'),
                'start_time': datetime.now(),
                'output_path': self.get_output_path(schedule_data)
            }

            self.is_recording = True
            self._stop_flag = False
            self.start()

        except Exception as e:
            self.recording_error.emit(f"เริ่มบันทึกผิดพลาด: {str(e)}")

    def get_output_path(self, schedule_data):
        """สร้างเส้นทางไฟล์ output"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        station_name = schedule_data['station_name'].replace(' ', '_')
        filename = f"{station_name}_{timestamp}"
        return self.output_dir / filename

    def run(self):
        """ทำการบันทึกจริง"""
        try:
            if not self.current_recording:
                return

            self.recording_started.emit(self.current_recording)

            # ใช้ welle.io หรือ rtl_sdr command line สำหรับการบันทึกจริง
            output_path = self.current_recording['output_path']
            frequency = self.current_recording['frequency_mhz']

            # สร้างคำสั่งสำหรับบันทึก (ตัวอย่าง)
            # ในการใช้งานจริง ใช้ welle.io หรือ rtl_fm
            self.record_with_mock(output_path, frequency)

            # อัปเดตข้อมูลการบันทึก
            end_time = datetime.now()
            duration = (end_time - self.current_recording['start_time']).total_seconds()

            result = {
                'station_name': self.current_recording['station_name'],
                'program_name': self.current_recording['program_name'],
                'start_time': self.current_recording['start_time'],
                'end_time': end_time,
                'duration': duration,
                'file_path': str(output_path),
                'file_size': self.get_file_size(output_path),
                'status': 'success'
            }

            self.recording_completed.emit(result)

        except Exception as e:
            self.recording_error.emit(f"บันทึกผิดพลาด: {str(e)}")
        finally:
            self.is_recording = False

    def record_with_mock(self, output_path, frequency):
        """จำลองการบันทึก (ในการใช้งานจริงใช้ welle.io)"""
        try:
            # สร้างไฟล์ mock audio
            audio_file = f"{output_path}.wav"
            metadata_file = f"{output_path}_metadata.json"
            slideshow_file = f"{output_path}_slideshow.jpg"

            # จำลองการบันทึกเสียง
            with open(audio_file, 'wb') as f:
                # สร้างไฟล์ WAV header อย่างง่าย
                f.write(b'RIFF')
                f.write((44100 * 2 * 2 * 60).to_bytes(4, 'little'))  # 1 minute mock
                f.write(b'WAVE')
                f.write(b'fmt ')
                f.write((16).to_bytes(4, 'little'))
                f.write((1).to_bytes(2, 'little'))
                f.write((2).to_bytes(2, 'little'))
                f.write((44100).to_bytes(4, 'little'))
                f.write((44100 * 2 * 2).to_bytes(4, 'little'))
                f.write((4).to_bytes(2, 'little'))
                f.write((16).to_bytes(2, 'little'))
                f.write(b'data')
                f.write((44100 * 2 * 2 * 60).to_bytes(4, 'little'))

                # เขียนข้อมูลเสียง mock
                for i in range(44100 * 60):  # 1 minute
                    if self._stop_flag:
                        break
                    f.write((0).to_bytes(4, 'little'))
                    if i % 4410 == 0:  # อัปเดต progress ทุก 0.1 วินาที
                        progress = int((i / (44100 * 60)) * 100)
                        self.recording_progress.emit(progress, f"บันทึกไป {progress}%")

            # สร้าง metadata
            metadata = {
                'station': self.current_recording['station_name'],
                'frequency': self.current_recording['frequency_mhz'],
                'program': self.current_recording['program_name'],
                'start_time': self.current_recording['start_time'].isoformat(),
                'bitrate': '128 kbps',
                'format': 'WAV'
            }

            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            # สร้าง slideshow mock
            with open(slideshow_file, 'wb') as f:
                # Mock JPEG header
                f.write(b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xFF\xDB\x00C\x00')
                f.write(b'\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f')

        except Exception as e:
            raise Exception(f"จำลองการบันทึกผิดพลาด: {str(e)}")

    def get_file_size(self, path):
        """คำนวณขนาดไฟล์"""
        try:
            if os.path.exists(f"{path}.wav"):
                return os.path.getsize(f"{path}.wav")
            return 0
        except:
            return 0

    def stop_recording(self):
        """หยุดการบันทึก"""
        self._stop_flag = True
        self.is_recording = False

# ---------- Schedule Manager ----------
class ScheduleManager(QThread):
    schedule_triggered = pyqtSignal(dict)

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
                self.check_schedules()
                self.msleep(60000)  # ตรวจสอบทุกนาที
            except Exception as e:
                logger.error(f"ตรวจสอบตารางเวลาผิดพลาด: {str(e)}")
                self.msleep(5000)

    def check_schedules(self):
        """ตรวจสอบตารางเวลาว่าถึงเวลาบันทึกหรือไม่"""
        try:
            current_time = datetime.now()
            current_weekday = current_time.weekday()  # 0=Monday, 6=Sunday
            schedules = self.db.get_all_schedules()

            for schedule in schedules:
                # schedule: (id, station_name, frequency_mhz, program_name, start_time, end_time, days_of_week, is_active, created_date, notes)
                if not schedule[7]:  # is_active
                    continue

                try:
                    days_of_week = json.loads(schedule[6]) if schedule[6] else []
                    if current_weekday not in days_of_week:
                        continue

                    # แปลง time string เป็น datetime object
                    start_time_str = schedule[4]  # start_time
                    start_hour, start_minute = map(int, start_time_str.split(':'))

                    scheduled_time = current_time.replace(
                        hour=start_hour,
                        minute=start_minute,
                        second=0,
                        microsecond=0
                    )

                    # ตรวจสอบว่าถึงเวลาแล้วหรือไม่ (± 1 นาที)
                    time_diff = abs((current_time - scheduled_time).total_seconds())
                    if time_diff <= 60:
                        schedule_data = {
                            'id': schedule[0],
                            'station_name': schedule[1],
                            'frequency_mhz': schedule[2],
                            'program_name': schedule[3],
                            'start_time': schedule[4],
                            'end_time': schedule[5]
                        }
                        self.schedule_triggered.emit(schedule_data)
                        logger.info(f"ถึงเวลาบันทึก: {schedule[1]} - {schedule[3]}")

                except Exception as e:
                    logger.error(f"ตรวจสอบตารางเวลา {schedule[0]} ผิดพลาด: {str(e)}")

        except Exception as e:
            logger.error(f"ตรวจสอบตารางเวลาผิดพลาด: {str(e)}")

    def stop_manager(self):
        """หยุดการทำงาน"""
        self.running = False
        self._stop_flag = True

# ---------- Schedule Widget ----------
class ScheduleWidget(QWidget):
    schedule_added = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db = RecordingDatabase()
        self.setup_ui()
        self.refresh_schedules()

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

        # Station name
        form_layout.addWidget(QLabel("ชื่อสถานี:"), 0, 0)
        self.station_name_edit = QComboBox()
        self.station_name_edit.setEditable(True)
        self.station_name_edit.addItems([
            "BBC Radio 1", "Heart FM", "Capital FM", "Classic FM",
            "LBC", "Virgin Radio", "Smooth Radio"
        ])
        form_layout.addWidget(self.station_name_edit, 0, 1)

        # Frequency
        form_layout.addWidget(QLabel("ความถี่ (MHz):"), 0, 2)
        self.frequency_spin = QSpinBox()
        self.frequency_spin.setRange(174, 240)
        self.frequency_spin.setValue(174)
        form_layout.addWidget(self.frequency_spin, 0, 3)

        # Program name
        form_layout.addWidget(QLabel("ชื่อรายการ:"), 1, 0)
        self.program_name_edit = QComboBox()
        self.program_name_edit.setEditable(True)
        self.program_name_edit.addItems([
            "Morning Show", "News", "Music Hour", "Talk Show",
            "Sports", "Weather", "Traffic Update"
        ])
        form_layout.addWidget(self.program_name_edit, 1, 1)

        # Time range
        form_layout.addWidget(QLabel("เวลาเริ่ม:"), 1, 2)
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setTime(QTime(8, 0))
        form_layout.addWidget(self.start_time_edit, 1, 3)

        form_layout.addWidget(QLabel("เวลาสิ้นสุด:"), 2, 0)
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setTime(QTime(9, 0))
        form_layout.addWidget(self.end_time_edit, 2, 1)

        # Days of week
        days_widget = QWidget()
        days_layout = QHBoxLayout(days_widget)
        days_layout.addWidget(QLabel("วันในสัปดาห์:"))

        self.day_checkboxes = []
        days = ["จ", "อ", "พ", "พฤ", "ศ", "ส", "อา"]
        for i, day in enumerate(days):
            cb = QCheckBox(day)
            cb.setProperty("day_index", i)
            self.day_checkboxes.append(cb)
            days_layout.addWidget(cb)

        form_layout.addWidget(days_widget, 2, 2, 1, 2)

        # Add button
        self.add_schedule_btn = QPushButton("➕ เพิ่มตารางเวลา")
        self.add_schedule_btn.setMinimumHeight(40)
        self.add_schedule_btn.clicked.connect(self.add_schedule)
        form_layout.addWidget(self.add_schedule_btn, 3, 0, 1, 4)

        layout.addWidget(form_group)

        # ตารางแสดงตารางเวลา
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(6)
        self.schedule_table.setHorizontalHeaderLabels([
            "สถานี", "รายการ", "เวลาเริ่ม", "เวลาสิ้นสุด", "วัน", "สถานะ"
        ])

        header = self.schedule_table.horizontalHeader()
        header.setStretchLastSection(True)

        layout.addWidget(self.schedule_table)

        # ปุ่มควบคุม
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 รีเฟรช")
        self.delete_btn = QPushButton("🗑️ ลบ")
        self.toggle_btn = QPushButton("⏯️ เปิด/ปิด")

        for btn in [self.refresh_btn, self.delete_btn, self.toggle_btn]:
            btn.setMinimumHeight(40)
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        # เชื่อมต่อ signals
        self.refresh_btn.clicked.connect(self.refresh_schedules)

    def add_schedule(self):
        """เพิ่มตารางเวลาใหม่"""
        try:
            # รวบรวมข้อมูล
            selected_days = []
            for cb in self.day_checkboxes:
                if cb.isChecked():
                    selected_days.append(cb.property("day_index"))

            if not selected_days:
                QMessageBox.warning(self, "ข้อมูลไม่ครบ", "กรุณาเลือกวันในสัปดาห์")
                return

            schedule_data = {
                'station_name': self.station_name_edit.currentText(),
                'frequency_mhz': float(self.frequency_spin.value()),
                'program_name': self.program_name_edit.currentText(),
                'start_time': self.start_time_edit.time().toString("HH:mm"),
                'end_time': self.end_time_edit.time().toString("HH:mm"),
                'days_of_week': selected_days,
                'notes': ''
            }

            # บันทึกลงฐานข้อมูล
            schedule_id = self.db.add_schedule(schedule_data)

            if schedule_id:
                QMessageBox.information(self, "เพิ่มสำเร็จ", "เพิ่มตารางเวลาแล้ว")
                self.refresh_schedules()
                self.schedule_added.emit()
                self.clear_form()
            else:
                QMessageBox.critical(self, "เพิ่มไม่สำเร็จ", "ไม่สามารถเพิ่มตารางเวลาได้")

        except Exception as e:
            QMessageBox.critical(self, "เกิดข้อผิดพลาด", str(e))
            logger.error(f"เพิ่มตารางเวลาผิดพลาด: {str(e)}")

    def clear_form(self):
        """เคลียร์ฟอร์ม"""
        for cb in self.day_checkboxes:
            cb.setChecked(False)

    def refresh_schedules(self):
        """รีเฟรชตารางเวลา"""
        try:
            schedules = self.db.get_all_schedules()
            self.schedule_table.setRowCount(len(schedules))

            for i, schedule in enumerate(schedules):
                self.schedule_table.setItem(i, 0, QTableWidgetItem(schedule[1]))  # station_name
                self.schedule_table.setItem(i, 1, QTableWidgetItem(schedule[3]))  # program_name
                self.schedule_table.setItem(i, 2, QTableWidgetItem(schedule[4]))  # start_time
                self.schedule_table.setItem(i, 3, QTableWidgetItem(schedule[5]))  # end_time

                # แปลงวันในสัปดาห์
                days_json = schedule[6]
                if days_json:
                    days_list = json.loads(days_json)
                    day_names = ["จ", "อ", "พ", "พฤ", "ศ", "ส", "อา"]
                    day_str = ",".join([day_names[d] for d in days_list])
                    self.schedule_table.setItem(i, 4, QTableWidgetItem(day_str))

                status = "เปิด" if schedule[7] else "ปิด"  # is_active
                self.schedule_table.setItem(i, 5, QTableWidgetItem(status))

            logger.info(f"รีเฟรชตารางเวลา {len(schedules)} รายการ")

        except Exception as e:
            logger.error(f"รีเฟรชตารางเวลาผิดพลาด: {str(e)}")

# ---------- Recording History Widget ----------
class RecordingHistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db = RecordingDatabase()
        self.media_player = QMediaPlayer()
        self.setup_ui()
        self.refresh_history()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # หัวข้อ
        title = QLabel("ประวัติการบันทึก")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # ตารางประวัติ
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "สถานี", "รายการ", "วันที่บันทึก", "ระยะเวลา", "ขนาดไฟล์", "สถานะ"
        ])

        header = self.history_table.horizontalHeader()
        header.setStretchLastSection(True)

        layout.addWidget(self.history_table)

        # Media Player Controls
        player_group = QGroupBox("เล่นไฟล์ที่บันทึก")
        player_layout = QVBoxLayout(player_group)

        # ข้อมูลไฟล์ปัจจุบัน
        self.current_file_label = QLabel("ยังไม่ได้เลือกไฟล์")
        player_layout.addWidget(self.current_file_label)

        # Progress bar
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        player_layout.addWidget(self.position_slider)

        # Control buttons
        control_layout = QHBoxLayout()
        self.play_btn = QPushButton("▶️ เล่น")
        self.pause_btn = QPushButton("⏸️ หยุดชั่วคราว")
        self.stop_btn = QPushButton("⏹️ หยุด")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)

        for btn in [self.play_btn, self.pause_btn, self.stop_btn]:
            btn.setMinimumHeight(40)
            control_layout.addWidget(btn)

        control_layout.addWidget(QLabel("🔊"))
        control_layout.addWidget(self.volume_slider)

        player_layout.addLayout(control_layout)
        layout.addWidget(player_group)

        # ปุ่มควบคุม
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 รีเฟรช")
        self.play_selected_btn = QPushButton("🎵 เล่นที่เลือก")
        self.delete_btn = QPushButton("🗑️ ลบไฟล์")
        self.export_btn = QPushButton("📤 ส่งออก")

        for btn in [self.refresh_btn, self.play_selected_btn, self.delete_btn, self.export_btn]:
            btn.setMinimumHeight(40)
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        # เชื่อมต่อ signals
        self.refresh_btn.clicked.connect(self.refresh_history)
        self.play_selected_btn.clicked.connect(self.play_selected_recording)
        self.play_btn.clicked.connect(self.media_player.play)
        self.pause_btn.clicked.connect(self.media_player.pause)
        self.stop_btn.clicked.connect(self.media_player.stop)
        self.volume_slider.valueChanged.connect(self.media_player.setVolume)
        self.history_table.itemSelectionChanged.connect(self.on_selection_changed)

        # Media player signals
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

    def refresh_history(self):
        """รีเฟรชประวัติการบันทึก"""
        try:
            recordings = self.db.get_recordings()
            self.history_table.setRowCount(len(recordings))

            for i, recording in enumerate(recordings):
                # recording: (id, schedule_id, station_name, program_name, start_time, end_time, file_path, file_size, status, error_message)
                self.history_table.setItem(i, 0, QTableWidgetItem(recording[2]))  # station_name
                self.history_table.setItem(i, 1, QTableWidgetItem(recording[3]))  # program_name

                # วันที่บันทึก
                start_time = datetime.fromisoformat(recording[4]) if recording[4] else None
                date_str = start_time.strftime("%d/%m/%Y %H:%M") if start_time else "Unknown"
                self.history_table.setItem(i, 2, QTableWidgetItem(date_str))

                # ระยะเวลา
                if recording[4] and recording[5]:
                    start = datetime.fromisoformat(recording[4])
                    end = datetime.fromisoformat(recording[5])
                    duration = (end - start).total_seconds()
                    duration_str = f"{int(duration//60):02d}:{int(duration%60):02d}"
                else:
                    duration_str = "Unknown"
                self.history_table.setItem(i, 3, QTableWidgetItem(duration_str))

                # ขนาดไฟล์
                file_size = recording[7] if recording[7] else 0
                size_str = f"{file_size/1024/1024:.1f} MB" if file_size > 0 else "0 MB"
                self.history_table.setItem(i, 4, QTableWidgetItem(size_str))

                # สถานะ
                status = recording[8] or "Unknown"
                self.history_table.setItem(i, 5, QTableWidgetItem(status))

                # เก็บ file path ไว้
                if recording[6]:
                    self.history_table.item(i, 0).setData(Qt.UserRole, recording[6])

            logger.info(f"รีเฟรชประวัติ {len(recordings)} รายการ")

        except Exception as e:
            logger.error(f"รีเฟรชประวัติผิดพลาด: {str(e)}")

    def on_selection_changed(self):
        """เมื่อเลือกแถวในตาราง"""
        try:
            current_row = self.history_table.currentRow()
            if current_row >= 0:
                file_path = self.history_table.item(current_row, 0).data(Qt.UserRole)
                if file_path:
                    station = self.history_table.item(current_row, 0).text()
                    program = self.history_table.item(current_row, 1).text()
                    date = self.history_table.item(current_row, 2).text()
                    self.current_file_label.setText(f"{station} - {program} ({date})")
        except Exception as e:
            logger.error(f"เลือกไฟล์ผิดพลาด: {str(e)}")

    def play_selected_recording(self):
        """เล่นไฟล์ที่เลือก"""
        try:
            current_row = self.history_table.currentRow()
            if current_row >= 0:
                file_path = self.history_table.item(current_row, 0).data(Qt.UserRole)
                if file_path and os.path.exists(f"{file_path}.wav"):
                    audio_file = f"{file_path}.wav"
                    url = QUrl.fromLocalFile(os.path.abspath(audio_file))
                    content = QMediaContent(url)
                    self.media_player.setMedia(content)
                    self.media_player.play()
                    logger.info(f"เล่นไฟล์: {audio_file}")
                else:
                    QMessageBox.warning(self, "ไม่พบไฟล์", "ไม่พบไฟล์เสียงที่ต้องการเล่น")
            else:
                QMessageBox.warning(self, "ไม่ได้เลือกไฟล์", "กรุณาเลือกไฟล์ที่ต้องการเล่น")
        except Exception as e:
            QMessageBox.critical(self, "เล่นไฟล์ผิดพลาด", str(e))

    def position_changed(self, position):
        """อัปเดตตำแหน่งการเล่น"""
        self.position_slider.setValue(position)

    def duration_changed(self, duration):
        """อัปเดตระยะเวลาทั้งหมด"""
        self.position_slider.setRange(0, duration)

# ---------- Manual Recording Widget ----------
class ManualRecordingWidget(QWidget):
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

        # ฟอร์มการตั้งค่า
        form_group = QGroupBox("การตั้งค่าการบันทึก")
        form_layout = QGridLayout(form_group)

        # Station settings
        form_layout.addWidget(QLabel("ชื่อสถานี:"), 0, 0)
        self.station_combo = QComboBox()
        self.station_combo.setEditable(True)
        self.station_combo.addItems([
            "BBC Radio 1", "Heart FM", "Capital FM", "Classic FM",
            "LBC", "Virgin Radio", "Smooth Radio"
        ])
        form_layout.addWidget(self.station_combo, 0, 1)

        form_layout.addWidget(QLabel("ความถี่ (MHz):"), 0, 2)
        self.frequency_spin = QSpinBox()
        self.frequency_spin.setRange(174, 240)
        self.frequency_spin.setValue(174)
        form_layout.addWidget(self.frequency_spin, 0, 3)

        # Program name
        form_layout.addWidget(QLabel("ชื่อรายการ:"), 1, 0)
        self.program_edit = QComboBox()
        self.program_edit.setEditable(True)
        self.program_edit.addItems([
            "Live Show", "News Bulletin", "Music Program", "Talk Show"
        ])
        form_layout.addWidget(self.program_edit, 1, 1)

        # Duration
        form_layout.addWidget(QLabel("ระยะเวลา (นาที):"), 1, 2)
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 240)
        self.duration_spin.setValue(30)
        form_layout.addWidget(self.duration_spin, 1, 3)

        layout.addWidget(form_group)

        # สถานะการบันทึก
        status_group = QGroupBox("สถานะการบันทึก")
        status_layout = QVBoxLayout(status_group)

        self.status_label = QLabel("ไม่ได้บันทึก")
        self.progress_bar = QProgressBar()
        self.time_label = QLabel("00:00 / 00:00")

        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)
        status_layout.addWidget(self.time_label)

        layout.addWidget(status_group)

        # ปุ่มควบคุม
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("⏺️ เริ่มบันทึก")
        self.stop_btn = QPushButton("⏹️ หยุดบันทึก")
        self.start_btn.setMinimumHeight(48)
        self.stop_btn.setMinimumHeight(48)
        self.stop_btn.setEnabled(False)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)

        layout.addLayout(button_layout)

        # เชื่อมต่อ signals
        self.start_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)

    def start_recording(self):
        """เริ่มการบันทึกแมนนวล"""
        try:
            recording_data = {
                'station_name': self.station_combo.currentText(),
                'frequency_mhz': float(self.frequency_spin.value()),
                'program_name': self.program_edit.currentText(),
                'duration_minutes': self.duration_spin.value()
            }

            self.recording_requested.emit(recording_data)

            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("กำลังบันทึก...")
            self.progress_bar.setValue(0)

        except Exception as e:
            QMessageBox.critical(self, "เริ่มบันทึกผิดพลาด", str(e))

    def stop_recording(self):
        """หยุดการบันทึก"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("หยุดบันทึก")

    def update_recording_progress(self, progress, message):
        """อัปเดตความก้าวหน้า"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)

    def recording_completed(self):
        """การบันทึกเสร็จสิ้น"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("บันทึกเสร็จสิ้น")
        self.progress_bar.setValue(100)

# ---------- Main Window ----------
class Lab5MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = RecordingDatabase()
        self.recorder = DABRecorder()
        self.schedule_manager = ScheduleManager()

        self.setup_ui()
        self.setup_touch_interface()
        self.setup_connections()

        self.setWindowTitle("LAB 5: สร้าง DAB+ Program Recorder")
        self.resize(1200, 900)

        # เริ่ม schedule manager
        self.schedule_manager.start()

    def setup_ui(self):
        """สร้าง UI หลัก"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # หัวข้อ
        title_label = QLabel("LAB 5: สร้าง DAB+ Program Recorder")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 20px; font-weight: bold; color: #2c3e50;
            padding: 15px; background-color: #ecf0f1; border-radius: 10px;
        """)
        main_layout.addWidget(title_label)

        # Tab widget
        self.tab_widget = QTabWidget()

        # Tab 1: Manual Recording
        self.manual_recording_widget = ManualRecordingWidget()
        self.tab_widget.addTab(self.manual_recording_widget, "⏺️ Manual Record")

        # Tab 2: Schedule Management
        self.schedule_widget = ScheduleWidget()
        self.tab_widget.addTab(self.schedule_widget, "📅 Schedule")

        # Tab 3: Recording History
        self.history_widget = RecordingHistoryWidget()
        self.tab_widget.addTab(self.history_widget, "📼 History")

        main_layout.addWidget(self.tab_widget)

        # Status bar
        self.status_label = QLabel("พร้อมใช้งาน - เลือกสถานีและเริ่มบันทึก")
        self.status_label.setStyleSheet("background-color: #d5f4e6; padding: 8px;")
        main_layout.addWidget(self.status_label)

    def setup_touch_interface(self):
        """ปรับการแสดงผลสำหรับหน้าจอสัมผัส"""
        font = QFont()
        font.setPointSize(14)
        self.setFont(font)

        # ปรับ tab widget
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setFont(QFont("Arial", 14))

        # ปรับปุ่มควบคุม
        buttons = [
            self.manual_recording_widget.start_btn,
            self.manual_recording_widget.stop_btn,
            self.schedule_widget.add_schedule_btn,
            self.schedule_widget.refresh_btn,
            self.history_widget.refresh_btn,
            self.history_widget.play_selected_btn,
            self.history_widget.play_btn,
            self.history_widget.pause_btn,
            self.history_widget.stop_btn
        ]

        for btn in buttons:
            btn.setMinimumHeight(48)
            btn.setFont(QFont("Arial", 14))

    def setup_connections(self):
        """เชื่อมต่อ signals และ slots"""
        # Manual recording signals
        self.manual_recording_widget.recording_requested.connect(self.start_manual_recording)

        # Recorder signals
        self.recorder.recording_started.connect(self.on_recording_started)
        self.recorder.recording_progress.connect(self.manual_recording_widget.update_recording_progress)
        self.recorder.recording_completed.connect(self.on_recording_completed)
        self.recorder.recording_error.connect(self.show_error)

        # Schedule manager signals
        self.schedule_manager.schedule_triggered.connect(self.on_schedule_triggered)

        # Schedule widget signals
        self.schedule_widget.schedule_added.connect(self.history_widget.refresh_history)

    def start_manual_recording(self, recording_data):
        """เริ่มการบันทึกแมนนวล"""
        try:
            if self.recorder.is_recording:
                QMessageBox.warning(self, "กำลังบันทึก", "กำลังบันทึกอยู่แล้ว")
                return

            self.recorder.start_recording(recording_data)
            self.status_label.setText(f"เริ่มบันทึก {recording_data['station_name']}")

        except Exception as e:
            self.show_error(f"เริ่มบันทึกผิดพลาด: {str(e)}")

    def on_recording_started(self, recording_info):
        """เมื่อเริ่มการบันทึก"""
        station = recording_info['station_name']
        program = recording_info['program_name']
        self.status_label.setText(f"กำลังบันทึก: {station} - {program}")
        logger.info(f"เริ่มบันทึก: {station} - {program}")

    def on_recording_completed(self, result):
        """เมื่อการบันทึกเสร็จสิ้น"""
        try:
            # บันทึกลงฐานข้อมูล
            self.db.add_recording(result)

            # อัปเดต UI
            self.manual_recording_widget.recording_completed()
            self.history_widget.refresh_history()

            station = result['station_name']
            duration = result.get('duration', 0)
            self.status_label.setText(f"บันทึกเสร็จสิ้น: {station} ({duration:.0f} วินาที)")

            QMessageBox.information(self, "บันทึกสำเร็จ", f"บันทึก {station} เสร็จสิ้น")
            logger.info(f"บันทึกเสร็จสิ้น: {station}")

        except Exception as e:
            logger.error(f"บันทึกผลการบันทึกผิดพลาด: {str(e)}")

    def on_schedule_triggered(self, schedule_data):
        """เมื่อถึงเวลาตามตารางเวลา"""
        try:
            if self.recorder.is_recording:
                logger.warning(f"กำลังบันทึกอยู่ ข้ามตารางเวลา: {schedule_data['station_name']}")
                return

            # เริ่มการบันทึกอัตโนมัติ
            self.recorder.start_recording(schedule_data)

            # แสดงการแจ้งเตือน
            self.status_label.setText(f"บันทึกตามตารางเวลา: {schedule_data['station_name']}")

            # TODO: แสดง notification popup

            logger.info(f"บันทึกตามตารางเวลา: {schedule_data['station_name']}")

        except Exception as e:
            logger.error(f"บันทึกตามตารางเวลาผิดพลาด: {str(e)}")

    def show_error(self, error_message):
        """แสดงข้อความผิดพลาด"""
        QMessageBox.critical(self, "เกิดข้อผิดพลาด", error_message)
        self.status_label.setText(f"ข้อผิดพลาด: {error_message}")
        logger.error(error_message)

    def closeEvent(self, event):
        """เมื่อปิดโปรแกรม"""
        try:
            # หยุดการทำงานของ threads
            if self.recorder.is_recording:
                self.recorder.stop_recording()
                self.recorder.wait()

            if self.schedule_manager.running:
                self.schedule_manager.stop_manager()
                self.schedule_manager.wait()

            event.accept()

        except Exception as e:
            logger.error(f"ปิดโปรแกรมผิดพลาด: {str(e)}")
            event.accept()

# ---------- Main Function ----------
def main():
    """ฟังก์ชันหลัก"""
    try:
        app = QApplication(sys.argv)

        # ตั้งค่า font สำหรับ touch interface
        font = QFont()
        font.setPointSize(14)
        app.setFont(font)

        # สร้างและแสดงหน้าต่างหลัก
        window = Lab5MainWindow()
        window.show()

        sys.exit(app.exec_())

    except Exception as e:
        print(f"เริ่มโปรแกรมผิดพลาด: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("LAB 5: สร้าง DAB+ Program Recorder (เฉลย)")
    main()