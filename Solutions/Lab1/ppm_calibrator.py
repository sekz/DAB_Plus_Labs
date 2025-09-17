#!/usr/bin/env python3
"""
PPM Calibration Implementation
Solution for Lab 1 Trap 1.3: PPM Calibration Analysis
"""

import subprocess
import re
import numpy as np
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class PPMCalibrator:
    """RTL-SDR PPM (Parts Per Million) calibration tools"""

    def __init__(self, device_index: int = 0):
        self.device_index = device_index
        self.calibration_history = []
        self.current_ppm = 0

    def scan_gsm_channels(self, band: str = 'GSM900') -> List[Dict]:
        """Scan for GSM channels using kalibrate-rtl"""
        channels = []

        try:
            print(f"Scanning {band} band for GSM signals...")

            # Use kalibrate-rtl to scan for channels
            result = subprocess.run(
                ['kal', '-s', band, '-g', '40'],
                capture_output=True, text=True, timeout=120
            )

            if result.returncode != 0:
                print(f"GSM scan failed: {result.stderr}")
                return []

            # Parse output for channel information
            for line in result.stdout.split('\n'):
                if 'chan:' in line.lower():
                    channel_match = re.search(r'chan:\s*(\d+)', line)
                    power_match = re.search(r'power:\s*([-\d.]+)', line)
                    freq_match = re.search(r'freq:\s*([\d.]+)', line)

                    if channel_match and power_match:
                        channel_info = {
                            'channel': int(channel_match.group(1)),
                            'power': float(power_match.group(1)),
                            'frequency': float(freq_match.group(1)) if freq_match else None,
                            'band': band,
                            'scan_time': datetime.now().isoformat()
                        }
                        channels.append(channel_info)

            # Sort by power (strongest first)
            channels.sort(key=lambda x: x['power'], reverse=True)

        except subprocess.TimeoutExpired:
            print("GSM scan timed out - try again or check antenna connection")
        except FileNotFoundError:
            print("kalibrate-rtl (kal) not found - install with: sudo apt install kalibrate-rtl")
        except Exception as e:
            print(f"GSM scan error: {e}")

        return channels

    def calibrate_ppm(self, channel: int, band: str = 'GSM900', duration: int = 30) -> Optional[Dict]:
        """Calibrate PPM using specific GSM channel"""
        try:
            print(f"Calibrating PPM using {band} channel {channel}...")

            # Run calibration
            result = subprocess.run(
                ['kal', '-c', str(channel), '-g', '40', '-d', str(self.device_index)],
                capture_output=True, text=True, timeout=duration + 10
            )

            if result.returncode != 0:
                print(f"Calibration failed: {result.stderr}")
                return None

            # Parse calibration results
            calibration_data = self._parse_calibration_output(result.stdout)

            if calibration_data:
                calibration_data.update({
                    'channel': channel,
                    'band': band,
                    'device_index': self.device_index,
                    'calibration_time': datetime.now().isoformat(),
                    'raw_output': result.stdout
                })

                # Update current PPM
                if 'average_absolute_error' in calibration_data:
                    self.current_ppm = calibration_data['average_absolute_error']

                # Store in history
                self.calibration_history.append(calibration_data)

                return calibration_data

        except subprocess.TimeoutExpired:
            print("Calibration timed out - signal may be weak")
        except Exception as e:
            print(f"Calibration error: {e}")

        return None

    def _parse_calibration_output(self, output: str) -> Dict:
        """Parse kalibrate-rtl calibration output"""
        data = {}

        # Look for average absolute error (main PPM value)
        error_match = re.search(
            r'average\s+absolute\s+error:\s+([-\d.]+)\s+ppm',
            output, re.IGNORECASE
        )
        if error_match:
            data['average_absolute_error'] = float(error_match.group(1))

        # Look for standard deviation
        std_match = re.search(
            r'standard\s+deviation:\s+([\d.]+)',
            output, re.IGNORECASE
        )
        if std_match:
            data['standard_deviation'] = float(std_match.group(1))

        # Look for individual measurements
        measurements = []
        for line in output.split('\n'):
            measure_match = re.search(r'cal:\s+([-\d.]+)ppm', line)
            if measure_match:
                measurements.append(float(measure_match.group(1)))

        if measurements:
            data['measurements'] = measurements
            data['measurement_count'] = len(measurements)
            data['min_error'] = min(measurements)
            data['max_error'] = max(measurements)

        # Calculate confidence metrics
        if 'standard_deviation' in data and 'average_absolute_error' in data:
            data['confidence'] = self._calculate_confidence(
                data['average_absolute_error'],
                data['standard_deviation']
            )

        return data

    def _calculate_confidence(self, avg_error: float, std_dev: float) -> str:
        """Calculate confidence level of calibration"""
        if std_dev < 0.5:
            return "High"
        elif std_dev < 1.0:
            return "Medium"
        else:
            return "Low"

    def apply_ppm_correction(self, target_frequency: float, ppm_offset: Optional[float] = None) -> float:
        """Apply PPM correction to a target frequency"""
        if ppm_offset is None:
            ppm_offset = self.current_ppm

        # PPM correction formula: corrected_freq = freq * (1 + ppm/1000000)
        corrected_frequency = target_frequency * (1 + ppm_offset / 1000000)

        return corrected_frequency

    def get_calibration_summary(self) -> Dict:
        """Get summary of all calibrations performed"""
        if not self.calibration_history:
            return {'status': 'No calibrations performed'}

        latest = self.calibration_history[-1]
        all_errors = []

        for cal in self.calibration_history:
            if 'average_absolute_error' in cal:
                all_errors.append(cal['average_absolute_error'])

        summary = {
            'total_calibrations': len(self.calibration_history),
            'latest_ppm': latest.get('average_absolute_error', 'Unknown'),
            'latest_confidence': latest.get('confidence', 'Unknown'),
            'latest_channel': latest.get('channel', 'Unknown'),
            'latest_band': latest.get('band', 'Unknown'),
            'calibration_stability': 'Good' if len(set(all_errors)) <= 2 else 'Variable'
        }

        if all_errors:
            summary.update({
                'average_ppm_error': np.mean(all_errors),
                'ppm_std_deviation': np.std(all_errors),
                'min_ppm_error': min(all_errors),
                'max_ppm_error': max(all_errors)
            })

        return summary

    def test_frequency_accuracy(self, test_frequencies: List[float]) -> List[Dict]:
        """Test frequency accuracy with current PPM calibration"""
        results = []

        for freq in test_frequencies:
            corrected_freq = self.apply_ppm_correction(freq)
            error_hz = abs(corrected_freq - freq)
            error_ppm = (error_hz / freq) * 1000000

            results.append({
                'original_frequency': freq,
                'corrected_frequency': corrected_freq,
                'error_hz': error_hz,
                'error_ppm': error_ppm,
                'improvement': 'Yes' if error_ppm < abs(self.current_ppm) else 'No'
            })

        return results

    def save_calibration_data(self, filename: str) -> bool:
        """Save calibration history to JSON file"""
        try:
            data = {
                'device_index': self.device_index,
                'current_ppm': self.current_ppm,
                'calibration_history': self.calibration_history,
                'summary': self.get_calibration_summary(),
                'export_time': datetime.now().isoformat()
            }

            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)

            return True

        except Exception as e:
            print(f"Failed to save calibration data: {e}")
            return False

    def load_calibration_data(self, filename: str) -> bool:
        """Load calibration history from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            self.device_index = data.get('device_index', 0)
            self.current_ppm = data.get('current_ppm', 0)
            self.calibration_history = data.get('calibration_history', [])

            return True

        except Exception as e:
            print(f"Failed to load calibration data: {e}")
            return False

def main():
    """Main function for standalone PPM calibration"""
    print("RTL-SDR PPM Calibration Tool")
    print("=" * 50)

    calibrator = PPMCalibrator()

    # Step 1: Scan for GSM channels
    print("\n1. Scanning for GSM channels...")
    channels = calibrator.scan_gsm_channels('GSM900')

    if not channels:
        print("No GSM channels found. Try:")
        print("  - Check antenna connection")
        print("  - Try GSM1800 band: kal -s GSM1800")
        print("  - Increase gain: kal -s GSM900 -g 45")
        return

    print(f"Found {len(channels)} GSM channels:")
    for i, ch in enumerate(channels[:5]):  # Show top 5
        print(f"  {i+1}. Channel {ch['channel']}: {ch['power']:.1f} dB")

    # Step 2: Calibrate using strongest channel
    strongest_channel = channels[0]['channel']
    print(f"\n2. Calibrating using strongest channel {strongest_channel}...")

    calibration = calibrator.calibrate_ppm(strongest_channel)

    if calibration:
        print(f"Calibration successful!")
        print(f"  PPM Error: {calibration['average_absolute_error']:.2f} ppm")
        print(f"  Standard Deviation: {calibration.get('standard_deviation', 'N/A')}")
        print(f"  Confidence: {calibration.get('confidence', 'N/A')}")

        # Step 3: Test frequency accuracy
        print("\n3. Testing frequency accuracy...")
        test_freqs = [100e6, 174.928e6, 433.92e6, 868e6]  # Various frequencies
        accuracy_results = calibrator.test_frequency_accuracy(test_freqs)

        for result in accuracy_results:
            freq_mhz = result['original_frequency'] / 1e6
            error_hz = result['error_hz']
            print(f"  {freq_mhz:.3f} MHz: Error = {error_hz:.1f} Hz")

        # Step 4: Save results
        filename = f"ppm_calibration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        if calibrator.save_calibration_data(filename):
            print(f"\nCalibration data saved to: {filename}")

        # Show summary
        summary = calibrator.get_calibration_summary()
        print(f"\nCalibration Summary:")
        print(f"  Latest PPM: {summary['latest_ppm']:.2f}")
        print(f"  Confidence: {summary['latest_confidence']}")
        print(f"  Channel: {summary['latest_channel']} ({summary['latest_band']})")

    else:
        print("Calibration failed. Check:")
        print("  - GSM signal strength")
        print("  - Device connection")
        print("  - kalibrate-rtl installation")

if __name__ == '__main__':
    main()