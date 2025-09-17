#!/usr/bin/env python3
"""
RTL-SDR GUI Testing Application
Solution for Lab 1 Trap 1.4: GUI Threading Challenge
"""

import sys
import subprocess
import time
import json
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RTLTestWorker(QThread):
    """Worker thread for RTL-SDR testing"""

    # Signals for communication with main thread
    progress_updated = pyqtSignal(str)
    test_completed = pyqtSignal(bool, str, dict)
    device_found = pyqtSignal(int, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, device_index=0, test_duration=10):
        super().__init__()
        self.device_index = device_index
        self.test_duration = test_duration
        self.is_running = False
        self.should_stop = False

    def run(self):
        """Main thread execution"""
        self.is_running = True
        self.should_stop = False

        try:
            # Step 1: Device detection
            self.progress_updated.emit("🔍 Detecting RTL-SDR devices...")
            device_count = self._detect_devices()

            if device_count == 0:
                self.test_completed.emit(False, "No RTL-SDR devices found", {})
                return

            # Step 2: Device information
            self.progress_updated.emit(f"📡 Found {device_count} device(s), getting info...")
            device_info = self._get_device_info()

            # Step 3: Basic functionality test
            self.progress_updated.emit("⚡ Testing basic device functionality...")
            basic_test = self._test_basic_functionality()

            if not basic_test['success']:
                self.test_completed.emit(False, basic_test['error'], device_info)
                return

            # Step 4: Sample rate test
            self.progress_updated.emit("📊 Testing sample rates...")
            sample_rate_test = self._test_sample_rates()

            # Step 5: Frequency range test
            self.progress_updated.emit("📻 Testing frequency range...")
            frequency_test = self._test_frequency_range()

            # Step 6: Signal quality test
            self.progress_updated.emit("📈 Testing signal quality...")
            quality_test = self._test_signal_quality()

            # Compile results
            test_results = {
                'device_count': device_count,
                'device_info': device_info,
                'basic_test': basic_test,
                'sample_rate_test': sample_rate_test,
                'frequency_test': frequency_test,
                'quality_test': quality_test,
                'test_timestamp': datetime.now().isoformat()
            }

            # Overall success
            overall_success = all([
                basic_test['success'],
                sample_rate_test['success'],
                frequency_test['success']
            ])

            message = "All tests passed!" if overall_success else "Some tests failed"
            self.test_completed.emit(overall_success, message, test_results)

        except Exception as e:
            self.error_occurred.emit(f"Test execution error: {str(e)}")

        finally:
            self.is_running = False

    def _detect_devices(self):
        """Detect RTL-SDR devices"""
        try:
            if self.should_stop:
                return 0

            result = subprocess.run(
                ['rtl_test', '-t'],
                capture_output=True, text=True, timeout=10
            )

            if "Found" in result.stdout:
                import re
                match = re.search(r'Found (\d+)', result.stdout)
                if match:
                    count = int(match.group(1))
                    self.device_found.emit(count, result.stdout)
                    return count

            return 0

        except subprocess.TimeoutExpired:
            self.error_occurred.emit("Device detection timed out")
            return 0
        except Exception as e:
            self.error_occurred.emit(f"Device detection failed: {str(e)}")
            return 0

    def _get_device_info(self):
        """Get detailed device information"""
        device_info = {}

        try:
            if self.should_stop:
                return device_info

            # Get device info using rtl_eeprom
            result = subprocess.run(
                ['rtl_eeprom', '-d', str(self.device_index)],
                capture_output=True, text=True, timeout=5
            )

            # Parse device information
            for line in result.stdout.split('\n'):
                if 'Vendor ID:' in line:
                    device_info['vendor_id'] = line.split(':')[1].strip()
                elif 'Product ID:' in line:
                    device_info['product_id'] = line.split(':')[1].strip()
                elif 'Manufacturer:' in line:
                    device_info['manufacturer'] = line.split(':')[1].strip()
                elif 'Product:' in line:
                    device_info['product'] = line.split(':')[1].strip()
                elif 'Serial number:' in line:
                    device_info['serial'] = line.split(':')[1].strip()

        except Exception as e:
            device_info['error'] = str(e)

        return device_info

    def _test_basic_functionality(self):
        """Test basic device functionality"""
        try:
            if self.should_stop:
                return {'success': False, 'error': 'Test cancelled'}

            # Quick read test
            result = subprocess.run(
                ['rtl_test', '-d', str(self.device_index), '-t'],
                capture_output=True, text=True, timeout=15
            )

            if result.returncode == 0:
                return {
                    'success': True,
                    'output': result.stdout,
                    'message': 'Basic functionality test passed'
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr or 'Basic test failed',
                    'output': result.stdout
                }

        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Basic test timed out'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _test_sample_rates(self):
        """Test various sample rates"""
        sample_rates = [250000, 1024000, 2048000, 2400000]
        results = {}

        for rate in sample_rates:
            if self.should_stop:
                break

            try:
                self.progress_updated.emit(f"Testing sample rate: {rate/1000:.0f} kHz")

                result = subprocess.run(
                    ['rtl_test', '-d', str(self.device_index), '-s', str(rate), '-t'],
                    capture_output=True, text=True, timeout=5
                )

                results[rate] = {
                    'success': result.returncode == 0,
                    'error': result.stderr if result.returncode != 0 else None
                }

            except subprocess.TimeoutExpired:
                results[rate] = {'success': False, 'error': 'Timeout'}
            except Exception as e:
                results[rate] = {'success': False, 'error': str(e)}

        successful_rates = [rate for rate, result in results.items() if result['success']]

        return {
            'success': len(successful_rates) > 0,
            'results': results,
            'successful_rates': successful_rates,
            'recommended_rate': max(successful_rates) if successful_rates else None
        }

    def _test_frequency_range(self):
        """Test frequency tuning range"""
        test_frequencies = [
            88000000,    # 88 MHz (FM)
            174000000,   # 174 MHz (DAB+)
            433000000,   # 433 MHz (ISM)
            868000000,   # 868 MHz (ISM)
            1090000000   # 1090 MHz (ADS-B)
        ]

        results = {}

        for freq in test_frequencies:
            if self.should_stop:
                break

            try:
                freq_mhz = freq / 1000000
                self.progress_updated.emit(f"Testing frequency: {freq_mhz:.0f} MHz")

                result = subprocess.run(
                    ['rtl_test', '-d', str(self.device_index), '-f', str(freq), '-t'],
                    capture_output=True, text=True, timeout=3
                )

                results[freq] = {
                    'success': result.returncode == 0,
                    'error': result.stderr if result.returncode != 0 else None
                }

                time.sleep(0.1)  # Brief pause between tests

            except subprocess.TimeoutExpired:
                results[freq] = {'success': False, 'error': 'Timeout'}
            except Exception as e:
                results[freq] = {'success': False, 'error': str(e)}

        successful_freqs = [freq for freq, result in results.items() if result['success']]

        return {
            'success': len(successful_freqs) > 0,
            'results': results,
            'successful_frequencies': successful_freqs,
            'frequency_range': {
                'min_mhz': min(successful_freqs) / 1000000 if successful_freqs else None,
                'max_mhz': max(successful_freqs) / 1000000 if successful_freqs else None
            }
        }

    def _test_signal_quality(self):
        """Test signal quality and stability"""
        try:
            if self.should_stop:
                return {'success': False, 'error': 'Test cancelled'}

            self.progress_updated.emit("Testing signal stability...")

            # Short signal capture test
            result = subprocess.run(
                ['rtl_test', '-d', str(self.device_index), '-s', '2048000', '-t'],
                capture_output=True, text=True, timeout=self.test_duration
            )

            # Parse output for quality metrics
            output_lines = result.stdout.split('\n')
            quality_metrics = {}

            for line in output_lines:
                if 'lost' in line.lower():
                    # Look for lost samples
                    import re
                    lost_match = re.search(r'(\d+).*lost', line)
                    if lost_match:
                        quality_metrics['lost_samples'] = int(lost_match.group(1))

            quality_metrics['output_lines'] = len(output_lines)
            quality_metrics['test_duration'] = self.test_duration

            return {
                'success': result.returncode == 0,
                'quality_metrics': quality_metrics,
                'raw_output': result.stdout[:500]  # First 500 chars
            }

        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Quality test timed out'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def stop_test(self):
        """Request test to stop"""
        self.should_stop = True

