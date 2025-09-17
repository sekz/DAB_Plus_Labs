#!/usr/bin/env python3
"""
Complete welle.io Integration Controller
Solution for Lab 2 Trap 2.2: welle.io Integration Challenge
"""

import subprocess
import threading
import queue
import time
import json
import re
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class WelleIOController(QObject):
    """Complete welle.io integration with PyQt5"""

    # Signals for status updates
    status_changed = pyqtSignal(str)
    station_found = pyqtSignal(str, str)  # station_name, service_info
    audio_started = pyqtSignal()
    error_occurred = pyqtSignal(str)
    ensemble_info = pyqtSignal(dict)  # ensemble information
    audio_level = pyqtSignal(float)   # audio level indicator

    def __init__(self):
        super().__init__()
        self.process = None
        self.is_running = False
        self.output_queue = queue.Queue()
        self.current_frequency = None
        self.current_gain = 40
        self.device_index = 0
        self.stations = {}
        self.ensemble_data = {}

    def start_welle_io(self, frequency_mhz: float, device_index: int = 0, gain: int = 40) -> bool:
        """Start welle.io with specified parameters"""
        try:
            self.device_index = device_index
            self.current_gain = gain

            # Build command
            cmd = [
                'welle-io',
                '-D', str(device_index),          # RTL-SDR device index
                '-C', str(int(frequency_mhz * 1e6)),  # Frequency in Hz
                '-G', str(gain),                  # Gain setting
                '--dump-programme',               # Enable programme dumping
                '--verbose',                      # Verbose output
                '--no-gui'                        # Command line mode
            ]

            self.status_changed.emit(f"Starting welle.io on {frequency_mhz} MHz (Gain: {gain}dB)...")

            # Start process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            self.is_running = True
            self.current_frequency = frequency_mhz

            # Start output monitoring thread
            self.monitor_thread = threading.Thread(
                target=self._monitor_output,
                daemon=True
            )
            self.monitor_thread.start()

            self.status_changed.emit("welle.io started successfully")
            return True

        except Exception as e:
            self.error_occurred.emit(f"Failed to start welle.io: {str(e)}")
            return False

    def _monitor_output(self):
        """Monitor welle.io output in separate thread"""
        while self.is_running and self.process:
            try:
                line = self.process.stdout.readline()
                if not line:
                    break

                line = line.strip()
                if line:
                    self._parse_output(line)

            except Exception as e:
                self.error_occurred.emit(f"Output monitoring error: {str(e)}")
                break

    def _parse_output(self, line: str):
        """Parse welle.io output for useful information"""
        # Ensemble detection
        if "Ensemble:" in line:
            ensemble_info = self._parse_ensemble_info(line)
            if ensemble_info:
                self.ensemble_data.update(ensemble_info)
                self.ensemble_info.emit(ensemble_info)

        # Service/Station detection
        elif "Service:" in line or "Programme:" in line:
            station_info = self._parse_station_info(line)
            if station_info:
                self.stations[station_info['name']] = station_info
                self.station_found.emit(station_info['name'], json.dumps(station_info))

        # Audio output detection
        elif "Audio output started" in line or "Playing" in line:
            self.audio_started.emit()

        # Signal quality information
        elif "SNR:" in line or "Signal strength:" in line:
            self._parse_signal_quality(line)

        # Error detection
        elif any(keyword in line.lower() for keyword in ['error', 'failed', 'timeout']):
            self.error_occurred.emit(line)

        # General status
        else:
            self.status_changed.emit(line)

    def _parse_ensemble_info(self, line: str) -> dict:
        """Parse ensemble information from welle.io output"""
        try:
            # Example: "Ensemble: Thai Digital Radio (ID: 0xE1C5)"
            if "Ensemble:" in line:
                parts = line.split("Ensemble:")
                if len(parts) > 1:
                    ensemble_text = parts[1].strip()

                    # Extract ensemble name and ID
                    id_match = re.search(r'\(ID:\s*(0x[0-9a-fA-F]+|\d+)\)', ensemble_text)
                    ensemble_id = id_match.group(1) if id_match else None

                    # Remove ID from name
                    ensemble_name = ensemble_text
                    if id_match:
                        ensemble_name = ensemble_text.replace(id_match.group(0), '').strip()

                    return {
                        'name': ensemble_name,
                        'id': ensemble_id,
                        'frequency_mhz': self.current_frequency,
                        'detection_time': datetime.now().isoformat()
                    }

        except Exception as e:
            print(f"Error parsing ensemble info: {e}")

        return {}

    def _parse_station_info(self, line: str) -> dict:
        """Parse station/service information"""
        try:
            station_info = {
                'detection_time': datetime.now().isoformat(),
                'frequency_mhz': self.current_frequency
            }

            if "Service:" in line:
                # Example: "Service: Thai PBS Radio (ID: 0x1001, Type: Audio)"
                parts = line.split("Service:")
                if len(parts) > 1:
                    service_text = parts[1].strip()

                    # Extract service ID
                    id_match = re.search(r'ID:\s*(0x[0-9a-fA-F]+|\d+)', service_text)
                    station_info['service_id'] = id_match.group(1) if id_match else None

                    # Extract service type
                    type_match = re.search(r'Type:\s*(\w+)', service_text)
                    station_info['service_type'] = type_match.group(1) if type_match else 'Unknown'

                    # Extract name (remove ID and Type)
                    name = service_text
                    if id_match:
                        name = name.replace(id_match.group(0), '').replace('ID:', '').strip()
                    if type_match:
                        name = name.replace(type_match.group(0), '').replace('Type:', '').strip()

                    name = re.sub(r'[(),]+', '', name).strip()
                    station_info['name'] = name

            elif "Programme:" in line:
                # Alternative format: "Programme: Station Name"
                parts = line.split("Programme:")
                if len(parts) > 1:
                    station_info['name'] = parts[1].strip()
                    station_info['service_type'] = 'Audio'

            return station_info

        except Exception as e:
            print(f"Error parsing station info: {e}")

        return {}

    def _parse_signal_quality(self, line: str):
        """Parse signal quality information"""
        try:
            # Extract SNR
            snr_match = re.search(r'SNR:\s*([\d.-]+)', line)
            if snr_match:
                snr_db = float(snr_match.group(1))
                self.status_changed.emit(f"Signal SNR: {snr_db:.1f} dB")

            # Extract signal strength
            strength_match = re.search(r'Signal strength:\s*([\d.-]+)', line)
            if strength_match:
                strength = float(strength_match.group(1))
                self.status_changed.emit(f"Signal strength: {strength:.1f}")

        except Exception as e:
            print(f"Error parsing signal quality: {e}")

    def stop_welle_io(self):
        """Stop welle.io process"""
        if self.process:
            self.is_running = False
            self.process.terminate()

            # Wait for process to end
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

            self.process = None
            self.status_changed.emit("welle.io stopped")

    def tune_frequency(self, frequency_mhz: float) -> bool:
        """Change frequency (requires restart)"""
        if self.is_running:
            self.stop_welle_io()
            time.sleep(1)  # Brief pause

        return self.start_welle_io(frequency_mhz, self.device_index, self.current_gain)

    def set_gain(self, gain: int) -> bool:
        """Change gain setting (requires restart)"""
        if self.is_running:
            current_freq = self.current_frequency
            self.stop_welle_io()
            time.sleep(1)
            return self.start_welle_io(current_freq, self.device_index, gain)
        else:
            self.current_gain = gain
            return True

    def get_status(self) -> dict:
        """Get current status"""
        return {
            'running': self.is_running,
            'frequency_mhz': self.current_frequency,
            'gain_db': self.current_gain,
            'device_index': self.device_index,
            'process_id': self.process.pid if self.process else None,
            'stations_detected': len(self.stations),
            'ensemble_data': self.ensemble_data
        }

    def get_stations(self) -> dict:
        """Get detected stations"""
        return self.stations.copy()

    def export_scan_results(self, filename: str) -> bool:
        """Export scan results to JSON file"""
        try:
            scan_data = {
                'scan_timestamp': datetime.now().isoformat(),
                'frequency_mhz': self.current_frequency,
                'gain_db': self.current_gain,
                'device_index': self.device_index,
                'ensemble': self.ensemble_data,
                'stations': self.stations,
                'status': self.get_status()
            }

            with open(filename, 'w') as f:
                json.dump(scan_data, f, indent=2)

            return True

        except Exception as e:
            self.error_occurred.emit(f"Export failed: {str(e)}")
            return False

