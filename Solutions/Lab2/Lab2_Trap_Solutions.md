# Lab 2 Trap Exercise Solutions

## Overview
This document contains comprehensive solutions for all trap exercises in Lab 2. Python implementation files are provided separately in this directory.

### Implementation Files:
- `dab_frequency_analyzer.py` - DAB+ frequency planning and analysis
- `welle_io_controller.py` - Complete welle.io integration with PyQt5
- `performance_monitor.py` - GUI threading and performance optimization

## Trap 2.1 Solution: DAB+ Frequency Planning

### NBTC Frequency Analysis:
```python
import requests
import json
from datetime import datetime

class DABFrequencyAnalyzer:
    def __init__(self):
        self.thailand_dab_frequencies = {
            'Bangkok': {
                'Block 5A': 174.928,  # MHz
                'Block 5B': 176.640,
                'Block 5C': 178.352,
                'Block 5D': 180.064
            },
            'Chiang Mai': {
                'Block 7A': 188.928,
                'Block 7B': 190.640,
                'Block 7C': 192.352
            },
            'Phuket': {
                'Block 9A': 202.928,
                'Block 9B': 204.640
            }
        }

    def get_frequency_info(self, block_name):
        """Get detailed frequency information for a DAB+ block"""
        for region, blocks in self.thailand_dab_frequencies.items():
            if block_name in blocks:
                freq_mhz = blocks[block_name]
                return {
                    'region': region,
                    'block': block_name,
                    'frequency_mhz': freq_mhz,
                    'frequency_hz': freq_mhz * 1e6,
                    'bandwidth_khz': 1536,  # DAB+ bandwidth
                    'center_freq': freq_mhz * 1e6,
                    'lower_bound': (freq_mhz - 0.768) * 1e6,
                    'upper_bound': (freq_mhz + 0.768) * 1e6
                }
        return None

    def scan_frequency_range(self, start_mhz, end_mhz, step_khz=100):
        """Generate frequency scan parameters"""
        start_hz = start_mhz * 1e6
        end_hz = end_mhz * 1e6
        step_hz = step_khz * 1e3

        frequencies = []
        current = start_hz

        while current <= end_hz:
            frequencies.append({
                'frequency_hz': int(current),
                'frequency_mhz': current / 1e6,
                'is_dab_block': self.is_dab_frequency(current / 1e6)
            })
            current += step_hz

        return frequencies

    def is_dab_frequency(self, freq_mhz):
        """Check if frequency matches a known DAB+ block"""
        tolerance = 0.1  # MHz tolerance
        for region, blocks in self.thailand_dab_frequencies.items():
            for block, freq in blocks.items():
                if abs(freq - freq_mhz) < tolerance:
                    return {'region': region, 'block': block}
        return False

# Usage example
analyzer = DABFrequencyAnalyzer()
bangkok_5a = analyzer.get_frequency_info('Block 5A')
print(f"Bangkok Block 5A: {bangkok_5a['frequency_mhz']} MHz")

# Scan Band III (174-230 MHz) for DAB+ signals
band_iii_scan = analyzer.scan_frequency_range(174, 230, 500)
dab_frequencies = [f for f in band_iii_scan if f['is_dab_block']]
```

### RTL-SDR Frequency Scanning:
```bash
# Scan Band III for DAB+ signals
rtl_power -f 174M:230M:1M -i 10 -1 dab_scan.csv

# Analyze scan results
python3 -c "
import csv
import matplotlib.pyplot as plt

frequencies = []
powers = []

with open('dab_scan.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 7:  # Skip header and incomplete rows
            freq_hz = float(row[2])
            power_db = float(row[6])
            frequencies.append(freq_hz / 1e6)  # Convert to MHz
            powers.append(power_db)

plt.figure(figsize=(12, 6))
plt.plot(frequencies, powers)
plt.xlabel('Frequency (MHz)')
plt.ylabel('Power (dB)')
plt.title('DAB+ Band III Spectrum Scan')
plt.grid(True)
plt.savefig('dab_spectrum.png')
print('Spectrum plot saved as dab_spectrum.png')
"
```

## Trap 2.2 Solution: welle.io Integration Challenge

