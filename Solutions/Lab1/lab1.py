#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAB 1: การติดตั้งและทดสอบ RTL-SDR - เฉลยครบถ้วน
วัตถุประสงค์: ทดสอบการเชื่อมต่อและการทำงานของ RTL-SDR dongle บน Raspberry Pi
"""

import sys
import subprocess
import time
import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QWidget, QPushButton, QTextEdit, QLabel, QProgressBar,
                            QMessageBox, QFileDialog)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPixmap

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RTLSDRTestThread(QThread):
    """Thread สำหรับทดสอบ RTL-SDR"""
    
    test_result = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    error_occurred = pyqtSignal(str)
    test_completed = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.test_results = []
        self.current_test = ""
        
    def run(self):
        """เมธอดหลักของ thread - รันการทดสอบทั้งหมด"""
        try:
            self.test_result.emit("=== เริ่มการทดสอบ RTL-SDR ===\n")
            self.progress_update.emit(0)
            
            # ขั้นตอนที่ 1: ตรวจสอบ USB device
            self.current_test = "ตรวจสอบการเชื่อมต่อ USB"
            self.test_result.emit(f"🔍 {self.current_test}...")
            success, message = self.check_usb_device()
            self.test_result.emit(f"{'✅' if success else '❌'} {message}\n")
            self.test_results.append(f"{self.current_test}: {'PASS' if success else 'FAIL'}")
            self.progress_update.emit(25)
            
            if not success:
                self.error_occurred.emit("RTL-SDR device ไม่พบ - โปรดตรวจสอบการเชื่อมต่อ")
                return
            
            # ขั้นตอนที่ 2: ตรวจสอบไดรเวอร์
            self.current_test = "ตรวจสอบไดรเวอร์"
            self.test_result.emit(f"🔍 {self.current_test}...")
            success, message = self.check_drivers()
            self.test_result.emit(f"{'✅' if success else '⚠️'} {message}\n")
            self.test_results.append(f"{self.current_test}: {'PASS' if success else 'WARNING'}")
            self.progress_update.emit(50)
            
            # ขั้นตอนที่ 3: ทดสอบการทำงานพื้นฐาน
            self.current_test = "ทดสอบการทำงานพื้นฐาน"
            self.test_result.emit(f"🔍 {self.current_test}...")
            success, message = self.test_rtlsdr_functionality()
            self.test_result.emit(f"{'✅' if success else '❌'} {message}\n")
            self.test_results.append(f"{self.current_test}: {'PASS' if success else 'FAIL'}")
            self.progress_update.emit(75)
            
            # ขั้นตอนที่ 4: ดึงข้อมูลอุปกรณ์
            self.current_test = "ดึงข้อมูลอุปกรณ์"
            self.test_result.emit(f"🔍 {self.current_test}...")
            success, message = self.get_device_info()
            self.test_result.emit(f"{'✅' if success else '❌'} {message}\n")
            self.test_results.append(f"{self.current_test}: {'PASS' if success else 'FAIL'}")
            self.progress_update.emit(100)
            
            # สรุปผลการทดสอบ
            passed = sum(1 for result in self.test_results if 'PASS' in result)
            total = len(self.test_results)
            
            self.test_result.emit("=== สรุปผลการทดสอบ ===")
            self.test_result.emit(f"ผ่าน: {passed}/{total} ข้อ")
            
            if passed == total:
                self.test_result.emit("🎉 RTL-SDR พร้อมใช้งานแล้ว!")
                self.test_completed.emit(True)
            else:
                self.test_result.emit("⚠️ พบปัญหาบางข้อ - โปรดตรวจสอบ")
                self.test_completed.emit(False)
                
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดในการทดสอบ: {str(e)}")
            self.error_occurred.emit(f"เกิดข้อผิดพลาด: {str(e)}")
    
    def check_usb_device(self):
        """ตรวจสอบการเชื่อมต่อ USB ของ RTL-SDR"""
        try:
            # ตรวจสอบด้วย lsusb
            result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                return False, "ไม่สามารถรัน lsusb ได้"
            
            usb_output = result.stdout.lower()
            
            # ตรวจหา RTL-SDR device IDs ที่รู้จัก
            known_devices = [
                ('0bda:2832', 'RTL2832U DVB-T'),
                ('0bda:2838', 'RTL2838 DVB-T'),
                ('1d50:604b', 'RTL-SDR Blog V3'),
                ('1209:2832', 'Generic RTL2832U')
            ]
            
            found_device = None
            for device_id, device_name in known_devices:
                if device_id in usb_output:
                    found_device = (device_id, device_name)
                    break
            
            if found_device:
                return True, f"พบ RTL-SDR device: {found_device[1]} (ID: {found_device[0]})"
            else:
                # ตรวจหาคีย์เวิร์ดอื่นๆ
                if 'rtl' in usb_output or 'realtek' in usb_output:
                    return True, "พบ RTL-SDR device (รุ่นไม่ระบุ)"
                else:
                    return False, "ไม่พบ RTL-SDR device - โปรดตรวจสอบการเสียบ USB"
                    
        except subprocess.TimeoutExpired:
            return False, "Timeout: lsusb ใช้เวลานานเกินไป"
        except Exception as e:
            return False, f"Error ในการตรวจสอบ USB: {str(e)}"
    
    def check_drivers(self):
        """ตรวจสอบและแก้ไขปัญหาไดรเวอร์"""
        try:
            issues = []
            warnings = []
            
            # ตรวจสอบไดรเวอร์ที่โหลดอยู่
            result = subprocess.run(['lsmod'], capture_output=True, text=True)
            loaded_modules = result.stdout.lower()
            
            # ตรวจสอบไดรเวอร์ที่อาจขัดแย้ง
            conflicting_drivers = ['dvb_usb_rtl28xxu', 'rtl2832', 'rtl2830', 'dvb_usb_rtl2832u']
            loaded_conflicts = [driver for driver in conflicting_drivers if driver in loaded_modules]
            
            if loaded_conflicts:
                warnings.append(f"พบไดรเวอร์ที่อาจขัดแย้ง: {', '.join(loaded_conflicts)}")
                
            # ตรวจสอบ blacklist
            blacklist_files = ['/etc/modprobe.d/blacklist-rtl.conf', '/etc/modprobe.d/rtl-sdr-blacklist.conf']
            blacklist_exists = any(os.path.exists(f) for f in blacklist_files)
            
            if not blacklist_exists and loaded_conflicts:
                issues.append("ควรสร้างไฟล์ blacklist สำหรับไดรเวอร์ DVB-T")
            
            # ตรวจสอบ udev rules
            udev_paths = ['/etc/udev/rules.d/20-rtlsdr.rules', '/lib/udev/rules.d/20-rtlsdr.rules']
            udev_exists = any(os.path.exists(f) for f in udev_paths)
            
            if not udev_exists:
                issues.append("ไม่พบ udev rules สำหรับ RTL-SDR")
            
            # ตรวจสอบ group membership
            try:
                result = subprocess.run(['groups'], capture_output=True, text=True)
                groups = result.stdout.lower()
                if 'plugdev' not in groups:
                    issues.append("User ไม่ได้อยู่ใน group plugdev")
            except:
                pass
            
            # สร้างข้อความตอบกลับ
            message = ""
            if not issues and not warnings:
                message = "การตั้งค่าไดรเวอร์ถูกต้อง"
                return True, message
            
            if warnings:
                message += "คำเตือน: " + "; ".join(warnings) + "\n"
            if issues:
                message += "ปัญหา: " + "; ".join(issues)
                return False, message
            else:
                return True, message
                
        except Exception as e:
            return False, f"Error ในการตรวจสอบไดรเวอร์: {str(e)}"
    
    def test_rtlsdr_functionality(self):
        """ทดสอบการทำงานของ RTL-SDR ด้วย rtl_test"""
        try:
            # ทดสอบด้วย rtl_test -t (test mode)
            result = subprocess.run(['rtl_test', '-t'], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                # แปลงผลลัพธ์
                output_lines = result.stdout.split('\n')
                success_indicators = ['found', 'success', 'supported', 'ok']
                error_indicators = ['error', 'failed', 'not found', 'permission denied']
                
                has_success = any(any(indicator in line.lower() for indicator in success_indicators) 
                                for line in output_lines)
                has_error = any(any(indicator in line.lower() for indicator in error_indicators) 
                              for line in output_lines)
                
                if has_success and not has_error:
                    # ดึงข้อมูลสำคัญจาก output
                    tuner_info = ""
                    for line in output_lines:
                        if 'tuner' in line.lower() or 'gain' in line.lower():
                            tuner_info += line.strip() + "\n"
                    
                    message = f"RTL-SDR ทำงานปกติ\n"
                    if tuner_info:
                        message += f"ข้อมูล tuner:\n{tuner_info}"
                    return True, message
                else:
                    return False, f"RTL-SDR มีปัญหา:\n{result.stdout[:300]}"
            else:
                return False, f"rtl_test failed (exit code: {result.returncode}):\n{result.stderr[:300]}"
                
        except subprocess.TimeoutExpired:
            return False, "Timeout: rtl_test ใช้เวลานานเกินไป (>15 วินาที)"
        except FileNotFoundError:
            return False, "ไม่พบ rtl_test command - โปรดติดตั้ง rtl-sdr packages"
        except Exception as e:
            return False, f"Error ในการทดสอบ RTL-SDR: {str(e)}"
    
    def get_device_info(self):
        """ดึงข้อมูลรายละเอียดของ RTL-SDR device"""
        try:
            info_dict = {}
            
            # ใช้ rtl_eeprom เพื่อดึงข้อมูลจาก EEPROM
            try:
                result = subprocess.run(['rtl_eeprom'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    # แยกข้อมูลจาก eeprom output
                    for line in result.stdout.split('\n'):
                        if ':' in line and any(key in line.lower() 
                                             for key in ['vendor', 'product', 'serial', 'tuner']):
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                key = parts[0].strip()
                                value = parts[1].strip()
                                info_dict[key] = value
            except:
                pass
            
            # ใช้ rtl_test เพื่อดึงข้อมูล tuner
            try:
                result = subprocess.run(['rtl_test', '-t'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'tuner' in line.lower():
                            info_dict['Tuner Type'] = line.strip()
                            break
            except:
                pass
            
            # สร้างข้อความแสดงข้อมูล
            if info_dict:
                message = "ข้อมูล RTL-SDR device:\n"
                for key, value in info_dict.items():
                    message += f"  {key}: {value}\n"
                return True, message
            else:
                return True, "สามารถเข้าถึงอุปกรณ์ได้ แต่ไม่สามารถดึงข้อมูลรายละเอียด"
                
        except Exception as e:
            return False, f"Error ในการดึงข้อมูลอุปกรณ์: {str(e)}"

class Lab1MainWindow(QMainWindow):
    """หน้าต่างหลักของ Lab 1"""
    
    def __init__(self):
        super().__init__()
        self.test_thread = None
        self.test_results = []
        self.setup_ui()
        self.setup_touch_interface()
        self.setup_connections()
        self.setWindowTitle("LAB 1: การติดตั้งและทดสอบ RTL-SDR")
        self.resize(800, 600)
        
    def setup_ui(self):
        """สร้าง UI elements"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # สร้าง layout หลัก
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # ชื่อแล็บ
        title_label = QLabel("LAB 1: การติดตั้งและทดสอบ RTL-SDR")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #2c3e50;
            padding: 15px;
            background-color: #ecf0f1;
            border-radius: 8px;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(title_label)
        
        # แถวปุ่มทดสอบแรก
        button_layout1 = QHBoxLayout()
        self.check_device_btn = QPushButton("🔍 ตรวจสอบอุปกรณ์")
        self.test_function_btn = QPushButton("⚡ ทดสอบการทำงาน")
        self.check_driver_btn = QPushButton("🔧 ตรวจสอบไดรเวอร์")
        
        button_layout1.addWidget(self.check_device_btn)
        button_layout1.addWidget(self.test_function_btn)
        button_layout1.addWidget(self.check_driver_btn)
        main_layout.addLayout(button_layout1)
        
        # แถวปุ่มทดสอบที่สอง
        button_layout2 = QHBoxLayout()
        self.run_all_btn = QPushButton("🚀 รันทดสอบทั้งหมด")
        self.clear_btn = QPushButton("🗑️ ล้างผลลัพธ์")
        self.save_btn = QPushButton("💾 บันทึกผล")
        
        button_layout2.addWidget(self.run_all_btn)
        button_layout2.addWidget(self.clear_btn)
        button_layout2.addWidget(self.save_btn)
        main_layout.addLayout(button_layout2)
        
        # พื้นที่แสดงผล
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                background-color: #2c3e50;
                color: #ecf0f1;
            }
        """)
        main_layout.addWidget(self.results_text, 1)  # ให้ขยายเต็มที่
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 4px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # แสดงข้อความต้อนรับ
        self.results_text.append("🎯 LAB 1: RTL-SDR Testing Laboratory")
        self.results_text.append("=" * 50)
        self.results_text.append("📋 เลือกการทดสอบจากปุ่มด้านบน")
        self.results_text.append("💡 แนะนำ: เริ่มจาก 'รันทดสอบทั้งหมด' เพื่อตรวจสอบระบบ")
        self.results_text.append("")
        
    def setup_touch_interface(self):
        """ปรับ UI สำหรับหน้าจอสัมผัส"""
        # ตั้งค่า font ขนาดใหญ่
        font = QFont()
        font.setPointSize(12)
        self.setFont(font)
        
        # ปรับขนาดปุ่มให้เหมาะกับการสัมผัส
        button_style = """
            QPushButton {
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #3498db, stop: 1 #2980b9);
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 8px;
                min-height: 50px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #5dade2, stop: 1 #3498db);
            }
            QPushButton:pressed {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #2980b9, stop: 1 #1f4e79);
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #7f8c8d;
            }
        """
        
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(button_style)
            button.setMinimumSize(120, 60)
    
    def setup_connections(self):
        """เชื่อม signals และ slots"""
        self.check_device_btn.clicked.connect(self.start_device_check)
        self.test_function_btn.clicked.connect(self.start_functionality_test)
        self.check_driver_btn.clicked.connect(self.start_driver_check)
        self.run_all_btn.clicked.connect(self.run_all_tests)
        self.clear_btn.clicked.connect(self.clear_results)
        self.save_btn.clicked.connect(self.save_results)
    
    def start_device_check(self):
        """เริ่มการตรวจสอบอุปกรณ์"""
        self.start_single_test("device")
    
    def start_functionality_test(self):
        """เริ่มการทดสอบการทำงาน"""
        self.start_single_test("function")
    
    def start_driver_check(self):
        """เริ่มการตรวจสอบไดรเวอร์"""
        self.start_single_test("driver")
    
    def start_single_test(self, test_type):
        """เริ่มการทดสอบแค่อย่างเดียว"""
        if self.test_thread and self.test_thread.isRunning():
            QMessageBox.warning(self, "คำเตือน", "การทดสอบกำลังดำเนินการอยู่")
            return
        
        self.set_buttons_enabled(False)
        self.progress_bar.setValue(0)
        
        # สร้าง thread สำหรับการทดสอบเฉพาะ
        self.test_thread = SingleTestThread(test_type)
        self.test_thread.test_result.connect(self.update_test_results)
        self.test_thread.progress_update.connect(self.update_progress)
        self.test_thread.error_occurred.connect(self.handle_test_error)
        self.test_thread.test_completed.connect(self.on_test_completed)
        self.test_thread.start()
    
    def run_all_tests(self):
        """รันการทดสอบทั้งหมด"""
        if self.test_thread and self.test_thread.isRunning():
            QMessageBox.warning(self, "คำเตือน", "การทดสอบกำลังดำเนินการอยู่")
            return
        
        self.set_buttons_enabled(False)
        self.progress_bar.setValue(0)
        self.results_text.append("\n" + "=" * 60)
        self.results_text.append(f"🚀 เริ่มการทดสอบครบชุด - {datetime.now().strftime('%H:%M:%S')}")
        self.results_text.append("=" * 60)
        
        # สร้าง thread สำหรับการทดสอบทั้งหมด
        self.test_thread = RTLSDRTestThread()
        self.test_thread.test_result.connect(self.update_test_results)
        self.test_thread.progress_update.connect(self.update_progress)
        self.test_thread.error_occurred.connect(self.handle_test_error)
        self.test_thread.test_completed.connect(self.on_test_completed)
        self.test_thread.start()
    
    def update_test_results(self, result_text):
        """อัพเดทผลการทดสอบใน UI"""
        self.results_text.append(result_text)
        # Auto-scroll ไปที่บรรทัดล่าสุด
        scrollbar = self.results_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def update_progress(self, value):
        """อัพเดทความคืบหน้า"""
        self.progress_bar.setValue(value)
    
    def handle_test_error(self, error_message):
        """จัดการกับ errors ที่เกิดขึ้น"""
        self.results_text.append(f"❌ Error: {error_message}")
        logger.error(f"Test error: {error_message}")
        self.set_buttons_enabled(True)
    
    def on_test_completed(self, success):
        """เมื่อการทดสอบเสร็จสิ้น"""
        self.set_buttons_enabled(True)
        
        if success:
            self.results_text.append("\n🎉 การทดสอบเสร็จสิ้น - ระบบพร้อมใช้งาน!")
        else:
            self.results_text.append("\n⚠️ การทดสอบเสร็จสิ้น - พบปัญหาบางข้อ")
        
        # เล่นเสียงแจ้งเตือน (ถ้ามี)
        QApplication.beep()
    
    def clear_results(self):
        """เคลียร์ผลการทดสอบ"""
        self.results_text.clear()
        self.progress_bar.setValue(0)
        self.results_text.append("🗑️ ล้างผลลัพธ์แล้ว - พร้อมสำหรับการทดสอบใหม่")
    
    def save_results(self):
        """บันทึกผลการทดสอบลงไฟล์"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"rtlsdr_test_results_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("RTL-SDR Test Results\n")
                f.write("=" * 50 + "\n")
                f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"System: Raspberry Pi OS\n\n")
                f.write(self.results_text.toPlainText())
            
            self.results_text.append(f"\n💾 บันทึกผลการทดสอบลงไฟล์: {filename}")
            QMessageBox.information(self, "สำเร็จ", f"บันทึกไฟล์สำเร็จ: {filename}")
            
        except Exception as e:
            error_msg = f"ไม่สามารถบันทึกไฟล์: {str(e)}"
            self.results_text.append(f"\n❌ {error_msg}")
            QMessageBox.critical(self, "ข้อผิดพลาด", error_msg)
    
    def set_buttons_enabled(self, enabled):
        """เปิด/ปิดการใช้งานปุ่มทั้งหมด"""
        for button in self.findChildren(QPushButton):
            button.setEnabled(enabled)

