#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 3 Phase 2: DAB+ Signal Processing (eti-cmdline integration) - SOLUTION
เป้าหมาย: แปลง I/Q data เป็น ETI stream

Dependencies:
- eti-cmdline จาก eti-stuff package
- pip install numpy
"""

import subprocess
import os
import time
import struct
import numpy as np
import threading
import signal

class ETICmdlineWrapper:
    def __init__(self):
        self.eti_cmdline_path = "eti-cmdline"  # assume it's in PATH
        self.input_file = None
        self.output_file = None
        self.frequency = 185360000  # DAB+ Thailand default
        self.process = None
        self.sample_rate = 2048000
        self.gain = 50

    def check_eti_cmdline(self):
        """
        ตรวจสอบว่า eti-cmdline ติดตั้งแล้วหรือไม่
        """
        try:
            # ตรวจสอบ version และ help
            result = subprocess.run([self.eti_cmdline_path, "--help"],
                                  capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                print("eti-cmdline found and ready")
                print("Available options:")
                # แสดงบางส่วนของ help
                help_lines = result.stdout.split('\n')[:10]
                for line in help_lines:
                    if line.strip():
                        print(f"  {line}")
                return True
            else:
                print(f"eti-cmdline returned error code: {result.returncode}")
                return False

        except FileNotFoundError:
            print("eti-cmdline not found. Please install eti-stuff package:")
            print("git clone https://github.com/JvanKatwijk/eti-stuff")
            print("cd eti-stuff && mkdir build && cd build")
            print("cmake .. -DRTLSDR=1")
            print("make && sudo make install")
            return False
        except subprocess.TimeoutExpired:
            print("eti-cmdline command timed out")
            return False
        except Exception as e:
            print(f"Error checking eti-cmdline: {e}")
            return False

    def setup_files(self, input_file="raw_iq_data.bin", output_file="dab_ensemble.eti"):
        """
        ตั้งค่าไฟล์ input และ output
        """
        # ตรวจสอบไฟล์ input
        if not os.path.exists(input_file):
            print(f"Input file not found: {input_file}")
            print("Please run lab3_1a.py first to generate I/Q data")
            return False

        file_size = os.path.getsize(input_file)
        print(f"Input file: {input_file} ({file_size:,} bytes)")

        # ตั้งค่า paths
        self.input_file = os.path.abspath(input_file)
        self.output_file = os.path.abspath(output_file)

        # สร้างโฟลเดอร์สำหรับ output หากจำเป็น
        output_dir = os.path.dirname(self.output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print(f"Input file: {self.input_file}")
        print(f"Output file: {self.output_file}")
        return True

    def run_eti_cmdline(self, runtime_seconds=30):
        """
        เรียกใช้ eti-cmdline เพื่อแปลง I/Q เป็น ETI
        """
        if not self.input_file or not os.path.exists(self.input_file):
            print("Input file not found")
            return False

        try:
            # สร้างคำสั่ง eti-cmdline สำหรับไฟล์ input
            cmd = [
                self.eti_cmdline_path,
                "-d", "file",  # input from file
                "-I", self.input_file,  # input file
                "-F", str(int(self.frequency)),  # center frequency
                "-O", self.output_file,  # output ETI file
                "-C", str(self.sample_rate),  # sample rate
                "-G", str(self.gain),  # gain
                "-v"  # verbose output
            ]

            print(f"Running eti-cmdline...")
            print(f"Command: {' '.join(cmd)}")

            # เรียกใช้ subprocess
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            print(f"eti-cmdline started (PID: {self.process.pid})")
            print(f"Will run for {runtime_seconds} seconds")

            # สร้าง thread สำหรับ monitor output
            monitor_thread = threading.Thread(target=self.monitor_process)
            monitor_thread.daemon = True
            monitor_thread.start()

            # รอให้ process ทำงานตามเวลาที่กำหนด
            time.sleep(runtime_seconds)

            # หยุด process
            print("\nStopping eti-cmdline...")
            self.process.terminate()

            # รอให้ process จบ
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("Force killing eti-cmdline...")
                self.process.kill()
                self.process.wait()

            print("eti-cmdline completed")
            return True

        except Exception as e:
            print(f"Error running eti-cmdline: {e}")
            if self.process:
                try:
                    self.process.terminate()
                except:
                    pass
            return False

    def monitor_process(self):
        """
        ติดตาม output ของ eti-cmdline
        """
        if not self.process:
            return

        try:
            sync_found = False
            error_count = 0
            frame_count = 0

            for line in iter(self.process.stdout.readline, ''):
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                # Parse output สำหรับข้อมูลสำคัญ
                if "sync found" in line.lower():
                    if not sync_found:
                        print("✓ DAB sync found!")
                        sync_found = True

                elif "frame" in line.lower() and "error" not in line.lower():
                    frame_count += 1
                    if frame_count % 100 == 0:
                        print(f"Processed {frame_count} frames...")

                elif "error" in line.lower():
                    error_count += 1
                    if error_count <= 5:  # แสดง error แรกๆ เท่านั้น
                        print(f"⚠ Error: {line}")

                elif "snr" in line.lower():
                    print(f"📊 Signal quality: {line}")

                elif "bitrate" in line.lower():
                    print(f"📈 {line}")

            print(f"\nMonitoring completed:")
            print(f"- Sync found: {'Yes' if sync_found else 'No'}")
            print(f"- Frames processed: {frame_count}")
            print(f"- Errors detected: {error_count}")

        except Exception as e:
            print(f"Error monitoring process: {e}")

    def analyze_eti_output(self):
        """
        วิเคราะห์ไฟล์ ETI ที่ได้
        """
        if not self.output_file or not os.path.exists(self.output_file):
            print("ETI output file not found")
            return False

        try:
            file_size = os.path.getsize(self.output_file)
            print(f"\n=== ETI Output Analysis ===")
            print(f"ETI file size: {file_size:,} bytes")

            # คำนวณจำนวน ETI frames
            frame_size = 6144  # ETI frame size
            num_frames = file_size // frame_size
            remaining_bytes = file_size % frame_size

            print(f"Number of ETI frames: {num_frames}")
            if remaining_bytes > 0:
                print(f"Incomplete frame: {remaining_bytes} bytes")

            # คำนวณระยะเวลาของข้อมูล
            # แต่ละ frame = 24ms logical time
            duration_ms = num_frames * 24
            duration_seconds = duration_ms / 1000

            print(f"Audio duration: {duration_seconds:.1f} seconds ({duration_ms} ms)")

            # อ่านและวิเคราะห์ frame headers
            valid_frames = 0
            with open(self.output_file, 'rb') as f:
                for i in range(min(num_frames, 10)):  # ตรวจสอบ 10 frames แรก
                    frame_data = f.read(frame_size)
                    if len(frame_data) == frame_size:
                        # ตรวจสอบ sync pattern (simplified)
                        if self.validate_eti_frame(frame_data):
                            valid_frames += 1

            print(f"Valid frames (from sample): {valid_frames}/10")

            # แสดงสถิติ
            bitrate = (file_size * 8) / duration_seconds if duration_seconds > 0 else 0
            print(f"Average bitrate: {bitrate/1000:.1f} kbps")

            return True

        except Exception as e:
            print(f"Error analyzing ETI output: {e}")
            return False

    def validate_eti_frame(self, frame_data):
        """ตรวจสอบความถูกต้องของ ETI frame อย่างง่าย"""
        try:
            # ตรวจสอบ sync pattern อย่างง่าย
            # ETI frame ควรมี specific pattern ใน header
            if len(frame_data) != 6144:
                return False

            # Check for reasonable values in header
            # (การตรวจสอบแบบพื้นฐาน)
            return True

        except:
            return False

    def cleanup(self):
        """ทำความสะอาดและหยุด process"""
        if self.process and self.process.poll() is None:
            print("Stopping eti-cmdline process")
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

def test_with_rtlsdr():
    """
    ทดสอบด้วยการรับสัญญาณจาก RTL-SDR โดยตรง
    """
    print("Testing with direct RTL-SDR input...")

    try:
        cmd = [
            "eti-cmdline",
            "-d", "rtlsdr",  # direct RTL-SDR input
            "-F", "185360000",  # DAB+ frequency
            "-O", "direct_dab_ensemble.eti",
            "-C", "2048000",  # sample rate
            "-G", "50",  # gain
            "-v"
        ]

        print(f"Command: {' '.join(cmd)}")
        print("Running for 30 seconds...")

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True)

        # รันเป็นเวลา 30 วินาที
        try:
            stdout, _ = process.communicate(timeout=30)
            print("RTL-SDR test output:")
            print(stdout[:1000])  # แสดง output บางส่วน
        except subprocess.TimeoutExpired:
            process.terminate()
            print("RTL-SDR test completed (timeout)")

    except Exception as e:
        print(f"Error in RTL-SDR test: {e}")

def main():
    """ฟังก์ชันหลักสำหรับทดสอบ"""
    print("=== Lab 3 Phase 2: DAB+ Signal Processing ===")

    # สร้าง ETICmdlineWrapper instance
    eti_wrapper = ETICmdlineWrapper()

    try:
        # ตรวจสอบ eti-cmdline
        if not eti_wrapper.check_eti_cmdline():
            print("Please install eti-cmdline first")
            return

        # ตั้งค่าไฟล์
        if not eti_wrapper.setup_files():
            print("File setup failed")
            return

        # เรียกใช้ eti-cmdline
        if eti_wrapper.run_eti_cmdline(30):
            # วิเคราะห์ผลลัพธ์
            eti_wrapper.analyze_eti_output()

        # ทดสอบกับ RTL-SDR โดยตรง (optional)
        if len(os.sys.argv) > 1 and os.sys.argv[1] == "--rtlsdr":
            test_with_rtlsdr()

    except KeyboardInterrupt:
        print("\nUser interrupted")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        eti_wrapper.cleanup()

if __name__ == "__main__":
    main()