### Complete welle.io Integration:
```python
import subprocess
import threading
import queue
import time
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class WelleIOController(QObject):
    """Complete welle.io integration with PyQt5"""

    # Signals for status updates
    status_changed = pyqtSignal(str)
    station_found = pyqtSignal(str, str)  # station_name, service_info
    audio_started = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.process = None
        self.is_running = False
        self.output_queue = queue.Queue()
        self.current_frequency = None

    def start_welle_io(self, frequency_mhz, device_index=0):
        """Start welle.io with specified parameters"""
        try:
            # Build command
            cmd = [
                'welle-io',
                '-D', str(device_index),  # RTL-SDR device index
                '-C', str(int(frequency_mhz * 1e6)),  # Frequency in Hz
                '--dump-programme',  # Enable programme dumping
                '--verbose'  # Verbose output
            ]

            self.status_changed.emit(f"Starting welle.io on {frequency_mhz} MHz...")

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

    def _parse_output(self, line):
        """Parse welle.io output for useful information"""
        # Station detection
        if "Programme:" in line:
            parts = line.split("Programme:")
            if len(parts) > 1:
                station_info = parts[1].strip()
                self.station_found.emit(station_info, line)

        # Audio start detection
        elif "Audio output started" in line:
            self.audio_started.emit()

        # Error detection
        elif "Error" in line or "error" in line:
            self.error_occurred.emit(line)

        # General status
        else:
            self.status_changed.emit(line)

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

    def tune_frequency(self, frequency_mhz):
        """Change frequency (requires restart)"""
        if self.is_running:
            self.stop_welle_io()
            time.sleep(1)  # Brief pause

        return self.start_welle_io(frequency_mhz)

    def get_status(self):
        """Get current status"""
        return {
            'running': self.is_running,
            'frequency': self.current_frequency,
            'process_id': self.process.pid if self.process else None
        }

class DABReceiverGUI(QMainWindow):
    """Main GUI for DAB+ receiver"""

    def __init__(self):
        super().__init__()
        self.welle_controller = WelleIOController()
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        self.setWindowTitle('DAB+ Receiver with welle.io')
        self.setGeometry(100, 100, 700, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Frequency control
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel('Frequency (MHz):'))

        self.freq_spinbox = QDoubleSpinBox()
        self.freq_spinbox.setRange(174.0, 230.0)
        self.freq_spinbox.setValue(174.928)  # Bangkok Block 5A
        self.freq_spinbox.setDecimals(3)
        self.freq_spinbox.setSingleStep(1.712)  # DAB+ block spacing
        freq_layout.addWidget(self.freq_spinbox)

        self.tune_button = QPushButton('Tune')
        self.tune_button.clicked.connect(self.tune_frequency)
        freq_layout.addWidget(self.tune_button)

        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_reception)
        freq_layout.addWidget(self.stop_button)

        layout.addLayout(freq_layout)

        # Status display
        layout.addWidget(QLabel('Status:'))
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(150)
        layout.addWidget(self.status_text)

        # Station list
        layout.addWidget(QLabel('Detected Stations:'))
        self.station_list = QListWidget()
        layout.addWidget(self.station_list)

        # Control buttons
        button_layout = QHBoxLayout()

        self.clear_button = QPushButton('Clear Log')
        self.clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)

    def connect_signals(self):
        """Connect welle.io controller signals"""
        self.welle_controller.status_changed.connect(self.update_status)
        self.welle_controller.station_found.connect(self.add_station)
        self.welle_controller.audio_started.connect(self.on_audio_started)
        self.welle_controller.error_occurred.connect(self.show_error)

    @pyqtSlot()
    def tune_frequency(self):
        """Start tuning to selected frequency"""
        frequency = self.freq_spinbox.value()
        self.welle_controller.start_welle_io(frequency)

    @pyqtSlot()
    def stop_reception(self):
        """Stop DAB+ reception"""
        self.welle_controller.stop_welle_io()

    @pyqtSlot(str)
    def update_status(self, message):
        """Update status display"""
        timestamp = time.strftime('%H:%M:%S')
        self.status_text.append(f"[{timestamp}] {message}")

        # Auto-scroll to bottom
        scrollbar = self.status_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    @pyqtSlot(str, str)
    def add_station(self, station_name, details):
        """Add detected station to list"""
        item_text = f"{station_name} - {details}"

        # Check if station already in list
        for i in range(self.station_list.count()):
            if self.station_list.item(i).text().startswith(station_name):
                return  # Station already listed

        self.station_list.addItem(item_text)

    @pyqtSlot()
    def on_audio_started(self):
        """Handle audio start event"""
        self.update_status("🔊 Audio streaming started")

    @pyqtSlot(str)
    def show_error(self, error_message):
        """Show error message"""
        self.update_status(f"❌ Error: {error_message}")
        QMessageBox.warning(self, "welle.io Error", error_message)

    @pyqtSlot()
    def clear_log(self):
        """Clear status log"""
        self.status_text.clear()
        self.station_list.clear()

    def closeEvent(self, event):
        """Clean shutdown"""
        self.welle_controller.stop_welle_io()
        event.accept()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = DABReceiverGUI()
    window.show()
    sys.exit(app.exec_())
```