class SingleTestThread(QThread):
    """Thread สำหรับการทดสอบแบบรายข้อ"""
    
    test_result = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    error_occurred = pyqtSignal(str)
    test_completed = pyqtSignal(bool)
    
    def __init__(self, test_type):
        super().__init__()
        self.test_type = test_type
        
    def run(self):
        """รันการทดสอบตาม type"""
        try:
            self.progress_update.emit(0)
            main_thread = RTLSDRTestThread()
            
            if self.test_type == "device":
                self.test_result.emit("🔍 ตรวจสอบการเชื่อมต่อ USB...")
                success, message = main_thread.check_usb_device()
                self.test_result.emit(f"{'✅' if success else '❌'} {message}")
                
            elif self.test_type == "function":
                self.test_result.emit("⚡ ทดสอบการทำงานของ RTL-SDR...")
                success, message = main_thread.test_rtlsdr_functionality()
                self.test_result.emit(f"{'✅' if success else '❌'} {message}")
                
            elif self.test_type == "driver":
                self.test_result.emit("🔧 ตรวจสอบไดรเวอร์...")
                success, message = main_thread.check_drivers()
                self.test_result.emit(f"{'✅' if success else '⚠️'} {message}")
                
            self.progress_update.emit(100)
            self.test_completed.emit(success)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

