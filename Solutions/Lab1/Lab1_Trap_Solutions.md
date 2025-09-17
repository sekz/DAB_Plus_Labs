# Lab 1 Trap Exercise Solutions

## Overview
This document contains comprehensive solutions for all trap exercises in Lab 1. Python implementation files are provided separately in this directory.

### Implementation Files:
- `rtl_device_detector.py` - Hardware detection implementation
- `driver_permission_manager.py` - Driver and permission management
- `ppm_calibrator.py` - PPM calibration tools
- `rtl_tester_gui.py` - Complete GUI threading example

## Trap 1.1 Solution: Hardware Detection Challenge

### Expected Analysis:
Students should identify RTL-SDR dongles using multiple methods:

```bash
# USB device detection
lsusb | grep -i "realtek\|rtl\|generic"
# Expected output patterns:
# Bus 001 Device 003: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T
# Bus 001 Device 004: ID 0bda:2832 Realtek Semiconductor Corp. RTL2832U DVB-T

# Kernel module check
lsmod | grep dvb_usb_rtl28xxu
dmesg | tail -20 | grep -i rtl

# Device node verification
ls -la /dev/swradio*
```

### Code Implementation:
```python
import subprocess
import re

def detect_rtlsdr_devices():
    """Comprehensive RTL-SDR device detection"""
    devices = []

    # Method 1: lsusb parsing
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if re.search(r'(0bda:2838|0bda:2832|RTL28)', line, re.IGNORECASE):
                devices.append({
                    'method': 'USB',
                    'info': line.strip(),
                    'bus': re.search(r'Bus (\d+)', line).group(1) if re.search(r'Bus (\d+)', line) else 'Unknown',
                    'device': re.search(r'Device (\d+)', line).group(1) if re.search(r'Device (\d+)', line) else 'Unknown'
                })
    except Exception as e:
        print(f"USB detection failed: {e}")

    # Method 2: rtl_test verification
    try:
        result = subprocess.run(['rtl_test', '-t'], capture_output=True, text=True, timeout=5)
        if "Found" in result.stdout:
            device_count = re.search(r'Found (\d+)', result.stdout)
            if device_count:
                devices.append({
                    'method': 'rtl_test',
                    'count': device_count.group(1),
                    'info': result.stdout.split('\n')[0]
                })
    except Exception as e:
        print(f"rtl_test detection failed: {e}")

    return devices
```

## Trap 1.2 Solution: Driver Permission Investigation

### Blacklist Analysis:
```bash
# Check current blacklist
cat /etc/modprobe.d/blacklist-rtl.conf
# Expected content:
# blacklist dvb_usb_rtl28xxu
# blacklist rtl2832
# blacklist rtl2830

# Verify modules are not loaded
lsmod | grep -E "(dvb_usb_rtl28xxu|rtl283)"
# Should return empty if properly blacklisted

# Test without blacklist (demonstration only)
sudo modprobe -r dvb_usb_rtl28xxu  # Remove if loaded
sudo modprobe dvb_usb_rtl28xxu     # Load DVB driver
rtl_test -t  # Should fail or show different behavior
```

### Permission Management Code:
```python
import os
import grp
import pwd

def check_user_permissions():
    """Check if user has proper permissions for RTL-SDR access"""
    current_user = pwd.getpwuid(os.getuid()).pw_name
    user_groups = [g.gr_name for g in grp.getgrall() if current_user in g.gr_mem]

    required_groups = ['plugdev', 'dialout']  # Common groups for hardware access
    missing_groups = [group for group in required_groups if group not in user_groups]

    return {
        'user': current_user,
        'groups': user_groups,
        'missing_groups': missing_groups,
        'has_access': len(missing_groups) == 0
    }

def create_udev_rule():
    """Generate udev rule for RTL-SDR access"""
    rule_content = '''# RTL-SDR udev rules
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", GROUP="plugdev", MODE="0666", SYMLINK+="rtl_sdr"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2832", GROUP="plugdev", MODE="0666", SYMLINK+="rtl_sdr"
'''
    return rule_content
```

## Trap 1.3 Solution: PPM Calibration Analysis

### GSM Calibration Method:
```bash
# Find strong GSM signal
rtl_power -f 900M:1000M:1000 -i 10 -1 gsm_scan.csv
# Analyze results to find strongest signal

# Calibrate using strong GSM downlink
kal -s GSM900  # Scan for GSM signals
kal -c 75 -v   # Calibrate using channel 75 (example)
# Expected output will show PPM offset
```

### Calibration Code Implementation:
```python
import subprocess
import re
import numpy as np

class PPMCalibrator:
    def __init__(self):
        self.ppm_offset = 0
        self.calibration_history = []

    def scan_gsm_channels(self, band='GSM900'):
        """Scan for available GSM channels"""
        try:
            result = subprocess.run(['kal', '-s', band],
                                  capture_output=True, text=True, timeout=60)

            channels = []
            for line in result.stdout.split('\n'):
                if 'chan:' in line:
                    channel_match = re.search(r'chan:\s*(\d+)', line)
                    power_match = re.search(r'power:\s*([\d.-]+)', line)
                    if channel_match and power_match:
                        channels.append({
                            'channel': int(channel_match.group(1)),
                            'power': float(power_match.group(1))
                        })

            # Sort by power (strongest first)
            return sorted(channels, key=lambda x: x['power'], reverse=True)

        except Exception as e:
            print(f"GSM scan failed: {e}")
            return []

    def calibrate_ppm(self, channel):
        """Calibrate PPM using specific GSM channel"""
        try:
            result = subprocess.run(['kal', '-c', str(channel), '-v'],
                                  capture_output=True, text=True, timeout=30)

            # Parse PPM offset from output
            ppm_match = re.search(r'average\s+absolute\s+error:\s+([-\d.]+)\s+ppm', result.stdout)
            if ppm_match:
                self.ppm_offset = float(ppm_match.group(1))
                self.calibration_history.append({
                    'channel': channel,
                    'ppm_offset': self.ppm_offset,
                    'output': result.stdout
                })
                return self.ppm_offset

        except Exception as e:
            print(f"PPM calibration failed: {e}")
            return None

    def apply_calibration(self, base_frequency):
        """Apply PPM correction to frequency"""
        corrected_freq = base_frequency * (1 + self.ppm_offset / 1000000)
        return corrected_freq
```