class RTLTesterGUI(QMainWindow):
    """Main GUI application for RTL-SDR testing"""

    def __init__(self):
        super().__init__()
        self.worker = None
        self.test_results = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('RTL-SDR Comprehensive Tester')
        self.setGeometry(100, 100, 800, 600)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Control panel
        control_group = QGroupBox("Test Configuration")
        control_layout = QGridLayout(control_group)

        # Device selection
        control_layout.addWidget(QLabel("Device Index:"), 0, 0)
        self.device_spinbox = QSpinBox()
        self.device_spinbox.setRange(0, 10)
        control_layout.addWidget(self.device_spinbox, 0, 1)

        # Test duration
        control_layout.addWidget(QLabel("Test Duration (s):"), 0, 2)
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setRange(5, 60)
        self.duration_spinbox.setValue(10)
        control_layout.addWidget(self.duration_spinbox, 0, 3)

        layout.addWidget(control_group)

        # Progress display
        progress_group = QGroupBox("Test Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.hide()
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready to test")
        progress_layout.addWidget(self.status_label)

        layout.addWidget(progress_group)

        # Results display
        results_group = QGroupBox("Test Results")
        results_layout = QVBoxLayout(results_group)

        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(['Test', 'Status', 'Details'])
        self.results_tree.setAlternatingRowColors(True)
        results_layout.addWidget(self.results_tree)

        layout.addWidget(results_group)

        # Control buttons
        button_layout = QHBoxLayout()

        self.start_button = QPushButton('🚀 Start Comprehensive Test')
        self.start_button.clicked.connect(self.start_test)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('⏹️ Stop Test')
        self.stop_button.clicked.connect(self.stop_test)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        self.save_button = QPushButton('💾 Save Results')
        self.save_button.clicked.connect(self.save_results)
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)

        self.clear_button = QPushButton('🗑️ Clear Results')
        self.clear_button.clicked.connect(self.clear_results)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)

        # Status bar
        self.statusBar().showMessage("RTL-SDR Tester Ready")

    @pyqtSlot()
    def start_test(self):
        """Start comprehensive RTL-SDR test"""
        if self.worker and self.worker.isRunning():
            return

        # Get test parameters
        device_index = self.device_spinbox.value()
        test_duration = self.duration_spinbox.value()

        # Create and configure worker
        self.worker = RTLTestWorker(device_index, test_duration)

        # Connect signals
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.test_completed.connect(self.test_finished)
        self.worker.device_found.connect(self.device_detected)
        self.worker.error_occurred.connect(self.show_error)

        # Update UI state
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.progress_bar.show()
        self.clear_results()

        # Start test
        self.worker.start()
        self.statusBar().showMessage("Testing in progress...")

    @pyqtSlot()
    def stop_test(self):
        """Stop current test"""
        if self.worker and self.worker.isRunning():
            self.worker.stop_test()
            self.worker.wait(5000)  # Wait up to 5 seconds

        self.test_finished(False, "Test stopped by user", {})

    @pyqtSlot(str)
    def update_progress(self, message):
        """Update progress display"""
        self.status_label.setText(message)
        self.statusBar().showMessage(message)

    @pyqtSlot(int, str)
    def device_detected(self, count, details):
        """Handle device detection"""
        item = QTreeWidgetItem(['Device Detection', '✅ Success', f'{count} device(s) found'])
        self.results_tree.addTopLevelItem(item)

    @pyqtSlot(bool, str, dict)
    def test_finished(self, success, message, results):
        """Handle test completion"""
        self.test_results = results

        # Update UI state
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.save_button.setEnabled(True)
        self.progress_bar.hide()

        # Update status
        status_icon = "✅" if success else "❌"
        self.status_label.setText(f"{status_icon} {message}")
        self.statusBar().showMessage(f"Test completed: {message}")

        # Display detailed results
        self._display_test_results(results)

    def _display_test_results(self, results):
        """Display detailed test results in tree widget"""
        if not results:
            return

        # Basic test results
        if 'basic_test' in results:
            basic = results['basic_test']
            status = "✅ Pass" if basic['success'] else "❌ Fail"
            details = basic.get('message', basic.get('error', 'No details'))
            item = QTreeWidgetItem(['Basic Functionality', status, details])
            self.results_tree.addTopLevelItem(item)

        # Sample rate test results
        if 'sample_rate_test' in results:
            sample_test = results['sample_rate_test']
            status = "✅ Pass" if sample_test['success'] else "❌ Fail"

            parent_item = QTreeWidgetItem(['Sample Rate Tests', status, ''])
            self.results_tree.addTopLevelItem(parent_item)

            for rate, result in sample_test.get('results', {}).items():
                rate_status = "✅ Pass" if result['success'] else "❌ Fail"
                error_info = result.get('error', 'OK')
                child_item = QTreeWidgetItem([f'{rate/1000:.0f} kHz', rate_status, error_info])
                parent_item.addChild(child_item)

        # Frequency test results
        if 'frequency_test' in results:
            freq_test = results['frequency_test']
            status = "✅ Pass" if freq_test['success'] else "❌ Fail"

            parent_item = QTreeWidgetItem(['Frequency Tests', status, ''])
            self.results_tree.addTopLevelItem(parent_item)

            for freq, result in freq_test.get('results', {}).items():
                freq_status = "✅ Pass" if result['success'] else "❌ Fail"
                error_info = result.get('error', 'OK')
                freq_mhz = freq / 1000000
                child_item = QTreeWidgetItem([f'{freq_mhz:.0f} MHz', freq_status, error_info])
                parent_item.addChild(child_item)

        # Device info
        if 'device_info' in results:
            device_info = results['device_info']
            if device_info:
                parent_item = QTreeWidgetItem(['Device Information', 'ℹ️ Info', ''])
                self.results_tree.addTopLevelItem(parent_item)

                for key, value in device_info.items():
                    if key != 'error':
                        child_item = QTreeWidgetItem([key.title(), '', str(value)])
                        parent_item.addChild(child_item)

        # Expand all items
        self.results_tree.expandAll()

    @pyqtSlot(str)
    def show_error(self, error_message):
        """Show error message"""
        QMessageBox.critical(self, "Test Error", error_message)
        self.statusBar().showMessage(f"Error: {error_message}")

    @pyqtSlot()
    def save_results(self):
        """Save test results to file"""
        if not self.test_results:
            QMessageBox.information(self, "No Results", "No test results to save")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Test Results",
            f"rtl_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )

        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.test_results, f, indent=2)

                QMessageBox.information(self, "Results Saved", f"Test results saved to:\n{filename}")

            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save results:\n{str(e)}")

    @pyqtSlot()
    def clear_results(self):
        """Clear test results display"""
        self.results_tree.clear()
        self.test_results = {}
        self.status_label.setText("Ready to test")

    def closeEvent(self, event):
        """Handle application close"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, "Test Running",
                "A test is currently running. Stop it and exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.worker.stop_test()
                self.worker.wait(3000)
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("RTL-SDR Tester")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("DAB+ Labs")

    # Create and show main window
    window = RTLTesterGUI()
    window.show()

    # Run application
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()