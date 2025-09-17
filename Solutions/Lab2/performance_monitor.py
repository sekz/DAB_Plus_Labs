#!/usr/bin/env python3
"""
Performance Monitor Implementation
Solution for Lab 2 Trap 2.5: GUI Threading and Performance
"""

import sys
import time
import psutil
import threading
from collections import deque
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

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

    def run(self):
        """Main monitoring loop"""
        self.running = True
        network_counters = psutil.net_io_counters()

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
                if network_counters:
                    sent_rate = (new_counters.bytes_sent - network_counters.bytes_sent) / self.update_interval
                    recv_rate = (new_counters.bytes_recv - network_counters.bytes_recv) / self.update_interval
                    self.network_updated.emit(sent_rate, recv_rate)

                network_counters = new_counters
                time.sleep(self.update_interval)

            except Exception as e:
                print(f"Performance monitoring error: {e}")
                break

    def stop(self):
        """Stop monitoring"""
        self.running = False

class PerformanceDashboard(QMainWindow):
    """Performance monitoring dashboard for DAB+ applications"""

    def __init__(self):
        super().__init__()
        self.monitor = PerformanceMonitor()
        self.init_ui()
        self.connect_signals()

        # Data storage for basic plotting
        self.cpu_data = deque(maxlen=60)
        self.memory_data = deque(maxlen=60)
        self.time_data = deque(maxlen=60)

    def init_ui(self):
        self.setWindowTitle('DAB+ Performance Monitor')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Control panel
        control_layout = QHBoxLayout()

        self.start_button = QPushButton('Start Monitoring')
        self.start_button.clicked.connect(self.start_monitoring)
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop Monitoring')
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)

        layout.addLayout(control_layout)

        # Status indicators
        status_layout = QGridLayout()

        # CPU
        status_layout.addWidget(QLabel('CPU Usage:'), 0, 0)
        self.cpu_label = QLabel('0.0%')
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        status_layout.addWidget(self.cpu_label, 0, 1)
        status_layout.addWidget(self.cpu_bar, 0, 2)

        # Memory
        status_layout.addWidget(QLabel('Memory:'), 1, 0)
        self.memory_label = QLabel('0 MB / 0 MB')
        self.memory_bar = QProgressBar()
        status_layout.addWidget(self.memory_label, 1, 1)
        status_layout.addWidget(self.memory_bar, 1, 2)

        # Network
        status_layout.addWidget(QLabel('Network:'), 2, 0)
        self.network_label = QLabel('↑ 0 B/s ↓ 0 B/s')
        status_layout.addWidget(self.network_label, 2, 1, 1, 2)

        layout.addLayout(status_layout)

        # Performance log
        layout.addWidget(QLabel('Performance Log:'))
        self.log_text = QTextEdit()
        layout.addWidget(self.log_text)

    def connect_signals(self):
        """Connect monitor signals"""
        self.monitor.cpu_updated.connect(self.update_cpu)
        self.monitor.memory_updated.connect(self.update_memory)
        self.monitor.network_updated.connect(self.update_network)

    @pyqtSlot()
    def start_monitoring(self):
        """Start performance monitoring"""
        self.monitor.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.log_performance("Performance monitoring started")

    @pyqtSlot()
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitor.stop()
        self.monitor.wait()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.log_performance("Performance monitoring stopped")

    @pyqtSlot(float)
    def update_cpu(self, cpu_percent):
        """Update CPU display"""
        self.cpu_label.setText(f'{cpu_percent:.1f}%')
        self.cpu_bar.setValue(int(cpu_percent))

        if cpu_percent > 80:
            self.log_performance(f"HIGH CPU: {cpu_percent:.1f}%")

    @pyqtSlot(float, float)
    def update_memory(self, used_mb, total_mb):
        """Update memory display"""
        self.memory_label.setText(f'{used_mb:.0f} MB / {total_mb:.0f} MB')
        usage_percent = (used_mb / total_mb) * 100
        self.memory_bar.setRange(0, int(total_mb))
        self.memory_bar.setValue(int(used_mb))

        if usage_percent > 90:
            self.log_performance(f"HIGH MEMORY: {usage_percent:.1f}%")

    @pyqtSlot(float, float)
    def update_network(self, sent_rate, recv_rate):
        """Update network display"""
        def format_bytes(bytes_val):
            for unit in ['B', 'KB', 'MB']:
                if bytes_val < 1024:
                    return f'{bytes_val:.1f} {unit}'
                bytes_val /= 1024
            return f'{bytes_val:.1f} GB'

        self.network_label.setText(
            f'↑ {format_bytes(sent_rate)}/s ↓ {format_bytes(recv_rate)}/s'
        )

    def log_performance(self, message):
        """Log performance message"""
        timestamp = time.strftime('%H:%M:%S')
        self.log_text.append(f'[{timestamp}] {message}')

    def closeEvent(self, event):
        """Clean shutdown"""
        if self.monitor.running:
            self.monitor.stop()
            self.monitor.wait()
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    dashboard = PerformanceDashboard()
    dashboard.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()