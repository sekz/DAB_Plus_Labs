#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 3 Phase 3: ETI Analysis and Parser - SOLUTION
เป้าหมาย: วิเคราะห์ ETI stream และแยก services

Dependencies:
pip install bitstring json struct
"""

import struct
import json
import os
import sys
from datetime import datetime
import bitstring

class ETIFrameParser:
    def __init__(self):
        self.frame_count = 0
        self.services = {}
        self.subchannels = {}
        self.ensemble_info = {}
        self.fic_data = bytearray()

        # ETI frame constants
        self.ETI_FRAME_SIZE = 6144  # bytes
        self.ETI_NI_FRAME_SIZE = 6144
        self.FC_LENGTH = 4  # Frame Characterization
        self.NST_MAX = 64   # Maximum number of subchannels

    def parse_eti_file(self, filename):
        """
        วิเคราะห์ไฟล์ ETI และแยกข้อมูล services
        """
        if not os.path.exists(filename):
            print(f"ETI file not found: {filename}")
            return False

        print(f"Parsing ETI file: {filename}")
        file_size = os.path.getsize(filename)
        expected_frames = file_size // self.ETI_FRAME_SIZE

        print(f"File size: {file_size:,} bytes")
        print(f"Expected frames: {expected_frames:,}")

        try:
            with open(filename, 'rb') as f:
                frame_number = 0

                while True:
                    # อ่าน ETI frame
                    frame_data = f.read(self.ETI_FRAME_SIZE)

                    if len(frame_data) < self.ETI_FRAME_SIZE:
                        break

                    # วิเคราะห์ frame
                    self.parse_eti_frame(frame_data, frame_number)
                    frame_number += 1

                    # แสดงความคืบหน้าทุก 100 frames
                    if frame_number % 100 == 0:
                        print(f"Processed {frame_number} frames...")

                    # จำกัดการวิเคราะห์เพื่อประหยัดเวลา (สำหรับทดสอบ)
                    if frame_number >= 1000:
                        print("Limiting analysis to first 1000 frames for demo")
                        break

                print(f"Completed parsing {frame_number} frames")

                # วิเคราะห์ FIC data ที่เก็บรวบรวม
                self.analyze_fic_data()

                return True

        except Exception as e:
            print(f"Error parsing ETI file: {e}")
            return False

    def parse_eti_frame(self, frame_data, frame_number):
        """
        วิเคราะห์ ETI frame แต่ละ frame
        """
        try:
            # ETI-NI frame structure:
            # LIDATA field (6144 bytes total)
            # - Frame Characterization (FC) - 4 bytes
            # - Number of Streams (NST) - 4 bytes
            # - Fast Information Channel (FIC) - 96 bytes
            # - Main Service Channel (MSC) - remaining bytes

            offset = 0

            # Frame Characterization (FC)
            fc_bytes = frame_data[offset:offset+4]
            fc_info = self.parse_frame_characterization(fc_bytes)
            offset += 4

            # อ่าน NST (Number of Streams)
            nst_bytes = frame_data[offset:offset+4]
            nst = struct.unpack('>I', nst_bytes)[0]
            offset += 4

            # Fast Information Channel (FIC) - 96 bytes
            fic_bytes = frame_data[offset:offset+96]
            self.fic_data.extend(fic_bytes)
            offset += 96

            # Main Service Channel (MSC) - ส่วนที่เหลือ
            msc_bytes = frame_data[offset:]

            # เก็บข้อมูลสำหรับการวิเคราะห์
            if frame_number == 0:
                self.ensemble_info.update(fc_info)
                self.ensemble_info['nst'] = nst

            # นับ frame
            self.frame_count += 1

        except Exception as e:
            print(f"Error parsing frame {frame_number}: {e}")

    def parse_frame_characterization(self, fc_bytes):
        """
        วิเคราะห์ Frame Characterization (FC)
        """
        try:
            # แปลง FC bytes เป็น bit string
            fc_bits = bitstring.BitArray(bytes=fc_bytes)

            # FC structure (simplified)
            # Bits 0-7: Frame Characterization Field (FCT)
            # Bits 8-15: Network/Service Identifier
            # Bits 16-23: Mode Information
            # Bits 24-31: Additional flags

            fct = fc_bits[0:8].uint
            nsi = fc_bits[8:16].uint
            mode = fc_bits[16:24].uint
            flags = fc_bits[24:32].uint

            return {
                'frame_characterization': fct,
                'network_service_id': nsi,
                'mode': mode,
                'flags': flags
            }

        except Exception as e:
            print(f"Error parsing FC: {e}")
            return {}

    def analyze_fic_data(self):
        """
        วิเคราะห์ FIC (Fast Information Channel) data
        เพื่อหา service และ subchannel information
        """
        print("\nAnalyzing FIC data...")

        try:
            # FIC ประกอบด้วย FIBs (Fast Information Blocks)
            # แต่ละ FIB = 32 bytes, มี 3 FIBs ต่อ frame
            # รวม 96 bytes FIC ต่อ frame

            fib_size = 32
            num_fibs = len(self.fic_data) // fib_size

            print(f"Total FIC data: {len(self.fic_data)} bytes")
            print(f"Number of FIBs: {num_fibs}")

            for i in range(min(num_fibs, 100)):  # จำกัดการวิเคราะห์
                fib_start = i * fib_size
                fib_data = self.fic_data[fib_start:fib_start + fib_size]

                # วิเคราะห์ FIB
                self.parse_fib(fib_data, i)

            print(f"Found {len(self.services)} services")
            print(f"Found {len(self.subchannels)} subchannels")

        except Exception as e:
            print(f"Error analyzing FIC data: {e}")

    def parse_fib(self, fib_data, fib_number):
        """
        วิเคราะห์ FIB (Fast Information Block)
        """
        try:
            # FIB structure:
            # - FIGs (Fast Information Groups)
            # - CRC (2 bytes at end)

            # ตรวจสอบ CRC ก่อน (optional)
            crc_bytes = fib_data[-2:]
            data_bytes = fib_data[:-2]

            # วิเคราะห์ FIGs
            offset = 0
            while offset < len(data_bytes) - 2:
                if data_bytes[offset] == 0xFF:  # End marker
                    break

                # อ่าน FIG header
                if offset + 1 >= len(data_bytes):
                    break

                fig_header = data_bytes[offset]
                fig_length = data_bytes[offset + 1] if offset + 1 < len(data_bytes) else 0

                if fig_length == 0 or offset + 2 + fig_length > len(data_bytes):
                    break

                fig_data = data_bytes[offset + 2:offset + 2 + fig_length]

                # วิเคราะห์ FIG ตาม type
                self.parse_fig(fig_header, fig_data)

                offset += 2 + fig_length

        except Exception as e:
            print(f"Error parsing FIB {fib_number}: {e}")

    def parse_fig(self, fig_header, fig_data):
        """
        วิเคราะห์ FIG (Fast Information Group)
        """
        try:
            # FIG Type อยู่ใน bits 5-7 ของ header
            fig_type = (fig_header >> 5) & 0x07

            if fig_type == 0:
                # FIG 0: MCI (Multiplex Configuration Information)
                self.parse_fig0(fig_data)
            elif fig_type == 1:
                # FIG 1: Labels
                self.parse_fig1(fig_data)
            # อื่นๆ สามารถเพิ่มได้ตามต้องการ

        except Exception as e:
            print(f"Error parsing FIG type {fig_type}: {e}")

    def parse_fig0(self, fig_data):
        """
        วิเคราะห์ FIG 0 (Multiplex Configuration Information)
        """
        try:
            if len(fig_data) < 1:
                return

            # FIG 0 extension อยู่ใน bits 0-4
            extension = fig_data[0] & 0x1F

            if extension == 0:
                # FIG 0/0: Ensemble information
                self.parse_fig0_0(fig_data[1:])
            elif extension == 1:
                # FIG 0/1: Subchannel organization
                self.parse_fig0_1(fig_data[1:])
            elif extension == 2:
                # FIG 0/2: Service organization
                self.parse_fig0_2(fig_data[1:])

        except Exception as e:
            print(f"Error parsing FIG 0: {e}")

    def parse_fig0_0(self, data):
        """FIG 0/0: Ensemble information"""
        try:
            if len(data) >= 4:
                ensemble_id = struct.unpack('>H', data[0:2])[0]
                self.ensemble_info['ensemble_id'] = ensemble_id

        except Exception as e:
            print(f"Error parsing FIG 0/0: {e}")

    def parse_fig0_1(self, data):
        """FIG 0/1: Subchannel organization"""
        try:
            offset = 0
            while offset + 3 <= len(data):
                subch_id = (data[offset] >> 2) & 0x3F
                start_addr = ((data[offset] & 0x03) << 8) | data[offset + 1]

                if offset + 2 < len(data):
                    table_switch = (data[offset + 2] >> 6) & 0x01
                    table_index = data[offset + 2] & 0x3F

                    self.subchannels[subch_id] = {
                        'subchannel_id': subch_id,
                        'start_address': start_addr,
                        'table_switch': table_switch,
                        'table_index': table_index
                    }

                offset += 3

        except Exception as e:
            print(f"Error parsing FIG 0/1: {e}")

    def parse_fig0_2(self, data):
        """FIG 0/2: Service organization"""
        try:
            offset = 0
            while offset + 3 <= len(data):
                service_id = struct.unpack('>H', data[offset:offset+2])[0]

                if offset + 2 < len(data):
                    local_flag = (data[offset + 2] >> 7) & 0x01
                    caid = (data[offset + 2] >> 4) & 0x07
                    num_components = data[offset + 2] & 0x0F

                    service_info = {
                        'service_id': service_id,
                        'local_flag': local_flag,
                        'caid': caid,
                        'num_components': num_components,
                        'components': []
                    }

                    offset += 3

                    # อ่าน component information
                    for i in range(num_components):
                        if offset + 2 <= len(data):
                            component_info = {
                                'tmid': (data[offset] >> 6) & 0x03,
                                'component_type': data[offset] & 0x3F,
                                'subchannel_id': (data[offset + 1] >> 2) & 0x3F
                            }
                            service_info['components'].append(component_info)
                            offset += 2

                    self.services[service_id] = service_info
                else:
                    break

        except Exception as e:
            print(f"Error parsing FIG 0/2: {e}")

    def parse_fig1(self, fig_data):
        """
        วิเคราะห์ FIG 1 (Labels)
        """
        try:
            if len(fig_data) < 1:
                return

            # FIG 1 extension
            extension = fig_data[0] & 0x07

            if extension == 0:
                # FIG 1/0: Ensemble label
                self.parse_ensemble_label(fig_data[1:])
            elif extension == 1:
                # FIG 1/1: Service label
                self.parse_service_label(fig_data[1:])

        except Exception as e:
            print(f"Error parsing FIG 1: {e}")

    def parse_ensemble_label(self, data):
        """Parse ensemble label"""
        try:
            if len(data) >= 18:  # 2 bytes ID + 16 bytes label
                ensemble_id = struct.unpack('>H', data[0:2])[0]
                label = data[2:18].decode('utf-8', errors='ignore').strip()

                if ensemble_id in self.ensemble_info or 'ensemble_id' not in self.ensemble_info:
                    self.ensemble_info['ensemble_label'] = label

        except Exception as e:
            print(f"Error parsing ensemble label: {e}")

    def parse_service_label(self, data):
        """Parse service label"""
        try:
            if len(data) >= 18:  # 2 bytes ID + 16 bytes label
                service_id = struct.unpack('>H', data[0:2])[0]
                label = data[2:18].decode('utf-8', errors='ignore').strip()

                if service_id in self.services:
                    self.services[service_id]['label'] = label

        except Exception as e:
            print(f"Error parsing service label: {e}")

    def export_service_list(self, filename="service_list.json"):
        """
        ส่งออกรายการ services เป็น JSON
        """
        try:
            # สร้างข้อมูลสำหรับ export
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'ensemble_info': self.ensemble_info,
                'frame_count': self.frame_count,
                'services': []
            }

            # จัดรูปแบบข้อมูล services
            for service_id, service_info in self.services.items():
                service_export = {
                    'service_id': service_id,
                    'service_id_hex': f"0x{service_id:04X}",
                    'label': service_info.get('label', f"Service {service_id}"),
                    'local_flag': service_info.get('local_flag', 0),
                    'num_components': service_info.get('num_components', 0),
                    'components': []
                }

                # เพิ่มข้อมูล components
                for comp in service_info.get('components', []):
                    component_export = {
                        'tmid': comp.get('tmid', 0),
                        'component_type': comp.get('component_type', 0),
                        'subchannel_id': comp.get('subchannel_id', 0)
                    }

                    # เพิ่มข้อมูล subchannel หากมี
                    subch_id = comp.get('subchannel_id', 0)
                    if subch_id in self.subchannels:
                        component_export['subchannel_info'] = self.subchannels[subch_id]

                    service_export['components'].append(component_export)

                export_data['services'].append(service_export)

            # บันทึกเป็นไฟล์ JSON
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            print(f"Service list exported to: {filename}")
            return True

        except Exception as e:
            print(f"Error exporting service list: {e}")
            return False

    def export_subchannel_info(self, filename="subchannel_info.json"):
        """
        ส่งออกข้อมูล subchannels เป็น JSON
        """
        try:
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'ensemble_info': self.ensemble_info,
                'subchannels': []
            }

            for subch_id, subch_info in self.subchannels.items():
                subchannel_export = {
                    'subchannel_id': subch_id,
                    'start_address': subch_info.get('start_address', 0),
                    'table_switch': subch_info.get('table_switch', 0),
                    'table_index': subch_info.get('table_index', 0),
                    'services_using': []
                }

                # หา services ที่ใช้ subchannel นี้
                for service_id, service_info in self.services.items():
                    for comp in service_info.get('components', []):
                        if comp.get('subchannel_id') == subch_id:
                            subchannel_export['services_using'].append({
                                'service_id': service_id,
                                'service_label': service_info.get('label', f"Service {service_id}")
                            })

                export_data['subchannels'].append(subchannel_export)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            print(f"Subchannel info exported to: {filename}")
            return True

        except Exception as e:
            print(f"Error exporting subchannel info: {e}")
            return False

    def print_summary(self):
        """แสดงสรุปข้อมูลที่วิเคราะห์ได้"""
        print("\n" + "="*60)
        print("ETI ANALYSIS SUMMARY")
        print("="*60)

        print(f"Frames analyzed: {self.frame_count:,}")
        print(f"Ensemble ID: {self.ensemble_info.get('ensemble_id', 'Unknown')}")
        print(f"Ensemble Label: {self.ensemble_info.get('ensemble_label', 'Unknown')}")

        print(f"\nServices found: {len(self.services)}")
        for service_id, service_info in self.services.items():
            label = service_info.get('label', f"Service {service_id}")
            components = len(service_info.get('components', []))
            print(f"  - {label} (ID: 0x{service_id:04X}, Components: {components})")

        print(f"\nSubchannels found: {len(self.subchannels)}")
        for subch_id, subch_info in self.subchannels.items():
            start_addr = subch_info.get('start_address', 0)
            table_idx = subch_info.get('table_index', 0)
            print(f"  - Subchannel {subch_id} (Start: {start_addr}, Table: {table_idx})")

        print("="*60)

def analyze_eti_from_lab2():
    """
    วิเคราะห์ ETI file ที่สร้างจาก lab3_2.py
    """
    eti_filename = "dab_ensemble.eti"

    if not os.path.exists(eti_filename):
        print(f"ETI file not found: {eti_filename}")
        print("Run lab3_2.py first to generate ETI stream")
        return False

    parser = ETIFrameParser()

    if parser.parse_eti_file(eti_filename):
        parser.print_summary()
        parser.export_service_list()
        parser.export_subchannel_info()
        return True

    return False

def main():
    """ฟังก์ชันหลักสำหรับทดสอบ"""
    print("=== Lab 3 Phase 3: ETI Analysis and Parser ===")

    # ตรวจสอบ arguments
    if len(sys.argv) > 1:
        eti_filename = sys.argv[1]
    else:
        eti_filename = "dab_ensemble.eti"

    try:
        # วิเคราะห์ ETI file
        parser = ETIFrameParser()

        if parser.parse_eti_file(eti_filename):
            # แสดงสรุป
            parser.print_summary()

            # ส่งออกข้อมูล
            parser.export_service_list()
            parser.export_subchannel_info()

            print(f"\nAnalysis completed successfully!")
            print(f"Output files:")
            print(f"  - service_list.json")
            print(f"  - subchannel_info.json")

        else:
            print("ETI analysis failed")

    except KeyboardInterrupt:
        print("\nUser interrupted")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()