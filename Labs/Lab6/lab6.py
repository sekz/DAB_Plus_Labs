#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAB 6: สร้าง DAB+ Signal Analyzer (โจทย์ - ใช้ Lab 3 ETI approach)
- พัฒนาเครื่องมือวิเคราะห์สัญญาณ DAB+ อย่างละเอียด ด้วย RTL-SDR + ETI processing
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
        # TODO: สร้างตาราง signal_measurements และ spectrum_data
        # TODO: สร้างตาราง eti_analysis สำหรับข้อมูล ETI
        pass

    def add_measurement(self, measurement_data):
        """เพิ่มข้อมูลการวัดสัญญาณ"""
        # TODO: เพิ่มข้อมูลลง SQLite และ return measurement_id
        pass

    def export_to_csv(self, filename):
        """ส่งออกข้อมูลเป็น CSV"""
        # TODO: ส่งออกข้อมูลการวัดเป็น CSV
        pass

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
        # TODO: เริ่มต้น RTLSDRDataAcquisition, ETIProcessor, ETIFrameParser
        # TODO: return True หากสำเร็จ
        return True

    def run(self):
        """วิเคราะห์สัญญาณอย่างต่อเนื่อง"""
        self.is_analyzing = True
        self._stop_flag = False

        if not self.setup_lab3_pipeline():
            self.error_occurred.emit("Cannot setup Lab 3 pipeline")
            return

        while self.is_analyzing and not self._stop_flag:
            try:
                # TODO: ใช้ Lab 3 pipeline วิเคราะห์และส่ง signals
                self.msleep(500)  # อัปเดตทุก 0.5 วินาที
            except Exception as e:
                self.error_occurred.emit(f"Analysis error: {e}")
                self.msleep(1000)

    def capture_iq_data(self):
        """รับ I/Q data จาก RTL-SDR"""
        # TODO: ใช้ Lab 3 RTL-SDR capture หรือ mock data
        return self.generate_mock_iq_data()

    def generate_mock_iq_data(self):
        """สร้างข้อมูล I/Q จำลองสำหรับทดสอบ"""
        # TODO: สร้างสัญญาณ complex OFDM-like จำลอง
        duration = 2.0
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        carrier = np.exp(1j * 2 * np.pi * 0 * t)
        noise = np.random.normal(0, 0.1, len(t)) + 1j * np.random.normal(0, 0.1, len(t))
        return (carrier + noise).astype(np.complex64)

    def analyze_spectrum(self, iq_data):
        """วิเคราะห์สเปกตรัมความถี่"""
        # TODO: คำนวณ FFT และ power spectrum
        window = np.hanning(len(iq_data))
        fft_data = np.fft.fft(iq_data * window)
        power_spectrum = 20 * np.log10(np.abs(fft_data) + 1e-12)
        frequencies = np.fft.fftfreq(len(iq_data), 1/self.sample_rate) + self.frequency * 1e6
        return frequencies, power_spectrum

    def process_eti_analysis(self, iq_data):
        """ประมวลผล ETI และวิเคราะห์ขั้นสูง"""
        # TODO: ใช้ Lab 3 ETI processor วิเคราะห์ OFDM และ constellation
        return {
            'ofdm_sync_quality': 75.0,
            'constellation_quality': 80.0,
            'services_found': 3
        }

    def stop_analysis(self):
        """หยุดการวิเคราะห์"""
        self.is_analyzing = False
        self._stop_flag = True

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
        title = QLabel("Advanced Spectrum Analyzer & Waterfall")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # TODO: สร้าง matplotlib canvas
        self.setup_plots()
        layout.addWidget(self.canvas)

        # TODO: สร้างปุ่มควบคุม (Freeze, Clear, Save, Toggle Waterfall)
        controls_layout = QHBoxLayout()
        self.freeze_btn = QPushButton("Freeze")
        self.clear_btn = QPushButton("Clear")
        controls_layout.addWidget(self.freeze_btn)
        controls_layout.addWidget(self.clear_btn)
        layout.addLayout(controls_layout)

        self.setLayout(layout)
        self.frozen = False

    def setup_plots(self):
        """ตั้งค่า matplotlib plots"""
        # TODO: สร้าง Figure และ subplots สำหรับ spectrum และ waterfall
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        self.ax_spectrum = self.figure.add_subplot(2, 1, 1)
        self.ax_waterfall = self.figure.add_subplot(2, 1, 2)

    def update_spectrum(self, frequencies, powers):
        """อัปเดตสเปกตรัม"""
        if self.frozen:
            return
        # TODO: วาดกราฟ spectrum และ waterfall
        # TODO: อัปเดต spectrum_history
        freq_mhz = frequencies / 1e6
        self.ax_spectrum.clear()
        self.ax_spectrum.plot(freq_mhz, powers, 'b-', linewidth=1)
        self.ax_spectrum.set_title('Real-time Spectrum')
        self.canvas.draw_idle()

