#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAB 0: Introduction to PyQt5 สำหรับผู้เริ่มต้น
วัตถุประสงค์: เรียนรู้พื้นฐาน PyQt5 GUI programming ใน 1 ชั่วโมง
"""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QWidget, QPushButton, QLabel, QLineEdit, QTextEdit,
                            QSlider, QProgressBar, QMessageBox, QGroupBox,
                            QCheckBox, QRadioButton, QComboBox, QSpinBox)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon

class BasicWidgetsDemo(QWidget):
    """ตัวอย่างการใช้ Widget พื้นฐาน"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 1. ป้ายข้อความ (Label)
        self.title_label = QLabel("🎯 PyQt5 Widget Demo")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # 2. ช่องใส่ข้อความ (LineEdit)
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("ชื่อ:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("ใส่ชื่อของคุณ...")
        input_layout.addWidget(self.name_input)
        layout.addLayout(input_layout)
        
        # 3. ปุ่ม (Button)
        self.hello_btn = QPushButton("👋 สวัสดี")
        self.hello_btn.clicked.connect(self.say_hello)  # เชื่อม signal กับ slot
        layout.addWidget(self.hello_btn)
        
        # 4. พื้นที่ข้อความ (TextEdit)
        self.output_text = QTextEdit()
        self.output_text.setMaximumHeight(100)
        layout.addWidget(self.output_text)
        
        # 5. Slider และ Progress Bar
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("ระดับ:"))
        self.value_slider = QSlider(Qt.Horizontal)
        self.value_slider.setRange(0, 100)
        self.value_slider.setValue(50)
        self.value_slider.valueChanged.connect(self.update_progress)
        slider_layout.addWidget(self.value_slider)
        layout.addLayout(slider_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(50)
        layout.addWidget(self.progress_bar)
        
    def say_hello(self):
        """เมื่อกดปุ่มสวัสดี"""
        # TODO: อ่านชื่อจาก self.name_input.text()
        name = ""  # <-- เติมโค้ดตรงนี้
        
        if name:
            message = f"สวัสดี {name}! ยินดีต้อนรับสู่ PyQt5"
            # TODO: เพิ่มข้อความลงใน self.output_text
            pass  # <-- เติมโค้ดตรงนี้
        else:
            QMessageBox.information(self, "แจ้งเตือน", "กรุณาใส่ชื่อก่อนครับ")
    
    def update_progress(self, value):
        """อัพเดท Progress Bar เมื่อ Slider เปลี่ยน"""
        # TODO: ตั้งค่า progress bar ให้เท่ากับ value
        pass  # <-- เติมโค้ดตรงนี้

class SignalsAndSlotsDemo(QWidget):
    """ตัวอย่างการใช้ Signals และ Slots"""
    
    # สร้าง custom signal
    custom_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("🔌 Signals & Slots Demo"))
        
        # ปุ่มทดสอบ signals
        self.signal_btn = QPushButton("ส่ง Signal")
        layout.addWidget(self.signal_btn)
        
        # พื้นที่แสดงผล
        self.signal_output = QTextEdit()
        self.signal_output.setMaximumHeight(120)
        layout.addWidget(self.signal_output)
        
        # Timer demo
        self.timer_btn = QPushButton("เริ่ม Timer")
        layout.addWidget(self.timer_btn)
        
        self.timer_label = QLabel("Timer: 0 วินาที")
        layout.addWidget(self.timer_label)
        
        self.timer = QTimer()
        self.timer_count = 0
        
    def setup_connections(self):
        """เชื่อม signals กับ slots"""
        # Built-in signals
        self.signal_btn.clicked.connect(self.emit_custom_signal)
        
        # Custom signals
        self.custom_signal.connect(self.handle_custom_signal)
        
        # Timer
        self.timer_btn.clicked.connect(self.toggle_timer)
        self.timer.timeout.connect(self.update_timer)
        
    def emit_custom_signal(self):
        """ส่ง custom signal"""
        message = f"Custom Signal ส่งเมื่อ {QTimer().currentTime().toString()}"
        self.custom_signal.emit(message)
        
    def handle_custom_signal(self, message):
        """รับ custom signal"""
        self.signal_output.append(f"📡 รับ Signal: {message}")
        
    def toggle_timer(self):
        """เปิด/ปิด Timer"""
        if self.timer.isActive():
            self.timer.stop()
            self.timer_btn.setText("เริ่ม Timer")
            self.timer_count = 0
        else:
            # TODO: เริ่ม timer ให้ทำงานทุก 1000 ms (1 วินาที)
            pass  # <-- เติมโค้ดตรงนี้
            self.timer_btn.setText("หยุด Timer")
            
    def update_timer(self):
        """อัพเดท Timer"""
        self.timer_count += 1
        # TODO: อัพเดทข้อความใน timer_label ให้แสดง timer_count
        pass  # <-- เติมโค้ดตรงนี้