## Trap 2.3 Solution: Audio Routing Investigation

### Audio System Analysis:
```python
import subprocess
import re
import os
from pathlib import Path

class AudioSystemAnalyzer:
    """Analyze and configure audio routing for DAB+"""

    def __init__(self):
        self.audio_system = self.detect_audio_system()
        self.devices = self.scan_audio_devices()

    def detect_audio_system(self):
        """Detect primary audio system (ALSA/PulseAudio)"""
        systems = {}

        # Check for PulseAudio
        try:
            result = subprocess.run(['pulseaudio', '--check', '-v'],
                                  capture_output=True, text=True)
            systems['pulseaudio'] = result.returncode == 0
        except FileNotFoundError:
            systems['pulseaudio'] = False

        # Check for ALSA
        try:
            result = subprocess.run(['aplay', '-l'],
                                  capture_output=True, text=True)
            systems['alsa'] = result.returncode == 0
        except FileNotFoundError:
            systems['alsa'] = False

        # Check for JACK
        try:
            result = subprocess.run(['jack_control', 'status'],
                                  capture_output=True, text=True)
            systems['jack'] = 'started' in result.stdout
        except FileNotFoundError:
            systems['jack'] = False

        return systems

    def scan_audio_devices(self):
        """Scan available audio devices"""
        devices = {'playback': [], 'capture': []}

        if self.audio_system.get('alsa', False):
            devices.update(self._scan_alsa_devices())

        if self.audio_system.get('pulseaudio', False):
            devices.update(self._scan_pulse_devices())

        return devices

    def _scan_alsa_devices(self):
        """Scan ALSA audio devices"""
        devices = {'playback': [], 'capture': []}

        try:
            # Playback devices
            result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'card' in line and 'device' in line:
                    match = re.search(r'card (\d+): ([^,]+).*device (\d+): ([^,]+)', line)
                    if match:
                        devices['playback'].append({
                            'system': 'alsa',
                            'card': int(match.group(1)),
                            'card_name': match.group(2).strip(),
                            'device': int(match.group(3)),
                            'device_name': match.group(4).strip(),
                            'alsa_name': f"hw:{match.group(1)},{match.group(3)}"
                        })

            # Capture devices
            result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'card' in line and 'device' in line:
                    match = re.search(r'card (\d+): ([^,]+).*device (\d+): ([^,]+)', line)
                    if match:
                        devices['capture'].append({
                            'system': 'alsa',
                            'card': int(match.group(1)),
                            'card_name': match.group(2).strip(),
                            'device': int(match.group(3)),
                            'device_name': match.group(4).strip(),
                            'alsa_name': f"hw:{match.group(1)},{match.group(3)}"
                        })

        except Exception as e:
            print(f"ALSA scan error: {e}")

        return devices

    def _scan_pulse_devices(self):
        """Scan PulseAudio devices"""
        devices = {'playback': [], 'capture': []}

        try:
            # Playback sinks
            result = subprocess.run(['pactl', 'list', 'short', 'sinks'],
                                  capture_output=True, text=True)
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        devices['playback'].append({
                            'system': 'pulseaudio',
                            'index': parts[0],
                            'name': parts[1],
                            'driver': parts[2] if len(parts) > 2 else 'unknown'
                        })

            # Capture sources
            result = subprocess.run(['pactl', 'list', 'short', 'sources'],
                                  capture_output=True, text=True)
            for line in result.stdout.strip().split('\n'):
                if line and not line.endswith('.monitor'):  # Skip monitor sources
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        devices['capture'].append({
                            'system': 'pulseaudio',
                            'index': parts[0],
                            'name': parts[1],
                            'driver': parts[2] if len(parts) > 2 else 'unknown'
                        })

        except Exception as e:
            print(f"PulseAudio scan error: {e}")

        return devices

    def configure_audio_for_dab(self, preferred_device=None):
        """Configure audio routing for optimal DAB+ reception"""
        config = {
            'environment_vars': {},
            'command_args': [],
            'recommendations': []
        }

        if self.audio_system.get('pulseaudio', False):
            # PulseAudio configuration
            if preferred_device:
                config['environment_vars']['PULSE_SINK'] = preferred_device

            config['command_args'].extend([
                '--audio-backend', 'pulseaudio'
            ])

            config['recommendations'].append(
                "Using PulseAudio - good for desktop systems with mixing"
            )

        elif self.audio_system.get('alsa', False):
            # ALSA configuration for lower latency
            if preferred_device:
                config['environment_vars']['ALSA_DEVICE'] = preferred_device

            config['command_args'].extend([
                '--audio-backend', 'alsa',
                '--alsa-device', preferred_device or 'default'
            ])

            config['recommendations'].append(
                "Using ALSA - lower latency, good for dedicated DAB+ reception"
            )

        # Audio buffer recommendations
        config['command_args'].extend([
            '--audio-buffer-size', '8192',  # Larger buffer for stability
            '--sample-rate', '48000'        # Standard DAB+ sample rate
        ])

        return config

    def test_audio_output(self, device_name=None):
        """Test audio output to verify configuration"""
        try:
            if self.audio_system.get('pulseaudio', False):
                # Test with PulseAudio
                cmd = ['paplay']
                if device_name:
                    cmd.extend(['--device', device_name])
                cmd.append('/usr/share/sounds/alsa/Front_Left.wav')

            elif self.audio_system.get('alsa', False):
                # Test with ALSA
                cmd = ['aplay']
                if device_name:
                    cmd.extend(['-D', device_name])
                cmd.append('/usr/share/sounds/alsa/Front_Left.wav')

            else:
                return False, "No supported audio system found"

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0, result.stderr

        except Exception as e:
            return False, str(e)

# Usage example
analyzer = AudioSystemAnalyzer()
print("Audio System Status:", analyzer.audio_system)
print("Available Devices:", analyzer.devices)

# Configure for DAB+
dab_config = analyzer.configure_audio_for_dab()
print("DAB+ Audio Configuration:", dab_config)

# Test audio output
success, message = analyzer.test_audio_output()
print(f"Audio test: {'PASS' if success else 'FAIL'} - {message}")
```

