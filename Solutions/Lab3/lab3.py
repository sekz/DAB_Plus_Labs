rapberrypi-dabplus-lab/DAB_Plus_Labs/Solutions/Lab3/lab3.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAB 3: การควบคุม RTL-SDR โดยตรงด้วย pyrtlsdr (เฉลย)
- เข้าถึงและควบคุม RTL-SDR โดยตรงผ่าน Python
- วิเคราะห์และแสดงผลสเปกตรัมความถี่แบบ real-time
- รองรับหน้าจอสัมผัส 7" ด้วย PyQt5 + matplotlib
- มี error handling, logging, และบันทึกไฟล์ spectrum
"""

import sys
import os
import numpy as np
import json
import csv
import logging
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QLabel, QSlider, QSpinBox, QComboBox, QGroupBox, QProgressBar, QTextEdit,
    QSplitter, QFileDialog, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

try:
    from rtlsdr import RtlSdr
except ImportError:
    RtlSdr = None

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Lab3")

# ---------- Controller Thread สำหรับ RTL-SDR ----------
class RTLSDRController(QThread):
    spectrum_data = pyqtSignal(np.ndarray, np.ndarray)  # frequencies, power
    signal_info = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    device_info = pyqtSignal(dict)
    connected = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.sdr = None
        self.is_running = False
        self.center_freq = 100e6
        self.sample_rate = 2.4e6
        self.gain = 'auto'
        self.num_samples = 1024 * 1024
        self._stop_flag = False

    def connect_rtlsdr(self):
        try:
            if RtlSdr is None:
                raise ImportError("ไม่พบโมดูล pyrtlsdr กรุณาติดตั้งด้วย pip3 install pyrtlsdr")
            self.sdr = RtlSdr()
            self.sdr.sample_rate = self.sample_rate
            self.sdr.center_freq = self.center_freq
            self.sdr.gain = self.gain
            info = {
                "tuner_type": str(self.sdr.get_tuner_type()),
                "gain_range": str(self.sdr.gain),
                "sample_rate": self.sdr.sample_rate,
                "center_freq": self.sdr.center_freq
            }
            self.device_info.emit(info)
            test_samples = self.sdr.read_samples(1024)
            if len(test_samples) > 0:
                self.connected.emit(True)
                logger.info("เชื่อมต่อ RTL-SDR สำเร็จ")
                return True
            else:
                self.connected.emit(False)
                return False
        except Exception as e:
            self.error_occurred.emit(f"เชื่อมต่อ RTL-SDR ไม่ได้: {str(e)}")
            self.connected.emit(False)
            logger.error(f"เชื่อมต่อ RTL-SDR ไม่ได้: {str(e)}")
            return False

    def disconnect_rtlsdr(self):
        try:
            self.is_running = False
            self._stop_flag = True
            if self.sdr:
                self.sdr.close()
                self.sdr = None
                logger.info("ตัดการเชื่อมต่อ RTL-SDR แล้ว")
        except Exception as e:
            logger.error(f"ปิด RTL-SDR error: {str(e)}")

    def set_center_frequency(self, frequency):
        self.center_freq = frequency
        if self.sdr:
            try:
                self.sdr.center_freq = frequency
                logger.info(f"ตั้งค่าความถี่กลาง: {frequency/1e6:.3f} MHz")
            except Exception as e:
                self.error_occurred.emit(f"ตั้งค่าความถี่ error: {str(e)}")

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        if self.sdr:
            try:
                self.sdr.sample_rate = sample_rate
                logger.info(f"ตั้งค่า sample rate: {sample_rate/1e6:.2f} MHz")
            except Exception as e:
                self.error_occurred.emit(f"ตั้งค่า sample rate error: {str(e)}")

    def set_gain(self, gain):
        self.gain = gain
        if self.sdr:
            try:
                self.sdr.gain = gain if gain != "auto" else 'auto'
                logger.info(f"ตั้งค่า gain: {gain}")
            except Exception as e:
                self.error_occurred.emit(f"ตั้งค่า gain error: {str(e)}")

    def read_samples(self, num_samples=None):
        try:
            if self.sdr:
                n = num_samples if num_samples else self.num_samples
                samples = self.sdr.read_samples(n)
                return samples
            return None
        except Exception as e:
            self.error_occurred.emit(f"อ่าน samples ไม่ได้: {str(e)}")
            return None

    def calculate_spectrum(self, samples):
        try:
            # จำกัดขนาด samples
            if len(samples) > 1024*1024:
                samples = samples[:1024*1024]
            fft_data = np.fft.fft(samples)
            fft_shifted = np.fft.fftshift(fft_data)
            power = 20 * np.log10(np.abs(fft_shifted) + 1e-10)
            frequencies = np.fft.fftfreq(len(samples), 1/self.sample_rate)
            frequencies = np.fft.fftshift(frequencies) + self.center_freq
            return frequencies, power
        except Exception as e:
            self.error_occurred.emit(f"คำนวณสเปกตรัม error: {str(e)}")
            return None, None

    def analyze_signal(self, frequencies, power):
        try:
            # Peak detection
            peaks = find_peaks(frequencies, power, threshold=np.max(power)-15)
            snr = estimate_snr(power)
            info = {
                "snr": snr,
                "peak_count": len(peaks),
                "peaks": [{"freq": float(frequencies[p])/1e6, "power": float(power[p])} for p in peaks]
            }
            self.signal_info.emit(info)
        except Exception as e:
            logger.error(f"วิเคราะห์สัญญาณ error: {str(e)}")

    def run(self):
        self.is_running = True
        self._stop_flag = False
        while self.is_running and not self._stop_flag:
            try:
                samples = self.read_samples()
                if samples is not None:
                    freqs, power = self.calculate_spectrum(samples)
                    if freqs is not None and power is not None:
                        self.spectrum_data.emit(freqs, power)
                        self.analyze_signal(freqs, power)
                self.msleep(200)  # ~5 FPS
            except Exception as e:
                self.error_occurred.emit(f"Thread error: {str(e)}")
                break

    def start_capture(self):
        if not self.isRunning():
            self.is_running = True
            self._stop_flag = False
            self.start()
            logger.info("เริ่มการจับสัญญาณ")

    def stop_capture(self):
        self.is_running = False
        self._stop_flag = True
        logger.info("หยุดการจับสัญญาณ")

# ---------- Spectrum Analyzer Widget ----------
class SpectrumAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_matplotlib()
        self.setup_ui()
        self.frequencies = None
        self.power = None
        self.frozen = False

    def setup_matplotlib(self):
        self.figure = Figure(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('Frequency (MHz)')
        self.ax.set_ylabel('Power (dB)')
        self.ax.set_title('RF Spectrum Analyzer')
        self.ax.grid(True, alpha=0.3)
        self.line = None

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        control_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 บันทึกกราฟ")
        self.clear_btn = QPushButton("🗑️ เคลียร์")
        self.freeze_btn = QPushButton("❄️ หยุดชั่วคราว")
        self.save_btn.setMinimumHeight(40)
        self.clear_btn.setMinimumHeight(40)
        self.freeze_btn.setMinimumHeight(40)
        control_layout.addWidget(self.save_btn)
        control_layout.addWidget(self.clear_btn)
        control_layout.addWidget(self.freeze_btn)
        layout.addLayout(control_layout)
        self.save_btn.clicked.connect(self.save_spectrum_data)
        self.clear_btn.clicked.connect(self.clear_plot)
        self.freeze_btn.clicked.connect(self.toggle_freeze)

    def update_spectrum(self, frequencies, power):
        if self.frozen:
            return
        self.frequencies = frequencies
        self.power = power
        self.ax.clear()
        self.ax.plot(frequencies / 1e6, power, 'b-', linewidth=0.8)
        self.ax.set_xlabel('Frequency (MHz)')
        self.ax.set_ylabel('Power (dB)')
        self.ax.set_title('RF Spectrum - Real Time')
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw_idle()

    def clear_plot(self):
        self.ax.clear()
        self.ax.set_xlabel('Frequency (MHz)')
        self.ax.set_ylabel('Power (dB)')
        self.ax.set_title('RF Spectrum Analyzer')
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw_idle()

    def toggle_freeze(self):
        self.frozen = not self.frozen
        self.freeze_btn.setText("▶️ ดำเนินการต่อ" if self.frozen else "❄️ หยุดชั่วคราว")

    def save_spectrum_data(self):
        if self.frequencies is None or self.power is None:
            QMessageBox.warning(self, "ไม่มีข้อมูล", "ยังไม่มีข้อมูลสเปกตรัมให้บันทึก")
            return
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path, _ = QFileDialog.getSaveFileName(
            self, "บันทึกข้อมูลสเปกตรัม", f"spectrum_data_{now}.csv", "CSV Files (*.csv)"
        )
        if csv_path:
            try:
                with open(csv_path, "w", newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Frequency (Hz)", "Power (dB)"])
                    for fval, pval in zip(self.frequencies, self.power):
                        writer.writerow([fval, pval])
                logger.info(f"บันทึกข้อมูล spectrum: {csv_path}")
            except Exception as e:
                QMessageBox.critical(self, "บันทึกผิดพลาด", str(e))
        png_path, _ = QFileDialog.getSaveFileName(
            self, "บันทึกกราฟสเปกตรัม", f"spectrum_plot_{now}.png", "PNG Files (*.png)"
        )
        if png_path:
            try:
                self.figure.savefig(png_path)
                logger.info(f"บันทึกกราฟ spectrum: {png_path}")
            except Exception as e:
                QMessageBox.critical(self, "บันทึกผิดพลาด", str(e))

# ---------- Control Panel Widget ----------
class RTLSDRControlPanel(QWidget):
    frequency_changed = pyqtSignal(float)
    sample_rate_changed = pyqtSignal(float)
    gain_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        # Frequency control
        freq_group = QGroupBox("ความถี่กลาง (MHz)")
        freq_layout = QVBoxLayout(freq_group)
        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setRange(24, 1700)
        self.freq_slider.setValue(100)
        self.freq_spinbox = QSpinBox()
        self.freq_spinbox.setRange(24, 1700)
        self.freq_spinbox.setValue(100)
        self.freq_spinbox.setSuffix(" MHz")
        freq_layout.addWidget(self.freq_slider)
        freq_layout.addWidget(self.freq_spinbox)
        layout.addWidget(freq_group)
        # Sample rate control
        sr_group = QGroupBox("Sample Rate")
        sr_layout = QVBoxLayout(sr_group)
        self.sr_combo = QComboBox()
        self.sr_combo.addItems([
            "0.25 MHz", "0.5 MHz", "1.0 MHz",
            "1.2 MHz", "2.0 MHz", "2.4 MHz"
        ])
        self.sr_combo.setCurrentText("2.4 MHz")
        sr_layout.addWidget(self.sr_combo)
        layout.addWidget(sr_group)
        # Gain control
        gain_group = QGroupBox("Gain")
        gain_layout = QVBoxLayout(gain_group)
        self.gain_combo = QComboBox()
        self.gain_combo.addItems([
            "auto", "0 dB", "9 dB", "14 dB", "27 dB",
            "37 dB", "77 dB", "87 dB", "125 dB",
            "144 dB", "157 dB", "166 dB", "197 dB"
        ])
        gain_layout.addWidget(self.gain_combo)
        layout.addWidget(gain_group)
        # Device info
        self.device_info_label = QLabel("Device: -")
        layout.addWidget(self.device_info_label)
        # Signals
        self.freq_slider.valueChanged.connect(self.on_freq_changed)
        self.freq_spinbox.valueChanged.connect(self.on_freq_changed)
        self.sr_combo.currentTextChanged.connect(self.on_sr_changed)
        self.gain_combo.currentTextChanged.connect(self.on_gain_changed)

    def on_freq_changed(self, value):
        if self.sender() == self.freq_slider:
            self.freq_spinbox.setValue(value)
        else:
            self.freq_slider.setValue(value)
        self.frequency_changed.emit(value * 1e6)

    def on_sr_changed(self, text):
        sr_map = {
            "0.25 MHz": 0.25e6, "0.5 MHz": 0.5e6, "1.0 MHz": 1.0e6,
            "1.2 MHz": 1.2e6, "2.0 MHz": 2.0e6, "2.4 MHz": 2.4e6
        }
        self.sample_rate_changed.emit(sr_map.get(text, 2.4e6))

    def on_gain_changed(self, text):
        self.gain_changed.emit(text)

    def update_device_info(self, info):
        s = f"Tuner: {info.get('tuner_type', '-')}, Sample Rate: {info.get('sample_rate', '-')/1e6:.2f} MHz, Center: {info.get('center_freq', '-')/1e6:.2f} MHz"
        self.device_info_label.setText(s)

# ---------- Signal Analysis Widget ----------
class SignalAnalysisWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.snr_label = QLabel("SNR: -")
        self.peak_label = QLabel("Peak count: -")
        self.peak_list = QTextEdit()
        self.peak_list.setReadOnly(True)
        layout.addWidget(self.snr_label)
        layout.addWidget(self.peak_label)
        layout.addWidget(QLabel("Peak signals (MHz, dB):"))
        layout.addWidget(self.peak_list)

    def update_signal_info(self, signal_info):
        self.snr_label.setText(f"SNR: {signal_info.get('snr', '-'):0.2f} dB")
        self.peak_label.setText(f"Peak count: {signal_info.get('peak_count', '-')}")
        peaks = signal_info.get("peaks", [])
        txt = ""
        for p in peaks:
            txt += f"{p['freq']:.3f} MHz : {p['power']:.1f} dB\n"
        self.peak_list.setText(txt)

# ---------- Main Window ----------
class Lab3MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.rtlsdr_controller = RTLSDRController()
        self.setup_ui()
        self.setup_touch_interface()
        self.setup_connections()
        self.setWindowTitle("LAB 3: การควบคุม RTL-SDR โดยตรงด้วย pyrtlsdr")
        self.resize(1200, 800)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        title_label = QLabel("LAB 3: การควบคุม RTL-SDR โดยตรงด้วย pyrtlsdr")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 18px; font-weight: bold; color: #2c3e50;
            padding: 12px; background-color: #ecf0f1; border-radius: 8px;
        """)
        main_layout.addWidget(title_label)
        button_layout = QHBoxLayout()
        self.connect_btn = QPushButton("🔌 Connect RTL-SDR")
        self.disconnect_btn = QPushButton("❌ Disconnect")
        self.start_btn = QPushButton("▶️ Start Capture")
        self.stop_btn = QPushButton("⏹️ Stop")
        self.reset_btn = QPushButton("🔄 Reset")
        for btn in [self.connect_btn, self.disconnect_btn, self.start_btn, self.stop_btn, self.reset_btn]:
            btn.setMinimumHeight(40)
            btn.setFont(QFont("Arial", 13))
            button_layout.addWidget(btn)
        main_layout.addLayout(button_layout)
        content_splitter = QSplitter(Qt.Horizontal)
        self.control_panel = RTLSDRControlPanel()
        self.spectrum_analyzer = SpectrumAnalyzer()
        self.signal_analysis = SignalAnalysisWidget()
        content_splitter.addWidget(self.control_panel)
        content_splitter.addWidget(self.spectrum_analyzer)
        content_splitter.addWidget(self.signal_analysis)
        content_splitter.setSizes([250, 700, 250])
        main_layout.addWidget(content_splitter, 1)
        self.status_label = QLabel("พร้อมใช้งาน - เชื่อมต่อ RTL-SDR เพื่อเริ่มต้น")
        self.status_label.setStyleSheet("background-color: #f9e79f; padding: 8px;")
        main_layout.addWidget(self.status_label)

    def setup_touch_interface(self):
        font = QFont()
        font.setPointSize(13)
        self.setFont(font)
        # ปรับขนาดปุ่มและ widget สำหรับ touch
        for btn in [self.connect_btn, self.disconnect_btn, self.start_btn, self.stop_btn, self.reset_btn,
                    self.spectrum_analyzer.save_btn, self.spectrum_analyzer.clear_btn, self.spectrum_analyzer.freeze_btn]:
            btn.setMinimumHeight(48)
            btn.setMinimumWidth(120)
            btn.setFont(QFont("Arial", 14))
        self.control_panel.freq_slider.setSingleStep(1)
        self.control_panel.freq_slider.setPageStep(5)
        self.control_panel.freq_spinbox.setFont(QFont("Arial", 14))
        self.control_panel.sr_combo.setFont(QFont("Arial", 14))
        self.control_panel.gain_combo.setFont(QFont("Arial", 14))

    def setup_connections(self):
        self.connect_btn.clicked.connect(self.connect_rtlsdr)
        self.disconnect_btn.clicked.connect(self.disconnect_rtlsdr)
        self.start_btn.clicked.connect(self.start_capture)
        self.stop_btn.clicked.connect(self.stop_capture)
        self.reset_btn.clicked.connect(self.reset_settings)
        self.control_panel.frequency_changed.connect(self.rtlsdr_controller.set_center_frequency)
        self.control_panel.sample_rate_changed.connect(self.rtlsdr_controller.set_sample_rate)
        self.control_panel.gain_changed.connect(self.rtlsdr_controller.set_gain)
        self.rtlsdr_controller.spectrum_data.connect(self.spectrum_analyzer.update_spectrum)
        self.rtlsdr_controller.signal_info.connect(self.signal_analysis.update_signal_info)
        self.rtlsdr_controller.error_occurred.connect(self.show_error)
        self.rtlsdr_controller.device_info.connect(self.control_panel.update_device_info)
        self.rtlsdr_controller.connected.connect(self.on_connected)

    def connect_rtlsdr(self):
        self.status_label.setText("กำลังเชื่อมต่อ RTL-SDR ...")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        ok = self.rtlsdr_controller.connect_rtlsdr()
        QApplication.restoreOverrideCursor()
        if ok:
            self.status_label.setText("เชื่อมต่อ RTL-SDR สำเร็จ")
        else:
            self.status_label.setText("เชื่อมต่อ RTL-SDR ไม่สำเร็จ")

    def disconnect_rtlsdr(self):
        self.rtlsdr_controller.disconnect_rtlsdr()
        self.status_label.setText("ตัดการเชื่อมต่อ RTL-SDR แล้ว")

    def start_capture(self):
        self.rtlsdr_controller.start_capture()
        self.status_label.setText("เริ่มการจับสัญญาณ ...")

    def stop_capture(self):
        self.rtlsdr_controller.stop_capture()
        self.status_label.setText("หยุดการจับสัญญาณแล้ว")

    def reset_settings(self):
        self.control_panel.freq_slider.setValue(100)
        self.control_panel.sr_combo.setCurrentText("2.4 MHz")
        self.control_panel.gain_combo.setCurrentText("auto")
        self.status_label.setText("รีเซ็ตค่าพารามิเตอร์แล้ว")

    def show_error(self, msg):
        QMessageBox.critical(self, "เกิดข้อผิดพลาด", msg)
        self.status_label.setText(f"ข้อผิดพลาด: {msg}")

    def on_connected(self, ok):
        if ok:
            self.status_label.setText("เชื่อมต่อ RTL-SDR สำเร็จ")
        else:
            self.status_label.setText("เชื่อมต่อ RTL-SDR ไม่สำเร็จ")

    def closeEvent(self, event):
        self.rtlsdr_controller.disconnect_rtlsdr()
        event.accept()

# ---------- Helper Functions ----------
def find_peaks(frequencies, power, threshold=-50):
    # หา peaks ที่เกิน threshold (simple peak detection)
    peaks = []
    for i in range(1, len(power)-1):
        if power[i] > threshold and power[i] > power[i-1] and power[i] > power[i+1]:
            peaks.append(i)
    return peaks

def estimate_snr(power_spectrum):
    # SNR = (max - median) dB
    if len(power_spectrum) == 0:
        return 0
    peak = np.max(power_spectrum)
    noise = np.median(power_spectrum)
    return float(peak - noise)

# ---------- Main ----------
def main():
    if RtlSdr is None:
        print("ไม่พบ pyrtlsdr กรุณาติดตั้งด้วย pip3 install pyrtlsdr")
        sys.exit(1)
    app = QApplication(sys.argv)
    font = QFont()
    font.setPointSize(13)
    app.setFont(font)
    window = Lab3MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    print("LAB 3: การควบคุม RTL-SDR โดยตรงด้วย pyrtlsdr (Solutions)")
    main()
