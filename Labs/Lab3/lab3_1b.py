#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 3 Phase 1b: RTL-SDR Data Acquisition (rtl_tcp client version)
เป้าหมาย: รับ I/Q data ผ่าน network protocol

Dependencies:
pip install numpy scipy matplotlib
"""

import socket
import struct
import numpy as np
import time
import threading

class RTLTCPClient:
    def __init__(self, host='localhost', port=1234):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        # TODO: ตั้งค่าพารามิเตอร์การเชื่อมต่อ
        self.frequency = None  # TODO: กำหนดความถี่ DAB+ Thailand
        self.sample_rate = None  # TODO: กำหนด sample rate
        self.gain = None  # TODO: กำหนดค่า gain

    def connect(self):
        """
        เชื่อมต่อกับ rtl_tcp server
        TODO: เขียนโค้ดเพื่อ:
        - สร้าง TCP socket connection
        - ส่งคำสั่งตั้งค่าความถี่, sample rate, gain
        - ตรวจสอบสถานะการเชื่อมต่อ
        """
        try:
            # TODO: สร้าง socket connection

            print(f"Connecting to rtl_tcp server at {self.host}:{self.port}")

            # TODO: เชื่อมต่อกับ server

            self.connected = True
            print("Connected to rtl_tcp server")

            # TODO: ส่งคำสั่งตั้งค่าต่างๆ

            return True

        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def set_frequency(self, freq_hz):
        """
        ส่งคำสั่งตั้งค่าความถี่
        TODO: เขียนโค้ดเพื่อ:
        - ส่งคำสั่ง SET_FREQUENCY ไปยัง rtl_tcp
        - ใช้ format: 0x01 + 4 bytes frequency (big endian)
        """
        if not self.connected:
            return False

        try:
            # TODO: สร้างคำสั่ง SET_FREQUENCY
            # Command format: 0x01 + frequency (4 bytes, big endian)

            print(f"Set frequency: {freq_hz/1e6:.3f} MHz")
            return True

        except Exception as e:
            print(f"Failed to set frequency: {e}")
            return False

    def set_sample_rate(self, rate):
        """
        ส่งคำสั่งตั้งค่า sample rate
        TODO: เขียนโค้ดเพื่อ:
        - ส่งคำสั่ง SET_SAMPLE_RATE ไปยัง rtl_tcp
        - ใช้ format: 0x02 + 4 bytes sample rate (big endian)
        """
        if not self.connected:
            return False

        try:
            # TODO: สร้างคำสั่ง SET_SAMPLE_RATE
            # Command format: 0x02 + sample_rate (4 bytes, big endian)

            print(f"Set sample rate: {rate/1e6:.1f} Msps")
            return True

        except Exception as e:
            print(f"Failed to set sample rate: {e}")
            return False

    def set_gain(self, gain_db):
        """
        ส่งคำสั่งตั้งค่า gain
        TODO: เขียนโค้ดเพื่อ:
        - ส่งคำสั่ง SET_GAIN ไปยัง rtl_tcp
        - ใช้ format: 0x04 + 4 bytes gain (big endian)
        """
        if not self.connected:
            return False

        try:
            # TODO: สร้างคำสั่ง SET_GAIN
            # Command format: 0x04 + gain (4 bytes, big endian)

            print(f"Set gain: {gain_db} dB")
            return True

        except Exception as e:
            print(f"Failed to set gain: {e}")
            return False

    def receive_samples(self, duration_seconds=10):
        """
        รับ I/Q samples จาก network stream
        TODO: เขียนโค้ดเพื่อ:
        - รับข้อมูล I/Q samples ผ่าน TCP
        - แปลงข้อมูล uint8 เป็น complex float
        - คำนวณ signal strength
        - บันทึกเป็นไฟล์ networked_iq_data.bin
        """
        if not self.connected:
            print("Not connected to server")
            return None

        try:
            # TODO: คำนวณจำนวน bytes ที่ต้องรับ
            bytes_per_second = None  # TODO: คำนวณจาก sample rate
            total_bytes = None

            print(f"Receiving {duration_seconds} seconds of data...")
            print(f"Expected bytes: {total_bytes}")

            samples_data = bytearray()
            start_time = time.time()

            # TODO: รับข้อมูลจาก socket ในลูป
            while len(samples_data) < total_bytes:
                # TODO: รับข้อมูลจาก socket
                # TODO: เช็คเวลาที่ผ่านไป
                # TODO: แสดงความคืบหน้า
                pass

            # TODO: แปลงข้อมูล uint8 เป็น complex float
            # RTL-SDR format: IQIQIQ... (uint8, centered at 127.5)

            # TODO: คำนวณ signal strength

            # TODO: บันทึกเป็นไฟล์
            filename = "networked_iq_data.bin"

            print(f"Received {len(samples_data)} bytes")
            print(f"Signal strength: calculated_strength")
            print(f"Saved to {filename}")

            return None  # TODO: return converted samples

        except Exception as e:
            print(f"Error receiving samples: {e}")
            return None

    def disconnect(self):
        """ปิดการเชื่อมต่อ"""
        if self.socket:
            # TODO: ปิด socket connection
            self.connected = False
            print("Disconnected from rtl_tcp server")

def start_rtl_tcp_server():
    """
    เริ่มต้น rtl_tcp server (สำหรับทดสอบ)
    TODO: เขียนโค้ดเพื่อ:
    - เรียกใช้คำสั่ง rtl_tcp ผ่าน subprocess
    - ตรวจสอบว่า server ทำงานอยู่
    """
    import subprocess
    import os

    print("Starting rtl_tcp server...")
    try:
        # TODO: เรียกใช้ rtl_tcp ด้วย subprocess
        # ตัวอย่าง: rtl_tcp -a localhost -p 1234
        pass

    except Exception as e:
        print(f"Failed to start rtl_tcp server: {e}")
        return False

def main():
    """ฟังก์ชันหลักสำหรับทดสอบ"""
    print("=== Lab 3 Phase 1b: RTL-TCP Client ===")

    # TODO: เริ่มต้น rtl_tcp server (ถ้าจำเป็น)

    # TODO: สร้าง RTLTCPClient instance
    client = None

    try:
        # TODO: เชื่อมต่อกับ server

        # TODO: ตั้งค่าพารามิเตอร์ต่างๆ

        # TODO: รับ samples

    except KeyboardInterrupt:
        print("\nUser interrupted")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # TODO: ปิดการเชื่อมต่อ
        pass

if __name__ == "__main__":
    main()