class DABReceiverGUI(QMainWindow):
    """Advanced DAB+ receiver GUI"""

    def __init__(self):
        super().__init__()
        self.welle_controller = WelleIOController()
        self.scan_timer = QTimer()
        self.auto_scan_frequencies = [174.928, 176.640, 178.352, 180.064]  # Bangkok blocks
        self.current_scan_index = 0
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        self.setWindowTitle('Advanced DAB+ Receiver with welle.io')
        self.setGeometry(100, 100, 900, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Control panel
        control_group = QGroupBox("Reception Control")
        control_layout = QGridLayout(control_group)

        # Frequency control
        control_layout.addWidget(QLabel('Frequency (MHz):'), 0, 0)
        self.freq_spinbox = QDoubleSpinBox()
        self.freq_spinbox.setRange(174.0, 230.0)
        self.freq_spinbox.setValue(174.928)  # Bangkok Block 5A
        self.freq_spinbox.setDecimals(3)
        self.freq_spinbox.setSingleStep(1.712)  # DAB+ block spacing
        control_layout.addWidget(self.freq_spinbox, 0, 1)

        # Gain control
        control_layout.addWidget(QLabel('Gain (dB):'), 0, 2)
        self.gain_spinbox = QSpinBox()
        self.gain_spinbox.setRange(0, 50)
        self.gain_spinbox.setValue(40)
        control_layout.addWidget(self.gain_spinbox, 0, 3)

        # Device selection
        control_layout.addWidget(QLabel('Device:'), 1, 0)
        self.device_spinbox = QSpinBox()
        self.device_spinbox.setRange(0, 10)
        control_layout.addWidget(self.device_spinbox, 1, 1)

        # Buttons
        self.tune_button = QPushButton('📡 Tune')
        self.tune_button.clicked.connect(self.tune_frequency)
        control_layout.addWidget(self.tune_button, 1, 2)

        self.stop_button = QPushButton('⏹️ Stop')
        self.stop_button.clicked.connect(self.stop_reception)
        control_layout.addWidget(self.stop_button, 1, 3)

        layout.addWidget(control_group)

        # Auto-scan panel
        scan_group = QGroupBox("Auto Scan")
        scan_layout = QHBoxLayout(scan_group)

        self.scan_button = QPushButton('🔍 Start Auto Scan')
        self.scan_button.clicked.connect(self.start_auto_scan)
        scan_layout.addWidget(self.scan_button)

        self.scan_stop_button = QPushButton('⏸️ Stop Scan')
        self.scan_stop_button.clicked.connect(self.stop_auto_scan)
        self.scan_stop_button.setEnabled(False)
        scan_layout.addWidget(self.scan_stop_button)

        self.scan_progress = QProgressBar()
        scan_layout.addWidget(self.scan_progress)

        layout.addWidget(scan_group)

        # Status and ensemble info
        info_layout = QHBoxLayout()

        # Status display
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)

        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(150)
        status_layout.addWidget(self.status_text)

        info_layout.addWidget(status_group)

        # Ensemble info
        ensemble_group = QGroupBox("Ensemble Information")
        ensemble_layout = QFormLayout(ensemble_group)

        self.ensemble_name_label = QLabel("Not detected")
        self.ensemble_id_label = QLabel("N/A")
        self.ensemble_freq_label = QLabel("N/A")

        ensemble_layout.addRow("Name:", self.ensemble_name_label)
        ensemble_layout.addRow("ID:", self.ensemble_id_label)
        ensemble_layout.addRow("Frequency:", self.ensemble_freq_label)

        info_layout.addWidget(ensemble_group)

        layout.addLayout(info_layout)

        # Station list
        station_group = QGroupBox("Detected Stations")
        station_layout = QVBoxLayout(station_group)

        self.station_table = QTableWidget()
        self.station_table.setColumnCount(4)
        self.station_table.setHorizontalHeaderLabels(['Station Name', 'Service ID', 'Type', 'Frequency'])
        self.station_table.horizontalHeader().setStretchLastSection(True)
        station_layout.addWidget(self.station_table)

        layout.addWidget(station_group)

        # Control buttons
        button_layout = QHBoxLayout()

        self.export_button = QPushButton('💾 Export Results')
        self.export_button.clicked.connect(self.export_results)
        button_layout.addWidget(self.export_button)

        self.clear_button = QPushButton('🗑️ Clear Log')
        self.clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)

        # Status bar
        self.statusBar().showMessage("DAB+ Receiver Ready")

    def connect_signals(self):
        """Connect welle.io controller signals"""
        self.welle_controller.status_changed.connect(self.update_status)
        self.welle_controller.station_found.connect(self.add_station)
        self.welle_controller.audio_started.connect(self.on_audio_started)
        self.welle_controller.error_occurred.connect(self.show_error)
        self.welle_controller.ensemble_info.connect(self.update_ensemble_info)

        # Auto-scan timer
        self.scan_timer.timeout.connect(self.scan_next_frequency)

    @pyqtSlot()
    def tune_frequency(self):
        """Start tuning to selected frequency"""
        frequency = self.freq_spinbox.value()
        gain = self.gain_spinbox.value()
        device = self.device_spinbox.value()

        self.welle_controller.device_index = device
        self.welle_controller.start_welle_io(frequency, device, gain)

    @pyqtSlot()
    def stop_reception(self):
        """Stop DAB+ reception"""
        self.welle_controller.stop_welle_io()

    @pyqtSlot()
    def start_auto_scan(self):
        """Start automatic frequency scanning"""
        self.current_scan_index = 0
        self.scan_progress.setRange(0, len(self.auto_scan_frequencies))
        self.scan_progress.setValue(0)

        self.scan_button.setEnabled(False)
        self.scan_stop_button.setEnabled(True)

        # Start with first frequency
        self.scan_next_frequency()

        # Set timer for automatic progression
        self.scan_timer.start(15000)  # 15 seconds per frequency

    @pyqtSlot()
    def stop_auto_scan(self):
        """Stop automatic scanning"""
        self.scan_timer.stop()
        self.scan_button.setEnabled(True)
        self.scan_stop_button.setEnabled(False)
        self.welle_controller.stop_welle_io()

    @pyqtSlot()
    def scan_next_frequency(self):
        """Scan next frequency in auto-scan sequence"""
        if self.current_scan_index >= len(self.auto_scan_frequencies):
            self.stop_auto_scan()
            self.update_status("Auto-scan completed")
            return

        frequency = self.auto_scan_frequencies[self.current_scan_index]
        self.freq_spinbox.setValue(frequency)

        gain = self.gain_spinbox.value()
        device = self.device_spinbox.value()

        self.update_status(f"Auto-scanning: {frequency} MHz...")
        self.welle_controller.start_welle_io(frequency, device, gain)

        self.scan_progress.setValue(self.current_scan_index + 1)
        self.current_scan_index += 1

    @pyqtSlot(str)
    def update_status(self, message):
        """Update status display"""
        timestamp = time.strftime('%H:%M:%S')
        self.status_text.append(f"[{timestamp}] {message}")

        # Auto-scroll to bottom
        scrollbar = self.status_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        # Update status bar
        self.statusBar().showMessage(message)

    @pyqtSlot(str, str)
    def add_station(self, station_name, station_data_json):
        """Add detected station to table"""
        try:
            station_data = json.loads(station_data_json)

            # Check if station already exists
            for row in range(self.station_table.rowCount()):
                if self.station_table.item(row, 0).text() == station_name:
                    return  # Station already listed

            # Add new row
            row_count = self.station_table.rowCount()
            self.station_table.insertRow(row_count)

            # Populate row
            self.station_table.setItem(row_count, 0, QTableWidgetItem(station_name))
            self.station_table.setItem(row_count, 1, QTableWidgetItem(station_data.get('service_id', 'N/A')))
            self.station_table.setItem(row_count, 2, QTableWidgetItem(station_data.get('service_type', 'Audio')))
            self.station_table.setItem(row_count, 3, QTableWidgetItem(f"{station_data.get('frequency_mhz', 0):.3f} MHz"))

        except Exception as e:
            print(f"Error adding station: {e}")

    @pyqtSlot(dict)
    def update_ensemble_info(self, ensemble_data):
        """Update ensemble information display"""
        self.ensemble_name_label.setText(ensemble_data.get('name', 'Unknown'))
        self.ensemble_id_label.setText(ensemble_data.get('id', 'N/A'))
        self.ensemble_freq_label.setText(f"{ensemble_data.get('frequency_mhz', 0):.3f} MHz")

    @pyqtSlot()
    def on_audio_started(self):
        """Handle audio start event"""
        self.update_status("🔊 Audio streaming started")

    @pyqtSlot(str)
    def show_error(self, error_message):
        """Show error message"""
        self.update_status(f"❌ Error: {error_message}")

    @pyqtSlot()
    def export_results(self):
        """Export scan results"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Scan Results",
            f"dab_scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )

        if filename:
            if self.welle_controller.export_scan_results(filename):
                QMessageBox.information(self, "Export Successful",
                                      f"Results exported to:\n{filename}")
            else:
                QMessageBox.warning(self, "Export Failed",
                                  "Failed to export scan results")

    @pyqtSlot()
    def clear_log(self):
        """Clear status log and station list"""
        self.status_text.clear()
        self.station_table.setRowCount(0)
        self.ensemble_name_label.setText("Not detected")
        self.ensemble_id_label.setText("N/A")
        self.ensemble_freq_label.setText("N/A")

    def closeEvent(self, event):
        """Clean shutdown"""
        self.scan_timer.stop()
        self.welle_controller.stop_welle_io()
        event.accept()

def main():
    """Main application entry point"""
    import sys

    app = QApplication(sys.argv)
    app.setApplicationName("DAB+ Receiver")
    app.setApplicationVersion("2.0")

    window = DABReceiverGUI()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()