#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 3 Phase 1a: RTL-SDR Data Acquisition (pyrtlsdr version)
เป้าหมาย: รับ I/Q data พื้นฐานจาก RTL-SDR

Dependencies:
pip install pyrtlsdr numpy scipy matplotlib
"""

import numpy as np
from rtlsdr import RtlSdr
import time
import sys

class RTLSDRDataAcquisition:
    def __init__(self):
        self.sdr = None
        # TODO: ตั้งค่าความถี่ DAB+ Thailand (185.360 MHz - Bangkok/Phuket)
        self.frequency = None  # TODO: กำหนดความถี่ในหน่วย Hz
        self.sample_rate = None  # TODO: กำหนด sample rate ที่เหมาะสม
        self.gain = None  # TODO: กำหนดค่า gain

    def setup_rtlsdr(self):
        """
        ติดตั้งและตั้งค่า RTL-SDR
        TODO: เขียนโค้ดเพื่อ:
        - เชื่อมต่อกับ RTL-SDR device
        - ตั้งค่าความถี่, sample rate, gain
        - ตรวจสอบสถานะการเชื่อมต่อ
        """
        try:
            # TODO: สร้าง RtlSdr object
            pass

            # TODO: ตั้งค่า sample rate

            # TODO: ตั้งค่าความถี่

            # TODO: ตั้งค่า gain

            print(f"RTL-SDR setup completed:")
            print(f"Frequency: {self.frequency/1e6:.3f} MHz")
            print(f"Sample Rate: {self.sample_rate/1e6:.1f} Msps")
            print(f"Gain: {self.gain} dB")

        except Exception as e:
            print(f"Error setting up RTL-SDR: {e}")
            return False

        return True

    def capture_samples(self, duration_seconds=10):
        """
        รับ I/Q samples และบันทึกเป็นไฟล์
        TODO: เขียนโค้ดเพื่อ:
        - รับ I/Q samples ตามระยะเวลาที่กำหนด
        - คำนวณ signal strength
        - แสดงข้อมูล samples
        - บันทึกเป็นไฟล์ raw_iq_data.bin
        """
        if not self.sdr:
            print("RTL-SDR not initialized")
            return None

        try:
            # TODO: คำนวณจำนวน samples ที่ต้องการ
            num_samples = None

            print(f"Capturing {duration_seconds} seconds of data...")
            print(f"Number of samples: {num_samples}")

            # TODO: รับ samples จาก RTL-SDR
            samples = None

            # TODO: คำนวณ signal strength (RMS)
            signal_strength = None

            print(f"Signal strength: {signal_strength:.6f}")
            print(f"Max amplitude: {np.max(np.abs(samples)):.6f}")
            print(f"Sample data type: {samples.dtype}")

            # TODO: บันทึกเป็นไฟล์ binary
            filename = "raw_iq_data.bin"

            print(f"Saved to {filename}")
            return samples

        except Exception as e:
            print(f"Error capturing samples: {e}")
            return None

    def analyze_spectrum(self, samples):
        """
        วิเคราะห์สเปกตรัมของสัญญาณ
        TODO: เขียนโค้ดเพื่อ:
        - คำนวณ FFT เพื่อดูสเปกตรัม
        - แสดงข้อมูลสเปกตรัม
        - สร้างกราฟ (optional)
        """
        if samples is None:
            return

        # TODO: คำนวณ FFT

        # TODO: คำนวณ frequency bins

        # TODO: แสดงข้อมูลสเปกตรัม

        print("Spectrum analysis completed")

    def cleanup(self):
        """ปิดการเชื่อมต่อ RTL-SDR"""
        if self.sdr:
            # TODO: ปิดการเชื่อมต่อ
            print("RTL-SDR connection closed")

def main():
    """ฟังก์ชันหลักสำหรับทดสอบ"""
    print("=== Lab 3 Phase 1a: RTL-SDR Data Acquisition ===")

    # TODO: สร้าง instance ของ RTLSDRDataAcquisition
    rtl_capture = None

    try:
        # TODO: ตั้งค่า RTL-SDR

        # TODO: รับ samples

        # TODO: วิเคราะห์สเปกตรัม

    except KeyboardInterrupt:
        print("\nUser interrupted")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # TODO: ทำความสะอาด
        pass

if __name__ == "__main__":
    main()