class LayoutDemo(QWidget):
    """ตัวอย่างการจัดเรียง Layout"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        main_layout.addWidget(QLabel("📐 Layout Demo"))
        
        # Horizontal Layout
        h_group = QGroupBox("Horizontal Layout")
        h_layout = QHBoxLayout(h_group)
        h_layout.addWidget(QPushButton("ซ้าย"))
        h_layout.addWidget(QPushButton("กลาง"))
        h_layout.addWidget(QPushButton("ขวา"))
        main_layout.addWidget(h_group)
        
        # Vertical Layout
        v_group = QGroupBox("Vertical Layout")
        v_layout = QVBoxLayout(v_group)
        v_layout.addWidget(QPushButton("บน"))
        v_layout.addWidget(QPushButton("กลาง"))
        v_layout.addWidget(QPushButton("ล่าง"))
        main_layout.addWidget(v_group)
        
        # Mixed Layout
        mixed_group = QGroupBox("Mixed Layout")
        mixed_main = QVBoxLayout(mixed_group)
        
        top_row = QHBoxLayout()
        top_row.addWidget(QPushButton("A"))
        top_row.addWidget(QPushButton("B"))
        mixed_main.addLayout(top_row)
        
        mixed_main.addWidget(QPushButton("C (เต็มความกว้าง)"))
        main_layout.addWidget(mixed_group)

class InputWidgetsDemo(QWidget):
    """ตัวอย่าง Input Widgets ต่างๆ"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("⌨️ Input Widgets Demo"))
        
        # Text Input
        text_group = QGroupBox("Text Input")
        text_layout = QVBoxLayout(text_group)
        
        self.line_edit = QLineEdit("Text input")
        text_layout.addWidget(self.line_edit)
        
        self.text_edit = QTextEdit("Multi-line text input")
        self.text_edit.setMaximumHeight(80)
        text_layout.addWidget(self.text_edit)
        layout.addWidget(text_group)
        
        # Checkboxes และ Radio buttons
        choice_group = QGroupBox("Choices")
        choice_layout = QVBoxLayout(choice_group)
        
        self.checkbox1 = QCheckBox("ตัวเลือก 1")
        self.checkbox2 = QCheckBox("ตัวเลือก 2")
        choice_layout.addWidget(self.checkbox1)
        choice_layout.addWidget(self.checkbox2)
        
        self.radio1 = QRadioButton("Radio A")
        self.radio2 = QRadioButton("Radio B")
        self.radio1.setChecked(True)
        choice_layout.addWidget(self.radio1)
        choice_layout.addWidget(self.radio2)
        layout.addWidget(choice_group)
        
        # ComboBox และ SpinBox
        select_group = QGroupBox("Selection")
        select_layout = QVBoxLayout(select_group)
        
        self.combo = QComboBox()
        self.combo.addItems(["ตัวเลือก 1", "ตัวเลือก 2", "ตัวเลือก 3"])
        select_layout.addWidget(self.combo)
        
        self.spinbox = QSpinBox()
        self.spinbox.setRange(0, 100)
        self.spinbox.setValue(25)
        select_layout.addWidget(self.spinbox)
        layout.addWidget(select_group)
        
        # ปุ่มแสดงค่า
        self.show_values_btn = QPushButton("📊 แสดงค่าทั้งหมด")
        layout.addWidget(self.show_values_btn)
        
        self.result_text = QTextEdit()
        self.result_text.setMaximumHeight(100)
        layout.addWidget(self.result_text)
        
    def setup_connections(self):
        self.show_values_btn.clicked.connect(self.show_all_values)
        
    def show_all_values(self):
        """แสดงค่าจาก input widgets ทั้งหมด"""
        values = []
        values.append(f"Line Edit: {self.line_edit.text()}")
        values.append(f"Text Edit: {self.text_edit.toPlainText()[:20]}...")
        values.append(f"Checkbox 1: {self.checkbox1.isChecked()}")
        values.append(f"Checkbox 2: {self.checkbox2.isChecked()}")
        values.append(f"Radio A: {self.radio1.isChecked()}")
        values.append(f"ComboBox: {self.combo.currentText()}")
        values.append(f"SpinBox: {self.spinbox.value()}")
        
        self.result_text.clear()
        for value in values:
            self.result_text.append(value)

