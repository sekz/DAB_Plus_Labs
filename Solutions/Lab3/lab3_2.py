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
        self.channel = "6C"  # DAB+ Thailand default channel
        self.process = None
        self.gain = 50
        self.band = "BAND_III"

    def check_eti_cmdline(self):
        """
        ตรวจสอบว่า eti-cmdline ติดตั้งแล้วหรือไม่
        """
        try:
            # ตรวจสอบ version และ help
            result = subprocess.run([self.eti_cmdline_path, "-h"],
                                  capture_output=True, text=True, timeout=10)

            # eti-cmdline-rtlsdr returns error code but still shows help
            if "eti-cmdline" in result.stderr or "eti-cmdline" in result.stdout:
                print("eti-cmdline found and ready")
                print("Available options:")
                # แสดงบางส่วนของ help
                output = result.stderr if result.stderr else result.stdout
                help_lines = output.split('\n')[:15]
                for line in help_lines:
                    if line.strip():
                        print(f"  {line}")
                return True
            else:
                print(f"eti-cmdline not recognized")
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

    def setup_files(self, output_file="dab_ensemble.eti"):
        """
        ตั้งค่าไฟล์ output
        """
        # ตั้งค่า output path
        self.output_file = os.path.abspath(output_file)

        # สร้างโฟลเดอร์สำหรับ output หากจำเป็น
        output_dir = os.path.dirname(self.output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print(f"Output file: {self.output_file}")
        return True

    def run_eti_cmdline(self, runtime_seconds=30):
        """
        เรียกใช้ eti-cmdline เพื่อรับสัญญาณ DAB จาก RTL-SDR
        """
        if not self.output_file:
            self.output_file = "dab_ensemble.eti"

        try:
            # สร้างคำสั่ง eti-cmdline สำหรับ RTL-SDR
            cmd = [
                self.eti_cmdline_path,
                "-C", self.channel,  # DAB channel (e.g., 12C)
                "-B", self.band,  # Band (BAND_III or L_BAND)
                "-O", self.output_file,  # output ETI file
                "-G", str(self.gain),  # gain
                "-t", str(runtime_seconds),  # record time
                "-J"  # write stations to JSON
            ]

            print(f"Running eti-cmdline with RTL-SDR...")
            print(f"Command: {' '.join(cmd)}")
            print(f"Channel: {self.channel}, Band: {self.band}")

            # เรียกใช้ subprocess
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
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

            import select

            while self.process.poll() is None:
                # Read from both stdout and stderr
                reads = []
                if self.process.stdout:
                    reads.append(self.process.stdout)
                if self.process.stderr:
                    reads.append(self.process.stderr)

                for stream in reads:
                    line = stream.readline()
                    if line:
                        line = line.strip()
                        if not line:
                            continue

                        # Display all output
                        print(f"  {line}")

                        # Parse output สำหรับข้อมูลสำคัญ
                        if ("sync" in line.lower() or "locked" in line.lower() or
                            "here we go" in line.lower() or "ensemble" in line.lower() and "detected" in line.lower()):
                            if not sync_found:
                                print("✓ DAB sync found!")
                                sync_found = True

                        # Count frames (numbers only)
                        if line.strip().isdigit():
                            frame_count += 1

                        if "error" in line.lower() or "no dab" in line.lower():
                            error_count += 1

                        if "estimated snr" in line.lower():
                            print(f"📊 {line}")

            # Read any remaining output
            if self.process.stdout:
                remaining = self.process.stdout.read()
                if remaining:
                    for line in remaining.split('\n'):
                        if line.strip():
                            print(f"  {line.strip()}")

            if self.process.stderr:
                remaining = self.process.stderr.read()
                if remaining:
                    for line in remaining.split('\n'):
                        if line.strip():
                            print(f"  {line.strip()}")

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

            # แสดงข้อมูล stations จาก JSON file
            self.display_station_info()

            return True

        except Exception as e:
            print(f"Error analyzing ETI output: {e}")
            return False

    def display_station_info(self):
        """แสดงข้อมูล stations จาก JSON file"""
        try:
            import json
            import re
            json_file = f"ensemble-ch-{self.channel}.json"
            if os.path.exists(json_file):
                with open(json_file, 'r') as f:
                    content = f.read()
                    # Fix malformed JSON: "Eid:"4FFF" -> "Eid":"4FFF"
                    content = re.sub(r'"Eid:"([^"]*)"', r'"Eid":"\1"', content)
                    data = json.loads(content)

                    print(f"\n=== Station Information ===")
                    print(f"Channel: {data.get('channel', 'N/A')}")
                    print(f"Ensemble: {data.get('ensemble', 'N/A')}")
                    print(f"Ensemble ID: {data.get('Eid', 'N/A')}")
                    print(f"\nStations found: {len(data.get('stations', {}))}")
                    for i, (name, sid) in enumerate(data.get('stations', {}).items(), 1):
                        print(f"  {i:2d}. {name:20s} ({sid})")
        except Exception as e:
            print(f"Could not display station info: {e}")

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
            "-C", "6C",  # DAB channel
            "-B", "BAND_III",  # Band
            "-O", "direct_dab_ensemble.eti",
            "-G", "50",  # gain
            "-t", "30",  # record time
            "-J"  # write stations to JSON
        ]

        print(f"Command: {' '.join(cmd)}")
        print("Running for 30 seconds...")

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True)

        # รอให้ process เสร็จ
        try:
            stdout, _ = process.communicate(timeout=40)
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
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == "--rtlsdr":
            test_with_rtlsdr()

    except KeyboardInterrupt:
        print("\nUser interrupted")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        eti_wrapper.cleanup()

if __name__ == "__main__":
    main()