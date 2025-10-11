#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 3 Phase 1a: RTL-SDR Data Acquisition (pyrtlsdr version) - SOLUTION
เป้าหมาย: รับ I/Q data พื้นฐานจาก RTL-SDR

Dependencies:
pip install pyrtlsdr numpy scipy matplotlib
"""

import numpy as np
from rtlsdr import RtlSdr
import time
import sys
import matplotlib.pyplot as plt

class RTLSDRDataAcquisition:
    def __init__(self):
        self.sdr = None
        # ความถี่ DAB+ Thailand (185.360 MHz - Khon Kane/Mhasarakam Testing)
        self.frequency = 185360000  # Hz
        self.sample_rate = 2048000  # 2.048 MHz สำหรับ DAB+
        self.gain = 'auto'  # ใช้ auto gain แล้วปรับหากจำเป็น

    def setup_rtlsdr(self):
        """
        ติดตั้งและตั้งค่า RTL-SDR
        """
        try:
            # สร้าง RtlSdr object
            self.sdr = RtlSdr()

            # ตั้งค่า sample rate
            self.sdr.sample_rate = self.sample_rate
            print(f"Sample rate set to: {self.sdr.sample_rate/1e6:.3f} Msps")

            # ตั้งค่าความถี่
            self.sdr.center_freq = self.frequency
            print(f"Center frequency set to: {self.sdr.center_freq/1e6:.3f} MHz")

            # ตั้งค่า gain
            if self.gain == 'auto':
                self.sdr.gain = 'auto'
                print("Gain set to: auto")
            else:
                self.sdr.gain = self.gain
                print(f"Gain set to: {self.sdr.gain} dB")

            print(f"RTL-SDR setup completed:")
            print(f"Frequency: {self.frequency/1e6:.3f} MHz")
            print(f"Sample Rate: {self.sample_rate/1e6:.1f} Msps")
            print(f"Gain: {self.gain}")

            # แสดงข้อมูล device
            print(f"Device: {self.sdr.get_tuner_type()}")

        except Exception as e:
            print(f"Error setting up RTL-SDR: {e}")
            print("Make sure RTL-SDR is connected and drivers are installed.")
            return False

        return True

    def capture_samples(self, duration_seconds=10):
        """
        รับ I/Q samples และบันทึกเป็นไฟล์
        """
        if not self.sdr:
            print("RTL-SDR not initialized")
            return None

        try:
            # คำนวณจำนวน samples ที่ต้องการ
            num_samples = int(duration_seconds * self.sample_rate)

            print(f"Capturing {duration_seconds} seconds of data...")
            print(f"Number of samples: {num_samples:,}")

            # รับ samples จาก RTL-SDR
            start_time = time.time()
            samples = self.sdr.read_samples(num_samples)
            capture_time = time.time() - start_time

            print(f"Capture completed in {capture_time:.2f} seconds")
            print(f"Actual samples received: {len(samples):,}")

            # คำนวณ signal strength (RMS)
            signal_strength = np.sqrt(np.mean(np.abs(samples)**2))

            print(f"Signal strength (RMS): {signal_strength:.6f}")
            print(f"Max amplitude: {np.max(np.abs(samples)):.6f}")
            print(f"Sample data type: {samples.dtype}")

            # บันทึกเป็นไฟล์ binary
            filename = "raw_iq_data.bin"
            samples.tofile(filename)

            print(f"Saved {len(samples)} samples to {filename}")
            print(f"File size: {len(samples) * 8} bytes")  # complex64 = 8 bytes per sample

            return samples

        except Exception as e:
            print(f"Error capturing samples: {e}")
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
                plt.title(f'Spectrum Analysis - Center: {self.frequency/1e6:.3f} MHz')
                plt.grid(True)
                plt.savefig('spectrum_analysis.png', dpi=150, bbox_inches='tight')
                print("Spectrum plot saved as 'spectrum_analysis.png'")
                plt.close()
            except Exception as plot_error:
                print(f"Could not create plot: {plot_error}")

            print("Spectrum analysis completed")

        except Exception as e:
            print(f"Error in spectrum analysis: {e}")

    def cleanup(self):
        """ปิดการเชื่อมต่อ RTL-SDR"""
        if self.sdr:
            self.sdr.close()
            print("RTL-SDR connection closed")

def test_different_frequencies():
    """ทดสอบความถี่ DAB+ ต่างๆ ในประเทศไทย"""
    frequencies = {
        'Bangkok/Phuket': 185360000,  # Block 7A
        'Chiang Mai': 195936000,     # Block 8C
    }

    for location, freq in frequencies.items():
        print(f"\n=== Testing {location} - {freq/1e6:.3f} MHz ===")

        rtl_capture = RTLSDRDataAcquisition()
        rtl_capture.frequency = freq

        try:
            if rtl_capture.setup_rtlsdr():
                samples = rtl_capture.capture_samples(5)  # 5 seconds test
                if samples is not None:
                    rtl_capture.analyze_spectrum(samples)
        except Exception as e:
            print(f"Error testing {location}: {e}")
        finally:
            rtl_capture.cleanup()

def main():
    """ฟังก์ชันหลักสำหรับทดสอบ"""
    print("=== Lab 3 Phase 1a: RTL-SDR Data Acquisition ===")

    # สร้าง instance ของ RTLSDRDataAcquisition
    rtl_capture = RTLSDRDataAcquisition()

    try:
        # ตั้งค่า RTL-SDR
        if not rtl_capture.setup_rtlsdr():
            print("Failed to setup RTL-SDR. Exiting.")
            return

        # รับ samples
        samples = rtl_capture.capture_samples(10)

        if samples is not None:
            # วิเคราะห์สเปกตรัม
            rtl_capture.analyze_spectrum(samples)

            # แสดงสถิติเพิ่มเติม
            print(f"\n=== Additional Statistics ===")
            print(f"Mean amplitude: {np.mean(np.abs(samples)):.6f}")
            print(f"Standard deviation: {np.std(np.abs(samples)):.6f}")
            print(f"Peak-to-average ratio: {np.max(np.abs(samples))/np.mean(np.abs(samples)):.2f}")

        # ทดสอบความถี่อื่นๆ หากต้องการ
        if len(sys.argv) > 1 and sys.argv[1] == "--test-all":
            test_different_frequencies()

    except KeyboardInterrupt:
        print("\nUser interrupted")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        rtl_capture.cleanup()

if __name__ == "__main__":
    main()