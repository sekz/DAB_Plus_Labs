#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAB 4: สร้าง DAB+ Station Scanner (เฉลย)
- พัฒนาแอปพลิเคชันสแกนและติดตามสถานี DAB+
- ติดตามคุณภาพสัญญาณแบบเรียลไทม์
- รองรับหน้าจอสัมผัส 7" ด้วย PyQt5
- มี GUI สำหรับจัดการสถานี, บันทึกประวัติ, และสร้างรายงาน
"""

import sys
import os
import json
import csv
import sqlite3
import logging
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QProgressBar, QComboBox, QSpinBox,
    QGroupBox, QSplitter, QTextEdit, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QFileDialog, QMessageBox, QListWidget, QListWidgetItem, QHeaderView,
    QSlider, QCheckBox
)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, QDateTime
from PyQt5.QtGui import QFont, QPixmap, QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Lab4")

# ---------- Database Manager ----------
class StationDatabase:
    def __init__(self, db_path="dab_stations.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """สร้างฐานข้อมูลและตาราง"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # ตารางสถานี DAB+
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ensemble_id TEXT,
                    ensemble_name TEXT,
                    service_id TEXT,
                    service_name TEXT,
                    frequency_mhz REAL,
                    channel TEXT,
                    bitrate INTEGER,
                    audio_mode TEXT,
                    first_detected DATETIME,
                    last_detected DATETIME,
                    detection_count INTEGER DEFAULT 1
                )
            ''')

            # ตารางประวัติคุณภาพสัญญาณ
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signal_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    station_id INTEGER,
                    timestamp DATETIME,
                    signal_strength REAL,
                    snr REAL,
                    ber REAL,
                    status TEXT,
                    FOREIGN KEY (station_id) REFERENCES stations (id)
                )
            ''')

            # ตารางประวัติการสแกน
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_date DATETIME,
                    frequency_range TEXT,
                    stations_found INTEGER,
                    scan_duration REAL,
                    notes TEXT
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("ฐานข้อมูลพร้อมใช้งาน")
        except Exception as e:
            logger.error(f"สร้างฐานข้อมูลผิดพลาด: {str(e)}")

    def add_station(self, station_data):
        """เพิ่มสถานีใหม่"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            now = datetime.now()

            cursor.execute('''
                INSERT INTO stations
                (ensemble_id, ensemble_name, service_id, service_name,
                 frequency_mhz, channel, bitrate, audio_mode, first_detected, last_detected)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                station_data.get('ensemble_id'),
                station_data.get('ensemble_name'),
                station_data.get('service_id'),
                station_data.get('service_name'),
                station_data.get('frequency_mhz'),
                station_data.get('channel'),
                station_data.get('bitrate'),
                station_data.get('audio_mode'),
                now, now
            ))

            station_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return station_id
        except Exception as e:
            logger.error(f"เพิ่มสถานีผิดพลาด: {str(e)}")
            return None

    def get_all_stations(self):
        """ดึงข้อมูลสถานีทั้งหมด"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM stations ORDER BY frequency_mhz, service_name
            ''')
            stations = cursor.fetchall()
            conn.close()
            return stations
        except Exception as e:
            logger.error(f"ดึงข้อมูลสถานีผิดพลาด: {str(e)}")
            return []

    def add_signal_record(self, station_id, signal_data):
        """เพิ่มบันทึกคุณภาพสัญญาณ"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO signal_history
                (station_id, timestamp, signal_strength, snr, ber, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                station_id,
                datetime.now(),
                signal_data.get('signal_strength'),
                signal_data.get('snr'),
                signal_data.get('ber'),
                signal_data.get('status')
            ))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"บันทึกสัญญาณผิดพลาด: {str(e)}")

    def add_scan_record(self, scan_data):
        """เพิ่มบันทึกการสแกน"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO scan_history
                (scan_date, frequency_range, stations_found, scan_duration, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                scan_data.get('frequency_range'),
                scan_data.get('stations_found'),
                scan_data.get('scan_duration'),
                scan_data.get('notes')
            ))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"บันทึกประวัติสแกนผิดพลาด: {str(e)}")

# ---------- DAB+ Scanner Thread ----------
class DABScanner(QThread):
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
            "Full Range": (174, 1492)
        }
        self.current_range = "Band III (174-240 MHz)"
        self._stop_flag = False

    def set_frequency_range(self, range_name):
        """ตั้งค่าช่วงความถี่ที่จะสแกน"""
        self.current_range = range_name

    def run(self):
        """สแกนหาสถานี DAB+"""
        self.is_scanning = True
        self._stop_flag = False
        stations_found = 0

        try:
            start_freq, end_freq = self.frequency_ranges[self.current_range]
            step = 1.712  # DAB+ channel spacing in MHz

            current_freq = start_freq
            total_steps = int((end_freq - start_freq) / step)
            step_count = 0

            while current_freq <= end_freq and not self._stop_flag:
                self.scan_progress.emit(
                    int((step_count / total_steps) * 100),
                    f"สแกนความถี่ {current_freq:.3f} MHz"
                )

                # จำลองการสแกนด้วย welle.io หรือ rtl_sdr
                station_data = self.scan_frequency(current_freq)
                if station_data:
                    self.station_found.emit(station_data)
                    stations_found += 1

                current_freq += step
                step_count += 1
                self.msleep(100)  # ช่วงหยุดระหว่างการสแกน

            self.scan_completed.emit(stations_found)

        except Exception as e:
            self.error_occurred.emit(f"สแกนผิดพลาด: {str(e)}")
        finally:
            self.is_scanning = False

    def scan_frequency(self, frequency):
        """สแกนความถี่เฉพาะ (จำลอง)"""
        try:
            # ในการใช้งานจริง ใช้ welle.io หรือ rtl_sdr command
            # นี่เป็นการจำลองข้อมูล

            # สร้างข้อมูลสถานีจำลอง (บางความถี่)
            mock_stations = {
                174.928: {"name": "BBC Radio 1", "ensemble": "BBC National DAB"},
                181.936: {"name": "Heart FM", "ensemble": "Digital One"},
                188.352: {"name": "Capital FM", "ensemble": "Capital London"},
                195.936: {"name": "Classic FM", "ensemble": "Sound Digital"},
                210.096: {"name": "LBC", "ensemble": "MuxCo London"},
                215.072: {"name": "Virgin Radio", "ensemble": "Digital One"},
                225.648: {"name": "Smooth Radio", "ensemble": "Global"}
            }

            # ตรวจสอบว่าความถี่นี้มีสถานีจำลองหรือไม่
            for mock_freq, station_info in mock_stations.items():
                if abs(frequency - mock_freq) < 0.1:  # ความแม่นยำ 100 kHz
                    return {
                        'ensemble_id': f"E{int(mock_freq)}",
                        'ensemble_name': station_info['ensemble'],
                        'service_id': f"S{int(mock_freq)}01",
                        'service_name': station_info['name'],
                        'frequency_mhz': mock_freq,
                        'channel': self.freq_to_channel(mock_freq),
                        'bitrate': 128,
                        'audio_mode': 'stereo',
                        'signal_strength': 65.5,
                        'snr': 18.2,
                        'ber': 0.001,
                        'status': 'good'
                    }

            return None

        except Exception as e:
            logger.error(f"สแกนความถี่ {frequency} MHz ผิดพลาด: {str(e)}")
            return None

    def freq_to_channel(self, freq_mhz):
        """แปลงความถี่เป็นชื่อช่อง DAB+"""
        if 174 <= freq_mhz <= 240:
            channel_num = int((freq_mhz - 174.928) / 1.712) + 5
            return f"{channel_num}A"
        elif 1452 <= freq_mhz <= 1492:
            channel_num = int((freq_mhz - 1452.960) / 1.712) + 1
            return f"L{channel_num}"
        else:
            return "Unknown"

    def stop_scan(self):
        """หยุดการสแกน"""
        self._stop_flag = True
        self.is_scanning = False

# ---------- Real-time Signal Monitor ----------
class SignalMonitor(QThread):
    signal_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.monitoring = False
        self.monitored_stations = []
        self._stop_flag = False

    def add_station(self, station_id, frequency):
        """เพิ่มสถานีที่ต้องติดตาม"""
        self.monitored_stations.append({
            'id': station_id,
            'frequency': frequency
        })

    def remove_station(self, station_id):
        """ลบสถานีจากการติดตาม"""
        self.monitored_stations = [s for s in self.monitored_stations if s['id'] != station_id]

    def run(self):
        """ติดตามคุณภาพสัญญาณแบบ real-time"""
        self.monitoring = True
        self._stop_flag = False

        while self.monitoring and not self._stop_flag:
            try:
                for station in self.monitored_stations:
                    signal_data = self.measure_signal_quality(station)
                    if signal_data:
                        self.signal_updated.emit(signal_data)

                self.msleep(5000)  # อัปเดตทุก 5 วินาที

            except Exception as e:
                logger.error(f"ติดตามสัญญาณผิดพลาด: {str(e)}")
                self.msleep(1000)

    def measure_signal_quality(self, station):
        """วัดคุณภาพสัญญาณ (จำลอง)"""
        try:
            # จำลองค่าสัญญาณที่แปรผัน
            import random
            base_strength = 60 + random.gauss(0, 10)
            base_snr = 15 + random.gauss(0, 5)
            base_ber = 0.001 + random.gauss(0, 0.0005)

            return {
                'station_id': station['id'],
                'frequency': station['frequency'],
                'signal_strength': max(0, min(100, base_strength)),
                'snr': max(0, base_snr),
                'ber': max(0, base_ber),
                'status': 'good' if base_strength > 50 else 'weak',
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"วัดสัญญาณผิดพลาด: {str(e)}")
            return None

    def stop_monitoring(self):
        """หยุดการติดตาม"""
        self.monitoring = False
        self._stop_flag = True

# ---------- Station List Widget ----------
class StationListWidget(QWidget):
    station_selected = pyqtSignal(int)  # station_id

    def __init__(self):
        super().__init__()
        self.db = StationDatabase()
        self.setup_ui()
        self.refresh_stations()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # หัวข้อ
        title = QLabel("รายการสถานี DAB+")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # ตารางสถานี
        self.station_table = QTableWidget()
        self.station_table.setColumnCount(6)
        self.station_table.setHorizontalHeaderLabels([
            "ชื่อสถานี", "Ensemble", "ความถี่ (MHz)",
            "ช่อง", "Bitrate", "สถานะ"
        ])

        # ปรับขนาดคอลัมน์
        header = self.station_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        layout.addWidget(self.station_table)

        # ปุ่มควบคุม
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 รีเฟรช")
        self.monitor_btn = QPushButton("👁️ ติดตาม")
        self.export_btn = QPushButton("📊 ส่งออก CSV")

        for btn in [self.refresh_btn, self.monitor_btn, self.export_btn]:
            btn.setMinimumHeight(40)
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        # เชื่อมต่อ signals
        self.refresh_btn.clicked.connect(self.refresh_stations)
        self.monitor_btn.clicked.connect(self.toggle_monitoring)
        self.export_btn.clicked.connect(self.export_stations)
        self.station_table.itemSelectionChanged.connect(self.on_selection_changed)

    def refresh_stations(self):
        """รีเฟรชรายการสถานี"""
        try:
            stations = self.db.get_all_stations()
            self.station_table.setRowCount(len(stations))

            for i, station in enumerate(stations):
                # station: (id, ensemble_id, ensemble_name, service_id, service_name,
                #          frequency_mhz, channel, bitrate, audio_mode, first_detected, last_detected, detection_count)

                self.station_table.setItem(i, 0, QTableWidgetItem(station[4]))  # service_name
                self.station_table.setItem(i, 1, QTableWidgetItem(station[2]))  # ensemble_name
                self.station_table.setItem(i, 2, QTableWidgetItem(f"{station[5]:.3f}"))  # frequency_mhz
                self.station_table.setItem(i, 3, QTableWidgetItem(station[6]))  # channel
                self.station_table.setItem(i, 4, QTableWidgetItem(f"{station[7]} kbps"))  # bitrate
                self.station_table.setItem(i, 5, QTableWidgetItem("Active"))  # status

                # เก็บ ID ไว้ในแถว
                self.station_table.item(i, 0).setData(Qt.UserRole, station[0])

            logger.info(f"รีเฟรชสถานี {len(stations)} รายการ")

        except Exception as e:
            logger.error(f"รีเฟรชสถานีผิดพลาด: {str(e)}")

    def on_selection_changed(self):
        """เมื่อเลือกสถานี"""
        try:
            current_row = self.station_table.currentRow()
            if current_row >= 0:
                station_id = self.station_table.item(current_row, 0).data(Qt.UserRole)
                if station_id:
                    self.station_selected.emit(station_id)
        except Exception as e:
            logger.error(f"เลือกสถานีผิดพลาด: {str(e)}")

    def toggle_monitoring(self):
        """เปิด/ปิดการติดตาม"""
        # TODO: เชื่อมต่อกับ SignalMonitor
        QMessageBox.information(self, "การติดตาม", "ฟีเจอร์การติดตามสัญญาณแบบ real-time")

    def export_stations(self):
        """ส่งออกข้อมูลสถานีเป็น CSV"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "บันทึกรายการสถานี",
                f"dab_stations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )

            if filename:
                stations = self.db.get_all_stations()
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "ID", "Ensemble ID", "Ensemble Name", "Service ID", "Service Name",
                        "Frequency (MHz)", "Channel", "Bitrate (kbps)", "Audio Mode",
                        "First Detected", "Last Detected", "Detection Count"
                    ])
                    writer.writerows(stations)

                QMessageBox.information(self, "ส่งออกสำเร็จ", f"บันทึกไฟล์: {filename}")
                logger.info(f"ส่งออกสถานี: {filename}")

        except Exception as e:
            QMessageBox.critical(self, "ส่งออกผิดพลาด", str(e))
            logger.error(f"ส่งออกสถานีผิดพลาด: {str(e)}")

# ---------- Signal Quality Chart Widget ----------
class SignalQualityChart(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_matplotlib()
        self.setup_ui()
        self.signal_history = defaultdict(list)
        self.max_points = 100

    def setup_matplotlib(self):
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)

        # กราฟคุณภาพสัญญาณ
        self.ax_signal = self.figure.add_subplot(2, 1, 1)
        self.ax_signal.set_title('Signal Strength & SNR')
        self.ax_signal.set_ylabel('dB')
        self.ax_signal.grid(True, alpha=0.3)

        # กราฟ BER
        self.ax_ber = self.figure.add_subplot(2, 1, 2)
        self.ax_ber.set_title('Bit Error Rate')
        self.ax_ber.set_ylabel('BER')
        self.ax_ber.set_xlabel('Time')
        self.ax_ber.grid(True, alpha=0.3)

        self.figure.tight_layout()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("คุณภาพสัญญาณแบบ Real-time")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addWidget(self.canvas)

        # ปุ่มควบคุม
        button_layout = QHBoxLayout()
        self.clear_btn = QPushButton("🗑️ เคลียร์กราฟ")
        self.save_btn = QPushButton("💾 บันทึกกราฟ")

        for btn in [self.clear_btn, self.save_btn]:
            btn.setMinimumHeight(40)
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        self.clear_btn.clicked.connect(self.clear_charts)
        self.save_btn.clicked.connect(self.save_charts)

    def update_signal_data(self, signal_data):
        """อัปเดตข้อมูลสัญญาณ"""
        try:
            station_id = signal_data['station_id']
            timestamp = signal_data['timestamp']

            # เพิ่มข้อมูลใหม่
            self.signal_history[station_id].append({
                'time': timestamp,
                'signal_strength': signal_data['signal_strength'],
                'snr': signal_data['snr'],
                'ber': signal_data['ber'],
                'status': signal_data['status']
            })

            # จำกัดจำนวนจุดข้อมูล
            if len(self.signal_history[station_id]) > self.max_points:
                self.signal_history[station_id].pop(0)

            self.update_charts()

        except Exception as e:
            logger.error(f"อัปเดตข้อมูลสัญญาณผิดพลาด: {str(e)}")

    def update_charts(self):
        """อัปเดตกราฟ"""
        try:
            self.ax_signal.clear()
            self.ax_ber.clear()

            for station_id, history in self.signal_history.items():
                if not history:
                    continue

                times = [h['time'] for h in history]
                strengths = [h['signal_strength'] for h in history]
                snrs = [h['snr'] for h in history]
                bers = [h['ber'] for h in history]

                # กราฟ Signal Strength & SNR
                self.ax_signal.plot(times, strengths, label=f'Station {station_id} - Strength', linewidth=2)
                self.ax_signal.plot(times, snrs, label=f'Station {station_id} - SNR', linestyle='--', linewidth=2)

                # กราฟ BER
                self.ax_ber.plot(times, bers, label=f'Station {station_id} - BER', linewidth=2)

            # ตั้งค่ากราฟ
            self.ax_signal.set_title('Signal Strength & SNR')
            self.ax_signal.set_ylabel('dB')
            self.ax_signal.grid(True, alpha=0.3)
            self.ax_signal.legend()

            self.ax_ber.set_title('Bit Error Rate')
            self.ax_ber.set_ylabel('BER')
            self.ax_ber.set_xlabel('Time')
            self.ax_ber.grid(True, alpha=0.3)
            self.ax_ber.legend()

            self.figure.tight_layout()
            self.canvas.draw_idle()

        except Exception as e:
            logger.error(f"อัปเดตกราฟผิดพลาด: {str(e)}")

    def clear_charts(self):
        """เคลียร์กราฟ"""
        self.signal_history.clear()
        self.ax_signal.clear()
        self.ax_ber.clear()

        self.ax_signal.set_title('Signal Strength & SNR')
        self.ax_signal.set_ylabel('dB')
        self.ax_signal.grid(True, alpha=0.3)

        self.ax_ber.set_title('Bit Error Rate')
        self.ax_ber.set_ylabel('BER')
        self.ax_ber.set_xlabel('Time')
        self.ax_ber.grid(True, alpha=0.3)

        self.canvas.draw_idle()

    def save_charts(self):
        """บันทึกกราฟ"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "บันทึกกราฟคุณภาพสัญญาณ",
                f"signal_quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                "PNG Files (*.png)"
            )

            if filename:
                self.figure.savefig(filename, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "บันทึกสำเร็จ", f"บันทึกกราฟ: {filename}")
                logger.info(f"บันทึกกราฟ: {filename}")

        except Exception as e:
            QMessageBox.critical(self, "บันทึกผิดพลาด", str(e))

# ---------- Scanner Control Panel ----------
class ScannerControlPanel(QWidget):
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
        self.freq_combo.addItems([
            "Band III (174-240 MHz)",
            "L-Band (1452-1492 MHz)",
            "Full Range"
        ])
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
        self.start_scan_btn.setMinimumHeight(48)
        self.stop_scan_btn.setMinimumHeight(48)
        self.stop_scan_btn.setEnabled(False)

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

        # เชื่อมต่อ signals
        self.start_scan_btn.clicked.connect(self.start_scan)
        self.stop_scan_btn.clicked.connect(self.stop_scan)

    def start_scan(self):
        """เริ่มการสแกน"""
        frequency_range = self.freq_combo.currentText()
        self.scan_requested.emit(frequency_range)

        self.start_scan_btn.setEnabled(False)
        self.stop_scan_btn.setEnabled(True)
        self.progress_bar.setValue(0)

    def stop_scan(self):
        """หยุดการสแกน"""
        self.start_scan_btn.setEnabled(True)
        self.stop_scan_btn.setEnabled(False)

    def update_progress(self, percent, message):
        """อัปเดตความก้าวหน้า"""
        self.progress_bar.setValue(percent)
        self.progress_label.setText(message)

    def scan_completed(self, stations_found):
        """การสแกนเสร็จสิ้น"""
        self.start_scan_btn.setEnabled(True)
        self.stop_scan_btn.setEnabled(False)
        self.progress_label.setText(f"สแกนเสร็จสิ้น - พบสถานี {stations_found} รายการ")
        self.last_scan_label.setText(f"ครั้งล่าสุด: {datetime.now().strftime('%H:%M:%S')}")

# ---------- Main Window ----------
class Lab4MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = StationDatabase()
        self.scanner = DABScanner()
        self.signal_monitor = SignalMonitor()

        self.setup_ui()
        self.setup_touch_interface()
        self.setup_connections()

        self.setWindowTitle("LAB 4: สร้าง DAB+ Station Scanner")
        self.resize(1200, 800)

    def setup_ui(self):
        """สร้าง UI หลัก"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # หัวข้อ
        title_label = QLabel("LAB 4: สร้าง DAB+ Station Scanner")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 20px; font-weight: bold; color: #2c3e50;
            padding: 15px; background-color: #ecf0f1; border-radius: 10px;
        """)
        main_layout.addWidget(title_label)

        # Tab widget
        self.tab_widget = QTabWidget()

        # Tab 1: Scanner
        scanner_tab = QWidget()
        scanner_layout = QHBoxLayout(scanner_tab)

        # Control Panel
        self.control_panel = ScannerControlPanel()
        scanner_layout.addWidget(self.control_panel, 1)

        # Station List
        self.station_list = StationListWidget()
        scanner_layout.addWidget(self.station_list, 2)

        self.tab_widget.addTab(scanner_tab, "🔍 Scanner")

        # Tab 2: Signal Monitoring
        monitor_tab = QWidget()
        monitor_layout = QVBoxLayout(monitor_tab)

        self.signal_chart = SignalQualityChart()
        monitor_layout.addWidget(self.signal_chart)

        self.tab_widget.addTab(monitor_tab, "📊 Signal Monitor")

        # Tab 3: History & Reports
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)

        history_label = QLabel("ประวัติการสแกนและรายงาน")
        history_label.setFont(QFont("Arial", 16, QFont.Bold))
        history_label.setAlignment(Qt.AlignCenter)
        history_layout.addWidget(history_label)

        # TODO: เพิ่มตารางประวัติและปุ่มสร้างรายงาน
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setPlainText("ประวัติการสแกนจะแสดงที่นี่...")
        history_layout.addWidget(self.history_text)

        self.tab_widget.addTab(history_tab, "📋 History")

        main_layout.addWidget(self.tab_widget)

        # Status bar
        self.status_label = QLabel("พร้อมใช้งาน - เลือกช่วงความถี่และเริ่มสแกน")
        self.status_label.setStyleSheet("background-color: #d5f4e6; padding: 8px;")
        main_layout.addWidget(self.status_label)

    def setup_touch_interface(self):
        """ปรับการแสดงผลสำหรับหน้าจอสัมผัส"""
        font = QFont()
        font.setPointSize(14)
        self.setFont(font)

        # ปรับขนาดปุ่มสำหรับ touch
        buttons = [
            self.control_panel.start_scan_btn,
            self.control_panel.stop_scan_btn,
            self.station_list.refresh_btn,
            self.station_list.monitor_btn,
            self.station_list.export_btn,
            self.signal_chart.clear_btn,
            self.signal_chart.save_btn
        ]

        for btn in buttons:
            btn.setMinimumHeight(48)
            btn.setFont(QFont("Arial", 14))

        # ปรับขนาด combo box
        self.control_panel.freq_combo.setMinimumHeight(40)

        # ปรับ tab widget
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setFont(QFont("Arial", 14))

    def setup_connections(self):
        """เชื่อมต่อ signals และ slots"""
        # Scanner signals
        self.control_panel.scan_requested.connect(self.start_scan)
        self.scanner.station_found.connect(self.on_station_found)
        self.scanner.scan_progress.connect(self.control_panel.update_progress)
        self.scanner.scan_completed.connect(self.control_panel.scan_completed)
        self.scanner.scan_completed.connect(self.on_scan_completed)
        self.scanner.error_occurred.connect(self.show_error)

        # Station list signals
        self.station_list.station_selected.connect(self.on_station_selected)

        # Signal monitor signals
        self.signal_monitor.signal_updated.connect(self.signal_chart.update_signal_data)

    def start_scan(self, frequency_range):
        """เริ่มการสแกน"""
        try:
            if not self.scanner.isRunning():
                self.scanner.set_frequency_range(frequency_range)
                self.scanner.start()
                self.status_label.setText(f"เริ่มสแกน {frequency_range}")
                logger.info(f"เริ่มสแกน: {frequency_range}")
        except Exception as e:
            self.show_error(f"เริ่มสแกนผิดพลาด: {str(e)}")

    def on_station_found(self, station_data):
        """เมื่อพบสถานีใหม่"""
        try:
            # บันทึกสถานีลงฐานข้อมูล
            station_id = self.db.add_station(station_data)

            if station_id:
                # อัปเดตแสดงผล
                self.station_list.refresh_stations()

                # เพิ่มเข้าระบบติดตามสัญญาณ
                self.signal_monitor.add_station(station_id, station_data['frequency_mhz'])

                logger.info(f"พบสถานี: {station_data['service_name']} @ {station_data['frequency_mhz']:.3f} MHz")

        except Exception as e:
            logger.error(f"เพิ่มสถานีผิดพลาด: {str(e)}")

    def on_scan_completed(self, stations_found):
        """เมื่อการสแกนเสร็จสิ้น"""
        try:
            # บันทึกประวัติการสแกน
            scan_data = {
                'frequency_range': self.control_panel.freq_combo.currentText(),
                'stations_found': stations_found,
                'scan_duration': 0,  # TODO: คำนวณเวลาที่ใช้
                'notes': f'สแกนพบสถานี {stations_found} รายการ'
            }
            self.db.add_scan_record(scan_data)

            self.status_label.setText(f"สแกนเสร็จสิ้น - พบสถานี {stations_found} รายการ")
            logger.info(f"สแกนเสร็จสิ้น: พบ {stations_found} สถานี")

        except Exception as e:
            logger.error(f"บันทึกผลการสแกนผิดพลาด: {str(e)}")

    def on_station_selected(self, station_id):
        """เมื่อเลือกสถานี"""
        # TODO: แสดงรายละเอียดสถานีและเริ่มติดตาม
        self.status_label.setText(f"เลือกสถานี ID: {station_id}")

    def show_error(self, error_message):
        """แสดงข้อความผิดพลาด"""
        QMessageBox.critical(self, "เกิดข้อผิดพลาด", error_message)
        self.status_label.setText(f"ข้อผิดพลาด: {error_message}")
        logger.error(error_message)

    def closeEvent(self, event):
        """เมื่อปิดโปรแกรม"""
        try:
            # หยุดการทำงานของ threads
            if self.scanner.isRunning():
                self.scanner.stop_scan()
                self.scanner.wait()

            if self.signal_monitor.isRunning():
                self.signal_monitor.stop_monitoring()
                self.signal_monitor.wait()

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
        window = Lab4MainWindow()
        window.show()

        sys.exit(app.exec_())

    except Exception as e:
        print(f"เริ่มโปรแกรมผิดพลาด: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("LAB 4: สร้าง DAB+ Station Scanner (เฉลย)")
    main()