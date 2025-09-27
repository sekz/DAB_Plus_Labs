#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 3 Phase 4: Service Display & Audio (Audio playback and data services)
เป้าหมาย: decode และเล่นเสียงจาก DAB+ services

Dependencies:
pip install ffmpeg-python pyaudio pillow
sudo apt install ffmpeg
"""

import os
import json
import subprocess
import tempfile
import threading
import time
from PIL import Image
import pyaudio
import wave

class DABServicePlayer:
    def __init__(self, eti_file="dab_ensemble.eti", service_file="service_list.json"):
        self.eti_file = eti_file
        self.service_file = service_file
        self.services = {}
        self.current_service = None
        self.audio_player = None
        self.is_playing = False
        self.slideshow_images = []

    def load_service_list(self):
        """
        โหลดรายการ services จากไฟล์ JSON
        TODO: เขียนโค้ดเพื่อ:
        - อ่านไฟล์ service_list.json
        - parse ข้อมูล services
        - แสดงรายการ services ที่มี
        """
        try:
            # TODO: อ่านไฟล์ JSON

            print("Available DAB+ Services:")
            # TODO: แสดงรายการ services

            return True

        except FileNotFoundError:
            print(f"Service file not found: {self.service_file}")
            print("Please run lab3_3.py first to generate service list")
            return False
        except Exception as e:
            print(f"Error loading service list: {e}")
            return False

    def select_service(self, service_id=None, service_name=None):
        """
        เลือก service สำหรับเล่น
        TODO: เขียนโค้ดเพื่อ:
        - เลือก service ด้วย ID หรือชื่อ
        - ตรวจสอบว่า service มีอยู่
        - ตั้งค่า current_service
        """
        try:
            # TODO: หา service ที่ต้องการ

            if service_id:
                # TODO: หาด้วย service ID
                pass
            elif service_name:
                # TODO: หาด้วยชื่อ service
                pass
            else:
                # TODO: ใช้ service แรกที่เจอ
                pass

            print(f"Selected service: {self.current_service}")
            return True

        except Exception as e:
            print(f"Error selecting service: {e}")
            return False

    def extract_audio_data(self, output_dir="audio_output"):
        """
        แยกข้อมูลเสียงจาก ETI stream
        TODO: เขียนโค้ดเพื่อ:
        - ใช้ ffmpeg หรือเครื่องมืออื่นแยกเสียง
        - แปลง AAC เป็น PCM/WAV
        - บันทึกเป็นไฟล์เสียง
        """
        if not self.current_service:
            print("No service selected")
            return False

        try:
            # TODO: สร้างโฟลเดอร์ output
            os.makedirs(output_dir, exist_ok=True)

            # TODO: ใช้ ffmpeg แยกเสียงจาก ETI
            # หรือใช้เครื่องมือเฉพาะสำหรับ DAB+ เช่น dablin

            output_file = os.path.join(output_dir, "decoded_audio.wav")

            # TODO: เรียกใช้คำสั่งแยกเสียง

            print(f"Audio extracted to: {output_file}")
            return output_file

        except Exception as e:
            print(f"Error extracting audio: {e}")
            return None

    def setup_audio_player(self):
        """
        ตั้งค่า audio player สำหรับ Raspberry Pi
        TODO: เขียนโค้ดเพื่อ:
        - ตั้งค่า PyAudio สำหรับ 3.5mm jack
        - ตรวจสอบ audio devices ที่มี
        - เลือก output device ที่เหมาะสม
        """
        try:
            # TODO: สร้าง PyAudio instance
            self.audio_player = pyaudio.PyAudio()

            # TODO: แสดงรายการ audio devices
            print("Available audio devices:")
            for i in range(self.audio_player.get_device_count()):
                info = self.audio_player.get_device_info_by_index(i)
                print(f"  {i}: {info['name']} - {info['maxOutputChannels']} channels")

            # TODO: เลือก output device (3.5mm jack)

            return True

        except Exception as e:
            print(f"Error setting up audio player: {e}")
            return False

    def play_audio(self, audio_file):
        """
        เล่นไฟล์เสียง
        TODO: เขียนโค้ดเพื่อ:
        - อ่านไฟล์ WAV
        - เล่นผ่าน PyAudio
        - รองรับการ pause/resume/stop
        - แสดงสถานะการเล่น
        """
        if not audio_file or not os.path.exists(audio_file):
            print("Audio file not found")
            return False

        try:
            # TODO: อ่านไฟล์ WAV
            with wave.open(audio_file, 'rb') as wf:
                # TODO: ตั้งค่า audio stream

                # TODO: อ่านและเล่นข้อมูลเสียง

                self.is_playing = True
                print(f"Playing: {audio_file}")

                # TODO: เล่นในลูปจนจบไฟล์

                self.is_playing = False
                print("Playback finished")

            return True

        except Exception as e:
            print(f"Error playing audio: {e}")
            return False

    def extract_slideshow_images(self, output_dir="slideshow_images"):
        """
        แยก MOT Slideshow images
        TODO: เขียนโค้ดเพื่อ:
        - หา MOT data ใน ETI stream
        - แยก slideshow images
        - บันทึกเป็นไฟล์ภาพ
        - จัดเก็บใน list สำหรับแสดงผล
        """
        try:
            # TODO: สร้างโฟลเดอร์ output
            os.makedirs(output_dir, exist_ok=True)

            # TODO: ใช้เครื่องมือแยก MOT data จาก ETI
            # เช่น mot-encoder tools หรือ dablin

            # TODO: แปลงและบันทึกภาพ

            # TODO: โหลดภาพใส่ self.slideshow_images

            print(f"Found {len(self.slideshow_images)} slideshow images")
            return True

        except Exception as e:
            print(f"Error extracting slideshow images: {e}")
            return False

    def get_dynamic_label(self):
        """
        อ่าน Dynamic Label Segment (DLS) - ข้อความที่แสดงปัจจุบัน
        TODO: เขียนโค้ดเพื่อ:
        - แยก DLS data จาก ETI stream
        - decode ข้อความปัจจุบัน
        - return ข้อมูล DLS
        """
        try:
            # TODO: แยก DLS data

            # TODO: decode ข้อความ

            dls_info = {
                'text': None,  # TODO: ข้อความปัจจุบัน
                'timestamp': None,  # TODO: เวลาที่อัพเดท
                'service': self.current_service
            }

            return dls_info

        except Exception as e:
            print(f"Error getting dynamic label: {e}")
            return None

    def monitor_realtime_info(self, interval=5):
        """
        ติดตาม real-time information (DLS, slideshow)
        TODO: เขียนโค้ดเพื่อ:
        - สร้าง thread สำหรับติดตาม
        - อัพเดท DLS และ slideshow ตามเวลา
        - แสดงข้อมูลใหม่
        """
        def monitor_thread():
            while self.is_playing:
                try:
                    # TODO: อัพเดท DLS

                    # TODO: เช็ค slideshow ใหม่

                    # TODO: แสดงข้อมูลล่าสุด

                    time.sleep(interval)

                except Exception as e:
                    print(f"Monitor error: {e}")

        # TODO: เริ่ม monitoring thread
        pass

    def stop_playback(self):
        """หยุดการเล่นเสียง"""
        self.is_playing = False
        if self.audio_player:
            # TODO: ปิด audio streams
            self.audio_player.terminate()
            print("Playback stopped")

def interactive_mode():
    """
    โหมดโต้ตอบสำหรับเลือกและเล่น services
    TODO: เขียนโค้ดเพื่อ:
    - แสดงเมนูเลือก service
    - รับ input จากผู้ใช้
    - เรียกใช้ฟังก์ชันต่างๆ ตาม input
    """
    player = DABServicePlayer()

    print("=== DAB+ Service Player ===")

    try:
        # TODO: โหลดรายการ services

        while True:
            print("\nOptions:")
            print("1. List services")
            print("2. Select service")
            print("3. Play audio")
            print("4. Show slideshow")
            print("5. Show DLS info")
            print("0. Exit")

            choice = input("Enter your choice: ")

            # TODO: จัดการ user input

            if choice == "0":
                break

    except KeyboardInterrupt:
        print("\nUser interrupted")
    finally:
        player.stop_playback()

def main():
    """ฟังก์ชันหลักสำหรับทดสอบ"""
    print("=== Lab 3 Phase 4: Service Display & Audio ===")

    import sys

    # TODO: รับ command line arguments สำหรับเลือก service
    service_name = None
    if len(sys.argv) > 1:
        service_name = sys.argv[1]

    # TODO: สร้าง DABServicePlayer instance
    player = None

    try:
        # TODO: โหลดและเลือก service

        # TODO: แยกเสียงและเล่น

        # TODO: แยกและแสดง slideshow

        # TODO: ติดตาม real-time info

        # หรือเรียก interactive mode หากไม่มี argument
        if not service_name:
            interactive_mode()

    except KeyboardInterrupt:
        print("\nUser interrupted")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # TODO: ทำความสะอาด
        pass

if __name__ == "__main__":
    main()