def check_system_requirements():
    """ตรวจสอบความต้องการของระบบ"""
    issues = []
    warnings = []
    
    # ตรวจสอบ Python version
    if sys.version_info < (3, 7):
        issues.append(f"Python version {sys.version_info.major}.{sys.version_info.minor} ต่ำเกินไป (ต้องการ 3.7+)")
    
    # ตรวจสอบ PyQt5
    try:
        from PyQt5.QtCore import QT_VERSION_STR
        logger.info(f"PyQt5 version: {QT_VERSION_STR}")
    except ImportError:
        issues.append("PyQt5 ไม่ได้ติดตั้ง")
    
    # ตรวจสอบ rtl-sdr packages
    commands_to_check = ['rtl_test', 'rtl_eeprom', 'lsusb']
    for cmd in commands_to_check:
        if not subprocess.run(['which', cmd], capture_output=True).returncode == 0:
            if cmd == 'lsusb':
                warnings.append(f"คำสั่ง {cmd} ไม่พบ - อาจส่งผลต่อการตรวจสอบ")
            else:
                issues.append(f"คำสั่ง {cmd} ไม่พบ - โปรดติดตั้ง rtl-sdr packages")
    
    # ตรวจสอบ permissions
    try:
        import os
        user_groups = [g.gr_name for g in os.getgroups()]
        if 'plugdev' not in user_groups:
            warnings.append("ผู้ใช้ไม่ได้อยู่ใน group plugdev")
    except:
        pass
    
    return len(issues) == 0, issues, warnings

