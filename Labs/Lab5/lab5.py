#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAB 5: สร้าง DAB+ Program Recorder (โจทย์)
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
        # TODO: สร้างตาราง recording_schedule สำหรับเก็บตารางเวลาการบันทึก
        # ตาราง: id, station_name, frequency_mhz, program_name, start_time, end_time,
        #        days_of_week (JSON), is_active, created_date, notes

        # TODO: สร้างตาราง recording_history สำหรับเก็บประวัติการบันทึก
        # ตาราง: id, schedule_id, station_name, program_name, start_time, end_time,
        #        file_path, file_size, status, error_message

        # TODO: สร้างตาราง recorded_files สำหรับเก็บข้อมูลไฟล์ที่บันทึก
        # ตาราง: id, recording_id, file_type, file_path, file_name, file_size, created_date
        pass

    def add_schedule(self, schedule_data):
        """เพิ่มตารางเวลาการบันทึก"""
        # TODO: เพิ่มตารางเวลาลงในฐานข้อมูล
        # TODO: return schedule_id หากสำเร็จ หรือ None หากไม่สำเร็จ
        pass

    def get_all_schedules(self):
        """ดึงตารางเวลาทั้งหมด"""
        # TODO: ดึงตารางเวลาที่ active จากฐานข้อมูล
        return []

    def add_recording(self, recording_data):
        """เพิ่มบันทึกการบันทึก"""
        # TODO: เพิ่มบันทึกการบันทึกลงในฐานข้อมูล
        # TODO: return recording_id หากสำเร็จ หรือ None หากไม่สำเร็จ
        pass

    def get_recordings(self, limit=50):
        """ดึงประวัติการบันทึก"""
        # TODO: ดึงประวัติการบันทึกจากฐานข้อมูล
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
        # TODO: สร้างโฟลเดอร์ output ถ้ายังไม่มี

    def start_recording(self, schedule_data):
        """เริ่มการบันทึก"""
        # TODO: ตรวจสอบว่ากำลังบันทึกอยู่หรือไม่
        # TODO: ตั้งค่า current_recording
        # TODO: เริ่ม thread สำหรับบันทึก
        pass

    def get_output_path(self, schedule_data):
        """สร้างเส้นทางไฟล์ output"""
        # TODO: สร้างชื่อไฟล์ที่เหมาะสมตาม timestamp และชื่อสถานี
        pass

    def run(self):
        """ทำการบันทึกจริง"""
        # TODO: บันทึกเสียงจาก DAB+ station โดยใช้ welle.io หรือ rtl_sdr
        # TODO: ส่ง signal recording_started, recording_progress, recording_completed
        # TODO: จัดการข้อผิดพลาดและส่ง recording_error
        pass

    def record_with_mock(self, output_path, frequency):
        """จำลองการบันทึก (สำหรับการทดสอบ)"""
        # TODO: สร้างไฟล์ audio, metadata, slideshow แบบ mock
        # TODO: อัปเดต progress ระหว่างการบันทึก
        pass

    def get_file_size(self, path):
        """คำนวณขนาดไฟล์"""
        # TODO: คำนวณขนาดไฟล์ที่บันทึก
        return 0

    def stop_recording(self):
        """หยุดการบันทึก"""
        # TODO: หยุดการทำงานของ thread
        pass

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
        # TODO: วนลูปตรวจสอบตารางเวลา
        # TODO: เรียก check_schedules() ทุกนาที
        pass

    def check_schedules(self):
        """ตรวจสอบตารางเวลาว่าถึงเวลาบันทึกหรือไม่"""
        # TODO: ดึงตารางเวลาที่ active
        # TODO: ตรวจสอบว่าถึงเวลาบันทึกหรือไม่
        # TODO: ส่ง signal schedule_triggered เมื่อถึงเวลา
        pass

    def stop_manager(self):
        """หยุดการทำงาน"""
        # TODO: หยุดการทำงานของ thread
        pass

