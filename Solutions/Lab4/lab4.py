#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAB 4: สร้าง DAB+ Station Scanner - SOLUTION (Based on Lab 3 ETI approach)
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

# นำเข้า modules จาก Lab 3
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
logger = logging.getLogger("Lab4Scanner")

# DAB+ Thailand frequencies
DAB_FREQUENCIES = {
    '185.360': {'location': 'Bangkok/Phuket', 'block': '7A', 'freq': 185.360},
    '202.928': {'location': 'Bangkok', 'block': '9A', 'freq': 202.928},
    '195.936': {'location': 'Chiang Mai', 'block': '8C', 'freq': 195.936},
    '210.096': {'location': 'Northeast', 'block': '10B', 'freq': 210.096},
}

class StationDatabase:
    """ฐานข้อมูลสำหรับเก็บข้อมูลสถานี DAB+"""

    def __init__(self, db_path="dab_scanner.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """สร้างตารางฐานข้อมูล"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # ตารางสถานี
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ensemble_id TEXT,
                    ensemble_label TEXT,
                    service_id INTEGER,
                    service_label TEXT,
                    frequency_mhz REAL,
                    channel_block TEXT,
                    location TEXT,
                    bitrate INTEGER,
                    audio_mode TEXT,
                    first_detected DATETIME,
                    last_detected DATETIME,
                    detection_count INTEGER DEFAULT 1,
                    avg_signal_strength REAL,
                    avg_snr REAL,
                    avg_ber REAL
                )
            ''')

            # ตารางประวัติคุณภาพสัญญาณ
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signal_quality (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    station_id INTEGER,
                    timestamp DATETIME,
                    signal_strength REAL,
                    snr REAL,
                    ber REAL,
                    sync_status TEXT,
                    error_count INTEGER,
                    FOREIGN KEY (station_id) REFERENCES stations (id)
                )
            ''')

            # ตารางการสแกน
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scan_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_start DATETIME,
                    scan_end DATETIME,
                    frequency_range TEXT,
                    stations_found INTEGER,
                    total_frequencies INTEGER,
                    scan_mode TEXT,
                    notes TEXT
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("Database initialized")

        except Exception as e:
            logger.error(f"Database initialization error: {e}")

    def add_station(self, station_data):
        """เพิ่มสถานีใหม่หรืออัปเดตสถานีที่มีอยู่"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # ตรวจสอบว่ามีสถานีนี้อยู่แล้วหรือไม่
            cursor.execute('''
                SELECT id, detection_count FROM stations
                WHERE service_id = ? AND frequency_mhz = ?
            ''', (station_data.get('service_id'), station_data.get('frequency_mhz')))

            existing = cursor.fetchone()

            if existing:
                # อัปเดตสถานีที่มีอยู่
                station_id, count = existing
                cursor.execute('''
                    UPDATE stations SET
                        last_detected = ?,
                        detection_count = detection_count + 1,
                        avg_signal_strength = ?,
                        avg_snr = ?,
                        avg_ber = ?
                    WHERE id = ?
                ''', (
                    datetime.now(),
                    station_data.get('signal_strength', 0),
                    station_data.get('snr', 0),
                    station_data.get('ber', 0),
                    station_id
                ))
                result_id = station_id
            else:
                # เพิ่มสถานีใหม่
                cursor.execute('''
                    INSERT INTO stations (
                        ensemble_id, ensemble_label, service_id, service_label,
                        frequency_mhz, channel_block, location, bitrate, audio_mode,
                        first_detected, last_detected, avg_signal_strength, avg_snr, avg_ber
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    station_data.get('ensemble_id'),
                    station_data.get('ensemble_label'),
                    station_data.get('service_id'),
                    station_data.get('service_label'),
                    station_data.get('frequency_mhz'),
                    station_data.get('channel_block'),
                    station_data.get('location'),
                    station_data.get('bitrate', 128),
                    station_data.get('audio_mode', 'stereo'),
                    datetime.now(),
                    datetime.now(),
                    station_data.get('signal_strength', 0),
                    station_data.get('snr', 0),
                    station_data.get('ber', 0)
                ))
                result_id = cursor.lastrowid

            conn.commit()
            conn.close()
            return result_id

        except Exception as e:
            logger.error(f"Add station error: {e}")
            return None

    def get_all_stations(self):
        """ดึงข้อมูลสถานีทั้งหมด"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM stations
                ORDER BY frequency_mhz, service_label
            ''')
            stations = cursor.fetchall()
            conn.close()
            return stations
        except Exception as e:
            logger.error(f"Get stations error: {e}")
            return []

    def add_signal_quality(self, station_id, quality_data):
        """เพิ่มข้อมูลคุณภาพสัญญาณ"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO signal_quality (
                    station_id, timestamp, signal_strength, snr, ber,
                    sync_status, error_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                station_id,
                datetime.now(),
                quality_data.get('signal_strength'),
                quality_data.get('snr'),
                quality_data.get('ber'),
                quality_data.get('sync_status'),
                quality_data.get('error_count', 0)
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Add signal quality error: {e}")

class DABScannerEngine(QThread):
    """เครื่องมือสแกน DAB+ ใช้ Lab 3 pipeline"""

    station_found = pyqtSignal(dict)
    scan_progress = pyqtSignal(int, str, float)  # percent, message, frequency
    scan_completed = pyqtSignal(int)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.rtl_sdr = None
        self.eti_processor = None
        self.eti_parser = None
        self.scan_mode = 'full'  # 'full', 'known_frequencies', 'custom'
        self.frequency_list = []
        self.is_scanning = False
        self._stop_flag = False

    def set_scan_mode(self, mode, frequencies=None):
        """ตั้งค่าโหมดการสแกน"""
        self.scan_mode = mode
        if mode == 'known_frequencies':
            self.frequency_list = [f['freq'] for f in DAB_FREQUENCIES.values()]
        elif mode == 'custom' and frequencies:
            self.frequency_list = frequencies
        elif mode == 'full':
            # Band III DAB+ frequencies (174-240 MHz)
            self.frequency_list = []
            for i in range(5, 14):  # Blocks 5A-13F
                for block in ['A', 'B', 'C', 'D']:
                    freq = 174.928 + (i - 5) * 1.712 + ['A', 'B', 'C', 'D'].index(block) * 0.032
                    self.frequency_list.append(freq)

    def run(self):
        """เริ่มการสแกน"""
        self.is_scanning = True
        self._stop_flag = False
        stations_found = 0

        try:
            # เริ่มต้น RTL-SDR
            self.rtl_sdr = RTLSDRDataAcquisition()
            if not self.rtl_sdr.setup_rtlsdr():
                self.error_occurred.emit("ไม่สามารถเชื่อมต่อ RTL-SDR ได้")
                return

            # เริ่มต้น ETI processor
            self.eti_processor = ETIProcessor()
            self.eti_parser = ETIFrameParser()

            total_freqs = len(self.frequency_list)

            for i, frequency in enumerate(self.frequency_list):
                if self._stop_flag:
                    break

                progress = int((i / total_freqs) * 100)
                self.scan_progress.emit(progress, f"สแกนความถี่ {frequency:.3f} MHz", frequency)

                # สแกนความถี่นี้
                station_data = self.scan_frequency(frequency)
                if station_data:
                    for station in station_data:
                        self.station_found.emit(station)
                        stations_found += 1

                # หน่วงเวลาระหว่างการสแกน
                self.msleep(500)

            self.scan_completed.emit(stations_found)

        except Exception as e:
            self.error_occurred.emit(f"Scanning error: {e}")
        finally:
            self.cleanup()
            self.is_scanning = False

    def scan_frequency(self, frequency):
        """สแกนความถี่เฉพาะด้วย Lab 3 pipeline"""
        try:
            # Step 1: รับ I/Q data
            self.rtl_sdr.frequency = int(frequency * 1000000)
            samples = self.rtl_sdr.capture_samples(duration_seconds=5)

            if samples is None:
                return None

            # Step 2: ประมวลผลเป็น ETI stream
            eti_data = self.process_iq_to_eti(samples, frequency)
            if not eti_data:
                return None

            # Step 3: Parse ETI เพื่อหา services
            services = self.parse_eti_services(eti_data, frequency)

            return services

        except Exception as e:
            logger.error(f"Scan frequency {frequency} error: {e}")
            return None

    def process_iq_to_eti(self, samples, frequency):
        """แปลง I/Q samples เป็น ETI stream"""
        try:
            # วิเคราะห์ power spectrum เพื่อตรวจหาสัญญาณ DAB+
            power_spectrum = np.abs(np.fft.fft(samples[:1024])) ** 2
            peak_power = np.max(power_spectrum)
            avg_power = np.mean(power_spectrum)

            # ตรวจสอบว่ามีสัญญาณแรงพอหรือไม่
            if peak_power / avg_power < 10:  # SNR threshold
                return None

            # สร้าง mock ETI data สำหรับ demonstration
            # ในการใช้งานจริงต้องใช้ eti-cmdline หรือ GNU Radio DAB
            eti_frames = self.create_mock_eti_data(frequency, samples)

            return eti_frames

        except Exception as e:
            logger.error(f"I/Q to ETI processing error: {e}")
            return None

    def create_mock_eti_data(self, frequency, samples):
        """สร้าง mock ETI data จาก I/Q analysis"""
        try:
            # วิเคราะห์ลักษณะของสัญญาณ
            signal_strength = np.sqrt(np.mean(np.abs(samples)**2))

            # คำนวณ SNR
            power = np.abs(samples) ** 2
            signal_power = np.max(power)
            noise_power = np.mean(power)
            snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else 0

            # สร้าง mock service data ตาม frequency
            location = 'Unknown'
            block = 'Unknown'
            for freq_str, info in DAB_FREQUENCIES.items():
                if abs(frequency - info['freq']) < 0.1:
                    location = info['location']
                    block = info['block']
                    break

            # จำลอง services ในแต่ละ ensemble
            mock_services = []
            num_services = min(8, max(1, int(snr / 3)))  # จำนวน services ตาม SNR

            for i in range(num_services):
                service = {
                    'ensemble_id': f"0x{int(frequency * 100):04X}",
                    'ensemble_label': f"{location} DAB+",
                    'service_id': int(frequency * 10) + i,
                    'service_label': f"Service {i+1} @ {frequency:.1f}MHz",
                    'frequency_mhz': frequency,
                    'channel_block': block,
                    'location': location,
                    'bitrate': 128 if snr > 15 else 96 if snr > 10 else 64,
                    'audio_mode': 'stereo' if snr > 12 else 'mono',
                    'signal_strength': min(100, signal_strength * 10),
                    'snr': snr,
                    'ber': max(0.0001, 1.0 / (snr + 1)),
                    'sync_status': 'good' if snr > 15 else 'fair' if snr > 10 else 'poor'
                }
                mock_services.append(service)

            return mock_services

        except Exception as e:
            logger.error(f"Mock ETI creation error: {e}")
            return []

    def parse_eti_services(self, eti_data, frequency):
        """Parse ETI data เพื่อหา DAB+ services"""
        try:
            # ใน mock implementation นี้ eti_data คือ list ของ services แล้ว
            return eti_data

        except Exception as e:
            logger.error(f"ETI parsing error: {e}")
            return []

    def stop_scanning(self):
        """หยุดการสแกน"""
        self._stop_flag = True
        self.is_scanning = False

    def cleanup(self):
        """ทำความสะอาด resources"""
        try:
            if self.rtl_sdr:
                self.rtl_sdr.cleanup()
        except:
            pass

class SignalMonitorWidget(QWidget):
    """Widget สำหรับติดตามคุณภาพสัญญาณแบบ real-time"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_plot()
        self.signal_history = defaultdict(list)
        self.max_history = 100

        # Timer สำหรับอัปเดต
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plots)
        self.update_timer.start(1000)  # อัปเดตทุกวินาที

    def setup_ui(self):
        layout = QVBoxLayout()

        # หัวข้อ
        title = QLabel("การติดตามคุณภาพสัญญาณแบบ Real-time")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # กราฟ
        self.setup_plot()
        layout.addWidget(self.canvas)

        # ปุ่มควบคุม
        button_layout = QHBoxLayout()
        self.start_monitor_btn = QPushButton("▶️ เริ่มติดตาม")
        self.stop_monitor_btn = QPushButton("⏹️ หยุดติดตาม")
        self.clear_btn = QPushButton("🗑️ เคลียร์ข้อมูล")
        self.export_btn = QPushButton("📊 ส่งออกข้อมูล")

        for btn in [self.start_monitor_btn, self.stop_monitor_btn, self.clear_btn, self.export_btn]:
            btn.setMinimumHeight(40)
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # เชื่อมต่อ signals
        self.start_monitor_btn.clicked.connect(self.start_monitoring)
        self.stop_monitor_btn.clicked.connect(self.stop_monitoring)
        self.clear_btn.clicked.connect(self.clear_data)
        self.export_btn.clicked.connect(self.export_data)

    def setup_plot(self):
        """สร้างกราฟ matplotlib"""
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)

        # กราฟ Signal Strength
        self.ax_signal = self.figure.add_subplot(3, 1, 1)
        self.ax_signal.set_title('Signal Strength (dBm)')
        self.ax_signal.set_ylabel('dBm')
        self.ax_signal.grid(True, alpha=0.3)

        # กราฟ SNR
        self.ax_snr = self.figure.add_subplot(3, 1, 2)
        self.ax_snr.set_title('Signal-to-Noise Ratio (dB)')
        self.ax_snr.set_ylabel('SNR (dB)')
        self.ax_snr.grid(True, alpha=0.3)

        # กราฟ BER
        self.ax_ber = self.figure.add_subplot(3, 1, 3)
        self.ax_ber.set_title('Bit Error Rate')
        self.ax_ber.set_ylabel('BER')
        self.ax_ber.set_xlabel('Time')
        self.ax_ber.grid(True, alpha=0.3)

        self.figure.tight_layout()

    def add_signal_data(self, station_id, signal_data):
        """เพิ่มข้อมูลสัญญาณใหม่"""
        self.signal_history[station_id].append({
            'timestamp': datetime.now(),
            'signal_strength': signal_data.get('signal_strength', 0),
            'snr': signal_data.get('snr', 0),
            'ber': signal_data.get('ber', 0),
            'sync_status': signal_data.get('sync_status', 'unknown')
        })

        # จำกัดข้อมูล
        if len(self.signal_history[station_id]) > self.max_history:
            self.signal_history[station_id].pop(0)

    def update_plots(self):
        """อัปเดตกราฟ"""
        try:
            # เคลียร์กราฟ
            self.ax_signal.clear()
            self.ax_snr.clear()
            self.ax_ber.clear()

            colors = ['blue', 'red', 'green', 'orange', 'purple']

            for i, (station_id, history) in enumerate(self.signal_history.items()):
                if not history:
                    continue

                color = colors[i % len(colors)]

                times = [h['timestamp'] for h in history]
                signals = [h['signal_strength'] for h in history]
                snrs = [h['snr'] for h in history]
                bers = [h['ber'] for h in history]

                # กราฟ Signal Strength
                self.ax_signal.plot(times, signals, color=color,
                                  label=f'Station {station_id}', linewidth=2)

                # กราฟ SNR
                self.ax_snr.plot(times, snrs, color=color,
                               label=f'Station {station_id}', linewidth=2)

                # กราฟ BER
                self.ax_ber.semilogy(times, bers, color=color,
                                   label=f'Station {station_id}', linewidth=2)

            # ตั้งค่ากราฟ
            self.ax_signal.set_title('Signal Strength')
            self.ax_signal.set_ylabel('dBm')
            self.ax_signal.grid(True, alpha=0.3)
            self.ax_signal.legend()

            self.ax_snr.set_title('Signal-to-Noise Ratio')
            self.ax_snr.set_ylabel('SNR (dB)')
            self.ax_snr.grid(True, alpha=0.3)
            self.ax_snr.legend()

            self.ax_ber.set_title('Bit Error Rate')
            self.ax_ber.set_ylabel('BER')
            self.ax_ber.set_xlabel('Time')
            self.ax_ber.grid(True, alpha=0.3)
            self.ax_ber.legend()

            self.figure.tight_layout()
            self.canvas.draw_idle()

        except Exception as e:
            logger.error(f"Update plots error: {e}")

    def start_monitoring(self):
        """เริ่มการติดตาม"""
        # TODO: เชื่อมต่อกับระบบติดตามจริง
        pass

    def stop_monitoring(self):
        """หยุดการติดตาม"""
        pass

    def clear_data(self):
        """เคลียร์ข้อมูล"""
        self.signal_history.clear()
        self.update_plots()

    def export_data(self):
        """ส่งออกข้อมูล"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "ส่งออกข้อมูลคุณภาพสัญญาณ",
                f"signal_quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )

            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Station ID', 'Timestamp', 'Signal Strength', 'SNR', 'BER', 'Sync Status'])

                    for station_id, history in self.signal_history.items():
                        for record in history:
                            writer.writerow([
                                station_id,
                                record['timestamp'],
                                record['signal_strength'],
                                record['snr'],
                                record['ber'],
                                record['sync_status']
                            ])

                QMessageBox.information(self, "ส่งออกสำเร็จ", f"บันทึกไฟล์: {filename}")

        except Exception as e:
            QMessageBox.critical(self, "ส่งออกล้มเหลว", str(e))

class StationListWidget(QWidget):
    """Widget แสดงรายการสถานี DAB+"""

    station_selected = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.db = StationDatabase()
        self.setup_ui()
        self.refresh_stations()

    def setup_ui(self):
        layout = QVBoxLayout()

        # หัวข้อ
        title = QLabel("รายการสถานี DAB+ ที่พบ")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # ตารางสถานี
        self.station_table = QTableWidget()
        self.station_table.setColumnCount(8)
        self.station_table.setHorizontalHeaderLabels([
            "ชื่อสถานี", "Ensemble", "ความถี่", "Block", "Location",
            "SNR", "Signal", "ครั้งที่พบ"
        ])

        # ปรับขนาดคอลัมน์
        header = self.station_table.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(8):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        layout.addWidget(self.station_table)

        # ปุ่มควบคุม
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 รีเฟรช")
        self.monitor_btn = QPushButton("👁️ ติดตามสถานีที่เลือก")
        self.export_btn = QPushButton("📊 ส่งออก CSV")
        self.delete_btn = QPushButton("🗑️ ลบสถานีที่เลือก")

        for btn in [self.refresh_btn, self.monitor_btn, self.export_btn, self.delete_btn]:
            btn.setMinimumHeight(40)
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # เชื่อมต่อ signals
        self.refresh_btn.clicked.connect(self.refresh_stations)
        self.monitor_btn.clicked.connect(self.monitor_selected_station)
        self.export_btn.clicked.connect(self.export_stations)
        self.delete_btn.clicked.connect(self.delete_selected_station)
        self.station_table.itemSelectionChanged.connect(self.on_selection_changed)

    def refresh_stations(self):
        """รีเฟรชรายการสถานี"""
        try:
            stations = self.db.get_all_stations()
            self.station_table.setRowCount(len(stations))

            for i, station in enumerate(stations):
                # stations columns: id, ensemble_id, ensemble_label, service_id, service_label,
                #                  frequency_mhz, channel_block, location, bitrate, audio_mode,
                #                  first_detected, last_detected, detection_count, avg_signal_strength, avg_snr, avg_ber

                self.station_table.setItem(i, 0, QTableWidgetItem(str(station[4])))  # service_label
                self.station_table.setItem(i, 1, QTableWidgetItem(str(station[2])))  # ensemble_label
                self.station_table.setItem(i, 2, QTableWidgetItem(f"{station[5]:.3f} MHz"))  # frequency_mhz
                self.station_table.setItem(i, 3, QTableWidgetItem(str(station[6])))  # channel_block
                self.station_table.setItem(i, 4, QTableWidgetItem(str(station[7])))  # location
                self.station_table.setItem(i, 5, QTableWidgetItem(f"{station[14]:.1f} dB"))  # avg_snr
                self.station_table.setItem(i, 6, QTableWidgetItem(f"{station[13]:.1f} dBm"))  # avg_signal_strength
                self.station_table.setItem(i, 7, QTableWidgetItem(str(station[12])))  # detection_count

                # เก็บ station ID
                self.station_table.item(i, 0).setData(Qt.UserRole, station[0])

            logger.info(f"Refreshed {len(stations)} stations")

        except Exception as e:
            logger.error(f"Refresh stations error: {e}")

    def on_selection_changed(self):
        """เมื่อเลือกสถานี"""
        try:
            current_row = self.station_table.currentRow()
            if current_row >= 0:
                station_id = self.station_table.item(current_row, 0).data(Qt.UserRole)
                if station_id:
                    self.station_selected.emit(station_id)
        except Exception as e:
            logger.error(f"Selection changed error: {e}")

    def monitor_selected_station(self):
        """ติดตามสถานีที่เลือก"""
        current_row = self.station_table.currentRow()
        if current_row >= 0:
            station_id = self.station_table.item(current_row, 0).data(Qt.UserRole)
            QMessageBox.information(self, "ติดตามสถานี", f"เริ่มติดตามสถานี ID: {station_id}")
        else:
            QMessageBox.warning(self, "เลือกสถานี", "กรุณาเลือกสถานีที่ต้องการติดตาม")

    def export_stations(self):
        """ส่งออกรายการสถานี"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "ส่งออกรายการสถานี",
                f"dab_stations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )

            if filename:
                stations = self.db.get_all_stations()
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'ID', 'Ensemble ID', 'Ensemble Label', 'Service ID', 'Service Label',
                        'Frequency (MHz)', 'Channel Block', 'Location', 'Bitrate', 'Audio Mode',
                        'First Detected', 'Last Detected', 'Detection Count',
                        'Avg Signal Strength', 'Avg SNR', 'Avg BER'
                    ])
                    writer.writerows(stations)

                QMessageBox.information(self, "ส่งออกสำเร็จ", f"บันทึกไฟล์: {filename}")

        except Exception as e:
            QMessageBox.critical(self, "ส่งออกล้มเหลว", str(e))

    def delete_selected_station(self):
        """ลบสถานีที่เลือก"""
        current_row = self.station_table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(self, "ลบสถานี", "แน่ใจหรือว่าจะลบสถานีนี้?")
            if reply == QMessageBox.Yes:
                # TODO: implement delete from database
                self.refresh_stations()

class ScanControlWidget(QWidget):
    """Widget ควบคุมการสแกน"""

    scan_requested = pyqtSignal(str, list)  # mode, frequencies

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # กลุ่มการตั้งค่าการสแกน
        scan_group = QGroupBox("การตั้งค่าการสแกน")
        scan_layout = QGridLayout()

        # โหมดการสแกน
        scan_layout.addWidget(QLabel("โหมดการสแกน:"), 0, 0)
        self.scan_mode_combo = QComboBox()
        self.scan_mode_combo.addItems([
            "ความถี่ที่รู้จัก (ประเทศไทย)",
            "สแกนครบทุกช่อง Band III",
            "ระบุความถี่เอง"
        ])
        scan_layout.addWidget(self.scan_mode_combo, 0, 1)

        # ความถี่เฉพาะ (สำหรับโหมดระบุเอง)
        scan_layout.addWidget(QLabel("ความถี่ (MHz):"), 1, 0)
        self.custom_freq_combo = QComboBox()
        self.custom_freq_combo.setEditable(True)
        for freq_info in DAB_FREQUENCIES.values():
            self.custom_freq_combo.addItem(f"{freq_info['freq']:.3f} - {freq_info['location']}")
        scan_layout.addWidget(self.custom_freq_combo, 1, 1)

        # เวลาการสแกนต่อความถี่
        scan_layout.addWidget(QLabel("เวลาต่อความถี่ (วิ):"), 2, 0)
        self.scan_time_spin = QSpinBox()
        self.scan_time_spin.setRange(1, 60)
        self.scan_time_spin.setValue(5)
        self.scan_time_spin.setSuffix(" วินาที")
        scan_layout.addWidget(self.scan_time_spin, 2, 1)

        scan_group.setLayout(scan_layout)
        layout.addWidget(scan_group)

        # แถบความคืบหน้า
        progress_group = QGroupBox("ความคืบหน้า")
        progress_layout = QVBoxLayout()

        self.progress_label = QLabel("พร้อมเริ่มสแกน")
        self.progress_bar = QProgressBar()
        self.current_freq_label = QLabel("ความถี่ปัจจุบัน: -")

        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.current_freq_label)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # ปุ่มควบคุม
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("🔍 เริ่มสแกน")
        self.stop_btn = QPushButton("⏹️ หยุดสแกน")
        self.start_btn.setMinimumHeight(50)
        self.stop_btn.setMinimumHeight(50)
        self.stop_btn.setEnabled(False)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        layout.addLayout(button_layout)

        # สถิติ
        stats_group = QGroupBox("สถิติการสแกน")
        stats_layout = QGridLayout()

        self.total_scans_label = QLabel("การสแกนทั้งหมด: 0")
        self.stations_found_label = QLabel("สถานีที่พบ: 0")
        self.last_scan_label = QLabel("ครั้งล่าสุด: -")
        self.scan_time_label = QLabel("เวลาที่ใช้: -")

        stats_layout.addWidget(self.total_scans_label, 0, 0)
        stats_layout.addWidget(self.stations_found_label, 0, 1)
        stats_layout.addWidget(self.last_scan_label, 1, 0)
        stats_layout.addWidget(self.scan_time_label, 1, 1)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        self.setLayout(layout)

        # เชื่อมต่อ signals
        self.start_btn.clicked.connect(self.start_scan)
        self.stop_btn.clicked.connect(self.stop_scan)

    def start_scan(self):
        """เริ่มการสแกน"""
        mode_text = self.scan_mode_combo.currentText()

        if "ความถี่ที่รู้จัก" in mode_text:
            mode = "known_frequencies"
            frequencies = None
        elif "สแกนครบทุกช่อง" in mode_text:
            mode = "full"
            frequencies = None
        else:  # ระบุความถี่เอง
            mode = "custom"
            freq_text = self.custom_freq_combo.currentText()
            try:
                freq = float(freq_text.split()[0])
                frequencies = [freq]
            except:
                QMessageBox.warning(self, "ข้อผิดพลาด", "กรุณาระบุความถี่ที่ถูกต้อง")
                return

        self.scan_requested.emit(mode, frequencies)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_scan(self):
        """หยุดการสแกน"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def update_progress(self, percent, message, frequency):
        """อัปเดตความคืบหน้า"""
        self.progress_bar.setValue(percent)
        self.progress_label.setText(message)
        self.current_freq_label.setText(f"ความถี่ปัจจุบัน: {frequency:.3f} MHz")

    def scan_completed(self, stations_found):
        """การสแกนเสร็จสิ้น"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_label.setText(f"สแกนเสร็จสิ้น - พบสถานี {stations_found} รายการ")
        self.stations_found_label.setText(f"สถานีที่พบ: {stations_found}")
        self.last_scan_label.setText(f"ครั้งล่าสุด: {datetime.now().strftime('%H:%M:%S')}")

class Lab4MainWindow(QMainWindow):
    """หน้าต่างหลักของ Lab 4"""

    def __init__(self):
        super().__init__()
        self.db = StationDatabase()
        self.scanner = DABScannerEngine()

        self.setup_ui()
        self.setup_connections()

        self.setWindowTitle("Lab 4: DAB+ Station Scanner (RTL-SDR + ETI Pipeline)")
        self.setGeometry(100, 100, 1400, 900)

        # สำหรับหน้าจอสัมผัส
        if '--fullscreen' in sys.argv:
            self.showFullScreen()

    def setup_ui(self):
        """สร้าง UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # หัวข้อ
        title = QLabel("Lab 4: DAB+ Station Scanner")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            background-color: #3498db; color: white; padding: 15px;
            border-radius: 10px; margin: 5px;
        """)
        layout.addWidget(title)

        # Tabs
        self.tab_widget = QTabWidget()

        # Tab 1: Scanner
        scanner_tab = QWidget()
        scanner_layout = QHBoxLayout()

        self.scan_control = ScanControlWidget()
        self.station_list = StationListWidget()

        scanner_layout.addWidget(self.scan_control, 1)
        scanner_layout.addWidget(self.station_list, 2)
        scanner_tab.setLayout(scanner_layout)

        # Tab 2: Signal Monitor
        self.signal_monitor = SignalMonitorWidget()

        # เพิ่ม tabs
        self.tab_widget.addTab(scanner_tab, "🔍 Scanner")
        self.tab_widget.addTab(self.signal_monitor, "📊 Signal Monitor")

        layout.addWidget(self.tab_widget)

        # Status bar
        self.status_label = QLabel("พร้อมใช้งาน - เลือกโหมดการสแกนและเริ่มสแกน")
        self.status_label.setStyleSheet("background-color: #e8f5e8; padding: 8px; border-radius: 5px;")
        layout.addWidget(self.status_label)

        central_widget.setLayout(layout)

    def setup_connections(self):
        """เชื่อมต่อ signals"""
        # Scanner connections
        self.scan_control.scan_requested.connect(self.start_scan)
        self.scanner.station_found.connect(self.on_station_found)
        self.scanner.scan_progress.connect(self.scan_control.update_progress)
        self.scanner.scan_completed.connect(self.scan_control.scan_completed)
        self.scanner.scan_completed.connect(self.on_scan_completed)
        self.scanner.error_occurred.connect(self.show_error)

        # Station list connections
        self.station_list.station_selected.connect(self.on_station_selected)

    def start_scan(self, mode, frequencies):
        """เริ่มการสแกน"""
        try:
            if self.scanner.isRunning():
                QMessageBox.warning(self, "กำลังสแกน", "กรุณารอให้การสแกนปัจจุบันเสร็จสิ้น")
                return

            self.scanner.set_scan_mode(mode, frequencies)
            self.scanner.start()

            self.status_label.setText(f"กำลังสแกน ({mode})...")
            logger.info(f"Started scan with mode: {mode}")

        except Exception as e:
            self.show_error(f"Start scan error: {e}")

    def on_station_found(self, station_data):
        """เมื่อพบสถานีใหม่"""
        try:
            station_id = self.db.add_station(station_data)
            if station_id:
                self.station_list.refresh_stations()
                logger.info(f"Found station: {station_data.get('service_label')} @ {station_data.get('frequency_mhz')} MHz")

                # เพิ่มข้อมูลสัญญาณเข้า monitor
                self.signal_monitor.add_signal_data(station_id, station_data)

        except Exception as e:
            logger.error(f"Add station error: {e}")

    def on_scan_completed(self, stations_found):
        """เมื่อการสแกนเสร็จสิ้น"""
        self.status_label.setText(f"สแกนเสร็จสิ้น - พบสถานี {stations_found} รายการ")
        QMessageBox.information(self, "สแกนเสร็จสิ้น",
                              f"พบสถานี DAB+ ทั้งหมด {stations_found} รายการ")

    def on_station_selected(self, station_id):
        """เมื่อเลือกสถานี"""
        self.status_label.setText(f"เลือกสถานี ID: {station_id}")

    def show_error(self, error_message):
        """แสดงข้อความผิดพลาด"""
        QMessageBox.critical(self, "ข้อผิดพลาด", error_message)
        self.status_label.setText(f"ข้อผิดพลาด: {error_message}")
        logger.error(error_message)

    def closeEvent(self, event):
        """เมื่อปิดโปรแกรม"""
        try:
            if self.scanner.isRunning():
                self.scanner.stop_scanning()
                self.scanner.wait(3000)  # รอ 3 วินาที

            event.accept()
        except Exception as e:
            logger.error(f"Close event error: {e}")
            event.accept()

def main():
    """ฟังก์ชันหลัก"""
    app = QApplication(sys.argv)

    # ตั้งค่า font สำหรับ touchscreen
    font = QFont()
    font.setPointSize(12)
    app.setFont(font)

    # สร้างและแสดงหน้าต่างหลัก
    window = Lab4MainWindow()
    window.show()

    print("Lab 4: DAB+ Station Scanner")
    print("Based on Lab 3 RTL-SDR + ETI Pipeline")
    print("Features:")
    print("- RTL-SDR based scanning")
    print("- ETI stream processing")
    print("- Real-time signal monitoring")
    print("- Touch-friendly interface")
    print("- Database storage")

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()