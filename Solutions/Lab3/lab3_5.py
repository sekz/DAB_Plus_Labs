#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 3 Phase 5: Complete GUI Application - SOLUTION
เป้าหมาย: สร้าง complete DAB+ receiver application

Dependencies:
pip install PyQt5 pyqtgraph numpy scipy matplotlib
sudo apt install python3-pyqt5
"""

import sys
import json
import threading
import time
import os
import numpy as np
from datetime import datetime

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QGridLayout, QLabel, QPushButton,
                            QSlider, QListWidget, QListWidgetItem, QTextEdit,
                            QProgressBar, QGroupBox, QScrollArea, QFrame,
                            QSplitter, QTabWidget, QSpinBox, QComboBox)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

import pyqtgraph as pg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class SpectrumAnalyzer(QWidget):
    """Real-time spectrum analyzer widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Spectrum plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Power (dB)')
        self.plot_widget.setLabel('bottom', 'Frequency (MHz)')
        self.plot_widget.setTitle('Real-time Spectrum Analysis')
        self.plot_widget.showGrid(x=True, y=True)

        layout.addWidget(self.plot_widget)
        self.setLayout(layout)

        # Plot curve
        self.curve = self.plot_widget.plot(pen='g')

    def setup_data(self):
        # Mock spectrum data
        self.frequencies = np.linspace(184, 187, 1024)  # DAB Band III
        self.spectrum_data = np.random.normal(-80, 10, 1024)

        # Timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_spectrum)
        self.timer.start(100)  # 100ms updates

    def update_spectrum(self):
        # Simulate changing spectrum
        self.spectrum_data += np.random.normal(0, 1, 1024)
        self.spectrum_data = np.clip(self.spectrum_data, -120, -20)

        # Add DAB signal peak
        center_idx = len(self.spectrum_data) // 2
        self.spectrum_data[center_idx-10:center_idx+10] = -30 + np.random.normal(0, 2, 20)

        self.curve.setData(self.frequencies, self.spectrum_data)

class SignalQualityWidget(QWidget):
    """Signal quality indicators"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Signal strength
        self.signal_strength_label = QLabel("Signal Strength:")
        self.signal_strength_bar = QProgressBar()
        self.signal_strength_bar.setRange(0, 100)
        self.signal_strength_bar.setValue(75)

        # SNR
        self.snr_label = QLabel("SNR: 18.5 dB")
        self.snr_bar = QProgressBar()
        self.snr_bar.setRange(0, 30)
        self.snr_bar.setValue(18)

        # Bit Error Rate
        self.ber_label = QLabel("BER: 1.2e-4")
        self.ber_bar = QProgressBar()
        self.ber_bar.setRange(0, 100)
        self.ber_bar.setValue(15)

        # Frequency correction
        self.freq_corr_label = QLabel("Freq Correction: +2.3 kHz")

        layout.addWidget(self.signal_strength_label)
        layout.addWidget(self.signal_strength_bar)
        layout.addWidget(self.snr_label)
        layout.addWidget(self.snr_bar)
        layout.addWidget(self.ber_label)
        layout.addWidget(self.ber_bar)
        layout.addWidget(self.freq_corr_label)

        self.setLayout(layout)

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_quality)
        self.timer.start(1000)  # 1 second updates

    def update_quality(self):
        # Simulate changing signal quality
        signal_strength = max(0, min(100, self.signal_strength_bar.value() + np.random.randint(-5, 6)))
        snr = max(0, min(30, self.snr_bar.value() + np.random.randint(-2, 3)))
        ber = max(0, min(100, self.ber_bar.value() + np.random.randint(-3, 4)))

        self.signal_strength_bar.setValue(signal_strength)
        self.snr_bar.setValue(snr)
        self.ber_bar.setValue(ber)

        self.snr_label.setText(f"SNR: {snr/10:.1f} dB")
        self.ber_label.setText(f"BER: {ber/1000:.1e}")

        freq_corr = np.random.uniform(-5, 5)
        self.freq_corr_label.setText(f"Freq Correction: {freq_corr:+.1f} kHz")

class SlideshowViewer(QWidget):
    """MOT Slideshow viewer"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_images = []
        self.current_index = 0
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Image display
        self.image_label = QLabel()
        self.image_label.setMinimumSize(320, 240)
        self.image_label.setStyleSheet("border: 2px solid gray;")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("No slideshow images")

        # Controls
        controls_layout = QHBoxLayout()

        self.prev_button = QPushButton("◀ Previous")
        self.prev_button.clicked.connect(self.prev_image)
        self.prev_button.setEnabled(False)

        self.next_button = QPushButton("Next ▶")
        self.next_button.clicked.connect(self.next_image)
        self.next_button.setEnabled(False)

        self.image_counter = QLabel("0 / 0")

        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.image_counter)
        controls_layout.addWidget(self.next_button)

        layout.addWidget(self.image_label)
        layout.addWidget(QFrame())  # Spacer
        layout.addLayout(controls_layout)

        self.setLayout(layout)

        # Auto-advance timer
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.next_image)

    def load_images(self, image_paths):
        """Load slideshow images"""
        self.current_images = [path for path in image_paths if os.path.exists(path)]
        self.current_index = 0

        if self.current_images:
            self.show_current_image()
            self.prev_button.setEnabled(len(self.current_images) > 1)
            self.next_button.setEnabled(len(self.current_images) > 1)

            # Start auto-advance if multiple images
            if len(self.current_images) > 1:
                self.auto_timer.start(5000)  # 5 seconds
        else:
            self.image_label.setText("No slideshow images")
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.auto_timer.stop()

        self.update_counter()

    def show_current_image(self):
        """Display current image"""
        if self.current_images and 0 <= self.current_index < len(self.current_images):
            pixmap = QPixmap(self.current_images[self.current_index])
            if not pixmap.isNull():
                # Scale image to fit label
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.image_label.setText("Failed to load image")

    def prev_image(self):
        """Show previous image"""
        if self.current_images:
            self.current_index = (self.current_index - 1) % len(self.current_images)
            self.show_current_image()
            self.update_counter()

    def next_image(self):
        """Show next image"""
        if self.current_images:
            self.current_index = (self.current_index + 1) % len(self.current_images)
            self.show_current_image()
            self.update_counter()

    def update_counter(self):
        """Update image counter"""
        if self.current_images:
            self.image_counter.setText(f"{self.current_index + 1} / {len(self.current_images)}")
        else:
            self.image_counter.setText("0 / 0")

