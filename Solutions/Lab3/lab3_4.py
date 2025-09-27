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

        # สร้างโฟลเดอร์ที่จำเป็น
        os.makedirs(self.extracted_audio_dir, exist_ok=True)
        os.makedirs(self.slideshow_dir, exist_ok=True)

    def load_service_list(self, filename="service_list.json"):
        """
        โหลดรายการ services จาก JSON file
        """
        try:
            if not os.path.exists(filename):
                print(f"Service list file not found: {filename}")
                print("Run lab3_3.py first to analyze ETI and generate service list")
                return False

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

            print(f"Loaded {len(self.services)} services:")
            for service_id, service_info in self.services.items():
                print(f"  - {service_info['label']} (ID: 0x{service_id:04X})")

            return True

        except Exception as e:
            print(f"Error loading service list: {e}")
            return False

    def extract_audio_from_eti(self, service_id):
        """
        แยก audio data จาก ETI stream สำหรับ service ที่เลือก
        """
        if service_id not in self.services:
            print(f"Service ID {service_id} not found")
            return None

        service_info = self.services[service_id]
        service_label = service_info['label']

        print(f"Extracting audio for service: {service_label}")

        try:
            # สร้างชื่อไฟล์ output
            safe_label = "".join(c for c in service_label if c.isalnum() or c in (' ', '-', '_')).strip()
            audio_filename = f"{self.extracted_audio_dir}/service_{service_id}_{safe_label}.aac"

            # ใช้ ffmpeg extract audio จาก ETI stream
            # Note: การ extract จริงต้องใช้เครื่องมือพิเศษเช่น ODR-AudioEnc หรือ similar
            # ที่นี่เป็นการจำลองการทำงาน

            # วิธีการจำลอง: สร้าง dummy audio file
            if not os.path.exists(audio_filename):
                print("Note: Creating dummy audio file for demonstration")
                self.create_dummy_audio_file(audio_filename, service_label)

            return audio_filename

        except Exception as e:
            print(f"Error extracting audio: {e}")
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

            # ใช้ ffmpeg decode AAC เป็น PCM WAV
            cmd = [
                'ffmpeg', '-y', '-i', aac_filename,
                '-f', 'wav', '-acodec', 'pcm_s16le',
                '-ar', str(self.sample_rate),
                '-ac', str(self.channels),
                pcm_filename
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"Decoded audio to: {pcm_filename}")
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

                print(f"Playing audio:")
                print(f"  Channels: {channels}")
                print(f"  Sample width: {sample_width} bytes")
                print(f"  Frame rate: {frame_rate} Hz")
                print(f"  Duration: {frames/frame_rate:.2f} seconds")

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
                print("Playing audio... (Press Ctrl+C to stop)")

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

                print("Audio playback completed")

        except Exception as e:
            print(f"Error playing audio: {e}")
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
        """
        try:
            if service_id not in self.services:
                return []

            service_label = self.services[service_id]['label']
            safe_label = "".join(c for c in service_label if c.isalnum() or c in (' ', '-', '_')).strip()

            # จำลองการสร้าง slideshow images
            # ในการใช้งานจริง จะต้องแยกจาก MSC data ใน ETI stream

            images = []
            for i in range(3):  # สร้าง 3 images
                image_filename = f"{self.slideshow_dir}/service_{service_id}_{safe_label}_{i+1}.png"

                if not os.path.exists(image_filename):
                    self.create_dummy_slideshow_image(image_filename, service_label, i+1)

                images.append(image_filename)

            return images

        except Exception as e:
            print(f"Error extracting slideshow: {e}")
            return []

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

def main():
    """ฟังก์ชันหลักสำหรับทดสอบ"""
    print("=== Lab 3 Phase 4: Service Display & Audio Playback ===")

    # แสดงรายการ services
    available_services = list_available_services()

    if not available_services:
        print("No services found. Run lab3_3.py first to analyze ETI file.")
        return

    # ตรวจสอบ command line arguments
    if len(sys.argv) > 1:
        try:
            if sys.argv[1].startswith('0x'):
                service_id = int(sys.argv[1], 16)
            else:
                service_id = int(sys.argv[1])
        except ValueError:
            print("Invalid service ID format. Use decimal or hex (0x1234)")
            return
    else:
        # ใช้ service แรกที่มี
        service_id = available_services[0]
        print(f"\nNo service specified, using first service: 0x{service_id:04X}")

    # สร้าง player และเล่น service
    player = DABServicePlayer()

    try:
        if player.load_service_list():
            print(f"\nControls:")
            print(f"  Volume: Use arrow keys (not implemented in command line)")
            print(f"  Stop: Press Ctrl+C")

            # เล่น service
            player.play_service(service_id)

    except KeyboardInterrupt:
        print("\nStopping playback...")
        player.stop_playback()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()