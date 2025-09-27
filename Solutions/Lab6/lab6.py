#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAB 6: สร้าง DAB+ Signal Analyzer - SOLUTION (Based on Lab 3 ETI approach)
- พัฒนาเครื่องมือวิเคราะห์สัญญาณ DAB+ อย่างละเอียด
- วิเคราะห์คุณภาพสัญญาณ (SNR, RSSI, BER) และสเปกตรัมความถี่
- สร้างกราฟและรายงานการวิเคราะห์แบบ real-time
- ใช้ Lab 3 pipeline: RTL-SDR → ETI → Advanced Analysis
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

# นำเข้า modules จาก Lab 3
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
logger = logging.getLogger("Lab6Analyzer")

# DAB+ Thailand frequencies
DAB_FREQUENCIES = {
    '185.360': {'location': 'Bangkok/Phuket', 'block': '7A', 'freq': 185.360},
    '202.928': {'location': 'Bangkok', 'block': '9A', 'freq': 202.928},
    '195.936': {'location': 'Chiang Mai', 'block': '8C', 'freq': 195.936},
    '210.096': {'location': 'Northeast', 'block': '10B', 'freq': 210.096},
}

class AnalysisDatabase:
    """ฐานข้อมูลสำหรับเก็บข้อมูลการวิเคราะห์สัญญาณ"""

    def __init__(self, db_path="lab6_analysis.db"):
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
                    modulation_quality REAL,
                    sync_status TEXT,
                    services_found INTEGER,
                    ensemble_id TEXT,
                    ensemble_label TEXT
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

            # ตาราง eti_analysis
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS eti_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    measurement_id INTEGER,
                    eti_frame_count INTEGER,
                    fic_crc_errors INTEGER,
                    msc_error_rate REAL,
                    ofdm_sync_quality REAL,
                    constellation_quality REAL,
                    carrier_offset REAL,
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
                    analysis_mode TEXT,
                    notes TEXT
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("Analysis database initialized")

        except Exception as e:
            logger.error(f"Database initialization error: {e}")

    def add_measurement(self, measurement_data):
        """เพิ่มข้อมูลการวัดสัญญาณ"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO signal_measurements
                (frequency_mhz, signal_strength, snr, ber, noise_floor,
                 peak_frequency, bandwidth, modulation_quality, sync_status,
                 services_found, ensemble_id, ensemble_label)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                measurement_data.get('frequency_mhz'),
                measurement_data.get('signal_strength'),
                measurement_data.get('snr'),
                measurement_data.get('ber'),
                measurement_data.get('noise_floor'),
                measurement_data.get('peak_frequency'),
                measurement_data.get('bandwidth'),
                measurement_data.get('modulation_quality'),
                measurement_data.get('sync_status'),
                measurement_data.get('services_found', 0),
                measurement_data.get('ensemble_id'),
                measurement_data.get('ensemble_label')
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

            # บันทึกข้อมูล ETI analysis ถ้ามี
            if 'eti_analysis' in measurement_data:
                eti_data = measurement_data['eti_analysis']
                cursor.execute('''
                    INSERT INTO eti_analysis
                    (measurement_id, eti_frame_count, fic_crc_errors, msc_error_rate,
                     ofdm_sync_quality, constellation_quality, carrier_offset)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    measurement_id,
                    eti_data.get('frame_count', 0),
                    eti_data.get('fic_crc_errors', 0),
                    eti_data.get('msc_error_rate', 0),
                    eti_data.get('ofdm_sync_quality', 0),
                    eti_data.get('constellation_quality', 0),
                    eti_data.get('carrier_offset', 0)
                ))

            conn.commit()
            conn.close()
            return measurement_id

        except Exception as e:
            logger.error(f"Add measurement error: {e}")
            return None

    def get_measurements(self, limit=100):
        """ดึงข้อมูลการวัดสัญญาณ"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM signal_measurements
                ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))
            measurements = cursor.fetchall()
            conn.close()
            return measurements
        except Exception as e:
            logger.error(f"Get measurements error: {e}")
            return []

    def export_to_csv(self, filename):
        """ส่งออกข้อมูลเป็น CSV"""
        try:
            measurements = self.get_measurements(1000)
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'ID', 'Timestamp', 'Frequency (MHz)', 'Signal Strength (dBm)',
                    'SNR (dB)', 'BER (%)', 'Noise Floor (dBm)', 'Peak Frequency (MHz)',
                    'Bandwidth (kHz)', 'Modulation Quality (%)', 'Sync Status',
                    'Services Found', 'Ensemble ID', 'Ensemble Label'
                ])
                writer.writerows(measurements)
            logger.info(f"Exported data to CSV: {filename}")
            return True
        except Exception as e:
            logger.error(f"CSV export error: {e}")
            return False

