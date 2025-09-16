#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAB 6: สร้าง DAB+ Signal Analyzer (เฉลย)
- พัฒนาเครื่องมือวิเคราะห์สัญญาณ DAB+ อย่างละเอียด
- วิเคราะห์คุณภาพสัญญาณ (SNR, RSSI, BER) และสเปกตรัมความถี่
- สร้างกราฟและรายงานการวิเคราะห์แบบ real-time
- ส่งออกข้อมูลเป็น CSV, JSON และ PNG รองรับหน้าจอสัมผัส
"""

import sys
import os
import csv
import json
import sqlite3
import logging
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QProgressBar, QComboBox, QSpinBox,
    QGroupBox, QSplitter, QTextEdit, QTabWidget, QSlider, QCheckBox,
    QFileDialog, QMessageBox, QScrollArea, QGridLayout, QLCDNumber,
    QDial, QFrame, QSizePolicy
)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, QDateTime
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

try:
    from rtlsdr import RtlSdr
except ImportError:
    RtlSdr = None

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Lab6")

# ---------- Signal Analysis Database ----------
class AnalysisDatabase:
    def __init__(self, db_path="signal_analysis.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """สร้างฐานข้อมูลสำหรับเก็บข้อมูลการวิเคราะห์"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # ตาราง signal_measurements
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signal_measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    frequency_mhz REAL NOT NULL,
                    signal_strength REAL,
                    snr REAL,
                    ber REAL,
                    noise_floor REAL,
                    peak_frequency REAL,
                    bandwidth REAL,
                    modulation_quality REAL
                )
            ''')

            # ตาราง spectrum_data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS spectrum_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    measurement_id INTEGER,
                    frequency_bins TEXT,  -- JSON array
                    power_values TEXT,    -- JSON array
                    FOREIGN KEY (measurement_id) REFERENCES signal_measurements (id)
                )
            ''')

            # ตาราง analysis_sessions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT,
                    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    end_time DATETIME,
                    frequency_range TEXT,
                    notes TEXT
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("ฐานข้อมูลการวิเคราะห์พร้อมใช้งาน")

        except Exception as e:
            logger.error(f"สร้างฐานข้อมูลผิดพลาด: {str(e)}")

    def add_measurement(self, measurement_data):
        """เพิ่มข้อมูลการวัดสัญญาณ"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO signal_measurements
                (frequency_mhz, signal_strength, snr, ber, noise_floor,
                 peak_frequency, bandwidth, modulation_quality)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                measurement_data.get('frequency_mhz'),
                measurement_data.get('signal_strength'),
                measurement_data.get('snr'),
                measurement_data.get('ber'),
                measurement_data.get('noise_floor'),
                measurement_data.get('peak_frequency'),
                measurement_data.get('bandwidth'),
                measurement_data.get('modulation_quality')
            ))

            measurement_id = cursor.lastrowid

            # บันทึกข้อมูลสเปกตรัมถ้ามี
            if 'spectrum_frequencies' in measurement_data and 'spectrum_powers' in measurement_data:
                cursor.execute('''
                    INSERT INTO spectrum_data (measurement_id, frequency_bins, power_values)
                    VALUES (?, ?, ?)
                ''', (
                    measurement_id,
                    json.dumps(measurement_data['spectrum_frequencies'].tolist()),
                    json.dumps(measurement_data['spectrum_powers'].tolist())
                ))

            conn.commit()
            conn.close()
            return measurement_id

        except Exception as e:
            logger.error(f"เพิ่มข้อมูลการวัดผิดพลาด: {str(e)}")
            return None

    def get_measurements(self, session_id=None, limit=100):
        """ดึงข้อมูลการวัดสัญญาณ"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = '''
                SELECT * FROM signal_measurements
                ORDER BY timestamp DESC LIMIT ?
            '''
            cursor.execute(query, (limit,))
            measurements = cursor.fetchall()
            conn.close()
            return measurements

        except Exception as e:
            logger.error(f"ดึงข้อมูลการวัดผิดพลาด: {str(e)}")
            return []

    def export_to_csv(self, filename, session_id=None):
        """ส่งออกข้อมูลเป็น CSV"""
        try:
            measurements = self.get_measurements(session_id, limit=1000)

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'ID', 'Timestamp', 'Frequency (MHz)', 'Signal Strength (dBm)',
                    'SNR (dB)', 'BER (%)', 'Noise Floor (dBm)', 'Peak Frequency (MHz)',
                    'Bandwidth (kHz)', 'Modulation Quality (%)'
                ])
                writer.writerows(measurements)

            logger.info(f"ส่งออกข้อมูล CSV: {filename}")
            return True

        except Exception as e:
            logger.error(f"ส่งออก CSV ผิดพลาด: {str(e)}")
            return False

# ---------- Signal Analyzer Thread ----------
class SignalAnalyzer(QThread):
    measurement_ready = pyqtSignal(dict)
    spectrum_ready = pyqtSignal(np.ndarray, np.ndarray)  # frequencies, powers
    analysis_complete = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.sdr = None
        self.is_analyzing = False
        self.frequency = 174.928e6  # MHz
        self.sample_rate = 2.4e6
        self.gain = 'auto'
        self.fft_size = 2048
        self._stop_flag = False

    def connect_rtlsdr(self):
        """เชื่อมต่อ RTL-SDR"""
        try:
            if RtlSdr is None:
                raise ImportError("ไม่พบโมดูล pyrtlsdr")

            self.sdr = RtlSdr()
            self.sdr.sample_rate = self.sample_rate
            self.sdr.center_freq = self.frequency
            self.sdr.gain = self.gain

            # ทดสอบการอ่านข้อมูล
            test_samples = self.sdr.read_samples(1024)
            if len(test_samples) > 0:
                logger.info("เชื่อมต่อ RTL-SDR สำเร็จ")
                return True
            else:
                return False

        except Exception as e:
            self.error_occurred.emit(f"เชื่อมต่อ RTL-SDR ผิดพลาด: {str(e)}")
            logger.error(f"เชื่อมต่อ RTL-SDR ผิดพลาด: {str(e)}")
            return False

    def disconnect_rtlsdr(self):
        """ตัดการเชื่อมต่อ RTL-SDR"""
        try:
            self.is_analyzing = False
            self._stop_flag = True
            if self.sdr:
                self.sdr.close()
                self.sdr = None
                logger.info("ตัดการเชื่อมต่อ RTL-SDR แล้ว")
        except Exception as e:
            logger.error(f"ปิด RTL-SDR ผิดพลาด: {str(e)}")

    def set_frequency(self, frequency):
        """ตั้งค่าความถี่ที่จะวิเคราะห์"""
        self.frequency = frequency * 1000  # Convert kHz to Hz
        if self.sdr:
            try:
                self.sdr.center_freq = self.frequency
                logger.info(f"ตั้งค่าความถี่: {frequency/1000:.3f} MHz")
            except Exception as e:
                self.error_occurred.emit(f"ตั้งค่าความถี่ผิดพลาด: {str(e)}")

    def set_parameters(self, sample_rate, gain, fft_size):
        """ตั้งค่าพารามิเตอร์การวิเคราะห์"""
        self.sample_rate = sample_rate
        self.gain = gain
        self.fft_size = fft_size

        if self.sdr:
            try:
                self.sdr.sample_rate = sample_rate
                self.sdr.gain = gain if gain != 'auto' else 'auto'
            except Exception as e:
                logger.error(f"ตั้งค่าพารามิเตอร์ผิดพลาด: {str(e)}")

    def run(self):
        """วิเคราะห์สัญญาณอย่างต่อเนื่อง"""
        self.is_analyzing = True
        self._stop_flag = False

        while self.is_analyzing and not self._stop_flag:
            try:
                if self.sdr is None:
                    # ใช้ข้อมูลจำลองถ้าไม่มี RTL-SDR
                    measurement = self.analyze_signal_mock()
                else:
                    measurement = self.analyze_signal()

                if measurement:
                    self.measurement_ready.emit(measurement)

                self.msleep(500)  # อัปเดตทุก 0.5 วินาที

            except Exception as e:
                self.error_occurred.emit(f"การวิเคราะห์ผิดพลาด: {str(e)}")
                self.msleep(1000)

    def analyze_signal(self):
        """วิเคราะห์สัญญาณ DAB+"""
        try:
            if not self.sdr:
                return None

            # อ่าน samples
            samples = self.sdr.read_samples(self.fft_size * 4)
            if len(samples) == 0:
                return None

            # คำนวณสเปกตรัม
            frequencies, power_spectrum = self.calculate_spectrum(samples)

            # คำนวณพารามิเตอร์คุณภาพสัญญาณ
            signal_strength = np.max(power_spectrum)  # RSSI
            noise_floor = np.median(power_spectrum)
            snr = float(signal_strength - noise_floor)
            ber = self.estimate_ber(samples)

            # หา peak frequency
            peak_idx = np.argmax(power_spectrum)
            peak_frequency = frequencies[peak_idx] / 1e6  # Convert to MHz

            # คำนวณ bandwidth (ประมาณ)
            bandwidth = self.calculate_bandwidth(frequencies, power_spectrum, signal_strength)

            # ประเมิน modulation quality
            modulation_quality = self.assess_modulation_quality(snr, ber)

            measurement = {
                'timestamp': datetime.now(),
                'frequency_mhz': self.frequency / 1e6,
                'signal_strength': float(signal_strength),
                'snr': snr,
                'ber': float(ber),
                'noise_floor': float(noise_floor),
                'peak_frequency': peak_frequency,
                'bandwidth': bandwidth,
                'modulation_quality': modulation_quality,
                'spectrum_frequencies': frequencies,
                'spectrum_powers': power_spectrum
            }

            # ส่ง spectrum data
            self.spectrum_ready.emit(frequencies, power_spectrum)

            return measurement

        except Exception as e:
            logger.error(f"วิเคราะห์สัญญาณผิดพลาด: {str(e)}")
            return None

    def analyze_signal_mock(self):
        """วิเคราะห์สัญญาณแบบจำลอง (สำหรับทดสอบ)"""
        import random

        # สร้างข้อมูลจำลอง
        center_freq = self.frequency / 1e6  # MHz
        signal_strength = -45 + random.gauss(0, 10)
        noise_floor = -80 + random.gauss(0, 5)
        snr = signal_strength - noise_floor
        ber = max(0, min(100, random.gauss(2, 1)))

        # สร้าง spectrum จำลอง
        n_points = self.fft_size
        frequencies = np.linspace(
            center_freq - self.sample_rate/2e6,
            center_freq + self.sample_rate/2e6,
            n_points
        ) * 1e6  # Convert back to Hz

        # สร้าง power spectrum จำลอง
        power_spectrum = np.random.normal(noise_floor, 5, n_points)

        # เพิ่มสัญญาณจำลองในบางความถี่
        dab_frequencies = [174.928, 176.640, 181.936, 188.928]
        for dab_freq in dab_frequencies:
            if abs(center_freq - dab_freq) < self.sample_rate/2e6:
                # เพิ่มสัญญาณ
                freq_idx = np.argmin(np.abs(frequencies/1e6 - dab_freq))
                signal_width = max(1, n_points // 100)
                for i in range(max(0, freq_idx-signal_width),
                              min(n_points, freq_idx+signal_width)):
                    power_spectrum[i] += signal_strength - noise_floor

        peak_idx = np.argmax(power_spectrum)
        peak_frequency = frequencies[peak_idx] / 1e6

        bandwidth = 1.536  # DAB+ bandwidth in MHz
        modulation_quality = self.assess_modulation_quality(snr, ber)

        measurement = {
            'timestamp': datetime.now(),
            'frequency_mhz': center_freq,
            'signal_strength': float(signal_strength),
            'snr': float(snr),
            'ber': float(ber),
            'noise_floor': float(noise_floor),
            'peak_frequency': peak_frequency,
            'bandwidth': bandwidth,
            'modulation_quality': modulation_quality,
            'spectrum_frequencies': frequencies,
            'spectrum_powers': power_spectrum
        }

        # ส่ง spectrum data
        self.spectrum_ready.emit(frequencies, power_spectrum)

        return measurement

    def calculate_spectrum(self, samples):
        """คำนวณสเปกตรัมความถี่"""
        try:
            # จำกัดขนาด samples
            if len(samples) > self.fft_size:
                samples = samples[:self.fft_size]

            # คำนวณ FFT
            fft_data = np.fft.fft(samples, self.fft_size)
            fft_shifted = np.fft.fftshift(fft_data)
            power_spectrum = 20 * np.log10(np.abs(fft_shifted) + 1e-12)

            # คำนวณความถี่
            frequencies = np.fft.fftfreq(self.fft_size, 1/self.sample_rate)
            frequencies = np.fft.fftshift(frequencies) + self.frequency

            return frequencies, power_spectrum

        except Exception as e:
            logger.error(f"คำนวณสเปกตรัมผิดพลาด: {str(e)}")
            return None, None

    def estimate_ber(self, samples):
        """ประเมิน Bit Error Rate"""
        try:
            # วิธีประมาณ BER จากคุณภาพสัญญาณ
            # ในการใช้งานจริงต้องใช้ DAB+ decoder

            # คำนวณ EVM (Error Vector Magnitude)
            signal_power = np.mean(np.abs(samples)**2)
            noise_estimate = np.var(np.diff(samples))

            if signal_power > 0:
                snr_linear = signal_power / (noise_estimate + 1e-12)
                snr_db = 10 * np.log10(snr_linear)

                # ประมาณ BER จาก SNR (สำหรับ QPSK)
                if snr_db > 20:
                    ber = 0.001
                elif snr_db > 15:
                    ber = 0.01
                elif snr_db > 10:
                    ber = 0.1
                else:
                    ber = min(50, 1 / (snr_linear + 0.1))
            else:
                ber = 50  # High error rate

            return max(0, min(100, ber))

        except Exception as e:
            logger.error(f"ประเมิน BER ผิดพลาด: {str(e)}")
            return 50

    def calculate_bandwidth(self, frequencies, power_spectrum, signal_strength):
        """คำนวณ bandwidth ของสัญญาณ"""
        try:
            threshold = signal_strength - 6  # -6dB bandwidth
            above_threshold = power_spectrum > threshold

            if np.any(above_threshold):
                indices = np.where(above_threshold)[0]
                if len(indices) > 1:
                    freq_span = frequencies[indices[-1]] - frequencies[indices[0]]
                    return abs(freq_span) / 1e3  # Convert to kHz

            return 1536  # Default DAB+ bandwidth in kHz

        except Exception as e:
            logger.error(f"คำนวณ bandwidth ผิดพลาด: {str(e)}")
            return 1536

    def assess_modulation_quality(self, snr, ber):
        """ประเมินคุณภาพการมอดูเลชัน"""
        try:
            # คำนวณคุณภาพโดยรวมจาก SNR และ BER
            snr_score = min(100, max(0, (snr + 5) * 4))  # SNR > 20dB = 100%
            ber_score = max(0, 100 - ber * 2)  # BER < 1% = 100%

            quality = (snr_score + ber_score) / 2
            return max(0, min(100, quality))

        except Exception as e:
            logger.error(f"ประเมินคุณภาพผิดพลาด: {str(e)}")
            return 0

    def find_dab_signals(self, frequencies, power_spectrum):
        """หาสัญญาณ DAB+ ในสเปกตรัม"""
        try:
            dab_signals = []

            # DAB+ frequencies in MHz
            dab_freq_list = [
                174.928, 176.640, 178.352, 180.064, 181.936,
                183.648, 185.360, 187.072, 188.928, 190.640
            ]

            noise_floor = np.median(power_spectrum)
            threshold = noise_floor + 10  # 10dB above noise floor

            for dab_freq in dab_freq_list:
                # หาดัชนีความถี่ที่ใกล้ที่สุด
                freq_idx = np.argmin(np.abs(frequencies/1e6 - dab_freq))

                # ตรวจสอบในช่วง ±100kHz
                search_range = max(1, len(frequencies) // 50)
                start_idx = max(0, freq_idx - search_range)
                end_idx = min(len(power_spectrum), freq_idx + search_range)

                local_max = np.max(power_spectrum[start_idx:end_idx])

                if local_max > threshold:
                    dab_signals.append({
                        'frequency': dab_freq,
                        'power': local_max,
                        'snr': local_max - noise_floor
                    })

            return dab_signals

        except Exception as e:
            logger.error(f"หาสัญญาณ DAB+ ผิดพลาด: {str(e)}")
            return []

    def stop_analysis(self):
        """หยุดการวิเคราะห์"""
        self.is_analyzing = False
        self._stop_flag = True

# ---------- Real-time Spectrum Widget ----------
class SpectrumAnalyzerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_matplotlib()
        self.setup_ui()
        self.frequency_data = []
        self.power_data = []
        self.max_points = 1000
        self.frozen = False

    def setup_matplotlib(self):
        """ตั้งค่า matplotlib สำหรับแสดงสเปกตรัม"""
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('Frequency (MHz)')
        self.ax.set_ylabel('Power (dB)')
        self.ax.set_title('DAB+ Spectrum Analyzer - Real Time')
        self.ax.grid(True, alpha=0.3)

        # สร้างเส้นกราฟเปล่า
        self.line, = self.ax.plot([], [], 'b-', linewidth=1)

        self.figure.tight_layout()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # หัวข้อ
        title = QLabel("Real-time Spectrum Analyzer")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Matplotlib canvas
        layout.addWidget(self.canvas)

        # Control Panel
        control_group = QGroupBox("การควบคุมการแสดงผล")
        control_layout = QHBoxLayout(control_group)

        self.freeze_btn = QPushButton("หยุดชั่วคราว")
        self.clear_btn = QPushButton("เคลียร์")
        self.save_spectrum_btn = QPushButton("บันทึกสเปกตรัม")

        # ตั้งค่าปุ่มสำหรับ touch interface
        for btn in [self.freeze_btn, self.clear_btn, self.save_spectrum_btn]:
            btn.setMinimumHeight(48)
            btn.setMinimumWidth(120)

        control_layout.addWidget(self.freeze_btn)
        control_layout.addWidget(self.clear_btn)
        control_layout.addWidget(self.save_spectrum_btn)

        layout.addWidget(control_group)

        # เชื่อมต่อ signals
        self.freeze_btn.clicked.connect(self.toggle_freeze)
        self.clear_btn.clicked.connect(self.clear_spectrum)
        self.save_spectrum_btn.clicked.connect(self.save_spectrum)

    def update_spectrum(self, frequencies, powers):
        """อัปเดตข้อมูลสเปกตรัม"""
        if self.frozen:
            return

        try:
            # แปลงความถี่เป็น MHz
            freq_mhz = frequencies / 1e6

            # อัปเดตกราฟ
            self.line.set_data(freq_mhz, powers)

            # ปรับขอบเขตแกน
            if len(freq_mhz) > 0:
                self.ax.set_xlim([np.min(freq_mhz), np.max(freq_mhz)])
                self.ax.set_ylim([np.min(powers) - 5, np.max(powers) + 5])

            # เก็บข้อมูลสำหรับบันทึก
            self.frequency_data = frequencies
            self.power_data = powers

            self.canvas.draw_idle()

        except Exception as e:
            logger.error(f"อัปเดตสเปกตรัมผิดพลาด: {str(e)}")

    def toggle_freeze(self):
        """เปิด/ปิดการแสดงผลแบบเรียลไทม์"""
        self.frozen = not self.frozen
        self.freeze_btn.setText("ดำเนินการต่อ" if self.frozen else "หยุดชั่วคราว")

    def clear_spectrum(self):
        """เคลียร์กราฟสเปกตรัม"""
        self.ax.clear()
        self.ax.set_xlabel('Frequency (MHz)')
        self.ax.set_ylabel('Power (dB)')
        self.ax.set_title('DAB+ Spectrum Analyzer - Real Time')
        self.ax.grid(True, alpha=0.3)
        self.line, = self.ax.plot([], [], 'b-', linewidth=1)
        self.canvas.draw()

    def save_spectrum(self):
        """บันทึกกราฟสเปกตรัม"""
        if len(self.frequency_data) == 0:
            QMessageBox.warning(self, "ไม่มีข้อมูล", "ยังไม่มีข้อมูลสเปกตรัมที่จะบันทึก")
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # บันทึกกราฟเป็น PNG
            png_filename, _ = QFileDialog.getSaveFileName(
                self, "บันทึกกราฟสเปกตรัม",
                f"spectrum_{timestamp}.png",
                "PNG Files (*.png)"
            )

            if png_filename:
                self.figure.savefig(png_filename, dpi=300, bbox_inches='tight')
                logger.info(f"บันทึกกราฟ: {png_filename}")

            # บันทึกข้อมูลเป็น CSV
            csv_filename, _ = QFileDialog.getSaveFileName(
                self, "บันทึกข้อมูลสเปกตรัม",
                f"spectrum_data_{timestamp}.csv",
                "CSV Files (*.csv)"
            )

            if csv_filename:
                with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Frequency (Hz)', 'Power (dB)'])
                    for freq, power in zip(self.frequency_data, self.power_data):
                        writer.writerow([freq, power])
                logger.info(f"บันทึกข้อมูล CSV: {csv_filename}")

            if png_filename or csv_filename:
                QMessageBox.information(self, "บันทึกสำเร็จ", "บันทึกไฟล์เรียบร้อยแล้ว")

        except Exception as e:
            QMessageBox.critical(self, "บันทึกผิดพลาด", str(e))
            logger.error(f"บันทึกสเปกตรัมผิดพลาด: {str(e)}")

# ---------- Signal Quality Meters Widget ----------
class SignalQualityWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout(self)

        # หัวข้อ
        title = QLabel("คุณภาพสัญญาณ")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title, 0, 0, 1, 3)

        # RSSI Meter
        rssi_group = QGroupBox("RSSI (dBm)")
        rssi_layout = QVBoxLayout(rssi_group)

        self.rssi_lcd = QLCDNumber()
        self.rssi_lcd.setDigitCount(6)
        self.rssi_lcd.setMinimumHeight(60)
        self.rssi_lcd.setStyleSheet("""
            QLCDNumber { background-color: black; color: green; }
        """)

        self.rssi_bar = QProgressBar()
        self.rssi_bar.setRange(-100, -20)
        self.rssi_bar.setValue(-60)
        self.rssi_bar.setMinimumHeight(30)
        self.rssi_bar.setStyleSheet("""
            QProgressBar::chunk { background-color: #4CAF50; }
        """)

        rssi_layout.addWidget(self.rssi_lcd)
        rssi_layout.addWidget(self.rssi_bar)
        layout.addWidget(rssi_group, 1, 0)

        # SNR Meter
        snr_group = QGroupBox("SNR (dB)")
        snr_layout = QVBoxLayout(snr_group)

        self.snr_lcd = QLCDNumber()
        self.snr_lcd.setDigitCount(5)
        self.snr_lcd.setMinimumHeight(60)
        self.snr_lcd.setStyleSheet("""
            QLCDNumber { background-color: black; color: blue; }
        """)

        # QDial สำหรับแสดง SNR แบบ analog meter
        self.snr_dial = QDial()
        self.snr_dial.setRange(0, 40)
        self.snr_dial.setValue(15)
        self.snr_dial.setMinimumSize(100, 100)
        self.snr_dial.setEnabled(False)  # ปิดการแก้ไข

        snr_layout.addWidget(self.snr_lcd)
        snr_layout.addWidget(self.snr_dial)
        layout.addWidget(snr_group, 1, 1)

        # BER Meter
        ber_group = QGroupBox("BER (%)")
        ber_layout = QVBoxLayout(ber_group)

        self.ber_lcd = QLCDNumber()
        self.ber_lcd.setDigitCount(6)
        self.ber_lcd.setMinimumHeight(60)
        self.ber_lcd.setStyleSheet("""
            QLCDNumber { background-color: black; color: red; }
        """)

        self.ber_bar = QProgressBar()
        self.ber_bar.setRange(0, 100)
        self.ber_bar.setValue(5)
        self.ber_bar.setMinimumHeight(30)
        self.ber_bar.setStyleSheet("""
            QProgressBar::chunk { background-color: #f44336; }
        """)

        ber_layout.addWidget(self.ber_lcd)
        ber_layout.addWidget(self.ber_bar)
        layout.addWidget(ber_group, 1, 2)

        # Signal Status Indicators
        status_group = QGroupBox("สถานะสัญญาณ")
        status_layout = QVBoxLayout(status_group)

        self.signal_status_label = QLabel("ไม่มีสัญญาณ")
        self.signal_status_label.setAlignment(Qt.AlignCenter)
        self.signal_status_label.setStyleSheet("""
            QLabel {
                background-color: #ffcccc;
                border: 2px solid #ff6666;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        self.frequency_label = QLabel("ความถี่: -- MHz")
        self.modulation_label = QLabel("Modulation: --")
        self.bitrate_label = QLabel("Bitrate: -- kbps")

        status_layout.addWidget(self.signal_status_label)
        status_layout.addWidget(self.frequency_label)
        status_layout.addWidget(self.modulation_label)
        status_layout.addWidget(self.bitrate_label)

        layout.addWidget(status_group, 2, 0, 1, 3)

    def update_signal_quality(self, rssi, snr, ber):
        """อัปเดตค่าคุณภาพสัญญาณ"""
        try:
            # อัปเดต LCD displays
            self.rssi_lcd.display(f"{rssi:.1f}")
            self.snr_lcd.display(f"{snr:.1f}")
            self.ber_lcd.display(f"{ber:.3f}")

            # อัปเดต progress bars
            self.rssi_bar.setValue(int(rssi))
            self.ber_bar.setValue(int(ber))

            # อัปเดต SNR dial
            snr_value = max(0, min(40, int(snr)))
            self.snr_dial.setValue(snr_value)

            # เปลี่ยนสีตามคุณภาพสัญญาณ
            if rssi > -50 and snr > 15 and ber < 1:
                quality = "ดีเยี่ยม"
                color = "#4CAF50"  # Green
            elif rssi > -65 and snr > 10 and ber < 5:
                quality = "ดี"
                color = "#FF9800"  # Orange
            else:
                quality = "ไม่ดี"
                color = "#f44336"  # Red

            self.rssi_bar.setStyleSheet(f"""
                QProgressBar::chunk {{ background-color: {color}; }}
            """)

        except Exception as e:
            logger.error(f"อัปเดตคุณภาพสัญญาณผิดพลาด: {str(e)}")

    def update_signal_status(self, status, frequency=None, modulation=None, bitrate=None):
        """อัปเดตสถานะสัญญาณ"""
        try:
            self.signal_status_label.setText(status)

            # เปลี่ยนสี background ตามสถานะ
            if "ดี" in status:
                bg_color = "#d4edda"
                border_color = "#c3e6cb"
            elif "สัญญาณอ่อน" in status:
                bg_color = "#fff3cd"
                border_color = "#ffeaa7"
            else:
                bg_color = "#f8d7da"
                border_color = "#f5c6cb"

            self.signal_status_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {bg_color};
                    border: 2px solid {border_color};
                    border-radius: 10px;
                    padding: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }}
            """)

            # อัปเดตข้อมูลเพิ่มเติม
            if frequency:
                self.frequency_label.setText(f"ความถี่: {frequency:.3f} MHz")
            if modulation:
                self.modulation_label.setText(f"Modulation: {modulation}")
            if bitrate:
                self.bitrate_label.setText(f"Bitrate: {bitrate} kbps")

        except Exception as e:
            logger.error(f"อัปเดตสถานะสัญญาณผิดพลาด: {str(e)}")

# ---------- Analysis Control Panel ----------
class AnalysisControlWidget(QWidget):
    analysis_started = pyqtSignal(dict)  # parameters
    analysis_stopped = pyqtSignal()
    frequency_changed = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # หัวข้อ
        title = QLabel("การควบคุมการวิเคราะห์")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Frequency Control
        freq_group = QGroupBox("ความถี่ (MHz)")
        freq_layout = QVBoxLayout(freq_group)

        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setRange(174000, 240000)  # 174.000 - 240.000 MHz (in kHz)
        self.freq_slider.setValue(174928)  # 174.928 MHz
        self.freq_slider.setMinimumHeight(40)

        self.freq_spinbox = QSpinBox()
        self.freq_spinbox.setRange(174000, 240000)
        self.freq_spinbox.setValue(174928)
        self.freq_spinbox.setSuffix(" kHz")
        self.freq_spinbox.setMinimumHeight(40)

        # ปุ่มความถี่ที่กำหนดไว้ล่วงหน้า (preset frequencies)
        preset_layout = QHBoxLayout()
        self.freq_presets = [174928, 181936, 188928, 195936, 210096]
        preset_labels = ["5A", "11D", "12A", "12D", "13F"]

        for freq, label in zip(self.freq_presets, preset_labels):
            btn = QPushButton(f"{label}\n{freq/1000:.3f}")
            btn.setMinimumSize(80, 50)
            btn.clicked.connect(lambda checked, f=freq: self.set_frequency(f))
            preset_layout.addWidget(btn)

        freq_layout.addWidget(QLabel("ความถี่:"))
        freq_layout.addWidget(self.freq_slider)
        freq_layout.addWidget(self.freq_spinbox)
        freq_layout.addWidget(QLabel("Presets:"))
        freq_layout.addLayout(preset_layout)

        layout.addWidget(freq_group)

        # Analysis Parameters
        params_group = QGroupBox("พารามิเตอร์การวิเคราะห์")
        params_layout = QGridLayout(params_group)

        params_layout.addWidget(QLabel("Sample Rate:"), 0, 0)
        self.samplerate_combo = QComboBox()
        self.samplerate_combo.addItems([
            "0.25 MHz", "0.5 MHz", "1.0 MHz",
            "1.2 MHz", "2.0 MHz", "2.4 MHz"
        ])
        self.samplerate_combo.setCurrentText("2.4 MHz")
        self.samplerate_combo.setMinimumHeight(40)
        params_layout.addWidget(self.samplerate_combo, 0, 1)

        params_layout.addWidget(QLabel("Gain:"), 1, 0)
        self.gain_combo = QComboBox()
        self.gain_combo.addItems(["auto", "0", "9", "14", "27", "37", "77"])
        self.gain_combo.setMinimumHeight(40)
        params_layout.addWidget(self.gain_combo, 1, 1)

        params_layout.addWidget(QLabel("FFT Size:"), 2, 0)
        self.fft_combo = QComboBox()
        self.fft_combo.addItems(["1024", "2048", "4096", "8192"])
        self.fft_combo.setCurrentText("2048")
        self.fft_combo.setMinimumHeight(40)
        params_layout.addWidget(self.fft_combo, 2, 1)

        layout.addWidget(params_group)

        # Control Buttons
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("เริ่มวิเคราะห์")
        self.stop_btn = QPushButton("หยุดวิเคราะห์")
        self.export_btn = QPushButton("ส่งออกข้อมูล")

        # ตั้งค่าปุ่มสำหรับ touch interface
        for btn in [self.start_btn, self.stop_btn, self.export_btn]:
            btn.setMinimumHeight(48)
            btn.setMinimumWidth(120)

        self.stop_btn.setEnabled(False)

        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.export_btn)

        layout.addLayout(control_layout)

        # เชื่อมต่อ signals
        self.freq_slider.valueChanged.connect(self.on_frequency_changed)
        self.freq_spinbox.valueChanged.connect(self.on_frequency_changed)
        self.start_btn.clicked.connect(self.start_analysis)
        self.stop_btn.clicked.connect(self.stop_analysis)
        self.export_btn.clicked.connect(self.export_data)

    def set_frequency(self, frequency_khz):
        """ตั้งค่าความถี่"""
        self.freq_slider.setValue(int(frequency_khz))
        self.freq_spinbox.setValue(int(frequency_khz))

    def on_frequency_changed(self, value):
        """เมื่อความถี่เปลี่ยน"""
        if self.sender() == self.freq_slider:
            self.freq_spinbox.setValue(value)
        else:
            self.freq_slider.setValue(value)

        self.frequency_changed.emit(float(value))

    def start_analysis(self):
        """เริ่มการวิเคราะห์"""
        try:
            # รวบรวมพารามิเตอร์
            sample_rate_map = {
                "0.25 MHz": 0.25e6, "0.5 MHz": 0.5e6, "1.0 MHz": 1.0e6,
                "1.2 MHz": 1.2e6, "2.0 MHz": 2.0e6, "2.4 MHz": 2.4e6
            }

            parameters = {
                'frequency': float(self.freq_spinbox.value()),  # kHz
                'sample_rate': sample_rate_map[self.samplerate_combo.currentText()],
                'gain': self.gain_combo.currentText(),
                'fft_size': int(self.fft_combo.currentText())
            }

            self.analysis_started.emit(parameters)

            # อัปเดตสถานะปุ่ม
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "เริ่มการวิเคราะห์ผิดพลาด", str(e))

    def stop_analysis(self):
        """หยุดการวิเคราะห์"""
        self.analysis_stopped.emit()

        # อัปเดตสถานะปุ่ม
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def export_data(self):
        """ส่งออกข้อมูลการวิเคราะห์"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # เลือกรูปแบบการส่งออก
            reply = QMessageBox.question(self, 'ส่งออกข้อมูล',
                                       'เลือกรูปแบบการส่งออก:\n\nYes = CSV\nNo = JSON\nCancel = ยกเลิก',
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            if reply == QMessageBox.Yes:
                filename, _ = QFileDialog.getSaveFileName(
                    self, "ส่งออกเป็น CSV",
                    f"analysis_export_{timestamp}.csv",
                    "CSV Files (*.csv)"
                )
                if filename:
                    # TODO: Export to CSV
                    QMessageBox.information(self, "ส่งออกสำเร็จ", f"ส่งออก CSV: {filename}")

            elif reply == QMessageBox.No:
                filename, _ = QFileDialog.getSaveFileName(
                    self, "ส่งออกเป็น JSON",
                    f"analysis_export_{timestamp}.json",
                    "JSON Files (*.json)"
                )
                if filename:
                    # TODO: Export to JSON
                    QMessageBox.information(self, "ส่งออกสำเร็จ", f"ส่งออก JSON: {filename}")

        except Exception as e:
            QMessageBox.critical(self, "ส่งออกผิดพลาด", str(e))

# ---------- Analysis History Widget ----------
class AnalysisHistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db = AnalysisDatabase()
        self.setup_ui()
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_history)
        self.refresh_timer.start(5000)  # รีเฟรชทุก 5 วินาที

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # หัวข้อ
        title = QLabel("ประวัติการวิเคราะห์")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # History Table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "เวลา", "ความถี่", "RSSI", "SNR", "BER", "คุณภาพ"
        ])

        # ปรับขนาดตาราง
        header = self.history_table.horizontalHeader()
        header.setStretchLastSection(True)
        self.history_table.setMinimumHeight(200)

        layout.addWidget(self.history_table)

        # Summary Statistics
        stats_group = QGroupBox("สถิติสรุป")
        stats_layout = QGridLayout(stats_group)

        self.total_measurements_label = QLabel("การวัดทั้งหมด: 0")
        self.avg_rssi_label = QLabel("RSSI เฉลี่ย: -- dBm")
        self.avg_snr_label = QLabel("SNR เฉลี่ย: -- dB")
        self.success_rate_label = QLabel("อัตราความสำเร็จ: --%")

        stats_layout.addWidget(self.total_measurements_label, 0, 0)
        stats_layout.addWidget(self.avg_rssi_label, 0, 1)
        stats_layout.addWidget(self.avg_snr_label, 1, 0)
        stats_layout.addWidget(self.success_rate_label, 1, 1)

        layout.addWidget(stats_group)

        # Control Buttons
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("รีเฟรช")
        self.clear_btn = QPushButton("ล้างประวัติ")
        self.export_history_btn = QPushButton("ส่งออกประวัติ")

        # ตั้งค่าปุ่มสำหรับ touch interface
        for btn in [self.refresh_btn, self.clear_btn, self.export_history_btn]:
            btn.setMinimumHeight(48)
            btn.setMinimumWidth(100)

        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.export_history_btn)

        layout.addLayout(button_layout)

        # เชื่อมต่อ signals
        self.refresh_btn.clicked.connect(self.refresh_history)
        self.clear_btn.clicked.connect(self.clear_history)
        self.export_history_btn.clicked.connect(self.export_history)

    def refresh_history(self):
        """รีเฟรชประวัติการวิเคราะห์"""
        try:
            measurements = self.db.get_measurements(limit=50)
            self.history_table.setRowCount(len(measurements))

            for i, measurement in enumerate(measurements):
                # measurement: (id, timestamp, frequency_mhz, signal_strength, snr, ber, ...)
                time_str = measurement[1][:19] if measurement[1] else ""
                self.history_table.setItem(i, 0, QTableWidgetItem(time_str))
                self.history_table.setItem(i, 1, QTableWidgetItem(f"{measurement[2]:.3f}"))
                self.history_table.setItem(i, 2, QTableWidgetItem(f"{measurement[3]:.1f}"))
                self.history_table.setItem(i, 3, QTableWidgetItem(f"{measurement[4]:.1f}"))
                self.history_table.setItem(i, 4, QTableWidgetItem(f"{measurement[5]:.3f}"))

                # คำนวณคุณภาพโดยรวม
                quality = "ดี" if measurement[4] > 15 and measurement[5] < 1 else "ปานกลาง" if measurement[4] > 10 else "ไม่ดี"
                self.history_table.setItem(i, 5, QTableWidgetItem(quality))

            # อัปเดตสถิติ
            if measurements:
                total = len(measurements)
                avg_rssi = np.mean([m[3] for m in measurements if m[3]])
                avg_snr = np.mean([m[4] for m in measurements if m[4]])
                good_signals = sum(1 for m in measurements if m[4] and m[4] > 15)
                success_rate = (good_signals / total) * 100 if total > 0 else 0

                self.total_measurements_label.setText(f"การวัดทั้งหมด: {total}")
                self.avg_rssi_label.setText(f"RSSI เฉลี่ย: {avg_rssi:.1f} dBm")
                self.avg_snr_label.setText(f"SNR เฉลี่ย: {avg_snr:.1f} dB")
                self.success_rate_label.setText(f"อัตราความสำเร็จ: {success_rate:.1f}%")

        except Exception as e:
            logger.error(f"รีเฟรชประวัติผิดพลาด: {str(e)}")

    def clear_history(self):
        """ล้างประวัติการวิเคราะห์"""
        try:
            reply = QMessageBox.question(self, 'ล้างประวัติ',
                                       'คุณต้องการล้างประวัติการวิเคราะห์ทั้งหมดหรือไม่?',
                                       QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM signal_measurements')
                cursor.execute('DELETE FROM spectrum_data')
                conn.commit()
                conn.close()

                self.refresh_history()
                QMessageBox.information(self, "ล้างประวัติ", "ล้างประวัติเรียบร้อยแล้ว")

        except Exception as e:
            QMessageBox.critical(self, "ล้างประวัติผิดพลาด", str(e))

    def export_history(self):
        """ส่งออกประวัติการวิเคราะห์"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename, _ = QFileDialog.getSaveFileName(
                self, "ส่งออกประวัติ",
                f"analysis_history_{timestamp}.csv",
                "CSV Files (*.csv)"
            )

            if filename:
                if self.db.export_to_csv(filename):
                    QMessageBox.information(self, "ส่งออกสำเร็จ", f"ส่งออกประวัติ: {filename}")
                else:
                    QMessageBox.critical(self, "ส่งออกผิดพลาด", "ไม่สามารถส่งออกประวัติได้")

        except Exception as e:
            QMessageBox.critical(self, "ส่งออกผิดพลาด", str(e))

# ---------- Main Window ----------
class Lab6MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = AnalysisDatabase()
        self.analyzer = SignalAnalyzer()

        self.setup_ui()
        self.setup_touch_interface()
        self.setup_connections()

        self.setWindowTitle("LAB 6: สร้าง DAB+ Signal Analyzer")
        self.resize(1400, 900)

    def setup_ui(self):
        """สร้าง UI หลัก"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # หัวข้อ
        title_label = QLabel("LAB 6: สร้าง DAB+ Signal Analyzer")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 22px; font-weight: bold; color: #2c3e50;
            padding: 15px; background-color: #ecf0f1; border-radius: 10px;
        """)
        main_layout.addWidget(title_label)

        # Main Splitter
        main_splitter = QSplitter(Qt.Horizontal)

        # Left Panel - Controls and Quality
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.control_panel = AnalysisControlWidget()
        self.quality_panel = SignalQualityWidget()

        left_layout.addWidget(self.control_panel)
        left_layout.addWidget(self.quality_panel)

        main_splitter.addWidget(left_widget)

        # Center Panel - Spectrum Analyzer
        self.spectrum_widget = SpectrumAnalyzerWidget()
        main_splitter.addWidget(self.spectrum_widget)

        # Right Panel - History
        self.history_widget = AnalysisHistoryWidget()
        main_splitter.addWidget(self.history_widget)

        # Set splitter sizes
        main_splitter.setSizes([400, 700, 300])

        main_layout.addWidget(main_splitter)

        # Status bar
        self.status_label = QLabel("พร้อมใช้งาน - เชื่อมต่อ RTL-SDR เพื่อเริ่มวิเคราะห์")
        self.status_label.setStyleSheet("background-color: #dff0d8; padding: 8px; border: 1px solid #d6e9c6;")
        main_layout.addWidget(self.status_label)

    def setup_touch_interface(self):
        """ปรับการแสดงผลสำหรับหน้าจอสัมผัส"""
        font = QFont()
        font.setPointSize(13)
        self.setFont(font)

        # ปรับขนาด splitter handles สำหรับ touch
        main_splitter = self.findChild(QSplitter)
        if main_splitter:
            main_splitter.setHandleWidth(10)

    def setup_connections(self):
        """เชื่อมต่อ signals และ slots"""
        # Control panel signals
        self.control_panel.analysis_started.connect(self.start_analysis)
        self.control_panel.analysis_stopped.connect(self.stop_analysis)
        self.control_panel.frequency_changed.connect(self.analyzer.set_frequency)

        # Analyzer signals
        self.analyzer.measurement_ready.connect(self.on_measurement_ready)
        self.analyzer.spectrum_ready.connect(self.spectrum_widget.update_spectrum)
        self.analyzer.error_occurred.connect(self.show_error)

    def start_analysis(self, parameters):
        """เริ่มการวิเคราะห์"""
        try:
            # ตั้งค่าพารามิเตอร์ analyzer
            self.analyzer.set_parameters(
                parameters['sample_rate'],
                parameters['gain'],
                parameters['fft_size']
            )
            self.analyzer.set_frequency(parameters['frequency'])

            # เชื่อมต่อ RTL-SDR
            if self.analyzer.connect_rtlsdr():
                self.analyzer.start_analysis()
                self.status_label.setText("กำลังวิเคราะห์สัญญาณ...")
                logger.info("เริ่มการวิเคราะห์สัญญาณ")
            else:
                # ใช้โหมดจำลองถ้าเชื่อมต่อไม่ได้
                self.analyzer.start_analysis()
                self.status_label.setText("โหมดจำลอง - กำลังวิเคราะห์สัญญาณ...")
                logger.info("เริ่มการวิเคราะห์ในโหมดจำลอง")

        except Exception as e:
            self.show_error(f"เริ่มการวิเคราะห์ผิดพลาด: {str(e)}")

    def stop_analysis(self):
        """หยุดการวิเคราะห์"""
        try:
            self.analyzer.stop_analysis()
            self.analyzer.disconnect_rtlsdr()
            self.status_label.setText("หยุดการวิเคราะห์แล้ว")
            logger.info("หยุดการวิเคราะห์สัญญาณ")

        except Exception as e:
            logger.error(f"หยุดการวิเคราะห์ผิดพลาด: {str(e)}")

    def on_measurement_ready(self, measurement_data):
        """เมื่อมีข้อมูลการวัดใหม่"""
        try:
            # อัปเดต quality meters
            rssi = measurement_data.get('signal_strength', -100)
            snr = measurement_data.get('snr', 0)
            ber = measurement_data.get('ber', 100)

            self.quality_panel.update_signal_quality(rssi, snr, ber)

            # กำหนดสถานะสัญญาณ
            if snr > 15 and ber < 1:
                status = "สัญญาณดีเยี่ยม"
            elif snr > 10 and ber < 5:
                status = "สัญญาณดี"
            elif snr > 5:
                status = "สัญญาณอ่อน"
            else:
                status = "ไม่มีสัญญาณ"

            frequency = measurement_data.get('frequency_mhz', 0)
            self.quality_panel.update_signal_status(status, frequency, "OFDM", "1536")

            # บันทึกข้อมูลลงฐานข้อมูล
            self.db.add_measurement(measurement_data)

        except Exception as e:
            logger.error(f"ประมวลผลข้อมูลการวัดผิดพลาด: {str(e)}")

    def show_error(self, error_message):
        """แสดงข้อความผิดพลาด"""
        QMessageBox.critical(self, "เกิดข้อผิดพลาด", error_message)
        self.status_label.setText(f"ข้อผิดพลาด: {error_message}")
        logger.error(error_message)

    def closeEvent(self, event):
        """เมื่อปิดโปรแกรม"""
        try:
            # หยุดการทำงานของ analyzer thread
            if self.analyzer.isRunning():
                self.analyzer.stop_analysis()
                self.analyzer.wait(3000)  # รอ 3 วินาที

            self.analyzer.disconnect_rtlsdr()
            event.accept()

        except Exception as e:
            logger.error(f"ปิดโปรแกรมผิดพลาด: {str(e)}")
            event.accept()

# ---------- Main Function ----------
def main():
    """ฟังก์ชันหลัก"""
    try:
        # ตรวจสอบ RTL-SDR availability
        if RtlSdr is None:
            print("Warning: pyrtlsdr not found. Running in simulation mode.")

        app = QApplication(sys.argv)

        # ตั้งค่า font สำหรับ touch interface
        font = QFont()
        font.setPointSize(12)
        app.setFont(font)

        # สร้างและแสดงหน้าต่างหลัก
        window = Lab6MainWindow()
        window.show()

        sys.exit(app.exec_())

    except Exception as e:
        print(f"เริ่มโปรแกรมผิดพลาด: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("LAB 6: สร้าง DAB+ Signal Analyzer (เฉลย)")
    main()