#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAB 4: สร้าง DAB+ Station Scanner (โจทย์ - ใช้ Lab 3 ETI approach)
- พัฒนาแอปพลิเคชันสแกนและติดตามสถานี DAB+ ด้วย RTL-SDR + ETI processing
- ติดตามคุณภาพสัญญาณแบบเรียลไทม์
- รองรับหน้าจอสัมผัส 7" ด้วย PyQt5
- ใช้ Lab 3 pipeline: RTL-SDR → ETI → Service parsing
"""

import sys
import os
import json
import csv
import sqlite3
import logging
import subprocess
import threading
import time
from datetime import datetime, timedelta
from collections import defaultdict

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QProgressBar, QComboBox, QSpinBox,
    QGroupBox, QSplitter, QTextEdit, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QFileDialog, QMessageBox, QListWidget, QListWidgetItem, QHeaderView,
    QSlider, QCheckBox, QGridLayout
)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, QDateTime
from PyQt5.QtGui import QFont, QPixmap, QIcon

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# นำเข้า modules จาก Lab 3 (สำหรับใช้ในการแก้โจทย์)
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Lab3'))
    from lab3_1a import RTLSDRDataAcquisition
    from lab3_2 import ETIProcessor
    from lab3_3 import ETIFrameParser
except ImportError as e:
    print(f"Warning: Cannot import Lab 3 modules: {e}")
    print("Make sure Lab 3 solutions are available")

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Lab4")

# DAB+ Thailand frequencies
DAB_FREQUENCIES = {
    '185.360': {'location': 'Bangkok/Phuket', 'block': '7A', 'freq': 185.360},
    '202.928': {'location': 'Bangkok', 'block': '9A', 'freq': 202.928},
    '195.936': {'location': 'Chiang Mai', 'block': '8C', 'freq': 195.936},
    '210.096': {'location': 'Northeast', 'block': '10B', 'freq': 210.096},
}

# ---------- Database Manager ----------
class StationDatabase:
    """ฐานข้อมูลสำหรับเก็บข้อมูลสถานี DAB+"""

    def __init__(self, db_path="dab_stations.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """สร้างฐานข้อมูลและตาราง"""
        # TODO: สร้างตารางสำหรับเก็บข้อมูลสถานี DAB+
        # ตาราง stations: id, ensemble_id, ensemble_name, service_id, service_name,
        #                frequency_mhz, channel, bitrate, audio_mode, first_detected, last_detected, detection_count
        # TODO: สร้างตารางประวัติคุณภาพสัญญาณ signal_history:
        #       id, station_id, timestamp, signal_strength, snr, ber, sync_status
        # TODO: สร้างตารางประวัติการสแกน scan_history:
        #       id, start_time, end_time, frequency_range, stations_found, scan_duration, notes
        pass

    def add_station(self, station_data):
        """เพิ่มสถานีใหม่หรืออัปเดตข้อมูลสถานีเดิม"""
        # TODO: เช็คว่ามีสถานีนี้แล้วหรือไม่ (จาก ensemble_id และ service_id)
        # TODO: หากมีแล้ว ให้อัปเดต last_detected และ detection_count
        # TODO: หากไม่มี ให้เพิ่มเป็นสถานีใหม่
        # TODO: return station_id หากสำเร็จ หรือ None หากไม่สำเร็จ
        pass

    def get_all_stations(self):
        """ดึงข้อมูลสถานีทั้งหมด"""
        # TODO: ดึงข้อมูลสถานีทั้งหมดจากฐานข้อมูล
        # TODO: เรียงลำดับตาม frequency_mhz และ service_name
        # TODO: return list ของ tuples ข้อมูลสถานี
        return []

    def add_signal_record(self, station_id, signal_data):
        """เพิ่มบันทึกคุณภาพสัญญาณ"""
        # TODO: บันทึกข้อมูลคุณภาพสัญญาณ (signal_strength, snr, ber, sync_status)
        # TODO: ใช้สำหรับสร้างกราฟแนวโน้มคุณภาพสัญญาณ
        pass

    def add_scan_record(self, scan_data):
        """เพิ่มบันทึกการสแกน"""
        # TODO: บันทึกประวัติการสแกน (frequency_range, stations_found, scan_duration, notes)
        # TODO: return scan_id หากสำเร็จ
        pass

    def get_station_history(self, station_id, hours=24):
        """ดึงประวัติสัญญาณของสถานีในช่วงเวลาที่กำหนด"""
        # TODO: ดึงข้อมูลประวัติสัญญาณของสถานีใน x ชั่วโมงที่ผ่านมา
        # TODO: return list ของข้อมูลสัญญาณพร้อม timestamp
        return []

# ---------- DAB+ Scanner Engine (ใช้ Lab 3 approach) ----------
class DABScannerEngine(QThread):
    """เครื่องมือสแกนสถานี DAB+ ใช้ Lab 3 pipeline"""

    station_found = pyqtSignal(dict)
    scan_progress = pyqtSignal(int, str)
    scan_completed = pyqtSignal(int)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_scanning = False
        self.frequency_ranges = {
            "Band III (174-240 MHz)": (174, 240),
            "L-Band (1452-1492 MHz)": (1452, 1492),
            "Thailand DAB+ Only": list(DAB_FREQUENCIES.keys())
        }
        self.current_range = "Thailand DAB+ Only"
        self._stop_flag = False

        # Lab 3 components
        self.rtl_sdr = None
        self.eti_processor = None
        self.eti_parser = None

    def setup_lab3_pipeline(self):
        """ตั้งค่า Lab 3 pipeline สำหรับสแกน"""
        try:
            # TODO: เริ่มต้น RTLSDRDataAcquisition
            # TODO: เริ่มต้น ETIProcessor
            # TODO: เริ่มต้น ETIFrameParser
            # TODO: return True หากสำเร็จ, False หากไม่สำเร็จ
            pass
        except Exception as e:
            logger.error(f"Lab 3 pipeline setup error: {e}")
            return False

    def set_frequency_range(self, range_name):
        """ตั้งค่าช่วงความถี่ที่จะสแกน"""
        # TODO: ตั้งค่า self.current_range
        # TODO: หยุดการสแกนปัจจุบันหากกำลังทำงาน
        pass

    def run(self):
        """สแกนหาสถานี DAB+"""
        self.is_scanning = True
        self._stop_flag = False
        stations_found = 0

        try:
            # TODO: ตั้งค่า Lab 3 pipeline
            # TODO: กำหนดรายการความถี่ที่จะสแกนตาม self.current_range
            # TODO: วนลูปสแกนแต่ละความถี่:
            #   - เรียก scan_frequency(frequency)
            #   - หากพบสถานี ส่ง signal station_found
            #   - ส่ง signal scan_progress เพื่ออัปเดตความก้าวหน้า
            #   - เช็ค self._stop_flag เพื่อหยุดการทำงาน
            # TODO: ส่ง signal scan_completed เมื่อสแกนเสร็จ
            pass
        except Exception as e:
            self.error_occurred.emit(f"Scan error: {e}")
        finally:
            self.cleanup()

    def scan_frequency(self, frequency):
        """สแกนความถี่เฉพาะใช้ Lab 3 approach"""
        try:
            # TODO: ตั้งค่าความถี่ให้ RTL-SDR
            # TODO: รับ I/Q data ด้วย capture_samples(duration_seconds=5)
            # TODO: ประมวลผล I/Q เป็น ETI ด้วย ETIProcessor
            # TODO: parse ETI frames ด้วย ETIFrameParser
            # TODO: หา DAB+ services จาก ETI data
            # TODO: return list ของ services หากพบ หรือ [] หากไม่พบ
            return []
        except Exception as e:
            logger.error(f"Frequency scan error at {frequency}: {e}")
            return []

    def process_iq_to_eti(self, iq_samples, frequency):
        """แปลง I/Q samples เป็น ETI data"""
        try:
            # TODO: ใช้ ETIProcessor.process_iq_data() หรือเรียก eti-cmdline
            # TODO: return ETI data หากสำเร็จ หรือ None หากไม่สำเร็จ
            return None
        except Exception as e:
            logger.error(f"IQ to ETI processing error: {e}")
            return None

    def parse_eti_services(self, eti_data, frequency):
        """parse ETI data เพื่อหา DAB+ services"""
        try:
            # TODO: ใช้ ETIFrameParser.parse_ensemble_info()
            # TODO: สร้าง dict ของข้อมูลสถานีที่พบ:
            #   {
            #       'ensemble_id': 'xxxx',
            #       'ensemble_name': 'Thailand DAB+',
            #       'service_id': 'xxxx',
            #       'service_name': 'Service Name',
            #       'frequency_mhz': frequency,
            #       'channel': 'xx',
            #       'bitrate': 128,
            #       'audio_mode': 'stereo'
            #   }
            # TODO: return list ของสถานีที่พบ
            return []
        except Exception as e:
            logger.error(f"ETI parsing error: {e}")
            return []

    def freq_to_channel(self, freq_mhz):
        """แปลงความถี่เป็นชื่อช่อง DAB+"""
        # TODO: แปลงความถี่เป็น channel name (เช่น 5A, 12B, L1 เป็นต้น)
        # TODO: ใช้มาตรฐาน DAB channel mapping
        return "Unknown"

    def stop_scan(self):
        """หยุดการสแกน"""
        # TODO: ตั้งค่า flags เพื่อหยุดการทำงาน
        self.is_scanning = False
        self._stop_flag = True

    def cleanup(self):
        """ทำความสะอาด resources"""
        try:
            # TODO: ปิดการเชื่อมต่อ RTL-SDR
            # TODO: หยุดการทำงานของ ETI processor
            pass
        except:
            pass

# ---------- Real-time Signal Monitor ----------
class SignalMonitor(QThread):
    """ติดตามคุณภาพสัญญาณแบบ real-time"""

    signal_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.monitoring = False
        self.monitored_stations = []  # list of {'station_id': int, 'frequency': float}
        self._stop_flag = False
        self.rtl_sdr = None

    def add_station(self, station_id, frequency):
        """เพิ่มสถานีที่ต้องติดตาม"""
        # TODO: เพิ่มสถานีในรายการติดตาม
        # TODO: เช็คว่ามีสถานีนี้อยู่แล้วหรือไม่
        pass

    def remove_station(self, station_id):
        """ลบสถานีจากการติดตาม"""
        # TODO: ลบสถานีจากรายการติดตาม
        pass

    def run(self):
        """ติดตามคุณภาพสัญญาณแบบ real-time"""
        self.monitoring = True
        self._stop_flag = False

        try:
            # TODO: ตั้งค่า RTL-SDR สำหรับการวัดสัญญาณ

            while self.monitoring and not self._stop_flag:
                # TODO: วนลูปติดตามสัญญาณของสถานีที่กำหนด
                # TODO: สำหรับแต่ละสถานีใน self.monitored_stations:
                #   - เรียก measure_signal_quality(station)
                #   - ส่ง signal signal_updated พร้อมข้อมูลคุณภาพ
                # TODO: รอ 5 วินาทีก่อนวัดครั้งต่อไป
                time.sleep(5)
        except Exception as e:
            self.error_occurred.emit(f"Signal monitoring error: {e}")
        finally:
            self.cleanup()

    def measure_signal_quality(self, station):
        """วัดคุณภาพสัญญาณ"""
        try:
            # TODO: ตั้งค่าความถี่ของ RTL-SDR
            # TODO: รับ I/Q samples สั้นๆ (1-2 วินาที)
            # TODO: คำนวณ signal strength, SNR, BER
            # TODO: ประเมินสถานะการ sync
            # TODO: return dict ของข้อมูลสัญญาณ:
            #   {
            #       'station_id': station['station_id'],
            #       'frequency': station['frequency'],
            #       'signal_strength': -50.0,  # dBm
            #       'snr': 15.0,               # dB
            #       'ber': 0.1,                # %
            #       'sync_status': 'good',     # excellent/good/fair/poor
            #       'timestamp': datetime.now()
            #   }
            return None
        except Exception as e:
            logger.error(f"Signal quality measurement error: {e}")
            return None

    def stop_monitoring(self):
        """หยุดการติดตาม"""
        # TODO: หยุดการทำงานของ thread
        self.monitoring = False
        self._stop_flag = True

    def cleanup(self):
        """ทำความสะอาด resources"""
        try:
            # TODO: ปิดการเชื่อมต่อ RTL-SDR
            pass
        except:
            pass

# ---------- Station List Widget ----------
class StationListWidget(QWidget):
    """Widget แสดงรายการสถานี DAB+"""

    station_selected = pyqtSignal(int)  # station_id

    def __init__(self):
        super().__init__()
        self.db = StationDatabase()
        self.setup_ui()
        # TODO: เรียก refresh_stations()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # หัวข้อ
        title = QLabel("รายการสถานี DAB+")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # ตารางสถานี
        self.station_table = QTableWidget()
        # TODO: ตั้งค่าจำนวนคอลัมน์และหัวข้อ:
        #       ['ID', 'Ensemble', 'Service', 'Frequency', 'Channel', 'Bitrate', 'Last Seen', 'Count']
        # TODO: ปรับขนาดคอลัมน์ให้เหมาะสม
        # TODO: ตั้งค่าให้เลือกได้ทีละแถว

        layout.addWidget(self.station_table)

        # ปุ่มควบคุม
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 รีเฟรช")
        self.monitor_btn = QPushButton("👁️ ติดตาม")
        self.export_btn = QPushButton("📊 ส่งออก CSV")

        # TODO: ตั้งค่าขนาดปุ่มสำหรับ touch interface (ความสูงอย่างน้อย 48px)
        # TODO: ตั้งค่า font ขนาดใหญ่

        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.monitor_btn)
        button_layout.addWidget(self.export_btn)

        layout.addLayout(button_layout)

        # TODO: เชื่อมต่อ signals:
        #   - self.refresh_btn.clicked.connect(self.refresh_stations)
        #   - self.monitor_btn.clicked.connect(self.toggle_monitoring)
        #   - self.export_btn.clicked.connect(self.export_stations)
        #   - self.station_table.itemSelectionChanged.connect(self.on_selection_changed)

    def refresh_stations(self):
        """รีเฟรชรายการสถานี"""
        # TODO: ดึงข้อมูลสถานีจากฐานข้อมูล
        # TODO: แสดงผลในตาราง (clear table แล้วเพิ่มข้อมูลใหม่)
        # TODO: format ข้อมูลให้อ่านง่าย (เช่น frequency เป็น MHz, datetime เป็น human readable)
        pass

    def on_selection_changed(self):
        """เมื่อเลือกสถานี"""
        # TODO: รับ station_id จากแถวที่เลือก
        # TODO: ส่ง signal station_selected พร้อม station_id
        pass

    def toggle_monitoring(self):
        """เปิด/ปิดการติดตาม"""
        # TODO: เช็คว่ามีสถานีที่เลือกหรือไม่
        # TODO: เชื่อมต่อกับ SignalMonitor เพื่อเริ่ม/หยุดการติดตาม
        # TODO: เปลี่ยนข้อความปุ่มตามสถานะ
        pass

    def export_stations(self):
        """ส่งออกข้อมูลสถานีเป็น CSV"""
        try:
            # TODO: เปิด file dialog เพื่อเลือกที่บันทึก
            # TODO: ส่งออกข้อมูลสถานีทั้งหมดเป็นไฟล์ CSV
            # TODO: แสดงข้อความยืนยันเมื่อสำเร็จ
            pass
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

# ---------- Signal Quality Chart Widget ----------
class SignalQualityChart(QWidget):
    """Widget แสดงกราฟคุณภาพสัญญาณ"""

    def __init__(self):
        super().__init__()
        self.setup_matplotlib()
        self.setup_ui()
        self.signal_history = defaultdict(list)  # {station_id: [data_points]}
        self.max_points = 100

    def setup_matplotlib(self):
        """ตั้งค่า matplotlib"""
        # TODO: สร้าง matplotlib Figure และ canvas
        # TODO: สร้าง subplots สำหรับ Signal Strength, SNR, และ BER
        # TODO: ตั้งค่า labels, grids, และสี
        pass

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("คุณภาพสัญญาณแบบ Real-time")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # TODO: เพิ่ม matplotlib canvas

        # ปุ่มควบคุม
        button_layout = QHBoxLayout()
        self.clear_btn = QPushButton("🗑️ เคลียร์กราฟ")
        self.save_btn = QPushButton("💾 บันทึกกราฟ")

        # TODO: ตั้งค่าปุ่มสำหรับ touch interface

        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

        # TODO: เชื่อมต่อ signals:
        #   - self.clear_btn.clicked.connect(self.clear_charts)
        #   - self.save_btn.clicked.connect(self.save_charts)

    def update_signal_data(self, signal_data):
        """อัปเดตข้อมูลสัญญาณ"""
        try:
            # TODO: เพิ่มข้อมูลสัญญาณใหม่เข้า self.signal_history
            # TODO: จำกัดจำนวนจุดข้อมูลตาม self.max_points
            # TODO: เรียก update_charts()
            pass
        except Exception as e:
            logger.error(f"Signal data update error: {e}")

    def update_charts(self):
        """อัปเดตกราฟ"""
        try:
            # TODO: clear axes ทั้งหมด
            # TODO: plot ข้อมูล Signal Strength, SNR, และ BER
            # TODO: ตั้งค่า title, labels, และ legend
            # TODO: refresh canvas
            pass
        except Exception as e:
            logger.error(f"Chart update error: {e}")

    def clear_charts(self):
        """เคลียร์กราฟ"""
        # TODO: เคลียร์ข้อมูลใน self.signal_history
        # TODO: เคลียร์กราฟและ refresh canvas
        pass

    def save_charts(self):
        """บันทึกกราฟ"""
        try:
            # TODO: เปิด file dialog เพื่อเลือกที่บันทึก
            # TODO: บันทึกกราฟเป็นไฟล์ PNG ด้วย savefig()
            # TODO: แสดงข้อความยืนยันเมื่อสำเร็จ
            pass
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

# ---------- Scanner Control Panel ----------
class ScannerControlPanel(QWidget):
    """Panel ควบคุมการสแกน"""

    scan_requested = pyqtSignal(str)  # frequency_range

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # การตั้งค่าการสแกน
        scan_group = QGroupBox("การตั้งค่าการสแกน")
        scan_layout = QVBoxLayout(scan_group)

        # ช่วงความถี่
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("ช่วงความถี่:"))
        self.freq_combo = QComboBox()
        # TODO: เพิ่มตัวเลือกช่วงความถี่:
        #   - "Thailand DAB+ Only"
        #   - "Band III (174-240 MHz)"
        #   - "L-Band (1452-1492 MHz)"
        freq_layout.addWidget(self.freq_combo)
        scan_layout.addLayout(freq_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("พร้อมสแกน")
        scan_layout.addWidget(self.progress_label)
        scan_layout.addWidget(self.progress_bar)

        # ปุ่มควบคุม
        button_layout = QHBoxLayout()
        self.start_scan_btn = QPushButton("🔍 เริ่มสแกน")
        self.stop_scan_btn = QPushButton("⏹️ หยุดสแกน")

        # TODO: ตั้งค่าขนาดปุ่มสำหรับ touch interface
        # TODO: ตั้งค่าสถานะปุ่ม (stop_scan_btn เริ่มต้นปิด)

        button_layout.addWidget(self.start_scan_btn)
        button_layout.addWidget(self.stop_scan_btn)
        scan_layout.addLayout(button_layout)

        layout.addWidget(scan_group)

        # สถิติการสแกน
        stats_group = QGroupBox("สถิติ")
        stats_layout = QVBoxLayout(stats_group)

        self.total_scans_label = QLabel("การสแกนทั้งหมด: 0")
        self.stations_found_label = QLabel("สถานีที่พบ: 0")
        self.last_scan_label = QLabel("ครั้งล่าสุด: -")

        stats_layout.addWidget(self.total_scans_label)
        stats_layout.addWidget(self.stations_found_label)
        stats_layout.addWidget(self.last_scan_label)

        layout.addWidget(stats_group)

        # TODO: เชื่อมต่อ signals:
        #   - self.start_scan_btn.clicked.connect(self.start_scan)
        #   - self.stop_scan_btn.clicked.connect(self.stop_scan)

    def start_scan(self):
        """เริ่มการสแกน"""
        # TODO: ส่ง signal scan_requested พร้อมช่วงความถี่ที่เลือก
        # TODO: ปิด/เปิดปุ่มตามสถานะ
        # TODO: reset progress bar
        pass

    def stop_scan(self):
        """หยุดการสแกน"""
        # TODO: ปิด/เปิดปุ่มตามสถานะ
        pass

    def update_progress(self, percent, message):
        """อัปเดตความก้าวหน้า"""
        # TODO: อัปเดต progress bar และข้อความ
        pass

    def scan_completed(self, stations_found):
        """การสแกนเสร็จสิ้น"""
        # TODO: อัปเดตสถิติและ UI
        # TODO: reset progress และปุ่ม
        # TODO: อัปเดตเวลาสแกนครั้งล่าสุด
        pass

# ---------- Main Window ----------
class Lab4MainWindow(QMainWindow):
    """หน้าต่างหลักของ Lab 4"""

    def __init__(self):
        super().__init__()
        self.db = StationDatabase()
        self.scanner = DABScannerEngine()
        self.signal_monitor = SignalMonitor()

        self.setup_ui()
        self.setup_touch_interface()
        self.setup_connections()

        self.setWindowTitle("LAB 4: สร้าง DAB+ Station Scanner (Lab 3 Pipeline)")
        self.resize(1200, 800)

        if '--fullscreen' in sys.argv:
            self.showFullScreen()

    def setup_ui(self):
        """สร้าง UI หลัก"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # หัวข้อ
        title_label = QLabel("LAB 4: DAB+ Station Scanner")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("""
            background-color: #2c3e50; color: white; padding: 15px;
            border-radius: 10px; margin: 5px;
        """)
        main_layout.addWidget(title_label)

        # Tab widget
        self.tab_widget = QTabWidget()

        # TODO: สร้าง Tab 1: Scanner
        #   - ใช้ ScannerControlPanel และ StationListWidget
        #   - จัด layout แบบ horizontal หรือ vertical

        # TODO: สร้าง Tab 2: Signal Monitoring
        #   - ใช้ SignalQualityChart
        #   - เพิ่ม controls สำหรับเลือกสถานีที่จะติดตาม

        # TODO: สร้าง Tab 3: History & Reports
        #   - แสดงประวัติการสแกน
        #   - สถิติการใช้งาน
        #   - export reports

        main_layout.addWidget(self.tab_widget)

        # Status bar
        self.status_label = QLabel("พร้อมใช้งาน - เลือกช่วงความถี่และเริ่มสแกน")
        self.status_label.setStyleSheet("background-color: #d5f4e6; padding: 8px; border-radius: 5px;")
        main_layout.addWidget(self.status_label)

    def setup_touch_interface(self):
        """ปรับการแสดงผลสำหรับหน้าจอสัมผัส"""
        # TODO: ตั้งค่า font ขนาดใหญ่สำหรับ application
        # TODO: ปรับขนาดปุ่มและ widget สำหรับ touch
        # TODO: ตั้งค่า tab widget ให้ใช้งานง่ายด้วยนิ้ว
        pass

    def setup_connections(self):
        """เชื่อมต่อ signals และ slots"""
        # TODO: เชื่อมต่อ signals ของ scanner:
        #   - self.scanner.station_found.connect(self.on_station_found)
        #   - self.scanner.scan_progress.connect(self.on_scan_progress)
        #   - self.scanner.scan_completed.connect(self.on_scan_completed)
        #   - self.scanner.error_occurred.connect(self.show_error)

        # TODO: เชื่อมต่อ signals ของ signal monitor:
        #   - self.signal_monitor.signal_updated.connect(self.on_signal_updated)
        #   - self.signal_monitor.error_occurred.connect(self.show_error)

        # TODO: เชื่อมต่อ signals ของ UI widgets
        pass

    def start_scan(self, frequency_range):
        """เริ่มการสแกน"""
        try:
            # TODO: ตั้งค่าช่วงความถี่ให้ scanner
            # TODO: เริ่มการทำงานของ DABScannerEngine
            # TODO: อัปเดตสถานะ UI
            self.status_label.setText(f"กำลังสแกน {frequency_range}...")
        except Exception as e:
            self.show_error(f"Start scan error: {e}")

    def on_station_found(self, station_data):
        """เมื่อพบสถานีใหม่"""
        try:
            # TODO: บันทึกสถานีลงฐานข้อมูล
            # TODO: อัปเดตแสดงผลในรายการสถานี
            # TODO: เพิ่มเข้าระบบติดตามสัญญาณ (ถ้าต้องการ)
            logger.info(f"Found station: {station_data.get('service_name', 'Unknown')}")
        except Exception as e:
            logger.error(f"Station found processing error: {e}")

    def on_scan_progress(self, percent, message):
        """อัปเดตความก้าวหน้าการสแกน"""
        # TODO: อัปเดต progress bar และข้อความใน scanner control panel
        # TODO: อัปเดตสถานะใน status bar
        pass

    def on_scan_completed(self, stations_found):
        """เมื่อการสแกนเสร็จสิ้น"""
        try:
            # TODO: บันทึกประวัติการสแกนลงฐานข้อมูล
            # TODO: อัปเดต UI และสถิติ
            # TODO: แสดงผลลัพธ์การสแกน
            self.status_label.setText(f"สแกนเสร็จ - พบสถานี {stations_found} สถานี")
        except Exception as e:
            logger.error(f"Scan completion processing error: {e}")

    def on_signal_updated(self, signal_data):
        """เมื่อมีข้อมูลสัญญาณใหม่"""
        try:
            # TODO: บันทึกข้อมูลสัญญาณลงฐานข้อมูล
            # TODO: อัปเดตกราฟคุณภาพสัญญาณ
            # TODO: อัปเดตสถานะการติดตาม
            pass
        except Exception as e:
            logger.error(f"Signal update processing error: {e}")

    def on_station_selected(self, station_id):
        """เมื่อเลือกสถานี"""
        try:
            # TODO: แสดงรายละเอียดสถานี
            # TODO: เริ่มติดตามสัญญาณ (ถ้าต้องการ)
            # TODO: เปลี่ยน tab ไปแสดงข้อมูลการติดตาม
            pass
        except Exception as e:
            logger.error(f"Station selection error: {e}")

    def show_error(self, error_message):
        """แสดงข้อความผิดพลาด"""
        QMessageBox.critical(self, "Error", error_message)
        self.status_label.setText(f"Error: {error_message}")
        logger.error(error_message)

    def closeEvent(self, event):
        """เมื่อปิดโปรแกรม"""
        try:
            # TODO: หยุดการทำงานของ scanner และ signal monitor
            # TODO: รอให้ threads หยุดทำงาน
            # TODO: ทำความสะอาด resources
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
    window = Lab4MainWindow()
    window.show()

    print("LAB 4: DAB+ Station Scanner")
    print("Based on Lab 3 RTL-SDR + ETI Pipeline")
    print("Features to implement:")
    print("- RTL-SDR frequency scanning")
    print("- ETI stream analysis")
    print("- Service discovery and database storage")
    print("- Real-time signal quality monitoring")
    print("- Touch-friendly interface")

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()