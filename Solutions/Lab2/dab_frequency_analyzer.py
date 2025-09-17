#!/usr/bin/env python3
"""
DAB+ Frequency Planning and Analysis
Solution for Lab 2 Trap 2.1: DAB+ Frequency Planning
"""

import json
import subprocess
import csv
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class DABFrequencyAnalyzer:
    """DAB+ frequency planning and analysis for Thailand"""

    def __init__(self):
        self.thailand_dab_frequencies = {
            'Bangkok': {
                'Block 5A': 174.928,  # MHz
                'Block 5B': 176.640,
                'Block 5C': 178.352,
                'Block 5D': 180.064
            },
            'Chiang Mai': {
                'Block 7A': 188.928,
                'Block 7B': 190.640,
                'Block 7C': 192.352
            },
            'Phuket': {
                'Block 9A': 202.928,
                'Block 9B': 204.640
            },
            'Khon Kaen': {
                'Block 6A': 181.936,
                'Block 6B': 183.648,
                'Block 6C': 185.360
            }
        }

        # DAB+ Band III frequency blocks (174-230 MHz)
        self.band_iii_blocks = self._generate_band_iii_blocks()

    def _generate_band_iii_blocks(self) -> Dict[str, float]:
        """Generate all possible DAB+ Band III frequency blocks"""
        blocks = {}

        # Block 5A-5D (174-180 MHz)
        base_5a = 174.928
        for i, letter in enumerate(['A', 'B', 'C', 'D']):
            blocks[f'5{letter}'] = base_5a + (i * 1.712)

        # Block 6A-6D (181-187 MHz)
        base_6a = 181.936
        for i, letter in enumerate(['A', 'B', 'C', 'D']):
            blocks[f'6{letter}'] = base_6a + (i * 1.712)

        # Block 7A-7D (188-194 MHz)
        base_7a = 188.944
        for i, letter in enumerate(['A', 'B', 'C', 'D']):
            blocks[f'7{letter}'] = base_7a + (i * 1.712)

        # Continue for blocks 8-12
        base_frequencies = [195.952, 202.928, 209.936, 216.928, 223.936]
        block_numbers = [8, 9, 10, 11, 12]

        for block_num, base_freq in zip(block_numbers, base_frequencies):
            for i, letter in enumerate(['A', 'B', 'C', 'D']):
                blocks[f'{block_num}{letter}'] = base_freq + (i * 1.712)

        return blocks

    def get_frequency_info(self, block_name: str) -> Optional[Dict]:
        """Get detailed frequency information for a DAB+ block"""
        if block_name in self.band_iii_blocks:
            freq_mhz = self.band_iii_blocks[block_name]
        else:
            # Search in assigned frequencies
            for region, blocks in self.thailand_dab_frequencies.items():
                if block_name in blocks:
                    freq_mhz = blocks[block_name]
                    break
            else:
                return None

        return {
            'block': block_name,
            'frequency_mhz': freq_mhz,
            'frequency_hz': freq_mhz * 1e6,
            'bandwidth_khz': 1536,  # DAB+ bandwidth
            'center_freq': freq_mhz * 1e6,
            'lower_bound': (freq_mhz - 0.768) * 1e6,
            'upper_bound': (freq_mhz + 0.768) * 1e6,
            'assigned_regions': self._find_assigned_regions(block_name)
        }

    def _find_assigned_regions(self, block_name: str) -> List[str]:
        """Find regions where this block is assigned"""
        regions = []
        for region, blocks in self.thailand_dab_frequencies.items():
            if block_name in blocks:
                regions.append(region)
        return regions

    def scan_band_iii_spectrum(self, output_file: str = 'dab_spectrum.csv') -> Dict:
        """Scan entire Band III spectrum using RTL-SDR"""
        try:
            print("Scanning DAB+ Band III spectrum (174-230 MHz)...")

            # Run rtl_power scan
            cmd = [
                'rtl_power',
                '-f', '174M:230M:1M',  # 174-230 MHz, 1 MHz steps
                '-i', '10',            # 10 second integration
                '-1',                  # Single scan
                output_file
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                return {'success': False, 'error': result.stderr}

            # Parse scan results
            scan_data = self._parse_spectrum_scan(output_file)

            return {
                'success': True,
                'scan_file': output_file,
                'data': scan_data,
                'peak_frequencies': self._find_spectrum_peaks(scan_data)
            }

        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Spectrum scan timed out'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _parse_spectrum_scan(self, csv_file: str) -> List[Dict]:
        """Parse rtl_power CSV output"""
        data = []

        try:
            with open(csv_file, 'r') as f:
                reader = csv.reader(f)

                for row in reader:
                    if len(row) >= 7:  # Valid rtl_power output
                        try:
                            entry = {
                                'timestamp': row[0] + ' ' + row[1],
                                'frequency_hz': float(row[2]),
                                'frequency_mhz': float(row[2]) / 1e6,
                                'power_db': float(row[6]),
                                'samples': int(row[5]) if row[5].isdigit() else 0
                            }
                            data.append(entry)
                        except (ValueError, IndexError):
                            continue  # Skip malformed rows

        except Exception as e:
            print(f"Error parsing spectrum data: {e}")

        return data

    def _find_spectrum_peaks(self, scan_data: List[Dict], threshold_db: float = -50) -> List[Dict]:
        """Find spectrum peaks that might indicate DAB+ signals"""
        if not scan_data:
            return []

        peaks = []
        frequencies = [d['frequency_mhz'] for d in scan_data]
        powers = [d['power_db'] for d in scan_data]

        # Find local maxima above threshold
        for i in range(1, len(powers) - 1):
            if (powers[i] > threshold_db and
                powers[i] > powers[i-1] and
                powers[i] > powers[i+1]):

                # Check if this frequency matches a DAB+ block
                closest_block = self._find_closest_dab_block(frequencies[i])

                peak_info = {
                    'frequency_mhz': frequencies[i],
                    'power_db': powers[i],
                    'potential_block': closest_block['block'] if closest_block else None,
                    'frequency_error_khz': closest_block['error_khz'] if closest_block else None
                }
                peaks.append(peak_info)

        return sorted(peaks, key=lambda x: x['power_db'], reverse=True)

    def _find_closest_dab_block(self, freq_mhz: float, tolerance_khz: float = 500) -> Optional[Dict]:
        """Find the closest DAB+ block to given frequency"""
        min_error = float('inf')
        closest_block = None

        for block, block_freq in self.band_iii_blocks.items():
            error_khz = abs((freq_mhz - block_freq) * 1000)

            if error_khz < min_error and error_khz <= tolerance_khz:
                min_error = error_khz
                closest_block = {
                    'block': block,
                    'frequency_mhz': block_freq,
                    'error_khz': error_khz
                }

        return closest_block

    def plot_spectrum(self, scan_data: List[Dict], output_file: str = 'dab_spectrum.png'):
        """Create spectrum plot with DAB+ block annotations"""
        if not scan_data:
            print("No scan data to plot")
            return

        frequencies = [d['frequency_mhz'] for d in scan_data]
        powers = [d['power_db'] for d in scan_data]

        plt.figure(figsize=(14, 8))
        plt.plot(frequencies, powers, 'b-', linewidth=0.8, alpha=0.7)

        # Mark assigned DAB+ frequencies
        for region, blocks in self.thailand_dab_frequencies.items():
            for block_name, freq in blocks.items():
                plt.axvline(x=freq, color='red', linestyle='--', alpha=0.6)
                plt.text(freq, max(powers) - 5, f'{block_name}\n{region}',
                        rotation=90, ha='center', va='top', fontsize=8)

        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Power (dB)')
        plt.title('DAB+ Band III Spectrum Scan (Thailand)')
        plt.grid(True, alpha=0.3)
        plt.legend(['Spectrum', 'Assigned DAB+ Blocks'])

        # Set frequency range to Band III
        plt.xlim(174, 230)

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.show()

        print(f"Spectrum plot saved as: {output_file}")

    def analyze_frequency_allocation(self) -> Dict:
        """Analyze current DAB+ frequency allocation in Thailand"""
        analysis = {
            'total_allocated_blocks': 0,
            'regions': {},
            'available_blocks': [],
            'frequency_utilization': {}
        }

        # Count allocated blocks
        all_allocated = set()
        for region, blocks in self.thailand_dab_frequencies.items():
            analysis['regions'][region] = {
                'block_count': len(blocks),
                'frequency_range': {
                    'min_mhz': min(blocks.values()),
                    'max_mhz': max(blocks.values())
                },
                'blocks': list(blocks.keys())
            }
            all_allocated.update(blocks.keys())

        analysis['total_allocated_blocks'] = len(all_allocated)

        # Find available blocks
        all_possible = set(self.band_iii_blocks.keys())
        available = all_possible - all_allocated
        analysis['available_blocks'] = sorted(list(available))

        # Frequency utilization
        total_possible = len(self.band_iii_blocks)
        utilization_percent = (len(all_allocated) / total_possible) * 100

        analysis['frequency_utilization'] = {
            'allocated_blocks': len(all_allocated),
            'available_blocks': len(available),
            'total_possible_blocks': total_possible,
            'utilization_percent': utilization_percent
        }

        return analysis

    def suggest_new_allocations(self, region: str, num_blocks: int = 2) -> List[Dict]:
        """Suggest new DAB+ block allocations for a region"""
        # Get currently allocated blocks
        all_allocated = set()
        for blocks in self.thailand_dab_frequencies.values():
            all_allocated.update(blocks.keys())

        # Find available blocks
        available_blocks = []
        for block, freq in self.band_iii_blocks.items():
            if block not in all_allocated:
                available_blocks.append({'block': block, 'frequency_mhz': freq})

        # Sort by frequency (lower frequencies generally better propagation)
        available_blocks.sort(key=lambda x: x['frequency_mhz'])

        # Return suggested allocations
        suggestions = available_blocks[:num_blocks]

        for suggestion in suggestions:
            suggestion.update({
                'region': region,
                'bandwidth_khz': 1536,
                'propagation_rating': self._rate_propagation(suggestion['frequency_mhz'])
            })

        return suggestions

    def _rate_propagation(self, freq_mhz: float) -> str:
        """Rate propagation characteristics based on frequency"""
        if freq_mhz < 180:
            return "Excellent"
        elif freq_mhz < 200:
            return "Good"
        elif freq_mhz < 220:
            return "Fair"
        else:
            return "Limited"

    def export_frequency_plan(self, filename: str) -> bool:
        """Export complete frequency plan to JSON"""
        try:
            plan = {
                'thailand_dab_allocations': self.thailand_dab_frequencies,
                'band_iii_blocks': self.band_iii_blocks,
                'analysis': self.analyze_frequency_allocation(),
                'export_timestamp': datetime.now().isoformat(),
                'frequency_standard': 'ETSI EN 300 401 (DAB+)',
                'band_name': 'Band III (174-230 MHz)'
            }

            with open(filename, 'w') as f:
                json.dump(plan, f, indent=2)

            return True

        except Exception as e:
            print(f"Export failed: {e}")
            return False

def main():
    """Main function for standalone frequency analysis"""
    analyzer = DABFrequencyAnalyzer()

    print("DAB+ Frequency Planning Analysis for Thailand")
    print("=" * 50)

    # Show current allocations
    print("\n1. Current DAB+ Allocations:")
    for region, blocks in analyzer.thailand_dab_frequencies.items():
        print(f"\n   {region}:")
        for block, freq in blocks.items():
            print(f"     {block}: {freq:.3f} MHz")

    # Analysis
    analysis = analyzer.analyze_frequency_allocation()
    print(f"\n2. Frequency Utilization:")
    print(f"   Allocated blocks: {analysis['frequency_utilization']['allocated_blocks']}")
    print(f"   Available blocks: {analysis['frequency_utilization']['available_blocks']}")
    print(f"   Utilization: {analysis['frequency_utilization']['utilization_percent']:.1f}%")

    # Show some available blocks
    available = analysis['available_blocks'][:10]
    print(f"\n3. Some Available Blocks:")
    for block in available:
        freq = analyzer.band_iii_blocks[block]
        print(f"   {block}: {freq:.3f} MHz")

    # Suggest new allocation
    suggestions = analyzer.suggest_new_allocations("Pattaya", 3)
    print(f"\n4. Suggested allocation for Pattaya:")
    for suggestion in suggestions:
        print(f"   {suggestion['block']}: {suggestion['frequency_mhz']:.3f} MHz "
              f"(Propagation: {suggestion['propagation_rating']})")

    # Export frequency plan
    export_file = f"thailand_dab_plan_{datetime.now().strftime('%Y%m%d')}.json"
    if analyzer.export_frequency_plan(export_file):
        print(f"\n5. Frequency plan exported to: {export_file}")

    # Optional: Run spectrum scan if rtl_power is available
    try:
        print("\n6. Running spectrum scan...")
        scan_result = analyzer.scan_band_iii_spectrum()
        if scan_result['success']:
            print(f"   Scan completed. Found {len(scan_result['peak_frequencies'])} potential signals")

            # Show top peaks
            for i, peak in enumerate(scan_result['peak_frequencies'][:5]):
                print(f"   Peak {i+1}: {peak['frequency_mhz']:.1f} MHz, "
                      f"{peak['power_db']:.1f} dB")
                if peak['potential_block']:
                    print(f"     -> Possible {peak['potential_block']} "
                          f"(±{peak['frequency_error_khz']:.0f} kHz)")

            # Create plot
            analyzer.plot_spectrum(scan_result['data'])
        else:
            print(f"   Scan failed: {scan_result['error']}")

    except Exception as e:
        print(f"   Spectrum scan not available: {e}")

if __name__ == '__main__':
    main()