# ---------- Schedule Widget ----------
class ScheduleWidget(QWidget):
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

        # TODO: สร้างฟิลด์สำหรับป้อนข้อมูล
        # Station name (ComboBox), Frequency (SpinBox), Program name (ComboBox)
        # Start time (TimeEdit), End time (TimeEdit), Days of week (CheckBoxes)

        # TODO: สร้างปุ่ม "เพิ่มตารางเวลา"

        layout.addWidget(form_group)

        # ตารางแสดงตารางเวลา
        self.schedule_table = QTableWidget()
        # TODO: ตั้งค่าคอลัมน์และหัวข้อตาราง

        layout.addWidget(self.schedule_table)

        # ปุ่มควบคุม
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 รีเฟรช")
        self.delete_btn = QPushButton("🗑️ ลบ")
        self.toggle_btn = QPushButton("⏯️ เปิด/ปิด")

        # TODO: ตั้งค่าปุ่มสำหรับ touch interface

        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.toggle_btn)

        layout.addLayout(button_layout)

        # TODO: เชื่อมต่อ signals

    def add_schedule(self):
        """เพิ่มตารางเวลาใหม่"""
        # TODO: รวบรวมข้อมูลจากฟอร์ม
        # TODO: ตรวจสอบความถูกต้องของข้อมูล
        # TODO: เรียก db.add_schedule()
        # TODO: แสดงผลลัพธ์และรีเฟรชตาราง
        pass

    def clear_form(self):
        """เคลียร์ฟอร์ม"""
        # TODO: เคลียร์ข้อมูลในฟอร์ม
        pass

    def refresh_schedules(self):
        """รีเฟรชตารางเวลา"""
        # TODO: ดึงข้อมูลตารางเวลาจากฐานข้อมูล
        # TODO: แสดงผลในตาราง
        pass