### welle.io Audio Configuration:
```bash
# Environment variables for audio routing
export PULSE_SINK="alsa_output.usb-Generic_USB_Audio-00.analog-stereo"
export ALSA_DEVICE="hw:1,0"

# Launch welle.io with specific audio backend
welle-io \
  --audio-backend pulseaudio \
  --audio-buffer-size 8192 \
  --sample-rate 48000 \
  -C 174928000  # Bangkok Block 5A

# Alternative ALSA configuration
welle-io \
  --audio-backend alsa \
  --alsa-device hw:1,0 \
  --audio-buffer-size 4096 \
  -C 174928000
```

## Trap 2.4 Solution: Metadata and Slideshow Analysis

### PAD/DLS/MOT Parser Implementation:
```python
import struct
import json
from datetime import datetime
from PIL import Image
import io

class DABMetadataParser:
    """Parse DAB+ Programme Associated Data (PAD)"""

    def __init__(self):
        self.dls_segments = {}  # Dynamic Label Segments
        self.mot_objects = {}  # Multimedia Object Transfer
        self.slideshow_cache = {}

    def parse_pad_data(self, pad_bytes):
        """Parse PAD data from DAB+ stream"""
        if len(pad_bytes) < 2:
            return None

        # PAD header analysis
        pad_header = pad_bytes[0]
        pad_length = pad_header & 0x1F  # Lower 5 bits

        if pad_length == 0:
            return None  # No PAD data

        # Check PAD type
        if pad_length >= 3:
            app_type = (pad_bytes[1] >> 5) & 0x07

            if app_type == 2:  # DLS (Dynamic Label)
                return self._parse_dls(pad_bytes[1:pad_length+1])
            elif app_type == 6:  # MOT (slideshow)
                return self._parse_mot(pad_bytes[1:pad_length+1])

        return None

    def _parse_dls(self, dls_data):
        """Parse Dynamic Label Segment"""
        if len(dls_data) < 2:
            return None

        # DLS header
        dls_header = dls_data[0]
        segment_number = (dls_header >> 4) & 0x07
        last_segment = (dls_header >> 3) & 0x01

        # Extract text data
        text_data = dls_data[1:].decode('utf-8', errors='ignore')

        # Store segment
        self.dls_segments[segment_number] = text_data

        # Check if we have complete message
        if last_segment:
            complete_text = ''.join(
                self.dls_segments.get(i, '')
                for i in range(segment_number + 1)
            )
            self.dls_segments.clear()  # Reset for next message

            return {
                'type': 'DLS',
                'text': complete_text.strip(),
                'timestamp': datetime.now()
            }

        return None

    def _parse_mot(self, mot_data):
        """Parse Multimedia Object Transfer data"""
        if len(mot_data) < 6:
            return None

        # MOT header parsing
        transport_id = struct.unpack('>H', mot_data[0:2])[0]
        segment_number = struct.unpack('>H', mot_data[2:4])[0]
        last_segment = (mot_data[4] >> 7) & 0x01

        # Store MOT segment
        if transport_id not in self.mot_objects:
            self.mot_objects[transport_id] = {}

        self.mot_objects[transport_id][segment_number] = mot_data[5:]

        # Check if object is complete
        if last_segment:
            return self._assemble_mot_object(transport_id)

        return None

    def _assemble_mot_object(self, transport_id):
        """Assemble complete MOT object from segments"""
        if transport_id not in self.mot_objects:
            return None

        segments = self.mot_objects[transport_id]

        # Assemble data in order
        complete_data = b''.join(
            segments.get(i, b'')
            for i in sorted(segments.keys())
        )

        # Parse MOT header
        if len(complete_data) < 7:
            return None

        content_type = struct.unpack('>H', complete_data[0:2])[0]
        content_subtype = complete_data[2]
        content_size = struct.unpack('>I', complete_data[3:7])[0]

        if content_type == 2:  # Image
            return self._parse_slideshow_image(
                complete_data[7:7+content_size],
                content_subtype,
                transport_id
            )

        # Clean up
        del self.mot_objects[transport_id]
        return None

    def _parse_slideshow_image(self, image_data, subtype, transport_id):
        """Parse slideshow image data"""
        try:
            # Determine image format
            if subtype == 1:  # JPEG
                image_format = 'JPEG'
            elif subtype == 2:  # PNG
                image_format = 'PNG'
            else:
                image_format = 'Unknown'

            # Create image object
            image = Image.open(io.BytesIO(image_data))

            # Cache the image
            cache_key = f"slide_{transport_id}"
            self.slideshow_cache[cache_key] = {
                'image': image,
                'format': image_format,
                'size': image.size,
                'timestamp': datetime.now(),
                'data_size': len(image_data)
            }

            return {
                'type': 'MOT_SLIDESHOW',
                'transport_id': transport_id,
                'image_format': image_format,
                'image_size': image.size,
                'data_size': len(image_data),
                'cache_key': cache_key,
                'timestamp': datetime.now()
            }

        except Exception as e:
            return {
                'type': 'MOT_ERROR',
                'error': str(e),
                'transport_id': transport_id
            }

    def get_slideshow_image(self, cache_key):
        """Retrieve slideshow image from cache"""
        return self.slideshow_cache.get(cache_key)

    def clear_cache(self):
        """Clear slideshow cache"""
        self.slideshow_cache.clear()
        self.dls_segments.clear()
        self.mot_objects.clear()

# Integration with welle.io output parsing
class WelleIOMetadataExtractor:
    """Extract metadata from welle.io output"""

    def __init__(self):
        self.parser = DABMetadataParser()
        self.current_programme = None

    def process_welle_output(self, output_line):
        """Process a line of welle.io output for metadata"""
        results = []

        # Programme information
        if "Programme:" in output_line:
            self.current_programme = self._extract_programme_info(output_line)
            results.append(self.current_programme)

        # DLS text
        elif "DLS:" in output_line:
            dls_info = self._extract_dls_text(output_line)
            if dls_info:
                results.append(dls_info)

        # Slideshow data
        elif "MOT:" in output_line:
            mot_info = self._extract_mot_info(output_line)
            if mot_info:
                results.append(mot_info)

        return results

    def _extract_programme_info(self, line):
        """Extract programme information"""
        # Example: "Programme: Thai PBS Radio (Service ID: 0x1001)"
        parts = line.split("Programme:")
        if len(parts) > 1:
            programme_text = parts[1].strip()

            # Extract service ID if present
            service_id = None
            if "Service ID:" in programme_text:
                import re
                match = re.search(r'Service ID:\s*(0x[0-9a-fA-F]+|\d+)', programme_text)
                if match:
                    service_id = match.group(1)
                    programme_text = programme_text.replace(match.group(0), '').strip()

            return {
                'type': 'PROGRAMME_INFO',
                'name': programme_text.rstrip('()').strip(),
                'service_id': service_id,
                'timestamp': datetime.now()
            }

        return None

    def _extract_dls_text(self, line):
        """Extract DLS (Dynamic Label) text"""
        # Example: "DLS: Now Playing: Artist - Song Title"
        parts = line.split("DLS:")
        if len(parts) > 1:
            dls_text = parts[1].strip()

            # Parse common DLS formats
            if " - " in dls_text:
                # Likely "Artist - Title" format
                artist, title = dls_text.split(" - ", 1)
                return {
                    'type': 'DLS_TRACK_INFO',
                    'artist': artist.strip(),
                    'title': title.strip(),
                    'full_text': dls_text,
                    'timestamp': datetime.now()
                }
            else:
                return {
                    'type': 'DLS_TEXT',
                    'text': dls_text,
                    'timestamp': datetime.now()
                }

        return None

    def _extract_mot_info(self, line):
        """Extract MOT (slideshow) information"""
        # Example: "MOT: Slideshow image received (320x240 JPEG)"
        if "Slideshow" in line:
            import re
            size_match = re.search(r'(\d+)x(\d+)', line)
            format_match = re.search(r'(JPEG|PNG|GIF)', line, re.IGNORECASE)

            return {
                'type': 'MOT_SLIDESHOW_INFO',
                'width': int(size_match.group(1)) if size_match else None,
                'height': int(size_match.group(2)) if size_match else None,
                'format': format_match.group(1).upper() if format_match else None,
                'raw_line': line,
                'timestamp': datetime.now()
            }

        return None

# Usage example
extractor = WelleIOMetadataExtractor()

# Process welle.io output
sample_outputs = [
    "Programme: Thai PBS Radio (Service ID: 0x1001)",
    "DLS: Adele - Rolling in the Deep",
    "MOT: Slideshow image received (320x240 JPEG)"
]

for output in sample_outputs:
    metadata = extractor.process_welle_output(output)
    for item in metadata:
        print(f"{item['type']}: {item}")
```