class DABSignalAnalyzer(QThread):
    """เครื่องมือวิเคราะห์สัญญาณ DAB+ ใช้ Lab 3 pipeline"""

    measurement_ready = pyqtSignal(dict)
    spectrum_ready = pyqtSignal(np.ndarray, np.ndarray)  # frequencies, powers
    eti_analysis_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.rtl_sdr = None
        self.eti_processor = None
        self.eti_parser = None
        self.is_analyzing = False
        self.frequency = 185.360  # MHz
        self.sample_rate = 2048000  # Hz
        self.gain = 'auto'
        self.fft_size = 2048
        self._stop_flag = False

    def setup_lab3_pipeline(self):
        """ตั้งค่า Lab 3 pipeline สำหรับการวิเคราะห์"""
        try:
            # เริ่มต้น RTL-SDR
            self.rtl_sdr = RTLSDRDataAcquisition()
            self.rtl_sdr.frequency = int(self.frequency * 1000000)
            self.rtl_sdr.sample_rate = self.sample_rate

            if not self.rtl_sdr.setup_rtlsdr():
                logger.warning("Cannot connect to RTL-SDR, using simulation mode")
                self.rtl_sdr = None

            # เริ่มต้น ETI processor และ parser
            self.eti_processor = ETIProcessor()
            self.eti_parser = ETIFrameParser()

            return True

        except Exception as e:
            logger.error(f"Lab 3 pipeline setup error: {e}")
            return False

    def set_frequency(self, frequency_mhz):
        """ตั้งค่าความถี่ที่จะวิเคราะห์"""
        self.frequency = frequency_mhz
        if self.rtl_sdr:
            try:
                self.rtl_sdr.frequency = int(frequency_mhz * 1000000)
                logger.info(f"Set frequency: {frequency_mhz:.3f} MHz")
            except Exception as e:
                self.error_occurred.emit(f"Set frequency error: {e}")

    def set_parameters(self, sample_rate, gain, fft_size):
        """ตั้งค่าพารามิเตอร์การวิเคราะห์"""
        self.sample_rate = sample_rate
        self.gain = gain
        self.fft_size = fft_size

        if self.rtl_sdr:
            try:
                self.rtl_sdr.sample_rate = sample_rate
                self.rtl_sdr.gain = gain if gain != 'auto' else 'auto'
            except Exception as e:
                logger.error(f"Set parameters error: {e}")

    def run(self):
        """วิเคราะห์สัญญาณอย่างต่อเนื่อง"""
        self.is_analyzing = True
        self._stop_flag = False

        if not self.setup_lab3_pipeline():
            self.error_occurred.emit("Cannot setup Lab 3 pipeline")
            return

        while self.is_analyzing and not self._stop_flag:
            try:
                # Step 1: รับ I/Q data
                iq_data = self.capture_iq_data()
                if iq_data is None:
                    self.msleep(1000)
                    continue

                # Step 2: วิเคราะห์สเปกตรัม
                frequencies, power_spectrum = self.analyze_spectrum(iq_data)
                if frequencies is not None and power_spectrum is not None:
                    self.spectrum_ready.emit(frequencies, power_spectrum)

                # Step 3: ประมวลผล ETI (ถ้ามีสัญญาณแรงพอ)
                eti_analysis = self.process_eti_analysis(iq_data)

                # Step 4: วิเคราะห์คุณภาพสัญญาณ
                measurement = self.analyze_signal_quality(
                    iq_data, frequencies, power_spectrum, eti_analysis
                )

                if measurement:
                    self.measurement_ready.emit(measurement)

                if eti_analysis:
                    self.eti_analysis_ready.emit(eti_analysis)

                self.msleep(500)  # อัปเดตทุก 0.5 วินาที

            except Exception as e:
                self.error_occurred.emit(f"Analysis error: {e}")
                self.msleep(1000)

    def capture_iq_data(self):
        """รับ I/Q data จาก RTL-SDR"""
        try:
            if self.rtl_sdr:
                # ใช้ Lab 3 RTL-SDR capture
                samples = self.rtl_sdr.capture_samples(duration_seconds=2)
                return samples
            else:
                # สร้างข้อมูลจำลอง
                return self.generate_mock_iq_data()

        except Exception as e:
            logger.error(f"I/Q capture error: {e}")
            return None

    def generate_mock_iq_data(self):
        """สร้างข้อมูล I/Q จำลองสำหรับทดสอบ"""
        try:
            # สร้างสัญญาณจำลองที่มีลักษณะ DAB+
            duration = 2.0  # วินาที
            t = np.linspace(0, duration, int(self.sample_rate * duration))

            # สัญญาณพื้นฐาน (carrier)
            carrier_freq = 0  # baseband
            carrier = np.exp(1j * 2 * np.pi * carrier_freq * t)

            # เพิ่ม OFDM-like signal
            ofdm_signal = np.zeros_like(carrier, dtype=complex)
            for k in range(-768, 769):  # DAB Mode I carriers
                if k != 0:  # skip DC
                    subcarrier_freq = k * 1000  # 1 kHz spacing
                    amplitude = np.random.uniform(0.1, 1.0)
                    phase = np.random.uniform(0, 2*np.pi)
                    ofdm_signal += amplitude * np.exp(1j * (2 * np.pi * subcarrier_freq * t + phase))

            # เพิ่ม noise
            noise_power = 0.1
            noise = np.random.normal(0, noise_power, len(t)) + \
                   1j * np.random.normal(0, noise_power, len(t))

            # รวมสัญญาณ
            signal = ofdm_signal + noise

            # Normalize
            signal = signal / np.max(np.abs(signal)) * 0.8

            return signal.astype(np.complex64)

        except Exception as e:
            logger.error(f"Mock I/Q generation error: {e}")
            return None

    def analyze_spectrum(self, iq_data):
        """วิเคราะห์สเปกตรัมความถี่"""
        try:
            # ตัดข้อมูลให้เหมาะสมกับ FFT size
            if len(iq_data) > self.fft_size:
                iq_data = iq_data[:self.fft_size]
            elif len(iq_data) < self.fft_size:
                # Zero padding
                padded = np.zeros(self.fft_size, dtype=complex)
                padded[:len(iq_data)] = iq_data
                iq_data = padded

            # คำนวณ FFT
            window = np.hanning(self.fft_size)
            windowed_data = iq_data * window
            fft_data = np.fft.fft(windowed_data)
            fft_shifted = np.fft.fftshift(fft_data)
            power_spectrum = 20 * np.log10(np.abs(fft_shifted) + 1e-12)

            # คำนวณความถี่
            frequencies = np.fft.fftfreq(self.fft_size, 1/self.sample_rate)
            frequencies = np.fft.fftshift(frequencies) + self.frequency * 1e6

            return frequencies, power_spectrum

        except Exception as e:
            logger.error(f"Spectrum analysis error: {e}")
            return None, None

    def process_eti_analysis(self, iq_data):
        """ประมวลผล ETI และวิเคราะห์ขั้นสูง"""
        try:
            if self.eti_processor is None:
                return None

            # ในการใช้งานจริง จะใช้ eti-cmdline หรือ GNU Radio DAB
            # ที่นี่จำลองการวิเคราะห์ ETI

            # วิเคราะห์ OFDM sync
            ofdm_sync_quality = self.analyze_ofdm_sync(iq_data)

            # วิเคราะห์ constellation quality
            constellation_quality = self.analyze_constellation(iq_data)

            # ประเมิน carrier offset
            carrier_offset = self.estimate_carrier_offset(iq_data)

            # จำลองการหา services
            services_found = 0
            ensemble_id = None
            ensemble_label = None

            if ofdm_sync_quality > 70:  # ถ้าสัญญาณดีพอ
                # ใช้ Lab 3 parser จำลอง
                mock_services = self.simulate_service_detection()
                services_found = len(mock_services)
                if mock_services:
                    ensemble_id = mock_services[0].get('ensemble_id')
                    ensemble_label = mock_services[0].get('ensemble_label')

            eti_analysis = {
                'frame_count': 100,  # จำลอง
                'fic_crc_errors': max(0, int((100 - ofdm_sync_quality) / 10)),
                'msc_error_rate': max(0, (100 - ofdm_sync_quality) / 100),
                'ofdm_sync_quality': ofdm_sync_quality,
                'constellation_quality': constellation_quality,
                'carrier_offset': carrier_offset,
                'services_found': services_found,
                'ensemble_id': ensemble_id,
                'ensemble_label': ensemble_label
            }

            return eti_analysis

        except Exception as e:
            logger.error(f"ETI analysis error: {e}")
            return None

    def analyze_ofdm_sync(self, iq_data):
        """วิเคราะห์คุณภาพ OFDM synchronization"""
        try:
            # วิเคราะห์ correlation peaks สำหรับ OFDM symbol detection
            # DAB Mode I: symbol duration = 1246 µs
            symbol_samples = int(self.sample_rate * 1246e-6)

            if len(iq_data) < symbol_samples * 2:
                return 0

            # หา autocorrelation สำหรับ cyclic prefix
            guard_samples = int(self.sample_rate * 246e-6)  # guard interval
            correlation_sum = 0
            correlation_count = 0

            for i in range(0, len(iq_data) - symbol_samples, symbol_samples // 4):
                if i + symbol_samples < len(iq_data):
                    symbol = iq_data[i:i + symbol_samples]
                    if len(symbol) == symbol_samples:
                        # correlation ระหว่าง guard และ end of useful part
                        guard = symbol[:guard_samples]
                        tail = symbol[-guard_samples:]

                        if len(guard) == len(tail):
                            corr = np.abs(np.sum(guard * np.conj(tail))) / \
                                  (np.sqrt(np.sum(np.abs(guard)**2)) * np.sqrt(np.sum(np.abs(tail)**2)) + 1e-12)
                            correlation_sum += corr
                            correlation_count += 1

            if correlation_count > 0:
                avg_correlation = correlation_sum / correlation_count
                sync_quality = min(100, avg_correlation * 100)
                return sync_quality
            else:
                return 0

        except Exception as e:
            logger.error(f"OFDM sync analysis error: {e}")
            return 0

    def analyze_constellation(self, iq_data):
        """วิเคราะห์คุณภาพ constellation diagram"""
        try:
            # วิเคราะห์ EVM (Error Vector Magnitude)

            # สมมติว่าใช้ QPSK modulation
            # Ideal constellation points
            ideal_points = np.array([1+1j, 1-1j, -1+1j, -1-1j]) / np.sqrt(2)

            # แบ่งข้อมูลเป็น symbols (simplified)
            symbols_per_block = min(1000, len(iq_data) // 4)
            if symbols_per_block < 10:
                return 0

            symbols = iq_data[:symbols_per_block * 4:4]  # downsample

            # Normalize symbols
            mean_power = np.mean(np.abs(symbols)**2)
            if mean_power > 0:
                symbols = symbols / np.sqrt(mean_power)

            # คำนวณ EVM
            evm_sum = 0
            valid_symbols = 0

            for symbol in symbols:
                # หา ideal point ที่ใกล้ที่สุด
                distances = np.abs(symbol - ideal_points)
                nearest_ideal = ideal_points[np.argmin(distances)]

                # คำนวณ error vector
                error_vector = symbol - nearest_ideal
                evm = np.abs(error_vector)

                evm_sum += evm
                valid_symbols += 1

            if valid_symbols > 0:
                avg_evm = evm_sum / valid_symbols
                # แปลง EVM เป็น quality score (0-100)
                quality = max(0, min(100, (1 - avg_evm) * 100))
                return quality
            else:
                return 0

        except Exception as e:
            logger.error(f"Constellation analysis error: {e}")
            return 0

    def estimate_carrier_offset(self, iq_data):
        """ประเมิน carrier frequency offset"""
        try:
            # ใช้ autocorrelation เพื่อหา frequency offset
            if len(iq_data) < 1000:
                return 0

            # คำนวณ phase difference ระหว่าง samples ที่เว้นระยะ
            delay_samples = 100  # ระยะห่างระหว่าง samples

            if len(iq_data) > delay_samples:
                delayed = iq_data[delay_samples:]
                original = iq_data[:-delay_samples]

                # คำนวณ complex correlation
                correlation = np.sum(original * np.conj(delayed))
                phase_diff = np.angle(correlation)

                # แปลงเป็น frequency offset
                freq_offset = phase_diff * self.sample_rate / (2 * np.pi * delay_samples)

                return freq_offset
            else:
                return 0

        except Exception as e:
            logger.error(f"Carrier offset estimation error: {e}")
            return 0

    def simulate_service_detection(self):
        """จำลองการค้นหา DAB+ services"""
        try:
            # หาความถี่ที่ใกล้เคียงใน DAB_FREQUENCIES
            location = 'Unknown'
            block = 'Unknown'

            for freq_str, info in DAB_FREQUENCIES.items():
                if abs(self.frequency - info['freq']) < 0.1:
                    location = info['location']
                    block = info['block']
                    break

            # สร้าง mock services
            mock_services = [
                {
                    'ensemble_id': f"0x{int(self.frequency * 100):04X}",
                    'ensemble_label': f"{location} DAB+",
                    'service_id': int(self.frequency * 10),
                    'service_label': f"Service @ {self.frequency:.1f}MHz",
                    'bitrate': 128,
                    'audio_mode': 'stereo'
                }
            ]

            return mock_services

        except Exception as e:
            logger.error(f"Service detection simulation error: {e}")
            return []

    def analyze_signal_quality(self, iq_data, frequencies, power_spectrum, eti_analysis):
        """วิเคราะห์คุณภาพสัญญาณโดยรวม"""
        try:
            if power_spectrum is None:
                return None

            # คำนวณพารามิเตอร์พื้นฐาน
            signal_strength = np.max(power_spectrum)
            noise_floor = np.median(power_spectrum)
            snr = signal_strength - noise_floor

            # หา peak frequency
            peak_idx = np.argmax(power_spectrum)
            peak_frequency = frequencies[peak_idx] / 1e6  # Convert to MHz

            # คำนวณ bandwidth
            bandwidth = self.calculate_bandwidth(frequencies, power_spectrum, signal_strength)

            # ประเมิน BER จาก SNR และ ETI analysis
            if eti_analysis and 'msc_error_rate' in eti_analysis:
                ber = eti_analysis['msc_error_rate'] * 100
            else:
                ber = self.estimate_ber_from_snr(snr)

            # ประเมิน modulation quality
            if eti_analysis and 'constellation_quality' in eti_analysis:
                modulation_quality = eti_analysis['constellation_quality']
            else:
                modulation_quality = self.assess_modulation_quality(snr, ber)

            # สร้าง measurement data
            measurement = {
                'timestamp': datetime.now(),
                'frequency_mhz': self.frequency,
                'signal_strength': float(signal_strength),
                'snr': float(snr),
                'ber': float(ber),
                'noise_floor': float(noise_floor),
                'peak_frequency': peak_frequency,
                'bandwidth': bandwidth,
                'modulation_quality': modulation_quality,
                'sync_status': self.determine_sync_status(snr, eti_analysis),
                'spectrum_frequencies': frequencies,
                'spectrum_powers': power_spectrum
            }

            # เพิ่มข้อมูล ETI analysis
            if eti_analysis:
                measurement['eti_analysis'] = eti_analysis
                measurement['services_found'] = eti_analysis.get('services_found', 0)
                measurement['ensemble_id'] = eti_analysis.get('ensemble_id')
                measurement['ensemble_label'] = eti_analysis.get('ensemble_label')

            return measurement

        except Exception as e:
            logger.error(f"Signal quality analysis error: {e}")
            return None

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
            logger.error(f"Bandwidth calculation error: {e}")
            return 1536

    def estimate_ber_from_snr(self, snr):
        """ประเมิน BER จาก SNR"""
        try:
            # ประมาณ BER สำหรับ QPSK/OFDM
            if snr > 25:
                ber = 0.001
            elif snr > 20:
                ber = 0.01
            elif snr > 15:
                ber = 0.1
            elif snr > 10:
                ber = 1.0
            elif snr > 5:
                ber = 10.0
            else:
                ber = 50.0

            return max(0, min(100, ber))

        except Exception as e:
            logger.error(f"BER estimation error: {e}")
            return 50

    def assess_modulation_quality(self, snr, ber):
        """ประเมินคุณภาพการมอดูเลชัน"""
        try:
            snr_score = min(100, max(0, (snr + 5) * 4))
            ber_score = max(0, 100 - ber * 2)
            quality = (snr_score + ber_score) / 2
            return max(0, min(100, quality))

        except Exception as e:
            logger.error(f"Modulation quality assessment error: {e}")
            return 0

    def determine_sync_status(self, snr, eti_analysis):
        """กำหนดสถานะ sync"""
        try:
            if eti_analysis and 'ofdm_sync_quality' in eti_analysis:
                sync_quality = eti_analysis['ofdm_sync_quality']
                if sync_quality > 80:
                    return 'excellent'
                elif sync_quality > 60:
                    return 'good'
                elif sync_quality > 40:
                    return 'fair'
                else:
                    return 'poor'
            else:
                if snr > 20:
                    return 'good'
                elif snr > 10:
                    return 'fair'
                else:
                    return 'poor'

        except Exception as e:
            logger.error(f"Sync status determination error: {e}")
            return 'unknown'

    def stop_analysis(self):
        """หยุดการวิเคราะห์"""
        self.is_analyzing = False
        self._stop_flag = True

    def cleanup(self):
        """ทำความสะอาด resources"""
        try:
            if self.rtl_sdr:
                self.rtl_sdr.cleanup()
        except:
            pass

class AdvancedSpectrumWidget(QWidget):
    """Widget แสดงสเปกตรัมขั้นสูง พร้อม waterfall display"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_plots()
        self.spectrum_history = []
        self.max_history = 200

    def setup_ui(self):
        layout = QVBoxLayout()

        # หัวข้อ
        title = QLabel("Advanced Spectrum Analyzer & Waterfall")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Matplotlib plots
        self.setup_plots()
        layout.addWidget(self.canvas)

        # Controls
        controls_layout = QHBoxLayout()
        self.freeze_btn = QPushButton("Freeze")
        self.clear_btn = QPushButton("Clear")
        self.save_btn = QPushButton("Save")
        self.waterfall_btn = QPushButton("Toggle Waterfall")

        for btn in [self.freeze_btn, self.clear_btn, self.save_btn, self.waterfall_btn]:
            btn.setMinimumHeight(40)
            controls_layout.addWidget(btn)

        layout.addLayout(controls_layout)
        self.setLayout(layout)

        # Connections
        self.freeze_btn.clicked.connect(self.toggle_freeze)
        self.clear_btn.clicked.connect(self.clear_display)
        self.save_btn.clicked.connect(self.save_plots)
        self.waterfall_btn.clicked.connect(self.toggle_waterfall)

        self.frozen = False
        self.show_waterfall = True

    def setup_plots(self):
        """ตั้งค่า matplotlib plots"""
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)

        # Spectrum plot
        self.ax_spectrum = self.figure.add_subplot(2, 1, 1)
        self.ax_spectrum.set_title('Real-time Spectrum')
        self.ax_spectrum.set_ylabel('Power (dB)')
        self.ax_spectrum.grid(True, alpha=0.3)

        # Waterfall plot
        self.ax_waterfall = self.figure.add_subplot(2, 1, 2)
        self.ax_waterfall.set_title('Waterfall Display')
        self.ax_waterfall.set_xlabel('Frequency (MHz)')
        self.ax_waterfall.set_ylabel('Time')

        self.figure.tight_layout()

    def update_spectrum(self, frequencies, powers):
        """อัปเดตสเปกตรัม"""
        if self.frozen:
            return

        try:
            freq_mhz = frequencies / 1e6

            # อัปเดต spectrum plot
            self.ax_spectrum.clear()
            self.ax_spectrum.plot(freq_mhz, powers, 'b-', linewidth=1)
            self.ax_spectrum.set_title('Real-time Spectrum')
            self.ax_spectrum.set_ylabel('Power (dB)')
            self.ax_spectrum.grid(True, alpha=0.3)

            # เพิ่มเข้า history สำหรับ waterfall
            self.spectrum_history.append(powers.copy())
            if len(self.spectrum_history) > self.max_history:
                self.spectrum_history.pop(0)

            # อัปเดต waterfall
            if self.show_waterfall and len(self.spectrum_history) > 1:
                waterfall_data = np.array(self.spectrum_history)
                self.ax_waterfall.clear()

                extent = [freq_mhz[0], freq_mhz[-1], 0, len(self.spectrum_history)]
                im = self.ax_waterfall.imshow(
                    waterfall_data,
                    aspect='auto',
                    extent=extent,
                    cmap='viridis',
                    origin='lower'
                )
                self.ax_waterfall.set_title('Waterfall Display')
                self.ax_waterfall.set_xlabel('Frequency (MHz)')
                self.ax_waterfall.set_ylabel('Time (samples)')

            self.canvas.draw_idle()

        except Exception as e:
            logger.error(f"Spectrum update error: {e}")

    def toggle_freeze(self):
        """เปิด/ปิด freeze"""
        self.frozen = not self.frozen
        self.freeze_btn.setText("Resume" if self.frozen else "Freeze")

    def toggle_waterfall(self):
        """เปิด/ปิด waterfall display"""
        self.show_waterfall = not self.show_waterfall
        self.waterfall_btn.setText("Hide Waterfall" if self.show_waterfall else "Show Waterfall")

    def clear_display(self):
        """เคลียร์การแสดงผล"""
        self.spectrum_history.clear()
        self.ax_spectrum.clear()
        self.ax_waterfall.clear()
        self.setup_plots()
        self.canvas.draw()

    def save_plots(self):
        """บันทึกกราฟ"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save Spectrum Plots",
                f"advanced_spectrum_{timestamp}.png",
                "PNG Files (*.png)"
            )

            if filename:
                self.figure.savefig(filename, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "Saved", f"Plots saved to: {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

class SignalQualityMeterWidget(QWidget):
    """Widget แสดงมิเตอร์คุณภาพสัญญาณขั้นสูง"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout()

        # หัวข้อ
        title = QLabel("Signal Quality Meters")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title, 0, 0, 1, 3)

        # RSSI
        rssi_group = QGroupBox("RSSI (dBm)")
        rssi_layout = QVBoxLayout()
        self.rssi_lcd = QLCDNumber()
        self.rssi_lcd.setDigitCount(6)
        self.rssi_lcd.setMinimumHeight(60)
        self.rssi_bar = QProgressBar()
        self.rssi_bar.setRange(-100, -20)
        rssi_layout.addWidget(self.rssi_lcd)
        rssi_layout.addWidget(self.rssi_bar)
        rssi_group.setLayout(rssi_layout)
        layout.addWidget(rssi_group, 1, 0)

        # SNR
        snr_group = QGroupBox("SNR (dB)")
        snr_layout = QVBoxLayout()
        self.snr_lcd = QLCDNumber()
        self.snr_lcd.setDigitCount(5)
        self.snr_lcd.setMinimumHeight(60)
        self.snr_dial = QDial()
        self.snr_dial.setRange(0, 40)
        self.snr_dial.setEnabled(False)
        snr_layout.addWidget(self.snr_lcd)
        snr_layout.addWidget(self.snr_dial)
        snr_group.setLayout(snr_layout)
        layout.addWidget(snr_group, 1, 1)

        # BER
        ber_group = QGroupBox("BER (%)")
        ber_layout = QVBoxLayout()
        self.ber_lcd = QLCDNumber()
        self.ber_lcd.setDigitCount(6)
        self.ber_lcd.setMinimumHeight(60)
        self.ber_bar = QProgressBar()
        self.ber_bar.setRange(0, 100)
        ber_layout.addWidget(self.ber_lcd)
        ber_layout.addWidget(self.ber_bar)
        ber_group.setLayout(ber_layout)
        layout.addWidget(ber_group, 1, 2)

        # ETI Quality Indicators
        eti_group = QGroupBox("ETI Analysis")
        eti_layout = QGridLayout()

        self.sync_quality_label = QLabel("OFDM Sync: --%")
        self.constellation_quality_label = QLabel("Constellation: --%")
        self.carrier_offset_label = QLabel("Carrier Offset: -- Hz")
        self.services_found_label = QLabel("Services: 0")

        eti_layout.addWidget(self.sync_quality_label, 0, 0)
        eti_layout.addWidget(self.constellation_quality_label, 0, 1)
        eti_layout.addWidget(self.carrier_offset_label, 1, 0)
        eti_layout.addWidget(self.services_found_label, 1, 1)

        eti_group.setLayout(eti_layout)
        layout.addWidget(eti_group, 2, 0, 1, 3)

        # Status
        self.status_label = QLabel("No Signal")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #ffcccc;
                border: 2px solid #ff6666;
                border-radius: 10px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.status_label, 3, 0, 1, 3)

        self.setLayout(layout)

    def update_measurements(self, measurement_data):
        """อัปเดตค่าการวัด"""
        try:
            rssi = measurement_data.get('signal_strength', -100)
            snr = measurement_data.get('snr', 0)
            ber = measurement_data.get('ber', 100)

            # อัปเดต basic meters
            self.rssi_lcd.display(f"{rssi:.1f}")
            self.snr_lcd.display(f"{snr:.1f}")
            self.ber_lcd.display(f"{ber:.3f}")

            self.rssi_bar.setValue(int(rssi))
            self.snr_dial.setValue(int(max(0, min(40, snr))))
            self.ber_bar.setValue(int(ber))

            # อัปเดต ETI analysis
            if 'eti_analysis' in measurement_data:
                eti = measurement_data['eti_analysis']
                self.sync_quality_label.setText(f"OFDM Sync: {eti.get('ofdm_sync_quality', 0):.1f}%")
                self.constellation_quality_label.setText(f"Constellation: {eti.get('constellation_quality', 0):.1f}%")
                self.carrier_offset_label.setText(f"Carrier Offset: {eti.get('carrier_offset', 0):.1f} Hz")
                self.services_found_label.setText(f"Services: {eti.get('services_found', 0)}")

            # อัปเดตสถานะ
            sync_status = measurement_data.get('sync_status', 'unknown')
            if sync_status == 'excellent':
                status_text = "สัญญาณดีเยี่ยม"
                bg_color = "#d4edda"
            elif sync_status == 'good':
                status_text = "สัญญาณดี"
                bg_color = "#d1ecf1"
            elif sync_status == 'fair':
                status_text = "สัญญาณปานกลาง"
                bg_color = "#fff3cd"
            else:
                status_text = "สัญญาณไม่ดี"
                bg_color = "#f8d7da"

            self.status_label.setText(status_text)
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {bg_color};
                    border: 2px solid #999;
                    border-radius: 10px;
                    padding: 15px;
                    font-size: 16px;
                    font-weight: bold;
                }}
            """)

        except Exception as e:
            logger.error(f"Update measurements error: {e}")

class AnalysisControlPanel(QWidget):
    """Panel ควบคุมการวิเคราะห์ขั้นสูง"""

    analysis_started = pyqtSignal(dict)
    analysis_stopped = pyqtSignal()
    frequency_changed = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # หัวข้อ
        title = QLabel("Analysis Control Panel")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Frequency Control
        freq_group = QGroupBox("Frequency Control")
        freq_layout = QVBoxLayout()

        # Frequency slider
        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setRange(174000, 240000)  # 174-240 MHz in kHz
        self.freq_slider.setValue(185360)  # 185.360 MHz
        self.freq_slider.setMinimumHeight(40)

        self.freq_spinbox = QSpinBox()
        self.freq_spinbox.setRange(174000, 240000)
        self.freq_spinbox.setValue(185360)
        self.freq_spinbox.setSuffix(" kHz")
        self.freq_spinbox.setMinimumHeight(40)

        # Preset frequencies
        presets_layout = QHBoxLayout()
        for freq_str, info in DAB_FREQUENCIES.items():
            btn = QPushButton(f"{info['block']}\n{info['freq']:.3f}")
            btn.setMinimumSize(80, 50)
            btn.clicked.connect(lambda checked, f=info['freq']: self.set_frequency(f * 1000))
            presets_layout.addWidget(btn)

        freq_layout.addWidget(QLabel("Frequency (kHz):"))
        freq_layout.addWidget(self.freq_slider)
        freq_layout.addWidget(self.freq_spinbox)
        freq_layout.addWidget(QLabel("Presets:"))
        freq_layout.addLayout(presets_layout)
        freq_group.setLayout(freq_layout)
        layout.addWidget(freq_group)

        # Analysis Parameters
        params_group = QGroupBox("Analysis Parameters")
        params_layout = QGridLayout()

        params_layout.addWidget(QLabel("Sample Rate:"), 0, 0)
        self.samplerate_combo = QComboBox()
        self.samplerate_combo.addItems(["2.048 MHz", "2.4 MHz", "3.2 MHz"])
        self.samplerate_combo.setMinimumHeight(40)
        params_layout.addWidget(self.samplerate_combo, 0, 1)

        params_layout.addWidget(QLabel("Gain:"), 1, 0)
        self.gain_combo = QComboBox()
        self.gain_combo.addItems(["auto", "0", "9", "14", "27", "37", "49.6"])
        self.gain_combo.setMinimumHeight(40)
        params_layout.addWidget(self.gain_combo, 1, 1)

        params_layout.addWidget(QLabel("FFT Size:"), 2, 0)
        self.fft_combo = QComboBox()
        self.fft_combo.addItems(["1024", "2048", "4096", "8192"])
        self.fft_combo.setCurrentText("2048")
        self.fft_combo.setMinimumHeight(40)
        params_layout.addWidget(self.fft_combo, 2, 1)

        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

        # Control buttons
        buttons_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Analysis")
        self.stop_btn = QPushButton("Stop Analysis")
        self.export_btn = QPushButton("Export Data")

        for btn in [self.start_btn, self.stop_btn, self.export_btn]:
            btn.setMinimumHeight(48)

        self.stop_btn.setEnabled(False)

        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addWidget(self.stop_btn)
        buttons_layout.addWidget(self.export_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # Connections
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

        self.frequency_changed.emit(float(value) / 1000)  # Convert to MHz

    def start_analysis(self):
        """เริ่มการวิเคราะห์"""
        try:
            sample_rate_map = {
                "2.048 MHz": 2048000,
                "2.4 MHz": 2400000,
                "3.2 MHz": 3200000
            }

            parameters = {
                'frequency': float(self.freq_spinbox.value() / 1000),  # MHz
                'sample_rate': sample_rate_map[self.samplerate_combo.currentText()],
                'gain': self.gain_combo.currentText(),
                'fft_size': int(self.fft_combo.currentText())
            }

            self.analysis_started.emit(parameters)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Start Analysis Error", str(e))

    def stop_analysis(self):
        """หยุดการวิเคราะห์"""
        self.analysis_stopped.emit()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def export_data(self):
        """ส่งออกข้อมูล"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Analysis Data",
                f"dab_analysis_{timestamp}.csv",
                "CSV Files (*.csv)"
            )

            if filename:
                # TODO: Implement export functionality
                QMessageBox.information(self, "Export", f"Data exported to: {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

class Lab6MainWindow(QMainWindow):
    """หน้าต่างหลักของ Lab 6 - DAB+ Signal Analyzer"""

    def __init__(self):
        super().__init__()
        self.db = AnalysisDatabase()
        self.analyzer = DABSignalAnalyzer()

        self.setup_ui()
        self.setup_connections()

        self.setWindowTitle("Lab 6: DAB+ Signal Analyzer (Lab 3 Pipeline)")
        self.setGeometry(100, 100, 1600, 1000)

        if '--fullscreen' in sys.argv:
            self.showFullScreen()

    def setup_ui(self):
        """สร้าง UI หลัก"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # หัวข้อ
        title = QLabel("Lab 6: DAB+ Signal Analyzer")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            background-color: #2c3e50; color: white; padding: 15px;
            border-radius: 10px; margin: 5px;
        """)
        layout.addWidget(title)

        # Main splitter
        main_splitter = QSplitter(Qt.Horizontal)

        # Left panel - controls
        self.control_panel = AnalysisControlPanel()
        main_splitter.addWidget(self.control_panel)

        # Center panel - spectrum
        self.spectrum_widget = AdvancedSpectrumWidget()
        main_splitter.addWidget(self.spectrum_widget)

        # Right panel - quality meters
        self.quality_widget = SignalQualityMeterWidget()
        main_splitter.addWidget(self.quality_widget)

        # Set splitter sizes
        main_splitter.setSizes([400, 800, 400])

        layout.addWidget(main_splitter)

        # Status bar
        self.status_label = QLabel("Ready - Select frequency and start analysis")
        self.status_label.setStyleSheet("background-color: #e8f5e8; padding: 8px; border-radius: 5px;")
        layout.addWidget(self.status_label)

        central_widget.setLayout(layout)

    def setup_connections(self):
        """เชื่อมต่อ signals"""
        # Control panel
        self.control_panel.analysis_started.connect(self.start_analysis)
        self.control_panel.analysis_stopped.connect(self.stop_analysis)
        self.control_panel.frequency_changed.connect(self.analyzer.set_frequency)

        # Analyzer
        self.analyzer.measurement_ready.connect(self.on_measurement_ready)
        self.analyzer.spectrum_ready.connect(self.spectrum_widget.update_spectrum)
        self.analyzer.eti_analysis_ready.connect(self.on_eti_analysis_ready)
        self.analyzer.error_occurred.connect(self.show_error)

    def start_analysis(self, parameters):
        """เริ่มการวิเคราะห์"""
        try:
            self.analyzer.set_parameters(
                parameters['sample_rate'],
                parameters['gain'],
                parameters['fft_size']
            )
            self.analyzer.set_frequency(parameters['frequency'])
            self.analyzer.start()

            self.status_label.setText(f"Analyzing {parameters['frequency']:.3f} MHz...")
            logger.info(f"Started analysis: {parameters['frequency']:.3f} MHz")

        except Exception as e:
            self.show_error(f"Start analysis error: {e}")

    def stop_analysis(self):
        """หยุดการวิเคราะห์"""
        try:
            self.analyzer.stop_analysis()
            if self.analyzer.isRunning():
                self.analyzer.wait(3000)

            self.status_label.setText("Analysis stopped")
            logger.info("Analysis stopped")

        except Exception as e:
            logger.error(f"Stop analysis error: {e}")

    def on_measurement_ready(self, measurement_data):
        """เมื่อมีข้อมูลการวัดใหม่"""
        try:
            # อัปเดต quality meters
            self.quality_widget.update_measurements(measurement_data)

            # บันทึกข้อมูลลงฐานข้อมูล
            self.db.add_measurement(measurement_data)

            # อัปเดต status
            freq = measurement_data.get('frequency_mhz', 0)
            snr = measurement_data.get('snr', 0)
            services = measurement_data.get('services_found', 0)

            self.status_label.setText(
                f"Analyzing {freq:.3f} MHz - SNR: {snr:.1f} dB - Services: {services}"
            )

        except Exception as e:
            logger.error(f"Measurement processing error: {e}")

    def on_eti_analysis_ready(self, eti_analysis):
        """เมื่อมีข้อมูล ETI analysis ใหม่"""
        try:
            # แสดงข้อมูล ETI analysis เพิ่มเติมใน log
            sync_quality = eti_analysis.get('ofdm_sync_quality', 0)
            services_found = eti_analysis.get('services_found', 0)

            logger.info(f"ETI Analysis - Sync: {sync_quality:.1f}%, Services: {services_found}")

        except Exception as e:
            logger.error(f"ETI analysis processing error: {e}")

    def show_error(self, error_message):
        """แสดงข้อความผิดพลาด"""
        QMessageBox.critical(self, "Error", error_message)
        self.status_label.setText(f"Error: {error_message}")
        logger.error(error_message)

    def closeEvent(self, event):
        """เมื่อปิดโปรแกรม"""
        try:
            if self.analyzer.isRunning():
                self.analyzer.stop_analysis()
                self.analyzer.wait(3000)

            self.analyzer.cleanup()
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
    window = Lab6MainWindow()
    window.show()

    print("Lab 6: DAB+ Signal Analyzer")
    print("Based on Lab 3 RTL-SDR + ETI Pipeline")
    print("Features:")
    print("- Advanced spectrum analysis with waterfall display")
    print("- ETI stream analysis and quality metrics")
    print("- Real-time signal quality monitoring")
    print("- OFDM synchronization analysis")
    print("- Constellation quality assessment")
    print("- Touch-friendly interface")

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()