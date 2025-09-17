#!/usr/bin/env python3
"""
RTL-SDR Device Detection Implementation
Solution for Lab 1 Trap 1.1: Hardware Detection Challenge
"""

import subprocess
import re
import os
import json
from typing import List, Dict, Optional

class RTLSDRDetector:
    """Comprehensive RTL-SDR device detection"""

    def __init__(self):
        self.rtl_device_ids = [
            ('0bda', '2838'),  # RTL2838
            ('0bda', '2832'),  # RTL2832U
            ('0bda', '2834'),  # RTL2834
        ]

    def detect_devices(self) -> List[Dict]:
        """Detect RTL-SDR devices using multiple methods"""
        devices = []

        # Method 1: USB detection
        usb_devices = self._detect_usb_devices()
        devices.extend(usb_devices)

        # Method 2: rtl_test verification
        rtl_devices = self._detect_via_rtl_test()
        devices.extend(rtl_devices)

        # Method 3: Device nodes
        node_devices = self._detect_device_nodes()
        devices.extend(node_devices)

        return self._deduplicate_devices(devices)

    def _detect_usb_devices(self) -> List[Dict]:
        """Detect RTL-SDR devices via USB"""
        devices = []

        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True)

            for line in result.stdout.split('\n'):
                for vendor_id, product_id in self.rtl_device_ids:
                    pattern = f'{vendor_id}:{product_id}'

                    if pattern in line.lower():
                        match = re.search(r'Bus (\d+) Device (\d+): ID ([0-9a-fA-F:]+) (.+)', line)
                        if match:
                            devices.append({
                                'method': 'USB',
                                'bus': int(match.group(1)),
                                'device': int(match.group(2)),
                                'vendor_product': match.group(3),
                                'description': match.group(4),
                                'raw_line': line.strip()
                            })

        except Exception as e:
            print(f"USB detection failed: {e}")

        return devices

    def _detect_via_rtl_test(self) -> List[Dict]:
        """Detect devices using rtl_test"""
        devices = []

        try:
            result = subprocess.run(['rtl_test', '-t'],
                                  capture_output=True, text=True, timeout=10)

            if result.returncode == 0 and "Found" in result.stdout:
                lines = result.stdout.strip().split('\n')

                for line in lines:
                    if 'Found' in line:
                        device_match = re.search(r'Found (\d+) device\(s\)', line)
                        if device_match:
                            count = int(device_match.group(1))
                            devices.append({
                                'method': 'rtl_test',
                                'device_count': count,
                                'status': 'detected',
                                'raw_output': result.stdout
                            })

                    elif re.search(r'Device #\d+', line):
                        devices.append({
                            'method': 'rtl_test_device',
                            'device_info': line.strip(),
                            'status': 'enumerated'
                        })

        except subprocess.TimeoutExpired:
            devices.append({
                'method': 'rtl_test',
                'status': 'timeout',
                'error': 'rtl_test timed out - device may be busy'
            })
        except FileNotFoundError:
            devices.append({
                'method': 'rtl_test',
                'status': 'not_found',
                'error': 'rtl_test not installed'
            })
        except Exception as e:
            devices.append({
                'method': 'rtl_test',
                'status': 'error',
                'error': str(e)
            })

        return devices

    def _detect_device_nodes(self) -> List[Dict]:
        """Detect RTL-SDR device nodes"""
        devices = []

        # Check for swradio devices
        swradio_pattern = '/dev/swradio*'
        try:
            import glob
            swradio_devices = glob.glob(swradio_pattern)

            for device_path in swradio_devices:
                stat_info = os.stat(device_path)
                devices.append({
                    'method': 'device_node',
                    'path': device_path,
                    'major': os.major(stat_info.st_rdev),
                    'minor': os.minor(stat_info.st_rdev),
                    'permissions': oct(stat_info.st_mode)[-3:]
                })

        except Exception as e:
            print(f"Device node detection failed: {e}")

        return devices

    def _deduplicate_devices(self, devices: List[Dict]) -> List[Dict]:
        """Remove duplicate device entries"""
        # Simple deduplication based on device characteristics
        seen = set()
        unique_devices = []

        for device in devices:
            # Create a signature for each device
            if device['method'] == 'USB':
                signature = f"usb_{device.get('bus')}_{device.get('device')}"
            elif device['method'] == 'rtl_test':
                signature = f"rtl_test_{device.get('device_count', 0)}"
            else:
                signature = f"{device['method']}_{hash(str(device))}"

            if signature not in seen:
                seen.add(signature)
                unique_devices.append(device)

        return unique_devices

    def get_device_summary(self) -> Dict:
        """Get a summary of detected devices"""
        devices = self.detect_devices()

        summary = {
            'total_detected': len(devices),
            'detection_methods': list(set(d['method'] for d in devices)),
            'usb_devices': [d for d in devices if d['method'] == 'USB'],
            'rtl_test_result': [d for d in devices if 'rtl_test' in d['method']],
            'device_nodes': [d for d in devices if d['method'] == 'device_node'],
            'errors': [d for d in devices if d.get('status') == 'error']
        }

        return summary

def main():
    """Main function for standalone testing"""
    detector = RTLSDRDetector()

    print("RTL-SDR Device Detection")
    print("=" * 50)

    # Detect devices
    devices = detector.detect_devices()

    if not devices:
        print("No RTL-SDR devices detected")
        return

    # Display results
    for i, device in enumerate(devices, 1):
        print(f"\nDevice {i}:")
        print(f"  Method: {device['method']}")

        if device['method'] == 'USB':
            print(f"  Bus: {device['bus']}, Device: {device['device']}")
            print(f"  ID: {device['vendor_product']}")
            print(f"  Description: {device['description']}")

        elif 'rtl_test' in device['method']:
            if 'device_count' in device:
                print(f"  Device Count: {device['device_count']}")
            if 'device_info' in device:
                print(f"  Info: {device['device_info']}")
            if 'error' in device:
                print(f"  Error: {device['error']}")

        elif device['method'] == 'device_node':
            print(f"  Path: {device['path']}")
            print(f"  Permissions: {device['permissions']}")

    # Summary
    summary = detector.get_device_summary()
    print(f"\nSummary:")
    print(f"  Total devices: {summary['total_detected']}")
    print(f"  Detection methods: {', '.join(summary['detection_methods'])}")

    if summary['errors']:
        print(f"  Errors encountered: {len(summary['errors'])}")

if __name__ == '__main__':
    main()