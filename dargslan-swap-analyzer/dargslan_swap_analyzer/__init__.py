"""
dargslan-swap-analyzer — Linux Swap Usage Analyzer

Find which processes use swap, measure swap pressure, and get recommendations.
Zero external dependencies — uses only Python standard library.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import os
import json


class SwapAnalyzer:
    """Analyze Linux swap usage and provide recommendations."""

    def __init__(self):
        pass

    @staticmethod
    def _format_kb(kb):
        if kb < 1024: return f"{kb} KB"
        if kb < 1048576: return f"{kb/1024:.1f} MB"
        return f"{kb/1048576:.1f} GB"

    def get_swap_info(self):
        """Get overall swap usage from /proc/meminfo."""
        info = {}
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('SwapTotal:'):
                        info['total_kb'] = int(line.split()[1])
                    elif line.startswith('SwapFree:'):
                        info['free_kb'] = int(line.split()[1])
                    elif line.startswith('SwapCached:'):
                        info['cached_kb'] = int(line.split()[1])
                    elif line.startswith('MemTotal:'):
                        info['mem_total_kb'] = int(line.split()[1])
                    elif line.startswith('MemFree:'):
                        info['mem_free_kb'] = int(line.split()[1])
                    elif line.startswith('MemAvailable:'):
                        info['mem_available_kb'] = int(line.split()[1])
        except (FileNotFoundError, PermissionError):
            return info

        info['used_kb'] = info.get('total_kb', 0) - info.get('free_kb', 0)
        total = info.get('total_kb', 1)
        info['usage_percent'] = round(info['used_kb'] / total * 100, 1) if total > 0 else 0
        info['total_human'] = self._format_kb(info.get('total_kb', 0))
        info['used_human'] = self._format_kb(info.get('used_kb', 0))
        info['free_human'] = self._format_kb(info.get('free_kb', 0))
        return info

    def get_swappiness(self):
        """Get vm.swappiness kernel parameter."""
        try:
            with open('/proc/sys/vm/swappiness', 'r') as f:
                return int(f.read().strip())
        except (FileNotFoundError, PermissionError):
            return None

    def get_swap_devices(self):
        """Get swap partitions/files from /proc/swaps."""
        devices = []
        try:
            with open('/proc/swaps', 'r') as f:
                lines = f.readlines()[1:]
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 5:
                        devices.append({
                            'device': parts[0],
                            'type': parts[1],
                            'size_kb': int(parts[2]),
                            'used_kb': int(parts[3]),
                            'priority': int(parts[4]),
                            'size_human': self._format_kb(int(parts[2])),
                            'used_human': self._format_kb(int(parts[3])),
                        })
        except (FileNotFoundError, PermissionError):
            pass
        return devices

    def get_process_swap(self):
        """Get per-process swap usage from /proc/[pid]/status."""
        processes = []
        try:
            for pid in os.listdir('/proc'):
                if not pid.isdigit(): continue
                try:
                    swap_kb = 0
                    name = ''
                    with open(f'/proc/{pid}/status', 'r') as f:
                        for line in f:
                            if line.startswith('VmSwap:'):
                                swap_kb = int(line.split()[1])
                            elif line.startswith('Name:'):
                                name = line.split(':', 1)[1].strip()
                    if swap_kb > 0:
                        processes.append({
                            'pid': int(pid),
                            'name': name,
                            'swap_kb': swap_kb,
                            'swap_human': self._format_kb(swap_kb),
                        })
                except (FileNotFoundError, PermissionError, ValueError, IndexError):
                    continue
        except (FileNotFoundError, PermissionError):
            pass

        processes.sort(key=lambda x: x['swap_kb'], reverse=True)
        return processes

    def get_pressure(self):
        """Get memory pressure from /proc/pressure/memory."""
        try:
            with open('/proc/pressure/memory', 'r') as f:
                lines = f.readlines()
                result = {}
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        ptype = parts[0]
                        metrics = {}
                        for p in parts[1:]:
                            k, v = p.split('=')
                            metrics[k] = float(v) if '.' in v else int(v)
                        result[ptype] = metrics
                return result
        except (FileNotFoundError, PermissionError):
            return {}

    def audit(self):
        """Run swap audit and return recommendations."""
        issues = []
        info = self.get_swap_info()
        swappiness = self.get_swappiness()

        if info.get('total_kb', 0) == 0:
            issues.append({'severity': 'warning', 'message': 'No swap configured'})
            return issues

        if info.get('usage_percent', 0) > 80:
            issues.append({'severity': 'critical', 'message': f"Swap usage critically high: {info['usage_percent']}%"})
        elif info.get('usage_percent', 0) > 50:
            issues.append({'severity': 'warning', 'message': f"Swap usage elevated: {info['usage_percent']}%"})

        if swappiness is not None:
            if swappiness > 60:
                issues.append({'severity': 'info', 'message': f'vm.swappiness={swappiness} (high — consider 10-30 for servers)'})

        mem_total = info.get('mem_total_kb', 1)
        swap_total = info.get('total_kb', 0)
        ratio = swap_total / mem_total if mem_total else 0
        if ratio < 0.25 and mem_total > 4 * 1048576:
            issues.append({'severity': 'info', 'message': f'Swap is only {ratio:.0%} of RAM — consider increasing'})

        top_procs = self.get_process_swap()[:5]
        if top_procs and top_procs[0]['swap_kb'] > 524288:
            issues.append({'severity': 'warning', 'message': f"Process '{top_procs[0]['name']}' using {top_procs[0]['swap_human']} swap"})

        return issues

    def print_report(self):
        """Print formatted swap analysis report."""
        info = self.get_swap_info()
        swappiness = self.get_swappiness()
        devices = self.get_swap_devices()
        top_procs = self.get_process_swap()[:10]
        issues = self.audit()

        print(f"\n{'='*60}")
        print(f"  Swap Usage Analysis Report")
        print(f"{'='*60}")
        print(f"\n  Total Swap: {info.get('total_human', 'N/A')}")
        print(f"  Used: {info.get('used_human', 'N/A')} ({info.get('usage_percent', 0)}%)")
        print(f"  Free: {info.get('free_human', 'N/A')}")
        print(f"  vm.swappiness: {swappiness}")

        if devices:
            print(f"\n  Swap Devices ({len(devices)}):")
            for d in devices:
                print(f"    {d['device']} ({d['type']}): {d['used_human']}/{d['size_human']} pri={d['priority']}")

        if top_procs:
            print(f"\n  Top Swap Consumers:")
            for p in top_procs[:10]:
                print(f"    PID {p['pid']:6d} {p['name']:20s} {p['swap_human']}")

        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in issues:
                print(f"    [{i['severity'].upper():8s}] {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["SwapAnalyzer"]