class SignalQualityMeterWidget(QWidget):
    """Widget แสดงมิเตอร์คุณภาพสัญญาณขั้นสูง"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout()
        title = QLabel("Signal Quality Meters")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title, 0, 0, 1, 3)

        # TODO: สร้าง LCD displays สำหรับ RSSI, SNR, BER
        self.rssi_lcd = QLCDNumber()
        self.snr_lcd = QLCDNumber()
        self.ber_lcd = QLCDNumber()

        # TODO: สร้าง ETI Quality Indicators
        self.sync_quality_label = QLabel("OFDM Sync: --%")
        self.constellation_quality_label = QLabel("Constellation: --%")

        layout.addWidget(self.rssi_lcd, 1, 0)
        layout.addWidget(self.snr_lcd, 1, 1)
        layout.addWidget(self.ber_lcd, 1, 2)
        layout.addWidget(self.sync_quality_label, 2, 0)
        layout.addWidget(self.constellation_quality_label, 2, 1)

        self.setLayout(layout)

    def update_measurements(self, measurement_data):
        """อัปเดตค่าการวัด"""
        # TODO: อัปเดต LCD displays และ labels
        # TODO: เปลี่ยนสีตามคุณภาพสัญญาณ
        rssi = measurement_data.get('signal_strength', -100)
        snr = measurement_data.get('snr', 0)
        ber = measurement_data.get('ber', 100)

        self.rssi_lcd.display(f"{rssi:.1f}")
        self.snr_lcd.display(f"{snr:.1f}")
        self.ber_lcd.display(f"{ber:.3f}")

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
        title = QLabel("Analysis Control Panel")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        # TODO: สร้าง frequency control slider และ preset buttons
        freq_group = QGroupBox("Frequency Control")
        freq_layout = QVBoxLayout()
        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setRange(174000, 240000)  # 174-240 MHz in kHz
        self.freq_slider.setValue(185360)

        # TODO: สร้าง analysis parameters (Sample Rate, Gain, FFT Size)
        params_group = QGroupBox("Analysis Parameters")
        params_layout = QGridLayout()
        self.samplerate_combo = QComboBox()
        self.samplerate_combo.addItems(["2.048 MHz", "2.4 MHz", "3.2 MHz"])
        self.gain_combo = QComboBox()
        self.gain_combo.addItems(["auto", "0", "9", "14", "27"])

        # TODO: สร้างปุ่ม Start/Stop Analysis
        self.start_btn = QPushButton("Start Analysis")
        self.stop_btn = QPushButton("Stop Analysis")

        freq_layout.addWidget(self.freq_slider)
        freq_group.setLayout(freq_layout)
        params_layout.addWidget(self.samplerate_combo, 0, 1)
        params_layout.addWidget(self.gain_combo, 1, 1)
        params_group.setLayout(params_layout)

        layout.addWidget(freq_group)
        layout.addWidget(params_group)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        self.setLayout(layout)

    def start_analysis(self):
        """เริ่มการวิเคราะห์"""
        # TODO: ส่ง signal analysis_started พร้อมพารามิเตอร์
        parameters = {
            'frequency': float(self.freq_slider.value() / 1000),  # MHz
            'sample_rate': 2048000,
            'gain': self.gain_combo.currentText()
        }
        self.analysis_started.emit(parameters)

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

        # TODO: สร้าง main splitter ด้วย 3 panels
        main_splitter = QSplitter(Qt.Horizontal)
        self.control_panel = AnalysisControlPanel()
        self.spectrum_widget = AdvancedSpectrumWidget()
        self.quality_widget = SignalQualityMeterWidget()

        main_splitter.addWidget(self.control_panel)
        main_splitter.addWidget(self.spectrum_widget)
        main_splitter.addWidget(self.quality_widget)
        main_splitter.setSizes([400, 800, 400])

        layout.addWidget(main_splitter)

        # Status bar
        self.status_label = QLabel("Ready - Select frequency and start analysis")
        self.status_label.setStyleSheet("background-color: #e8f5e8; padding: 8px; border-radius: 5px;")
        layout.addWidget(self.status_label)

        central_widget.setLayout(layout)

    def setup_connections(self):
        """เชื่อมต่อ signals"""
        # TODO: เชื่อมต่อ control panel กับ analyzer
        # TODO: เชื่อมต่อ analyzer กับ spectrum และ quality widgets
        self.control_panel.analysis_started.connect(self.start_analysis)
        self.control_panel.analysis_stopped.connect(self.stop_analysis)
        self.analyzer.measurement_ready.connect(self.quality_widget.update_measurements)
        self.analyzer.spectrum_ready.connect(self.spectrum_widget.update_spectrum)

    def start_analysis(self, parameters):
        """เริ่มการวิเคราะห์"""
        # TODO: ตั้งค่า analyzer และเริ่มการทำงาน
        self.analyzer.frequency = parameters['frequency']
        self.analyzer.start()
        self.status_label.setText(f"Analyzing {parameters['frequency']:.3f} MHz...")

    def stop_analysis(self):
        """หยุดการวิเคราะห์"""
        # TODO: หยุด analyzer และอัปเดต UI
        self.analyzer.stop_analysis()
        if self.analyzer.isRunning():
            self.analyzer.wait(3000)
        self.status_label.setText("Analysis stopped")

def main():
    """ฟังก์ชันหลัก"""
    app = QApplication(sys.argv)

    # ตั้งค่า font สำหรับ touchscreen
    font = QFont()
    font.setPointSize(12)
    app.setFont(font)

    window = Lab6MainWindow()
    window.show()

    print("Lab 6: DAB+ Signal Analyzer")
    print("Based on Lab 3 RTL-SDR + ETI Pipeline")
    print("Features:")
    print("- Advanced spectrum analysis with waterfall display")
    print("- ETI stream analysis and quality metrics")
    print("- Real-time signal quality monitoring")

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()