def main():
    """ฟังก์ชันหลัก"""
    # ตรวจสอบ system requirements ก่อน
    requirements_ok, issues, warnings = check_system_requirements()
    
    if not requirements_ok:
        print("❌ พบปัญหาในการตรวจสอบระบบ:")
        for issue in issues:
            print(f"  - {issue}")
        if warnings:
            print("⚠️ คำเตือน:")
            for warning in warnings:
                print(f"  - {warning}")
        print("\nโปรดแก้ไขปัญหาก่อนเรียกใช้งานแล็บ")
        return 1
    
    # สร้าง QApplication
    app = QApplication(sys.argv)
    
    # ตั้งค่า application properties
    app.setApplicationName("DAB+ Lab 1")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("DAB+ Labs")
    
    # ตั้งค่า font สำหรับหน้าจอสัมผัส
    font = QFont()
    font.setPointSize(11)
    font.setFamily("DejaVu Sans")
    app.setFont(font)
    
    # แสดงข้อมูลระบบ
    logger.info("เริ่มต้น RTL-SDR Testing Lab")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"PyQt5 version: {QT_VERSION_STR}")
    
    # สร้างและแสดง main window
    window = Lab1MainWindow()
    window.show()
    
    # เพิ่มข้อความต้อนรับในหน้าต่าง
    if warnings:
        window.update_test_results("⚠️ คำเตือน:")
        for warning in warnings:
            window.update_test_results(f"  - {warning}")
        window.update_test_results("")
    
    # รัน event loop
    return app.exec_()