## Trap 1.4 Solution: GUI Threading Challenge

### Proper Threading Implementation:
```python
import sys
import subprocess
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RTLTestWorker(QThread):
    """Worker thread for RTL-SDR testing to prevent GUI blocking"""

    # Signals for communication with main thread
    progress_updated = pyqtSignal(str)
    test_completed = pyqtSignal(bool, str)
    device_found = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        self.is_running = False

    def run(self):
        """Main thread execution"""
        self.is_running = True
        self.progress_updated.emit("Starting RTL-SDR detection...")

        try:
            # Step 1: Device detection
            self.progress_updated.emit("Detecting USB devices...")
            result = subprocess.run(['rtl_test', '-t'],
                                  capture_output=True, text=True, timeout=10)

            if "Found" in result.stdout:
                device_count = int(result.stdout.split()[1])
                self.device_found.emit(device_count, result.stdout)

                if device_count > 0:
                    # Step 2: Basic functionality test
                    self.progress_updated.emit("Testing device functionality...")
                    time.sleep(1)  # Simulate test time

                    # Step 3: Quick read test
                    self.progress_updated.emit("Performing quick read test...")
                    test_result = subprocess.run(['rtl_test', '-s', '2048000', '-t'],
                                               capture_output=True, text=True, timeout=5)

                    if test_result.returncode == 0:
                        self.test_completed.emit(True, "All tests passed!")
                    else:
                        self.test_completed.emit(False, f"Test failed: {test_result.stderr}")
            else:
                self.test_completed.emit(False, "No RTL-SDR devices found")

        except subprocess.TimeoutExpired:
            self.test_completed.emit(False, "Test timeout - device may be unresponsive")
        except Exception as e:
            self.test_completed.emit(False, f"Test error: {str(e)}")

        self.is_running = False

class RTLTesterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('RTL-SDR Hardware Tester')
        self.setGeometry(100, 100, 500, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Status display
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        layout.addWidget(QLabel("Test Status:"))
        layout.addWidget(self.status_text)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Control buttons
        button_layout = QHBoxLayout()

        self.test_button = QPushButton('Start Hardware Test')
        self.test_button.clicked.connect(self.start_test)
        button_layout.addWidget(self.test_button)

        self.stop_button = QPushButton('Stop Test')
        self.stop_button.clicked.connect(self.stop_test)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

    def start_test(self):
        """Start hardware test in separate thread"""
        if self.worker and self.worker.is_running:
            return

        self.worker = RTLTestWorker()

        # Connect signals
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.test_completed.connect(self.test_finished)
        self.worker.device_found.connect(self.device_detected)

        # Update UI state
        self.test_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.show()
        self.status_text.clear()

        # Start worker thread
        self.worker.start()

    def stop_test(self):
        """Stop current test"""
        if self.worker and self.worker.is_running:
            self.worker.terminate()
            self.worker.wait()

        self.test_finished(False, "Test stopped by user")

    @pyqtSlot(str)
    def update_progress(self, message):
        """Update progress display"""
        self.status_text.append(f"[{time.strftime('%H:%M:%S')}] {message}")
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )

    @pyqtSlot(int, str)
    def device_detected(self, count, details):
        """Handle device detection"""
        self.status_text.append(f"✓ Found {count} RTL-SDR device(s)")
        self.status_text.append(f"Details: {details}")

    @pyqtSlot(bool, str)
    def test_finished(self, success, message):
        """Handle test completion"""
        if success:
            self.status_text.append(f"✓ {message}")
        else:
            self.status_text.append(f"✗ {message}")

        # Reset UI state
        self.test_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.hide()

    def closeEvent(self, event):
        """Clean up on window close"""
        if self.worker and self.worker.is_running:
            self.worker.terminate()
            self.worker.wait()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RTLTesterGUI()
    window.show()
    sys.exit(app.exec_())
```

### Key Learning Points:
1. **Never block the main GUI thread** with subprocess calls
2. **Use QThread** for background operations
3. **Communicate via signals/slots** between threads
4. **Handle thread cleanup** properly on application exit
5. **Provide user feedback** during long operations
6. **Allow user cancellation** of background tasks

### Common Threading Mistakes to Avoid:
```python
# WRONG - Blocks GUI
def bad_test():
    result = subprocess.run(['rtl_test', '-t'], timeout=30)  # GUI freezes
    return result

# CORRECT - Non-blocking
def good_test(self):
    self.worker = RTLTestWorker()
    self.worker.test_completed.connect(self.handle_result)
    self.worker.start()  # GUI remains responsive
```