class TouchFriendlyDemo(QWidget):
    """ตัวอย่างการทำ UI ที่เหมาะกับหน้าจอสัมผัส"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.apply_touch_styles()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("📱 Touch-Friendly UI Demo")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # ปุ่มใหญ่สำหรับสัมผัส
        button_layout = QHBoxLayout()
        self.big_btn1 = QPushButton("🎯 ปุ่มใหญ่ 1")
        self.big_btn2 = QPushButton("🔧 ปุ่มใหญ่ 2")
        self.big_btn3 = QPushButton("📊 ปุ่มใหญ่ 3")
        
        button_layout.addWidget(self.big_btn1)
        button_layout.addWidget(self.big_btn2)
        button_layout.addWidget(self.big_btn3)
        layout.addLayout(button_layout)
        
        # Slider ที่ใหญ่พอสำหรับนิ้ว
        slider_layout = QVBoxLayout()
        slider_layout.addWidget(QLabel("🎚️ Big Slider for Touch"))
        self.big_slider = QSlider(Qt.Horizontal)
        self.big_slider.setRange(0, 100)
        self.big_slider.setValue(50)
        slider_layout.addWidget(self.big_slider)
        
        self.slider_value_label = QLabel("ค่า: 50")
        slider_layout.addWidget(self.slider_value_label)
        layout.addLayout(slider_layout)
        
        # การเชื่อม
        self.big_slider.valueChanged.connect(
            lambda v: self.slider_value_label.setText(f"ค่า: {v}")
        )
        
        # ปุ่มทดสอบ touch feedback
        self.feedback_btn = QPushButton("🎉 ทดสอบ Touch Feedback")
        self.feedback_btn.clicked.connect(self.show_touch_feedback)
        layout.addWidget(self.feedback_btn)
        
    def apply_touch_styles(self):
        """ใช้ styles ที่เหมาะกับการสัมผัส"""
        
        # Style สำหรับปุ่มใหญ่
        big_button_style = """
        QPushButton {
            border: 2px solid #3498db;
            border-radius: 8px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #5dade2, stop:1 #3498db);
            color: white;
            font-weight: bold;
            font-size: 14px;
            padding: 15px;
            min-height: 50px;
            min-width: 120px;
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3498db, stop:1 #2980b9);
            border: 2px solid #2980b9;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #85c1e9, stop:1 #5dade2);
        }
        """
        
        for btn in [self.big_btn1, self.big_btn2, self.big_btn3, self.feedback_btn]:
            btn.setStyleSheet(big_button_style)
            
        # Style สำหรับ slider
        self.big_slider.setStyleSheet("""
        QSlider::groove:horizontal {
            border: 1px solid #bbb;
            background: white;
            height: 20px;
            border-radius: 10px;
        }
        QSlider::handle:horizontal {
            background: #3498db;
            border: 2px solid #2980b9;
            width: 30px;
            height: 30px;
            margin: -8px 0;
            border-radius: 15px;
        }
        QSlider::handle:horizontal:pressed {
            background: #2980b9;
        }
        """)
        
    def show_touch_feedback(self):
        """แสดง feedback เมื่อสัมผัส"""
        QMessageBox.information(
            self, 
            "Touch Feedback", 
            "🎉 สัมผัสสำเร็จ!\n\nนี่คือตัวอย่าง feedback\nสำหรับหน้าจอสัมผัส"
        )

class Lab0MainWindow(QMainWindow):
    """หน้าต่างหลักของ Lab 0"""
    
    def __init__(self):
        super().__init__()
        self.current_demo = 0
        self.demos = []
        self.setup_ui()
        self.setup_demos()
        
    def setup_ui(self):
        """สร้าง UI หลัก"""
        self.setWindowTitle("LAB 0: PyQt5 Introduction")
        self.setGeometry(100, 100, 900, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("🎓 LAB 0: PyQt5 สำหรับผู้เริ่มต้น")
        header.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0px;
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Navigation
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("⬅️ ก่อนหน้า")
        self.next_btn = QPushButton("➡️ ถัดไป")
        self.demo_label = QLabel("Demo 1/5")
        self.demo_label.setAlignment(Qt.AlignCenter)
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.demo_label)
        nav_layout.addWidget(self.next_btn)
        layout.addLayout(nav_layout)
        
        # Demo area
        self.demo_area = QWidget()
        layout.addWidget(self.demo_area, 1)
        
        # เชื่อม navigation
        self.prev_btn.clicked.connect(self.prev_demo)
        self.next_btn.clicked.connect(self.next_demo)
        
        # Status
        self.status_label = QLabel("พร้อมเรียนรู้ PyQt5! กดปุ่มถัดไปเพื่อดู demos")
        self.status_label.setStyleSheet("padding: 8px; background-color: #d5f4e6; border-radius: 5px;")
        layout.addWidget(self.status_label)
        
    def setup_demos(self):
        """เตรียม demos ทั้งหมด"""
        self.demos = [
            ("🧩 Basic Widgets", BasicWidgetsDemo),
            ("🔌 Signals & Slots", SignalsAndSlotsDemo),
            ("📐 Layouts", LayoutDemo),
            ("⌨️ Input Widgets", InputWidgetsDemo),
            ("📱 Touch-Friendly UI", TouchFriendlyDemo)
        ]
        
        self.show_current_demo()
        
    def show_current_demo(self):
        """แสดง demo ปัจจุบัน"""
        # เคลียร์ demo area
        if self.demo_area.layout():
            for i in reversed(range(self.demo_area.layout().count())):
                self.demo_area.layout().itemAt(i).widget().setParent(None)
        else:
            layout = QVBoxLayout(self.demo_area)
            
        # สร้าง demo ใหม่
        demo_name, demo_class = self.demos[self.current_demo]
        demo_widget = demo_class()
        
        self.demo_area.layout().addWidget(demo_widget)
        
        # อัพเดท UI
        self.demo_label.setText(f"{demo_name} ({self.current_demo + 1}/{len(self.demos)})")
        self.prev_btn.setEnabled(self.current_demo > 0)
        self.next_btn.setEnabled(self.current_demo < len(self.demos) - 1)
        
        self.status_label.setText(f"กำลังแสดง: {demo_name}")
        
    def prev_demo(self):
        """ไปยัง demo ก่อนหน้า"""
        if self.current_demo > 0:
            self.current_demo -= 1
            self.show_current_demo()
            
    def next_demo(self):
        """ไปยัง demo ถัดไป"""
        if self.current_demo < len(self.demos) - 1:
            self.current_demo += 1
            self.show_current_demo()

def main():
    """ฟังก์ชันหลัก"""
    app = QApplication(sys.argv)
    
    # ตั้งค่า font สำหรับหน้าจอสัมผัส
    font = QFont()
    font.setPointSize(11)
    font.setFamily("DejaVu Sans")
    app.setFont(font)
    
    # สร้างและแสดงหน้าต่างหลัก
    window = Lab0MainWindow()
    window.show()
    
    return app.exec_()

if __name__ == "__main__":
    print("🎓 LAB 0: PyQt5 Introduction สำหรับผู้เริ่มต้น")
    print("📚 เรียนรู้พื้นฐาน PyQt5 ใน 1 ชั่วโมง")
    print("🚀 เริ่มต้นกันเถอะ!")
    sys.exit(main())