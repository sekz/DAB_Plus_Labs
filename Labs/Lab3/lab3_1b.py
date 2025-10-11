#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 3 Phase 1b: RTL-SDR Data Acquisition (rtl_tcp client version) - SOLUTION
เป้าหมาย: รับ I/Q data ผ่าน network protocol

Dependencies:
pip install numpy scipy matplotlib
sudo apt install rtl-sdr
"""

import socket
import struct
import numpy as np
import time
import sys
import threading
import matplotlib.pyplot as plt

class RTLTCPClient:
    def __init__(self, host='localhost', port=1234):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False

        # ความถี่ DAB+ Thailand (185.360 MHz - Bangkok/Phuket)
        self.frequency = 185360000  # Hz
        self.sample_rate = 2048000  # 2.048 MHz สำหรับ DAB+
        self.gain = 20  # dB, ปรับตามความเหมาะสม

        # Buffer สำหรับเก็บข้อมูล
        self.receive_buffer = bytearray()
        self.samples_buffer = []
        self.capture_active = False

    def connect_to_server(self):
        """
        เชื่อมต่อไปยัง rtl_tcp server
        """
        try:
            print(f"Connecting to rtl_tcp server at {self.host}:{self.port}")

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # 10 second timeout
            self.socket.connect((self.host, self.port))

            print("Connected to rtl_tcp server successfully")
            self.connected = True

            # ตั้งค่าเริ่มต้น
            self.configure_rtlsdr()

            return True

        except socket.timeout:
            print("Connection timeout - is rtl_tcp server running?")
            return False
        except ConnectionRefusedError:
            print("Connection refused - start rtl_tcp server first")
            print("Run: rtl_tcp -a 127.0.0.1 -p 1234")
            return False
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False

    def send_command(self, cmd, value):
        """
        ส่งคำสั่งไปยัง rtl_tcp server
        """
        if not self.connected:
            return False

        try:
            # rtl_tcp command format: [cmd:1byte][value:4bytes big-endian]
            command = struct.pack('>BI', cmd, value)
            self.socket.send(command)
            print(f"Sent command {cmd} with value {value}")
            return True
        except Exception as e:
            print(f"Error sending command: {e}")
            return False

    def configure_rtlsdr(self):
        """
        ตั้งค่า RTL-SDR ผ่าน rtl_tcp commands
        """
        print("Configuring RTL-SDR...")

        # rtl_tcp command definitions
        # 0x01: frequency
        # 0x02: sample rate
        # 0x03: gain mode (0=auto, 1=manual)
        # 0x04: gain
        # 0x05: frequency correction

        try:
            # ตั้งค่า sample rate
            success = self.send_command(0x02, self.sample_rate)
            if success:
                print(f"Sample rate set to: {self.sample_rate/1e6:.3f} Msps")
            time.sleep(0.1)

            # ตั้งค่าความถี่
            success = self.send_command(0x01, self.frequency)
            if success:
                print(f"Center frequency set to: {self.frequency/1e6:.3f} MHz")
            time.sleep(0.1)

            # ตั้งค่า gain mode เป็น manual
            success = self.send_command(0x03, 1)
            if success:
                print("Gain mode set to: manual")
            time.sleep(0.1)

            # ตั้งค่า gain
            success = self.send_command(0x04, self.gain * 10)  # gain in 0.1 dB
            if success:
                print(f"Gain set to: {self.gain} dB")
            time.sleep(0.1)

            print("RTL-SDR configuration completed")
            return True

        except Exception as e:
            print(f"Error configuring RTL-SDR: {e}")
            return False

    def receive_data_thread(self):
        """
        Thread สำหรับรับข้อมูลจาก rtl_tcp server
        """
        print("Starting data reception thread...")

        try:
            while self.capture_active and self.connected:
                # รับข้อมูลแบบ chunks
                try:
                    data = self.socket.recv(8192)  # 8KB buffer
                    if not data:
                        print("No data received - server disconnected")
                        break

                    self.receive_buffer.extend(data)

                    # แปลงข้อมูลเป็น I/Q samples เมื่อมีข้อมูลเพียงพอ
                    while len(self.receive_buffer) >= 2:
                        # rtl_tcp ส่งข้อมูลเป็น uint8 I,Q pairs
                        i_raw = self.receive_buffer[0]
                        q_raw = self.receive_buffer[1]

                        # แปลงจาก uint8 (0-255) เป็น float (-1 to 1)
                        i = (i_raw - 127.5) / 127.5
                        q = (q_raw - 127.5) / 127.5

                        # สร้าง complex sample
                        sample = complex(i, q)
                        self.samples_buffer.append(sample)

                        # ลบข้อมูลที่ใช้แล้วออกจาก buffer
                        del self.receive_buffer[:2]

                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error in receive thread: {e}")
                    break

        except Exception as e:
            print(f"Fatal error in receive thread: {e}")

        print("Data reception thread stopped")

    def capture_samples(self, duration_seconds=10):
        """
        รับ I/Q samples และบันทึกเป็นไฟล์
        """
        if not self.connected:
            print("Not connected to rtl_tcp server")
            return None

        try:
            # คำนวณจำนวน samples ที่ต้องการ
            expected_samples = int(duration_seconds * self.sample_rate)

            print(f"Capturing {duration_seconds} seconds of data...")
            print(f"Expected samples: {expected_samples:,}")

            # เริ่มการรับข้อมูล
            self.samples_buffer = []
            self.capture_active = True

            # เริ่ม thread สำหรับรับข้อมูล
            receive_thread = threading.Thread(target=self.receive_data_thread)
            receive_thread.start()

            # รอจนกว่าจะได้ข้อมูลเพียงพอ
            start_time = time.time()
            last_count = 0

            while len(self.samples_buffer) < expected_samples:
                current_time = time.time()
                elapsed = current_time - start_time
                current_count = len(self.samples_buffer)

                # แสดงความคืบหน้าทุก 1 วินาที
                if int(elapsed) > int(elapsed - 0.1):
                    rate = (current_count - last_count) if elapsed > 1 else current_count
                    percent = (current_count / expected_samples) * 100
                    print(f"Progress: {current_count:,}/{expected_samples:,} samples "
                          f"({percent:.1f}%) - Rate: {rate:,} sps")
                    last_count = current_count

                # ตรวจสอบ timeout
                if elapsed > duration_seconds + 5:  # พิเศษ 5 วินาที
                    print("Capture timeout - stopping")
                    break

                time.sleep(0.1)

            # หยุดการรับข้อมูล
            self.capture_active = False
            receive_thread.join(timeout=2)

            capture_time = time.time() - start_time
            actual_samples = len(self.samples_buffer)

            print(f"Capture completed in {capture_time:.2f} seconds")
            print(f"Actual samples received: {actual_samples:,}")

            if actual_samples == 0:
                print("No samples received!")
                return None

            # แปลงเป็น numpy array
            samples = np.array(self.samples_buffer[:expected_samples], dtype=np.complex64)

            # คำนวณ signal strength (RMS)
            signal_strength = np.sqrt(np.mean(np.abs(samples)**2))

            print(f"Signal strength (RMS): {signal_strength:.6f}")
            print(f"Max amplitude: {np.max(np.abs(samples)):.6f}")
            print(f"Sample data type: {samples.dtype}")

            # บันทึกเป็นไฟล์ binary
            filename = "networked_iq_data.bin"
            samples.tofile(filename)

            print(f"Saved {len(samples)} samples to {filename}")
            print(f"File size: {len(samples) * 8} bytes")  # complex64 = 8 bytes per sample

            return samples

        except Exception as e:
            print(f"Error capturing samples: {e}")
            self.capture_active = False
            return None

    def analyze_spectrum(self, samples):
        """
        วิเคราะห์สเปกตรัมของสัญญาณ
        """
        if samples is None:
            return

        print("\nAnalyzing spectrum...")

        try:
            # คำนวณ FFT
            fft_size = 1024
            num_ffts = len(samples) // fft_size

            if num_ffts == 0:
                print("Not enough samples for FFT analysis")
                return

            # คำนวณ average spectrum
            spectrum = np.zeros(fft_size)
            for i in range(num_ffts):
                start_idx = i * fft_size
                end_idx = start_idx + fft_size
                window = np.hanning(fft_size)
                fft_data = np.fft.fft(samples[start_idx:end_idx] * window)
                spectrum += np.abs(fft_data)**2

            spectrum = spectrum / num_ffts
            spectrum_db = 10 * np.log10(spectrum + 1e-12)

            # คำนวณ frequency bins
            freqs = np.fft.fftfreq(fft_size, 1/self.sample_rate)
            freqs = freqs + self.frequency  # แปลงเป็น absolute frequency

            # หาจุดที่มี signal แรงที่สุด
            max_idx = np.argmax(spectrum)
            max_freq = freqs[max_idx]
            max_power = spectrum_db[max_idx]

            print(f"Strongest signal at: {max_freq/1e6:.3f} MHz")
            print(f"Power: {max_power:.1f} dB")

            # แสดงข้อมูลสเปกตรัม
            print(f"Frequency range: {freqs[0]/1e6:.3f} - {freqs[-1]/1e6:.3f} MHz")
            print(f"Resolution: {(freqs[1] - freqs[0])/1e3:.1f} kHz")

            # สร้างกราฟ (optional)
            try:
                plt.figure(figsize=(12, 6))
                plt.plot(freqs/1e6, spectrum_db)
                plt.xlabel('Frequency (MHz)')
                plt.ylabel('Power (dB)')
                plt.title(f'Spectrum Analysis (rtl_tcp) - Center: {self.frequency/1e6:.3f} MHz')
                plt.grid(True)
                plt.savefig('spectrum_analysis_rtltcp.png', dpi=150, bbox_inches='tight')
                print("Spectrum plot saved as 'spectrum_analysis_rtltcp.png'")
                plt.close()
            except Exception as plot_error:
                print(f"Could not create plot: {plot_error}")

            print("Spectrum analysis completed")

        except Exception as e:
            print(f"Error in spectrum analysis: {e}")

    def disconnect(self):
        """ปิดการเชื่อมต่อ rtl_tcp server"""
        print("Disconnecting from rtl_tcp server...")

        self.capture_active = False
        self.connected = False

        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

        print("Disconnected from rtl_tcp server")

def start_rtl_tcp_server():
    """
    เริ่ม rtl_tcp server (สำหรับการทดสอบ)
    """
    import subprocess
    import os

    print("Starting rtl_tcp server...")
    print("Command: rtl_tcp -a 127.0.0.1 -p 1234 -f 185360000 -s 2048000")

    try:
        # เริ่ม rtl_tcp server ใน background
        process = subprocess.Popen([
            'rtl_tcp',
            '-a', '127.0.0.1',
            '-p', '1234',
            '-f', str(185360000),
            '-s', str(2048000)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print(f"rtl_tcp server started with PID: {process.pid}")
        print("Waiting for server to initialize...")
        time.sleep(3)

        return process

    except FileNotFoundError:
        print("rtl_tcp not found. Install with: sudo apt install rtl-sdr")
        return None
    except Exception as e:
        print(f"Error starting rtl_tcp server: {e}")
        return None

def test_connection(host='localhost', port=1234):
    """ทดสอบการเชื่อมต่อ rtl_tcp server"""
    print(f"Testing connection to {host}:{port}")

    client = RTLTCPClient(host, port)

    try:
        if client.connect_to_server():
            print("Connection test successful!")

            # ทดสอบรับข้อมูลสั้นๆ
            samples = client.capture_samples(2)  # 2 seconds
            if samples is not None:
                print("Data reception test successful!")
                client.analyze_spectrum(samples)
            else:
                print("Data reception test failed!")

        else:
            print("Connection test failed!")

    except Exception as e:
        print(f"Test error: {e}")
    finally:
        client.disconnect()

def main():
    """ฟังก์ชันหลักสำหรับทดสอบ"""
    print("=== Lab 3 Phase 1b: RTL-SDR Data Acquisition (rtl_tcp client) ===")

    # ตรวจสอบ arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--start-server":
            # เริ่ม rtl_tcp server
            server_process = start_rtl_tcp_server()
            if server_process:
                print("Press Ctrl+C to stop server")
                try:
                    server_process.wait()
                except KeyboardInterrupt:
                    print("\nStopping server...")
                    server_process.terminate()
            return

        elif sys.argv[1] == "--test":
            # ทดสอบการเชื่อมต่อ
            test_connection()
            return

    # การใช้งานปกติ
    client = RTLTCPClient()

    try:
        # เชื่อมต่อ rtl_tcp server
        if not client.connect_to_server():
            print("Failed to connect to rtl_tcp server.")
            print("Start server first with: python lab3_1b.py --start-server")
            print("Or manually: rtl_tcp -a 127.0.0.1 -p 1234")
            return

        # รับ samples
        samples = client.capture_samples(10)

        if samples is not None:
            # วิเคราะห์สเปกตรัม
            client.analyze_spectrum(samples)

            # แสดงสถิติเพิ่มเติม
            print(f"\n=== Additional Statistics ===")
            print(f"Mean amplitude: {np.mean(np.abs(samples)):.6f}")
            print(f"Standard deviation: {np.std(np.abs(samples)):.6f}")
            print(f"Peak-to-average ratio: {np.max(np.abs(samples))/np.mean(np.abs(samples)):.2f}")

            # เปรียบเทียบกับ lab3_1a.py
            print(f"\n=== Comparison with lab3_1a.py ===")
            try:
                # อ่านไฟล์จาก lab3_1a.py หากมี
                import os
                if os.path.exists('raw_iq_data.bin'):
                    direct_samples = np.fromfile('raw_iq_data.bin', dtype=np.complex64)
                    if len(direct_samples) > 0:
                        direct_strength = np.sqrt(np.mean(np.abs(direct_samples)**2))
                        network_strength = np.sqrt(np.mean(np.abs(samples)**2))
                        print(f"Direct RTL-SDR signal strength: {direct_strength:.6f}")
                        print(f"Network RTL-SDR signal strength: {network_strength:.6f}")
                        print(f"Strength ratio (network/direct): {network_strength/direct_strength:.3f}")
                    else:
                        print("No direct samples found for comparison")
                else:
                    print("raw_iq_data.bin not found - run lab3_1a.py first")
            except Exception as e:
                print(f"Error comparing with direct samples: {e}")

    except KeyboardInterrupt:
        print("\nUser interrupted")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()