class AudioControlWidget(QWidget):
    """Audio player controls"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.media_player = QMediaPlayer()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Now playing info
        self.now_playing_label = QLabel("No service selected")
        self.now_playing_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.now_playing_label.setStyleSheet("color: blue;")

        # Dynamic Label Segment (DLS)
        self.dls_label = QLabel("Dynamic Label Segment")
        self.dls_label.setWordWrap(True)
        self.dls_label.setStyleSheet("color: darkgreen;")

        # Transport controls
        controls_layout = QHBoxLayout()

        self.play_button = QPushButton("▶ Play")
        self.play_button.clicked.connect(self.toggle_playback)
        self.play_button.setMinimumSize(80, 40)

        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.clicked.connect(self.stop_playback)
        self.stop_button.setMinimumSize(80, 40)

        # Volume control
        volume_layout = QVBoxLayout()
        volume_layout.addWidget(QLabel("Volume"))

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.valueChanged.connect(self.set_volume)

        self.volume_label = QLabel("80%")

        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_label)

        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addLayout(volume_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        layout.addWidget(self.now_playing_label)
        layout.addWidget(self.dls_label)
        layout.addLayout(controls_layout)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        # Connect media player signals
        self.media_player.stateChanged.connect(self.media_state_changed)
        self.media_player.volumeChanged.connect(self.volume_changed)

    def load_service(self, service_info, audio_file=None):
        """Load service for playback"""
        service_label = service_info.get('label', 'Unknown Service')
        self.now_playing_label.setText(f"Service: {service_label}")

        # Mock DLS data
        dls_text = f"Now playing on {service_label} • DAB+ Digital Radio"
        self.dls_label.setText(dls_text)

        # Load audio file if provided
        if audio_file and os.path.exists(audio_file):
            self.media_player.setMedia(QMediaContent())  # Clear first
            # Note: QMediaPlayer doesn't directly support file paths in all Qt versions
            # In real implementation, might need to use QUrl.fromLocalFile()

    def toggle_playback(self):
        """Toggle play/pause"""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def stop_playback(self):
        """Stop playback"""
        self.media_player.stop()

    def set_volume(self, volume):
        """Set volume level"""
        self.media_player.setVolume(volume)
        self.volume_label.setText(f"{volume}%")

    def media_state_changed(self, state):
        """Handle media player state changes"""
        if state == QMediaPlayer.PlayingState:
            self.play_button.setText("⏸ Pause")
            self.progress_bar.setVisible(True)
        else:
            self.play_button.setText("▶ Play")
            if state == QMediaPlayer.StoppedState:
                self.progress_bar.setVisible(False)

    def volume_changed(self, volume):
        """Handle volume changes"""
        self.volume_slider.setValue(volume)

class ServiceListWidget(QWidget):
    """DAB+ Service list"""

    serviceSelected = pyqtSignal(dict)  # Signal when service is selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self.services = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("DAB+ Services")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))

        # Service list
        self.service_list = QListWidget()
        self.service_list.itemClicked.connect(self.service_clicked)

        # Make list items larger for touch
        self.service_list.setStyleSheet("""
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid gray;
                font-size: 14px;
            }
            QListWidget::item:selected {
                background-color: lightblue;
            }
        """)

        # Refresh button
        self.refresh_button = QPushButton("🔄 Refresh Services")
        self.refresh_button.clicked.connect(self.refresh_services)
        self.refresh_button.setMinimumSize(150, 40)

        layout.addWidget(title_label)
        layout.addWidget(self.service_list)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)

        # Load services on startup
        self.refresh_services()

    def refresh_services(self):
        """Load services from JSON file"""
        try:
            service_file = "service_list.json"
            if os.path.exists(service_file):
                with open(service_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.services = {}
                self.service_list.clear()

                for service in data.get('services', []):
                    service_id = service['service_id']
                    service_info = {
                        'id': service_id,
                        'label': service['label'],
                        'components': service['components']
                    }

                    self.services[service_id] = service_info

                    # Add to list widget
                    item_text = f"{service['label']} (0x{service_id:04X})"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, service_id)
                    self.service_list.addItem(item)

                print(f"✓ Loaded {len(self.services)} services from lab3_3.py output")

            else:
                # Add mock services for demo
                print("Service list not found, using mock services for demonstration")
                print("Run lab3_2.py and lab3_3.py to get real service data")
                self.add_mock_services()

        except Exception as e:
            print(f"Error loading services: {e}")
            self.add_mock_services()

    def add_mock_services(self):
        """Add mock services for demonstration"""
        mock_services = [
            {"id": 0x1001, "label": "Test FM Radio", "components": []},
            {"id": 0x1002, "label": "Classical Music", "components": []},
            {"id": 0x1003, "label": "News Channel", "components": []},
            {"id": 0x1004, "label": "Jazz Station", "components": []},
        ]

        self.services = {}
        self.service_list.clear()

        for service in mock_services:
            service_id = service['id']
            self.services[service_id] = service

            item_text = f"{service['label']} (0x{service_id:04X})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, service_id)
            self.service_list.addItem(item)

    def service_clicked(self, item):
        """Handle service selection"""
        service_id = item.data(Qt.UserRole)
        if service_id in self.services:
            self.serviceSelected.emit(self.services[service_id])

class SettingsWidget(QWidget):
    """Settings panel"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # RTL-SDR Settings
        rtlsdr_group = QGroupBox("RTL-SDR Settings")
        rtlsdr_layout = QGridLayout()

        # Frequency
        rtlsdr_layout.addWidget(QLabel("Frequency (MHz):"), 0, 0)
        self.freq_spinbox = QSpinBox()
        self.freq_spinbox.setRange(170000, 240000)  # kHz
        self.freq_spinbox.setValue(185360)
        self.freq_spinbox.setSuffix(" kHz")
        rtlsdr_layout.addWidget(self.freq_spinbox, 0, 1)

        # Gain
        rtlsdr_layout.addWidget(QLabel("Gain:"), 1, 0)
        self.gain_combo = QComboBox()
        self.gain_combo.addItems(["Auto", "0 dB", "10 dB", "20 dB", "30 dB", "40 dB"])
        rtlsdr_layout.addWidget(self.gain_combo, 1, 1)

        # Sample Rate
        rtlsdr_layout.addWidget(QLabel("Sample Rate:"), 2, 0)
        self.samplerate_combo = QComboBox()
        self.samplerate_combo.addItems(["2.048 MHz", "2.4 MHz", "3.2 MHz"])
        rtlsdr_layout.addWidget(self.samplerate_combo, 2, 1)

        rtlsdr_group.setLayout(rtlsdr_layout)

        # DAB+ Settings
        dab_group = QGroupBox("DAB+ Settings")
        dab_layout = QGridLayout()

        # Ensemble
        dab_layout.addWidget(QLabel("Ensemble:"), 0, 0)
        self.ensemble_combo = QComboBox()
        self.ensemble_combo.addItems(["Auto", "Thailand Multiplex 1", "Thailand Multiplex 2"])
        dab_layout.addWidget(self.ensemble_combo, 0, 1)

        # Audio Quality
        dab_layout.addWidget(QLabel("Audio Quality:"), 1, 0)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["High", "Medium", "Low"])
        dab_layout.addWidget(self.quality_combo, 1, 1)

        dab_group.setLayout(dab_layout)

        # Apply button
        self.apply_button = QPushButton("Apply Settings")
        self.apply_button.setMinimumSize(120, 40)
        self.apply_button.clicked.connect(self.apply_settings)

        layout.addWidget(rtlsdr_group)
        layout.addWidget(dab_group)
        layout.addWidget(self.apply_button)
        layout.addStretch()

        self.setLayout(layout)

    def apply_settings(self):
        """Apply settings"""
        freq = self.freq_spinbox.value()
        gain = self.gain_combo.currentText()
        sample_rate = self.samplerate_combo.currentText()

        print(f"Applying settings:")
        print(f"  Frequency: {freq} kHz")
        print(f"  Gain: {gain}")
        print(f"  Sample Rate: {sample_rate}")

        # In real application, would apply these settings to RTL-SDR