# ---------- Recording History Widget ----------
class RecordingHistoryWidget(QWidget):
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

        # ตารางประวัติ
        self.history_table = QTableWidget()
        # TODO: ตั้งค่าคอลัมน์และหัวข้อตาราง

        layout.addWidget(self.history_table)

        # Media Player Controls
        player_group = QGroupBox("เล่นไฟล์ที่บันทึก")
        player_layout = QVBoxLayout(player_group)

        # ข้อมูลไฟล์ปัจจุบัน
        self.current_file_label = QLabel("ยังไม่ได้เลือกไฟล์")
        player_layout.addWidget(self.current_file_label)

        # Progress bar สำหรับตำแหน่งการเล่น
        self.position_slider = QSlider(Qt.Horizontal)
        player_layout.addWidget(self.position_slider)

        # Control buttons
        control_layout = QHBoxLayout()
        self.play_btn = QPushButton("▶️ เล่น")
        self.pause_btn = QPushButton("⏸️ หยุดชั่วคราว")
        self.stop_btn = QPushButton("⏹️ หยุด")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)

        # TODO: ตั้งค่าปุ่มสำหรับ touch interface

        control_layout.addWidget(self.play_btn)
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.stop_btn)
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

        # TODO: ตั้งค่าปุ่มสำหรับ touch interface

        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.play_selected_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.export_btn)

        layout.addLayout(button_layout)

        # TODO: เชื่อมต่อ signals ของ media player และ UI

    def refresh_history(self):
        """รีเฟรชประวัติการบันทึก"""
        # TODO: ดึงข้อมูลประวัติจากฐานข้อมูล
        # TODO: แสดงผลในตาราง
        pass

    def on_selection_changed(self):
        """เมื่อเลือกแถวในตาราง"""
        # TODO: อัปเดตข้อมูลไฟล์ที่เลือก
        pass

    def play_selected_recording(self):
        """เล่นไฟล์ที่เลือก"""
        # TODO: เล่นไฟล์เสียงที่เลือกโดยใช้ QMediaPlayer
        pass

    def position_changed(self, position):
        """อัปเดตตำแหน่งการเล่น"""
        # TODO: อัปเดต position slider
        pass

    def duration_changed(self, duration):
        """อัปเดตระยะเวลาทั้งหมด"""
        # TODO: ตั้งค่า range ของ position slider
        pass

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

        # TODO: สร้างฟิลด์สำหรับการบันทึกแมนนวล
        # Station name (ComboBox), Frequency (SpinBox), Program name (ComboBox), Duration (SpinBox)

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
        # TODO: ตั้งค่าปุ่มสำหรับ touch interface
        # TODO: ตั้งค่าสถานะเริ่มต้น

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)

        layout.addLayout(button_layout)

        # TODO: เชื่อมต่อ signals

    def start_recording(self):
        """เริ่มการบันทึกแมนนวล"""
        # TODO: รวบรวมข้อมูลจากฟอร์ม
        # TODO: ส่ง signal recording_requested
        # TODO: อัปเดตสถานะ UI
        pass

    def stop_recording(self):
        """หยุดการบันทึก"""
        # TODO: อัปเดตสถานะ UI
        pass

    def update_recording_progress(self, progress, message):
        """อัปเดตความก้าวหน้า"""
        # TODO: อัปเดต progress bar และข้อความสถานะ
        pass

    def recording_completed(self):
        """การบันทึกเสร็จสิ้น"""
        # TODO: อัปเดตสถานะ UI เมื่อบันทึกเสร็จ
        pass

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

        # TODO: เริ่ม schedule manager

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

        # TODO: สร้าง Tab 1: Manual Recording (ใช้ ManualRecordingWidget)
        # TODO: สร้าง Tab 2: Schedule Management (ใช้ ScheduleWidget)
        # TODO: สร้าง Tab 3: Recording History (ใช้ RecordingHistoryWidget)

        main_layout.addWidget(self.tab_widget)

        # Status bar
        self.status_label = QLabel("พร้อมใช้งาน - เลือกสถานีและเริ่มบันทึก")
        self.status_label.setStyleSheet("background-color: #d5f4e6; padding: 8px;")
        main_layout.addWidget(self.status_label)

    def setup_touch_interface(self):
        """ปรับการแสดงผลสำหรับหน้าจอสัมผัส"""
        # TODO: ตั้งค่า font ขนาดใหญ่
        # TODO: ปรับขนาด tab widget
        # TODO: ปรับขนาดปุ่มทั้งหมดให้เหมาะสำหรับ touch
        pass

    def setup_connections(self):
        """เชื่อมต่อ signals และ slots"""
        # TODO: เชื่อมต่อ signals ของ manual recording
        # TODO: เชื่อมต่อ signals ของ recorder
        # TODO: เชื่อมต่อ signals ของ schedule manager
        pass

    def start_manual_recording(self, recording_data):
        """เริ่มการบันทึกแมนนวล"""
        # TODO: ตรวจสอบว่ากำลังบันทึกอยู่หรือไม่
        # TODO: เริ่มการบันทึก
        pass

    def on_recording_started(self, recording_info):
        """เมื่อเริ่มการบันทึก"""
        # TODO: อัปเดตสถานะใน UI
        pass

    def on_recording_completed(self, result):
        """เมื่อการบันทึกเสร็จสิ้น"""
        # TODO: บันทึกผลลงฐานข้อมูล
        # TODO: อัปเดต UI
        # TODO: แสดงข้อความแจ้งเตือน
        pass

    def on_schedule_triggered(self, schedule_data):
        """เมื่อถึงเวลาตามตารางเวลา"""
        # TODO: ตรวจสอบว่ากำลังบันทึกอยู่หรือไม่
        # TODO: เริ่มการบันทึกอัตโนมัติ
        # TODO: แสดงการแจ้งเตือน
        pass

    def show_error(self, error_message):
        """แสดงข้อความผิดพลาด"""
        # TODO: แสดง error dialog และอัปเดตสถานะ
        pass

    def closeEvent(self, event):
        """เมื่อปิดโปรแกรม"""
        # TODO: หยุดการทำงานของ threads ก่อนปิดโปรแกรม
        pass

# ---------- Main Function ----------
def main():
    """ฟังก์ชันหลัก"""
    # TODO: สร้าง QApplication
    # TODO: ตั้งค่า font สำหรับ touch interface
    # TODO: สร้างและแสดงหน้าต่างหลัก
    # TODO: เริ่มการทำงาน
    pass

if __name__ == "__main__":
    print("LAB 5: สร้าง DAB+ Program Recorder (โจทย์)")
    # TODO: เรียก main()