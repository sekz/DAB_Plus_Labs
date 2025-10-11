#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 3 Phase 4: Service Display & Audio Playback - SOLUTION
เป้าหมาย: decode และเล่นเสียงจาก DAB+ services

Dependencies:
pip install ffmpeg-python pyaudio pillow
sudo apt install ffmpeg
"""

import subprocess
import pyaudio
import wave
import threading
import time
import json
import os
import sys
import argparse
from PIL import Image
import struct

class DABServicePlayer:
    def __init__(self):
        self.services = {}
        self.current_service = None
        self.audio_player = None
        self.playing = False
        self.volume = 0.8

        # Audio settings
        self.sample_rate = 48000
        self.channels = 2
        self.chunk_size = 1024

        # Dynamic Label Segment (DLS) data
        self.current_dls = ""
        self.slideshow_images = []

        # ETI processing
        self.eti_filename = "dab_ensemble.eti"
        self.extracted_audio_dir = "extracted_audio"
        self.slideshow_dir = "slideshow_images"

        # ni2out tool path
        self.ni2out_path = "/home/pi/DAB_Plus_Labs/eti/ni2out"

        # สร้างโฟลเดอร์ที่จำเป็น
        os.makedirs(self.extracted_audio_dir, exist_ok=True)
        os.makedirs(self.slideshow_dir, exist_ok=True)

    def load_service_list_from_eti(self):
        """
        โหลดรายการ services โดยตรงจาก ETI file ผ่าน ni2out --list
        """
        try:
            if not os.path.exists(self.ni2out_path):
                print(f"Error: ni2out tool not found at {self.ni2out_path}")
                return False

            if not os.path.exists(self.eti_filename):
                print(f"Error: ETI file not found: {self.eti_filename}")
                return False

            print(f"Reading services from ETI file: {self.eti_filename}")

            # รัน ni2out --list เพื่อดูรายการ services
            result = subprocess.run([
                self.ni2out_path,
                '--list',
                '-i', self.eti_filename
            ], capture_output=True, text=True)

            # ni2out outputs to stderr, not stdout
            output_text = result.stderr if result.stderr else result.stdout

            if not output_text:
                print(f"Error: No output from ni2out")
                return False

            # แยกข้อมูล services จาก output
            self.services = {}
            output_lines = output_text.strip().split('\n')

            for line in output_lines:
                # ตัวอย่าง output: " 0 : JKP TEST01       (0xa001) Pri subch= 1 ..."
                if ':' in line and '(' in line and ')' in line:
                    try:
                        # แยกชื่อ service และ service ID
                        parts = line.split(':')
                        if len(parts) >= 2:
                            # หาตำแหน่งของ '(' และ ')'
                            label_start = parts[1].find(' ')
                            label_end = parts[1].find('(')
                            sid_start = parts[1].find('(') + 1
                            sid_end = parts[1].find(')')

                            if label_end > 0 and sid_start > 0 and sid_end > 0:
                                label_part = parts[1][label_start:label_end].strip()
                                sid_part = parts[1][sid_start:sid_end].strip()

                                if sid_part.startswith('0x'):
                                    service_id = int(sid_part, 16)
                                    self.services[service_id] = {
                                        'label': label_part,
                                        'service_id': service_id,
                                        'components': []
                                    }
                    except Exception as e:
                        continue

            if self.services:
                print(f"\n✓ Found {len(self.services)} services:")
                for service_id, service_info in self.services.items():
                    print(f"  - {service_info['label']} (ID: 0x{service_id:04X})")
                return True
            else:
                print("No services found in ETI file")
                return False

        except Exception as e:
            print(f"Error loading service list from ETI: {e}")
            import traceback
            traceback.print_exc()
            return False

    def load_service_list(self, filename="service_list.json"):
        """
        โหลดรายการ services จาก JSON file หรือจาก ETI file
        """
        try:
            # ลองโหลดจาก JSON file ก่อน
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.services = {}
                for service in data.get('services', []):
                    service_id = service['service_id']
                    self.services[service_id] = {
                        'label': service['label'],
                        'service_id': service_id,
                        'components': service['components']
                    }

                print(f"\n✓ Loaded {len(self.services)} services from JSON:")
                for service_id, service_info in self.services.items():
                    print(f"  - {service_info['label']} (ID: 0x{service_id:04X})")

                return True

            # ถ้าไม่มี JSON file ให้ลองอ่านจาก ETI file โดยตรง
            else:
                print(f"\nService list file not found: {filename}")
                print("Trying to read services directly from ETI file...")
                return self.load_service_list_from_eti()

        except Exception as e:
            print(f"Error loading service list: {e}")
            # ถ้า error ให้ลองอ่านจาก ETI file
            return self.load_service_list_from_eti()

    def extract_audio_from_eti(self, service_id):
        """
        แยก audio data จาก ETI stream สำหรับ service ที่เลือก
        ใช้ ni2out tool สำหรับการ extract จริง
        """
        if service_id not in self.services:
            print(f"Service ID {service_id} not found")
            return None

        service_info = self.services[service_id]
        service_label = service_info['label']

        print(f"Extracting audio for service: {service_label} (0x{service_id:04X})")

        try:
            # ตรวจสอบว่า ni2out tool มีอยู่หรือไม่
            if not os.path.exists(self.ni2out_path):
                print(f"Error: ni2out tool not found at {self.ni2out_path}")
                print("Please build eti-tools or check the path")
                return None

            # ตรวจสอบว่า ETI file มีอยู่หรือไม่
            if not os.path.exists(self.eti_filename):
                print(f"Error: ETI file not found: {self.eti_filename}")
                return None

            # สร้างชื่อไฟล์ output
            safe_label = "".join(c for c in service_label if c.isalnum() or c in (' ', '-', '_')).strip()
            audio_filename = f"{self.extracted_audio_dir}/service_0x{service_id:04X}_{safe_label}.aac"

            # ใช้ ni2out tool แยก audio จาก ETI file
            print(f"Running: {self.ni2out_path} -i {self.eti_filename} -s 0x{service_id:04X}")

            with open(audio_filename, 'wb') as output_file:
                process = subprocess.Popen([
                    self.ni2out_path,
                    '-i', self.eti_filename,
                    '-s', f'0x{service_id:04X}'
                ], stdout=output_file, stderr=subprocess.PIPE)

                # รอให้ extract เสร็จ (หรือจำกัดเวลา)
                try:
                    stderr_output = process.communicate(timeout=10)[1]
                    if process.returncode != 0 and process.returncode is not None:
                        print(f"Warning: ni2out returned code {process.returncode}")
                except subprocess.TimeoutExpired:
                    # หยุดการ extract หลังจาก 10 วินาที
                    process.kill()
                    print("Extracted 10 seconds of audio")

            # ตรวจสอบว่าไฟล์ถูกสร้างและมีขนาด
            if os.path.exists(audio_filename) and os.path.getsize(audio_filename) > 0:
                file_size = os.path.getsize(audio_filename) / 1024  # KB
                print(f"✓ Audio extracted: {audio_filename} ({file_size:.1f} KB)")
                return audio_filename
            else:
                print(f"Error: Failed to extract audio")
                return None

        except Exception as e:
            print(f"Error extracting audio: {e}")
            import traceback
            traceback.print_exc()
            return None

    def create_dummy_audio_file(self, filename, service_label):
        """
        สร้างไฟล์เสียง dummy สำหรับการทดสอบ
        """
        try:
            # สร้าง sine wave tone สำหรับทดสอบ
            import numpy as np

            duration = 10  # วินาที
            sample_rate = 48000
            frequency = 440  # Hz (A4 note)

            # สร้าง stereo sine wave
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            left_channel = np.sin(2 * np.pi * frequency * t) * 0.3
            right_channel = np.sin(2 * np.pi * frequency * 1.2 * t) * 0.3

            # แปลงเป็น 16-bit PCM
            left_channel = (left_channel * 32767).astype(np.int16)
            right_channel = (right_channel * 32767).astype(np.int16)

            # สร้างไฟล์ WAV
            wav_filename = filename.replace('.aac', '.wav')
            with wave.open(wav_filename, 'w') as wav_file:
                wav_file.setnchannels(2)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)

                # Interleave stereo channels
                stereo_data = np.empty((len(left_channel) * 2,), dtype=np.int16)
                stereo_data[0::2] = left_channel
                stereo_data[1::2] = right_channel

                wav_file.writeframes(stereo_data.tobytes())

            print(f"Created test audio file: {wav_filename}")

            # แปลงเป็น AAC ด้วย ffmpeg (หากมี)
            try:
                subprocess.run([
                    'ffmpeg', '-y', '-i', wav_filename,
                    '-c:a', 'aac', '-b:a', '128k',
                    filename
                ], check=True, capture_output=True)

                # ลบไฟล์ WAV ชั่วคราว
                os.remove(wav_filename)
                print(f"Converted to AAC: {filename}")

            except (subprocess.CalledProcessError, FileNotFoundError):
                # หาก ffmpeg ไม่มี ให้ใช้ไฟล์ WAV แทน
                print("ffmpeg not available, using WAV file")
                os.rename(wav_filename, filename.replace('.aac', '.wav'))

        except Exception as e:
            print(f"Error creating dummy audio: {e}")

    def decode_aac_to_pcm(self, aac_filename):
        """
        Decode AAC file เป็น PCM สำหรับเล่นผ่าน PyAudio
        """
        try:
            pcm_filename = aac_filename.replace('.aac', '_pcm.wav')

            # ตรวจสอบว่าไฟล์ PCM มีอยู่แล้วหรือไม่
            if os.path.exists(pcm_filename):
                print(f"Using existing PCM file: {pcm_filename}")
                return pcm_filename

            # ใช้ ffmpeg decode AAC เป็น PCM WAV
            print("Decoding AAC to PCM using ffmpeg...")
            cmd = [
                'ffmpeg', '-y', '-i', aac_filename,
                '-f', 'wav', '-acodec', 'pcm_s16le',
                '-ar', str(self.sample_rate),
                '-ac', str(self.channels),
                pcm_filename
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✓ Decoded audio to: {pcm_filename}")
                return pcm_filename
            else:
                print(f"FFmpeg error: {result.stderr}")
                return None

        except Exception as e:
            print(f"Error decoding AAC: {e}")
            return None

    def play_audio_file(self, filename):
        """
        เล่นไฟล์เสียงผ่าน PyAudio
        """
        try:
            # เปิดไฟล์ WAV
            with wave.open(filename, 'rb') as wav_file:
                # ตรวจสอบ audio parameters
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                frame_rate = wav_file.getframerate()
                frames = wav_file.getnframes()

                print(f"\n{'='*50}")
                print(f"Playing audio:")
                print(f"  File: {os.path.basename(filename)}")
                print(f"  Channels: {channels}")
                print(f"  Sample width: {sample_width} bytes")
                print(f"  Frame rate: {frame_rate} Hz")
                print(f"  Duration: {frames/frame_rate:.2f} seconds")
                print(f"  Volume: {self.volume*100:.0f}%")
                print(f"{'='*50}")

                # เริ่ม PyAudio
                p = pyaudio.PyAudio()

                # เปิด audio stream
                stream = p.open(
                    format=p.get_format_from_width(sample_width),
                    channels=channels,
                    rate=frame_rate,
                    output=True,
                    frames_per_buffer=self.chunk_size
                )

                self.playing = True
                print("\n▶ Playing audio... (Press Ctrl+C to stop)\n")

                # อ่านและเล่นข้อมูลเสียง
                data = wav_file.readframes(self.chunk_size)
                while data and self.playing:
                    # ปรับระดับเสียง
                    if self.volume != 1.0:
                        # แปลงเป็น numpy array เพื่อปรับระดับเสียง
                        import numpy as np
                        if sample_width == 2:  # 16-bit
                            audio_data = np.frombuffer(data, dtype=np.int16)
                            audio_data = (audio_data * self.volume).astype(np.int16)
                            data = audio_data.tobytes()

                    stream.write(data)
                    data = wav_file.readframes(self.chunk_size)

                # ปิด stream
                stream.stop_stream()
                stream.close()
                p.terminate()

                print("\n■ Audio playback completed\n")

        except Exception as e:
            print(f"Error playing audio: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.playing = False

    def stop_playback(self):
        """หยุดการเล่นเสียง"""
        self.playing = False
        print("Stopping playback...")

    def set_volume(self, volume):
        """ตั้งค่าระดับเสียง (0.0 - 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        print(f"Volume set to: {self.volume*100:.0f}%")

    def extract_dynamic_label(self, service_id):
        """
        แยก Dynamic Label Segment (DLS) จาก service
        """
        try:
            # จำลองการแยก DLS data
            # ในการใช้งานจริง จะต้องแยกจาก MSC data ใน ETI stream

            if service_id in self.services:
                service_label = self.services[service_id]['label']

                # สร้าง mock DLS data
                mock_dls_data = [
                    f"Now Playing on {service_label}",
                    "Test Song Title - Test Artist",
                    "DAB+ Digital Radio",
                    f"Service ID: 0x{service_id:04X}"
                ]

                return mock_dls_data

        except Exception as e:
            print(f"Error extracting DLS: {e}")

        return []

    def extract_slideshow_images(self, service_id):
        """
        แยก MOT Slideshow images จาก service

        Solution: ni2out ไม่รองรับ MOT extraction โดยตรง
        วิธีการที่มี:
        1. ใช้ dablin_gtk (GUI) - รองรับ MOT slideshow แต่ต้องใช้ display
        2. ใช้ XPADxpert (Java GUI) - ต้อง manual save ผ่าน GUI
        3. Parse ETI stream manually - ต้องเขียน full DAB PAD parser

        สำหรับ lab นี้ เราจะใช้วิธี:
        - สร้าง mock images สำหรับการสาธิต
        - หรือใช้ dablin background mode (ถ้ามี X display)
        """
        try:
            if service_id not in self.services:
                return []

            service_label = self.services[service_id]['label']
            safe_label = "".join(c for c in service_label if c.isalnum() or c in (' ', '-', '_')).strip()

            images = []

            # วิธีที่ 1: ลอง extract จาก dablin (ถ้ามี display)
            # Note: dablin_gtk รองรับ MOT แต่ต้องมี GUI
            if os.environ.get('DISPLAY'):
                print("Attempting to extract MOT slideshow using dablin...")
                # dablin_gtk แสดง slideshow แต่ไม่มี option บันทึกไฟล์โดยตรง
                print("Note: dablin_gtk displays MOT but doesn't have CLI save option")

            # วิธีที่ 2: Parse ETI manually (Advanced - requires full implementation)
            # mot_images = self.parse_mot_from_eti(service_id)
            # if mot_images:
            #     return mot_images

            # วิธีที่ 3: สร้าง mock images สำหรับการสาธิต (educational purpose)
            print(f"Creating demo slideshow images for: {service_label}")
            print("Note: Real MOT extraction requires:")
            print("  - Full DAB PAD parser implementation")
            print("  - OR XPADxpert GUI tool for manual extraction")
            print("  - OR dablin_gtk for viewing (no CLI export)")

            for i in range(3):  # สร้าง 3 demo images
                image_filename = f"{self.slideshow_dir}/service_0x{service_id:04X}_{safe_label}_{i+1}.png"

                if not os.path.exists(image_filename):
                    self.create_dummy_slideshow_image(image_filename, service_label, i+1)

                images.append(image_filename)

            return images

        except Exception as e:
            print(f"Error extracting slideshow: {e}")
            return []

    def get_mot_extraction_info(self):
        """
        แสดงข้อมูลเกี่ยวกับวิธีการ extract MOT slideshow จริง
        """
        info = """
=== MOT Slideshow Extraction Methods ===

ni2out ไม่รองรับ MOT extraction โดยตรง

วิธีที่ 1: ใช้ dablin_gtk (แนะนำสำหรับการดู)
  - รองรับ MOT slideshow display
  - ต้องมี X display (GUI)
  - คำสั่ง: dablin_gtk -i dab_ensemble.eti
  - หมายเหตุ: แสดงภาพใน GUI แต่ไม่มี CLI export option

วิธีที่ 2: ใช้ XPADxpert (Java GUI tool)
  - ดาวน์โหลด: https://www.basicmaster.de/xpadxpert/
  - รองรับ ETI file analysis และ MOT extraction
  - คำสั่ง: java -jar XPADxpert.jar dab_ensemble.eti
  - สามารถ save MOT slides ผ่าน GUI (double-click)

วิธีที่ 3: ใช้ welle-io (รองรับ MOT)
  - GUI application สำหรับ DAB reception
  - รองรับ MOT slideshow display
  - คำสั่ง: welle-io

วิธีที่ 4: Parse ETI manually (Advanced)
  - ต้องเขียน DAB PAD parser เต็มรูปแบบ
  - อ้างอิง: ETSI EN 301 234 (MOT)
  - อ้างอิง: ETSI TS 101 499 (MOT Slideshow)
  - ต้อง decode X-PAD จาก MSC subchannel
  - Extract MOT headers และ body segments
  - Reassemble JPEG/PNG images

Python Libraries (สำหรับ encoding, not decoding):
  - python-mot-sls: MOT slideshow encoding
  - สำหรับ decoding ต้องเขียนเอง

สำหรับ Lab นี้:
  - ใช้ demo/mock images เพื่อแสดง concept
  - นักศึกษาสามารถใช้ dablin_gtk/XPADxpert ดู MOT จริง
        """
        return info

    def create_dummy_slideshow_image(self, filename, service_label, image_number):
        """
        สร้าง slideshow image dummy สำหรับการทดสอบ
        """
        try:
            from PIL import Image, ImageDraw, ImageFont

            # สร้างภาพ 320x240 pixels
            img = Image.new('RGB', (320, 240), color=(70, 130, 180))  # Steel blue
            draw = ImageDraw.Draw(img)

            # เขียนข้อความ
            try:
                # ใช้ font เริ่มต้น
                font = ImageFont.load_default()
            except:
                font = None

            # วาดกรอบ
            draw.rectangle([10, 10, 310, 230], outline=(255, 255, 255), width=2)

            # เขียนข้อความ
            text_lines = [
                f"Service: {service_label}",
                f"Slideshow Image #{image_number}",
                "DAB+ Digital Radio",
                "MOT Slideshow Demo"
            ]

            y_offset = 50
            for line in text_lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (320 - text_width) // 2
                draw.text((x, y_offset), line, fill=(255, 255, 255), font=font)
                y_offset += 30

            # บันทึกภาพ
            img.save(filename, 'PNG')
            print(f"Created slideshow image: {filename}")

        except Exception as e:
            print(f"Error creating slideshow image: {e}")

    def display_service_info(self, service_id):
        """
        แสดงข้อมูลของ service
        """
        if service_id not in self.services:
            print(f"Service ID {service_id} not found")
            return

        service_info = self.services[service_id]

        print(f"\n" + "="*50)
        print(f"SERVICE INFORMATION")
        print(f"="*50)
        print(f"Service ID: 0x{service_id:04X} ({service_id})")
        print(f"Label: {service_info['label']}")
        print(f"Components: {len(service_info['components'])}")

        for i, comp in enumerate(service_info['components']):
            print(f"  Component {i+1}:")
            print(f"    Type: {comp.get('component_type', 'Unknown')}")
            print(f"    Subchannel: {comp.get('subchannel_id', 'Unknown')}")

        # แสดง Dynamic Label
        dls_data = self.extract_dynamic_label(service_id)
        if dls_data:
            print(f"\nDynamic Label Segment (DLS):")
            for dls in dls_data:
                print(f"  {dls}")

        # แสดงรายการ slideshow images
        images = self.extract_slideshow_images(service_id)
        if images:
            print(f"\nSlideshow Images:")
            for img in images:
                if os.path.exists(img):
                    print(f"  {img}")

        print(f"="*50)

    def play_service(self, service_id):
        """
        เล่น service ที่เลือก
        """
        if service_id not in self.services:
            print(f"Service ID {service_id} not found")
            return

        print(f"Playing service: {self.services[service_id]['label']}")

        try:
            # แสดงข้อมูล service
            self.display_service_info(service_id)

            # แยก audio
            audio_filename = self.extract_audio_from_eti(service_id)
            if not audio_filename:
                print("Failed to extract audio")
                return

            # ตรวจสอบว่าเป็นไฟล์ AAC หรือ WAV
            if audio_filename.endswith('.aac'):
                # Decode AAC เป็น PCM
                pcm_filename = self.decode_aac_to_pcm(audio_filename)
                if pcm_filename:
                    audio_filename = pcm_filename
                else:
                    print("Failed to decode AAC audio")
                    return

            # เล่นเสียง
            if audio_filename and os.path.exists(audio_filename):
                self.current_service = service_id

                # เล่นใน thread แยก
                audio_thread = threading.Thread(
                    target=self.play_audio_file,
                    args=(audio_filename,)
                )
                audio_thread.start()

                # แสดง slideshow images
                self.show_slideshow(service_id)

                # รอจนกว่าเสียงจะเล่นจบ
                audio_thread.join()

            else:
                print("Audio file not found")

        except Exception as e:
            print(f"Error playing service: {e}")

    def show_slideshow(self, service_id):
        """
        แสดง slideshow images (สำหรับ command line)
        """
        images = self.extract_slideshow_images(service_id)

        if not images:
            return

        print(f"\nSlideshow for service: {self.services[service_id]['label']}")

        for i, img_path in enumerate(images):
            if os.path.exists(img_path):
                print(f"Image {i+1}: {img_path}")

                # ลองเปิดรูปด้วย default viewer (หากมี GUI)
                try:
                    if os.environ.get('DISPLAY'):  # มี X11 display
                        subprocess.Popen(['xdg-open', img_path])
                        time.sleep(2)  # แสดงแต่ละรูป 2 วินาที
                except:
                    pass

def list_available_services():
    """แสดงรายการ services ที่มี"""
    player = DABServicePlayer()

    if player.load_service_list():
        print("\nAvailable DAB+ Services:")
        print("-" * 40)

        for service_id, service_info in player.services.items():
            components = len(service_info['components'])
            print(f"ID: 0x{service_id:04X} | {service_info['label']} ({components} components)")

        print("-" * 40)
        print(f"Total: {len(player.services)} services")

        return list(player.services.keys())

    return []

def show_mot_info():
    """แสดงข้อมูลเกี่ยวกับการ extract MOT slideshow"""
    player = DABServicePlayer()
    print(player.get_mot_extraction_info())

def main():
    """ฟังก์ชันหลักสำหรับทดสอบ"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Lab 3 Phase 4: DAB+ Service Display & Audio Playback',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 lab3_4.py                  # Play first available service
  python3 lab3_4.py -s 0xa001        # Play specific service by ID
  python3 lab3_4.py -s 0xa001        # Also supports hex format
  python3 lab3_4.py -l               # List all services
  python3 lab3_4.py --mot-info       # Show MOT extraction information
        '''
    )

    parser.add_argument('-s', '--service',
                        type=str,
                        help='Service ID to play (hex: 0xa001 or decimal: 40961)')
    parser.add_argument('-l', '--list',
                        action='store_true',
                        help='List all available services and exit')
    parser.add_argument('--mot-info',
                        action='store_true',
                        help='Show MOT slideshow extraction information')

    args = parser.parse_args()

    print("=== Lab 3 Phase 4: Service Display & Audio Playback ===")
    print("\nThis lab continues from lab3_3.py")
    print("It loads the service list and plays audio from selected services\n")

    # Show MOT info if requested
    if args.mot_info:
        show_mot_info()
        return

    # แสดงรายการ services
    available_services = list_available_services()

    if not available_services:
        print("\n✗ No services found.")
        print("\nWorkflow:")
        print("  1. Run lab3_2.py to capture DAB signal and create ETI file")
        print("  2. Run lab3_3.py to analyze ETI and extract service list")
        print("  3. Run lab3_4.py to play audio from services")
        return

    # Just list services if requested
    if args.list:
        print("\nUse -s option to play a specific service")
        print("Example: python3 lab3_4.py -s 0xa001")
        return

    # Determine which service to play
    service_id = None
    if args.service:
        # Parse service ID from argument
        try:
            if args.service.startswith('0x') or args.service.startswith('0X'):
                service_id = int(args.service, 16)
            else:
                service_id = int(args.service)

            # Validate service ID exists
            if service_id not in available_services:
                print(f"\n✗ Service ID 0x{service_id:04X} not found in ensemble")
                print("\nAvailable services:")
                for sid in available_services:
                    print(f"  0x{sid:04X}")
                return

        except ValueError:
            print(f"✗ Invalid service ID format: {args.service}")
            print("Use hex (0xa001) or decimal (40961) format")
            return
    else:
        # Use first service as default
        service_id = available_services[0]
        print(f"\n→ No service specified, using first service: 0x{service_id:04X}")
        print(f"\nTip: Use -s option to select specific service")
        print(f"Example: python3 lab3_4.py -s 0x{service_id:04X}")

    # สร้าง player และเล่น service
    player = DABServicePlayer()

    try:
        if player.load_service_list():
            print(f"\nControls:")
            print(f"  Volume: Use arrow keys (not implemented in command line)")
            print(f"  Stop: Press Ctrl+C")
            print(f"\nNote: For MOT slideshow info, run: python3 lab3_4.py --mot-info")

            # เล่น service
            player.play_service(service_id)

    except KeyboardInterrupt:
        print("\nStopping playback...")
        player.stop_playback()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()