class DABPlusGUI(QMainWindow):
    """Main DAB+ GUI Application"""

    def __init__(self):
        super().__init__()
        self.current_service = None
        self.setup_ui()
        self.setup_window()

    def setup_window(self):
        """Setup main window properties"""
        self.setWindowTitle("DAB+ Digital Radio Receiver")
        self.setGeometry(0, 0, 800, 600)  # 7" touchscreen friendly

        # Dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: white;
            }
            QWidget {
                background-color: #2b2b2b;
                color: white;
            }
            QPushButton {
                background-color: #404040;
                border: 2px solid #606060;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #606060;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #606060;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

    def setup_ui(self):
        """Setup user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left panel (Service list and controls)
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(300)

        # Service list
        self.service_list_widget = ServiceListWidget()
        self.service_list_widget.serviceSelected.connect(self.service_selected)

        # Audio controls
        self.audio_control_widget = AudioControlWidget()

        left_layout.addWidget(self.service_list_widget)
        left_layout.addWidget(self.audio_control_widget)

        # Right panel (Tabs)
        right_panel = QTabWidget()

        # Spectrum tab
        spectrum_tab = QWidget()
        spectrum_layout = QVBoxLayout()
        self.spectrum_analyzer = SpectrumAnalyzer()
        self.signal_quality_widget = SignalQualityWidget()

        spectrum_layout.addWidget(self.spectrum_analyzer, 3)  # 3/4 of space
        spectrum_layout.addWidget(self.signal_quality_widget, 1)  # 1/4 of space
        spectrum_tab.setLayout(spectrum_layout)

        # Slideshow tab
        self.slideshow_viewer = SlideshowViewer()

        # Settings tab
        self.settings_widget = SettingsWidget()

        # Add tabs
        right_panel.addTab(spectrum_tab, "📊 Spectrum")
        right_panel.addTab(self.slideshow_viewer, "🖼️ Slideshow")
        right_panel.addTab(self.settings_widget, "⚙️ Settings")

        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)

        # Status bar
        self.statusBar().showMessage("Ready - Select a service to begin")

    def service_selected(self, service_info):
        """Handle service selection"""
        self.current_service = service_info
        service_label = service_info.get('label', 'Unknown')
        service_id = service_info.get('id', 0)

        print(f"Selected service: {service_label} (0x{service_id:04X})")

        # Update audio control
        self.audio_control_widget.load_service(service_info)

        # Load slideshow images (mock)
        from lab3_4 import DABServicePlayer
        player = DABServicePlayer()
        images = player.extract_slideshow_images(service_id)
        self.slideshow_viewer.load_images(images)

        # Update status
        self.statusBar().showMessage(f"Service: {service_label}")

def main():
    """Main function"""
    print("=== Lab 3 Phase 5: Complete GUI Application ===")
    print("\nThis lab creates a complete DAB+ receiver GUI application")
    print("It integrates all previous labs into a graphical interface\n")

    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("DAB+ Digital Radio")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("DAB+ Labs")

    # Set font for touch interface
    font = QFont("Arial", 10)
    app.setFont(font)

    # Create and show main window
    window = DABPlusGUI()
    window.show()

    # For Raspberry Pi touchscreen, might want to start fullscreen
    if '--fullscreen' in sys.argv:
        window.showFullScreen()

    print("✓ DAB+ GUI Application started")
    print("\nWorkflow:")
    print("  1. Run lab3_2.py to capture DAB signal → creates dab_ensemble.eti")
    print("  2. Run lab3_3.py to analyze ETI → creates service_list.json")
    print("  3. Click 'Refresh Services' in GUI to load service_list.json")
    print("\nControls:")
    print("  - Select service from left panel")
    print("  - Use tabs to switch between spectrum, slideshow, and settings")
    print("  - Audio controls are in the left panel")
    print("  - Press Alt+F4 to exit (or use window controls)")
    print("\nNote: GUI will work with mock data if service_list.json not found")

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()