## Trap 2.5 Solution: GUI Threading and Performance

### Complete Performance Monitoring Solution:
```python
import sys
import time
import psutil
import threading
from collections import deque
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pyqtgraph as pg

class PerformanceMonitor(QThread):
    """Real-time performance monitoring thread"""

    # Signals for data updates
    cpu_updated = pyqtSignal(float)
    memory_updated = pyqtSignal(float, float)  # used_mb, total_mb
    network_updated = pyqtSignal(float, float)  # bytes_sent, bytes_recv

    def __init__(self):
        super().__init__()
        self.running = False
        self.update_interval = 1.0  # seconds
        self.network_counters = None

    def run(self):
        """Main monitoring loop"""
        self.running = True
        self.network_counters = psutil.net_io_counters()

        while self.running:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=None)
                self.cpu_updated.emit(cpu_percent)

                # Memory usage
                memory = psutil.virtual_memory()
                used_mb = memory.used / 1024 / 1024
                total_mb = memory.total / 1024 / 1024
                self.memory_updated.emit(used_mb, total_mb)

                # Network activity
                new_counters = psutil.net_io_counters()
                if self.network_counters:
                    sent_rate = (new_counters.bytes_sent - self.network_counters.bytes_sent) / self.update_interval
                    recv_rate = (new_counters.bytes_recv - self.network_counters.bytes_recv) / self.update_interval
                    self.network_updated.emit(sent_rate, recv_rate)

                self.network_counters = new_counters

                # Sleep for update interval
                time.sleep(self.update_interval)

            except Exception as e:
                print(f"Performance monitoring error: {e}")
                break

    def stop(self):
        """Stop monitoring"""
        self.running = False

class ResourceOptimizer(QObject):
    """Optimize resource usage for DAB+ reception"""

    optimization_applied = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.original_priority = None

    def optimize_for_realtime(self, process_name="welle-io"):
        """Apply real-time optimizations"""
        optimizations = []

        try:
            # Find the process
            for proc in psutil.process_iter(['pid', 'name']):
                if process_name.lower() in proc.info['name'].lower():
                    process = psutil.Process(proc.info['pid'])

                    # Store original priority
                    self.original_priority = process.nice()

                    # Set higher priority (lower nice value)
                    if self.original_priority > -10:
                        try:
                            process.nice(-5)  # Higher priority
                            optimizations.append(f"Set process priority to -5 (was {self.original_priority})")
                        except PermissionError:
                            optimizations.append("Could not change process priority (requires sudo)")

                    # Set CPU affinity to specific cores if multi-core
                    cpu_count = psutil.cpu_count()
                    if cpu_count > 2:
                        try:
                            # Use last 2 cores for real-time processing
                            affinity = list(range(cpu_count-2, cpu_count))
                            process.cpu_affinity(affinity)
                            optimizations.append(f"Set CPU affinity to cores {affinity}")
                        except:
                            optimizations.append("Could not set CPU affinity")

                    break

            # System-level optimizations
            optimizations.extend(self._apply_system_optimizations())

        except Exception as e:
            optimizations.append(f"Optimization error: {e}")

        # Emit results
        for opt in optimizations:
            self.optimization_applied.emit(opt)

        return optimizations

    def _apply_system_optimizations(self):
        """Apply system-level optimizations"""
        optimizations = []

        try:
            # Disable CPU frequency scaling if possible
            import subprocess

            # Check current CPU governor
            try:
                result = subprocess.run(['cat', '/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor'],
                                      capture_output=True, text=True)
                current_governor = result.stdout.strip()

                if current_governor != 'performance':
                    optimizations.append(f"CPU governor: {current_governor} (consider 'performance' for real-time)")
                else:
                    optimizations.append("CPU governor: performance (optimal)")

            except:
                optimizations.append("Could not check CPU governor")

            # Check swap usage
            swap = psutil.swap_memory()
            if swap.percent > 10:
                optimizations.append(f"Warning: {swap.percent:.1f}% swap usage detected")
            else:
                optimizations.append("Swap usage: optimal")

        except Exception as e:
            optimizations.append(f"System optimization check failed: {e}")

        return optimizations

class PerformanceDashboard(QMainWindow):
    """Complete performance monitoring dashboard"""

    def __init__(self):
        super().__init__()
        self.monitor = PerformanceMonitor()
        self.optimizer = ResourceOptimizer()
        self.init_ui()
        self.init_plots()
        self.connect_signals()

        # Data storage for plots
        self.cpu_data = deque(maxlen=60)
        self.memory_data = deque(maxlen=60)
        self.network_sent_data = deque(maxlen=60)
        self.network_recv_data = deque(maxlen=60)
        self.time_data = deque(maxlen=60)

    def init_ui(self):
        self.setWindowTitle('DAB+ Performance Monitor')
        self.setGeometry(100, 100, 1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Control panel
        control_layout = QHBoxLayout()

        self.start_button = QPushButton('Start Monitoring')
        self.start_button.clicked.connect(self.start_monitoring)
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop Monitoring')
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)

        self.optimize_button = QPushButton('Optimize for Real-time')
        self.optimize_button.clicked.connect(self.apply_optimizations)
        control_layout.addWidget(self.optimize_button)

        control_layout.addStretch()
        main_layout.addLayout(control_layout)

        # Status indicators
        status_layout = QGridLayout()

        # CPU indicator
        status_layout.addWidget(QLabel('CPU Usage:'), 0, 0)
        self.cpu_label = QLabel('0.0%')
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        status_layout.addWidget(self.cpu_label, 0, 1)
        status_layout.addWidget(self.cpu_bar, 0, 2)

        # Memory indicator
        status_layout.addWidget(QLabel('Memory:'), 1, 0)
        self.memory_label = QLabel('0 MB / 0 MB')
        self.memory_bar = QProgressBar()
        status_layout.addWidget(self.memory_label, 1, 1)
        status_layout.addWidget(self.memory_bar, 1, 2)

        # Network indicators
        status_layout.addWidget(QLabel('Network:'), 2, 0)
        self.network_label = QLabel('↑ 0 B/s ↓ 0 B/s')
        status_layout.addWidget(self.network_label, 2, 1, 1, 2)

        main_layout.addLayout(status_layout)

        # Plot area
        self.plot_widget = pg.GraphicsLayoutWidget()
        main_layout.addWidget(self.plot_widget)

        # Optimization log
        main_layout.addWidget(QLabel('Optimization Log:'))
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        main_layout.addWidget(self.log_text)

    def init_plots(self):
        """Initialize performance plots"""
        # CPU plot
        self.cpu_plot = self.plot_widget.addPlot(title="CPU Usage (%)")
        self.cpu_plot.setLabel('left', 'Percentage')
        self.cpu_plot.setLabel('bottom', 'Time (s)')
        self.cpu_plot.setYRange(0, 100)
        self.cpu_curve = self.cpu_plot.plot(pen='r')

        self.plot_widget.nextRow()

        # Memory plot
        self.memory_plot = self.plot_widget.addPlot(title="Memory Usage (MB)")
        self.memory_plot.setLabel('left', 'MB')
        self.memory_plot.setLabel('bottom', 'Time (s)')
        self.memory_curve = self.memory_plot.plot(pen='b')

        self.plot_widget.nextRow()

        # Network plot
        self.network_plot = self.plot_widget.addPlot(title="Network Activity (B/s)")
        self.network_plot.setLabel('left', 'Bytes/second')
        self.network_plot.setLabel('bottom', 'Time (s)')
        self.network_sent_curve = self.network_plot.plot(pen='g', name='Sent')
        self.network_recv_curve = self.network_plot.plot(pen='m', name='Received')

    def connect_signals(self):
        """Connect monitor signals"""
        self.monitor.cpu_updated.connect(self.update_cpu)
        self.monitor.memory_updated.connect(self.update_memory)
        self.monitor.network_updated.connect(self.update_network)
        self.optimizer.optimization_applied.connect(self.log_optimization)

    @pyqtSlot()
    def start_monitoring(self):
        """Start performance monitoring"""
        self.monitor.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.log_optimization("Performance monitoring started")

    @pyqtSlot()
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitor.stop()
        self.monitor.wait()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.log_optimization("Performance monitoring stopped")

    @pyqtSlot()
    def apply_optimizations(self):
        """Apply real-time optimizations"""
        self.optimizer.optimize_for_realtime()

    @pyqtSlot(float)
    def update_cpu(self, cpu_percent):
        """Update CPU display"""
        self.cpu_label.setText(f'{cpu_percent:.1f}%')
        self.cpu_bar.setValue(int(cpu_percent))

        # Update plot data
        current_time = time.time()
        if not self.time_data or current_time - self.time_data[-1] >= 1.0:
            self.cpu_data.append(cpu_percent)
            self.time_data.append(current_time)

            # Update plot
            if len(self.time_data) > 1:
                time_range = [t - self.time_data[0] for t in self.time_data]
                self.cpu_curve.setData(time_range, list(self.cpu_data))

    @pyqtSlot(float, float)
    def update_memory(self, used_mb, total_mb):
        """Update memory display"""
        self.memory_label.setText(f'{used_mb:.0f} MB / {total_mb:.0f} MB')
        usage_percent = (used_mb / total_mb) * 100
        self.memory_bar.setRange(0, int(total_mb))
        self.memory_bar.setValue(int(used_mb))

        # Update plot data
        if len(self.cpu_data) == len(self.memory_data) + 1:
            self.memory_data.append(used_mb)

            # Update plot
            if len(self.time_data) > 1:
                time_range = [t - self.time_data[0] for t in self.time_data]
                self.memory_curve.setData(time_range[-len(self.memory_data):],
                                        list(self.memory_data))

    @pyqtSlot(float, float)
    def update_network(self, sent_rate, recv_rate):
        """Update network display"""
        def format_bytes(bytes_val):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_val < 1024:
                    return f'{bytes_val:.1f} {unit}'
                bytes_val /= 1024
            return f'{bytes_val:.1f} TB'

        self.network_label.setText(
            f'↑ {format_bytes(sent_rate)}/s ↓ {format_bytes(recv_rate)}/s'
        )

        # Update plot data
        if len(self.cpu_data) == len(self.network_sent_data) + 1:
            self.network_sent_data.append(sent_rate)
            self.network_recv_data.append(recv_rate)

            # Update plot
            if len(self.time_data) > 1:
                time_range = [t - self.time_data[0] for t in self.time_data]
                self.network_sent_curve.setData(time_range[-len(self.network_sent_data):],
                                               list(self.network_sent_data))
                self.network_recv_curve.setData(time_range[-len(self.network_recv_data):],
                                               list(self.network_recv_data))

    @pyqtSlot(str)
    def log_optimization(self, message):
        """Log optimization message"""
        timestamp = time.strftime('%H:%M:%S')
        self.log_text.append(f'[{timestamp}] {message}')

        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def closeEvent(self, event):
        """Clean shutdown"""
        if self.monitor.running:
            self.monitor.stop()
            self.monitor.wait()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dashboard = PerformanceDashboard()
    dashboard.show()
    sys.exit(app.exec_())
```

### Key Performance Optimization Tips:

1. **Threading Strategy**:
   - Use QThread for I/O operations (RTL-SDR, welle.io)
   - Keep GUI updates on main thread
   - Use signals/slots for thread communication

2. **Resource Management**:
   - Monitor CPU and memory usage
   - Set appropriate process priorities
   - Use CPU affinity for real-time processes

3. **Audio Optimization**:
   - Use larger audio buffers for stability
   - Choose appropriate audio backend (ALSA vs PulseAudio)
   - Monitor audio dropouts and adjust accordingly

4. **Network Efficiency**:
   - Monitor network usage for streaming
   - Implement efficient data structures for metadata
   - Cache slideshow images appropriately
