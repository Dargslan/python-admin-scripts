"""
dargslan-bandwidth-monitor — Network Bandwidth Monitor

Track network interface statistics and throughput in real-time.
Zero external dependencies — uses only Python standard library.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import os
import time
import json


class BandwidthMonitor:
    """Monitor network bandwidth and interface statistics."""

    def __init__(self):
        pass

    def _read_proc_net_dev(self):
        interfaces = {}
        try:
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()[2:]
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 17:
                        name = parts[0].rstrip(':')
                        interfaces[name] = {
                            'rx_bytes': int(parts[1]),
                            'rx_packets': int(parts[2]),
                            'rx_errors': int(parts[3]),
                            'rx_dropped': int(parts[4]),
                            'tx_bytes': int(parts[9]),
                            'tx_packets': int(parts[10]),
                            'tx_errors': int(parts[11]),
                            'tx_dropped': int(parts[12]),
                        }
        except (FileNotFoundError, PermissionError):
            pass
        return interfaces

    @staticmethod
    def _format_bytes(b):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if b < 1024: return f"{b:.2f} {unit}"
            b /= 1024
        return f"{b:.2f} PB"

    @staticmethod
    def _format_rate(bps):
        for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s']:
            if bps < 1024: return f"{bps:.2f} {unit}"
            bps /= 1024
        return f"{bps:.2f} TB/s"

    def get_stats(self):
        """Get current interface statistics."""
        interfaces = self._read_proc_net_dev()
        result = []
        for name, stats in interfaces.items():
            if name == 'lo': continue
            result.append({
                'interface': name,
                'rx_bytes': stats['rx_bytes'],
                'tx_bytes': stats['tx_bytes'],
                'rx_human': self._format_bytes(stats['rx_bytes']),
                'tx_human': self._format_bytes(stats['tx_bytes']),
                'rx_packets': stats['rx_packets'],
                'tx_packets': stats['tx_packets'],
                'rx_errors': stats['rx_errors'],
                'tx_errors': stats['tx_errors'],
                'rx_dropped': stats['rx_dropped'],
                'tx_dropped': stats['tx_dropped'],
            })
        return result

    def measure_throughput(self, interface=None, duration=2):
        """Measure throughput over a duration."""
        before = self._read_proc_net_dev()
        time.sleep(duration)
        after = self._read_proc_net_dev()

        results = []
        for name in after:
            if name == 'lo' or (interface and name != interface): continue
            if name not in before: continue
            rx_rate = (after[name]['rx_bytes'] - before[name]['rx_bytes']) / duration
            tx_rate = (after[name]['tx_bytes'] - before[name]['tx_bytes']) / duration
            results.append({
                'interface': name,
                'rx_rate': rx_rate,
                'tx_rate': tx_rate,
                'rx_rate_human': self._format_rate(rx_rate),
                'tx_rate_human': self._format_rate(tx_rate),
                'duration': duration,
            })
        return results

    def get_total_traffic(self):
        """Get total traffic across all interfaces."""
        stats = self.get_stats()
        total_rx = sum(s['rx_bytes'] for s in stats)
        total_tx = sum(s['tx_bytes'] for s in stats)
        return {
            'total_rx': total_rx,
            'total_tx': total_tx,
            'total': total_rx + total_tx,
            'total_rx_human': self._format_bytes(total_rx),
            'total_tx_human': self._format_bytes(total_tx),
            'total_human': self._format_bytes(total_rx + total_tx),
        }

    def check_errors(self):
        """Check for interface errors and drops."""
        issues = []
        for s in self.get_stats():
            if s['rx_errors'] > 0:
                issues.append({'interface': s['interface'], 'type': 'rx_errors', 'count': s['rx_errors']})
            if s['tx_errors'] > 0:
                issues.append({'interface': s['interface'], 'type': 'tx_errors', 'count': s['tx_errors']})
            if s['rx_dropped'] > 100:
                issues.append({'interface': s['interface'], 'type': 'rx_dropped', 'count': s['rx_dropped']})
            if s['tx_dropped'] > 100:
                issues.append({'interface': s['interface'], 'type': 'tx_dropped', 'count': s['tx_dropped']})
        return issues

    def print_report(self):
        """Print formatted bandwidth report."""
        stats = self.get_stats()
        total = self.get_total_traffic()
        errors = self.check_errors()

        print(f"\n{'='*60}")
        print(f"  Network Bandwidth Report")
        print(f"{'='*60}")

        for s in stats:
            print(f"\n  {s['interface']}:")
            print(f"    RX: {s['rx_human']} ({s['rx_packets']} packets)")
            print(f"    TX: {s['tx_human']} ({s['tx_packets']} packets)")
            if s['rx_errors'] or s['tx_errors']:
                print(f"    Errors: RX={s['rx_errors']}, TX={s['tx_errors']}")
            if s['rx_dropped'] or s['tx_dropped']:
                print(f"    Dropped: RX={s['rx_dropped']}, TX={s['tx_dropped']}")

        print(f"\n  Total: {total['total_human']} (RX: {total['total_rx_human']}, TX: {total['total_tx_human']})")

        if errors:
            print(f"\n  Issues ({len(errors)}):")
            for e in errors:
                print(f"    [WARNING] {e['interface']}: {e['type']} = {e['count']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["BandwidthMonitor"]