# Helper functions
def run_command(command, timeout=10):
    """รันคำสั่ง shell และคืนผลลัพธ์"""
    try:
        if isinstance(command, str):
            # ถ้าเป็น string ให้แยกเป็น list
            command = command.split()
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        
        return result.returncode, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        return -1, "", f"Timeout after {timeout} seconds"
    except FileNotFoundError:
        return -1, "", f"Command not found: {command[0] if command else 'unknown'}"
    except Exception as e:
        return -1, "", f"Error: {str(e)}"

def get_rtlsdr_info():
    """ดึงข้อมูลของ RTL-SDR device"""
    info = {
        'device_found': False,
        'device_id': None,
        'device_name': None,
        'tuner_type': None,
        'supported_sample_rates': [],
        'supported_gains': []
    }
    
    try:
        # ตรวจสอบ USB device
        returncode, stdout, stderr = run_command(['lsusb'])
        if returncode == 0:
            for line in stdout.split('\n'):
                line_lower = line.lower()
                if '0bda:2832' in line_lower:
                    info['device_found'] = True
                    info['device_id'] = '0bda:2832'
                    info['device_name'] = 'RTL2832U DVB-T'
                    break
                elif '0bda:2838' in line_lower:
                    info['device_found'] = True
                    info['device_id'] = '0bda:2838'
                    info['device_name'] = 'RTL2838 DVB-T'
                    break
                elif 'rtl' in line_lower:
                    info['device_found'] = True
                    info['device_name'] = 'RTL-SDR (Unknown model)'
                    break
        
        # ดึงข้อมูล tuner จาก rtl_test
        if info['device_found']:
            returncode, stdout, stderr = run_command(['rtl_test', '-t'], timeout=15)
            if returncode == 0:
                for line in stdout.split('\n'):
                    line_lower = line.lower()
                    if 'tuner' in line_lower:
                        info['tuner_type'] = line.strip()
                    elif 'gain' in line_lower and 'db' in line_lower:
                        # อาจจะมีข้อมูล gain ใน output
                        pass
        
    except Exception as e:
        logger.error(f"Error getting RTL-SDR info: {str(e)}")
    
    return info

def create_test_report():
    """สร้างรายงานผลการทดสอบ"""
    report = []
    report.append("RTL-SDR System Test Report")
    report.append("=" * 40)
    report.append(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"System: {os.uname().sysname} {os.uname().release}")
    report.append(f"Python: {sys.version.split()[0]}")
    
    # ดึงข้อมูลอุปกรณ์
    rtlsdr_info = get_rtlsdr_info()
    
    report.append("\nDevice Information:")
    report.append("-" * 20)
    if rtlsdr_info['device_found']:
        report.append(f"Device ID: {rtlsdr_info.get('device_id', 'Unknown')}")
        report.append(f"Device Name: {rtlsdr_info.get('device_name', 'Unknown')}")
        if rtlsdr_info.get('tuner_type'):
            report.append(f"Tuner: {rtlsdr_info['tuner_type']}")
    else:
        report.append("No RTL-SDR device found")
    
    return "\n".join(report)

if __name__ == "__main__":
    sys.exit(main())