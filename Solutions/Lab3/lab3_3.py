#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 3 Phase 3: ETI Analysis (Simplified) - SOLUTION
เป้าหมาย: สร้าง service list จาก eti-cmdline JSON output

This version uses the JSON file created by eti-cmdline (-J option)
rather than parsing the raw ETI frames directly.
"""

import json
import os
import sys
import re
from datetime import datetime

def load_ensemble_json(channel="6C"):
    """
    โหลดข้อมูล ensemble จาก JSON file ที่ eti-cmdline สร้าง
    """
    json_filename = f"ensemble-ch-{channel}.json"

    if not os.path.exists(json_filename):
        print(f"Ensemble JSON file not found: {json_filename}")
        print("Run lab3_2.py first to generate ETI stream with -J option")
        return None

    try:
        with open(json_filename, 'r', encoding='utf-8') as f:
            content = f.read()
            # Fix malformed JSON: "Eid:"4FFF" -> "Eid":"4FFF"
            content = re.sub(r'"Eid:"([^"]*)"', r'"Eid":"\1"', content)
            data = json.loads(content)

        print(f"✓ Loaded ensemble information from {json_filename}")
        return data

    except Exception as e:
        print(f"Error loading ensemble JSON: {e}")
        return None

def create_service_list(ensemble_data):
    """
    สร้าง service list จาก ensemble data
    """
    if not ensemble_data:
        return None

    try:
        channel = ensemble_data.get('channel', 'Unknown')
        ensemble_name = ensemble_data.get('ensemble', 'Unknown')
        ensemble_id = ensemble_data.get('Eid', 'Unknown')
        stations = ensemble_data.get('stations', {})

        print(f"\n=== DAB Ensemble Information ===")
        print(f"Channel: {channel}")
        print(f"Ensemble: {ensemble_name}")
        print(f"Ensemble ID: {ensemble_id}")
        print(f"Stations found: {len(stations)}")

        # สร้าง service list
        service_list = {
            'timestamp': datetime.now().isoformat(),
            'ensemble_info': {
                'channel': channel,
                'ensemble_name': ensemble_name,
                'ensemble_id': ensemble_id
            },
            'frame_count': 0,  # ไม่มีข้อมูลจาก JSON
            'services': []
        }

        # แปลง stations เป็น services
        for station_name, service_id_hex in stations.items():
            # แปลง hex string เป็น integer
            service_id = int(service_id_hex, 16)

            service_info = {
                'service_id': service_id,
                'service_id_hex': service_id_hex,
                'label': station_name,
                'local_flag': 0,  # ไม่มีข้อมูลจาก JSON
                'num_components': 1,  # สมมติว่ามี 1 component
                'components': [
                    {
                        'tmid': 0,
                        'component_type': 0,
                        'subchannel_id': 0
                    }
                ]
            }

            service_list['services'].append(service_info)
            print(f"  {len(service_list['services']):2d}. {station_name:20s} ({service_id_hex})")

        return service_list

    except Exception as e:
        print(f"Error creating service list: {e}")
        return None

def create_subchannel_info(ensemble_data):
    """
    สร้าง subchannel info (simplified)
    """
    if not ensemble_data:
        return None

    try:
        channel = ensemble_data.get('channel', 'Unknown')
        ensemble_name = ensemble_data.get('ensemble', 'Unknown')
        ensemble_id = ensemble_data.get('Eid', 'Unknown')
        stations = ensemble_data.get('stations', {})

        # สร้าง subchannel info
        subchannel_info = {
            'timestamp': datetime.now().isoformat(),
            'ensemble_info': {
                'channel': channel,
                'ensemble_name': ensemble_name,
                'ensemble_id': ensemble_id
            },
            'subchannels': []
        }

        # สร้าง subchannel สำหรับแต่ละ station (simplified)
        for idx, (station_name, service_id_hex) in enumerate(stations.items()):
            service_id = int(service_id_hex, 16)

            subchannel_export = {
                'subchannel_id': idx,
                'start_address': idx * 100,  # Mock address
                'table_switch': 0,
                'table_index': 0,
                'services_using': [
                    {
                        'service_id': service_id,
                        'service_label': station_name
                    }
                ]
            }

            subchannel_info['subchannels'].append(subchannel_export)

        print(f"\n✓ Created {len(subchannel_info['subchannels'])} subchannel entries")
        return subchannel_info

    except Exception as e:
        print(f"Error creating subchannel info: {e}")
        return None

def save_json(data, filename):
    """
    บันทึกข้อมูลเป็น JSON file
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved: {filename}")
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False

def main():
    """ฟังก์ชันหลักสำหรับทดสอบ"""
    print("=== Lab 3 Phase 3: ETI Analysis (Simplified) ===")
    print("\nThis version uses the JSON file from eti-cmdline")
    print("instead of parsing raw ETI frames\n")

    # ตรวจสอบ arguments
    if len(sys.argv) > 1:
        channel = sys.argv[1]
    else:
        channel = "6C"  # Default DAB+ Thailand channel
        print(f"Using default channel: {channel}")
        print(f"Usage: python3 lab3_3_simple.py [channel]")
        print(f"Example: python3 lab3_3_simple.py 12C\n")

    try:
        # โหลดข้อมูล ensemble จาก JSON
        ensemble_data = load_ensemble_json(channel)

        if not ensemble_data:
            print("\n✗ Failed to load ensemble data")
            print("\nWorkflow:")
            print("  1. Run lab3_2.py to capture DAB signal")
            print("     This creates ensemble-ch-{channel}.json")
            print("  2. Run lab3_3_simple.py to create service_list.json")
            return

        # สร้าง service list
        service_list = create_service_list(ensemble_data)
        if service_list:
            save_json(service_list, "service_list.json")

        # สร้าง subchannel info
        subchannel_info = create_subchannel_info(ensemble_data)
        if subchannel_info:
            save_json(subchannel_info, "subchannel_info.json")

        print("\n" + "="*60)
        print("✓ Analysis completed successfully!")
        print("="*60)
        print(f"\nOutput files:")
        print(f"  - service_list.json")
        print(f"  - subchannel_info.json")
        print(f"\nNext step:")
        print(f"  python3 lab3_4.py  # Play audio from services")

    except KeyboardInterrupt:
        print("\nUser interrupted")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
