"""
dargslan-memory-profiler — Linux Memory Profiler

Per-process RSS, shared memory, swap usage, and memory leak detection.
Zero external dependencies — reads /proc filesystem directly.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import os
import json


class MemoryProfiler:
    """Profile Linux system and per-process memory usage."""

    def __init__(self):
        pass

    @staticmethod
    def _format_bytes(kb):
        b = kb * 1024
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} PB"

    def _read_file(self, path):
        try:
            with open(path, 'r') as f:
                return f.read()
        except (FileNotFoundError, PermissionError):
            return ''

    def get_system_memory(self):
        content = self._read_file('/proc/meminfo')
        mem = {}
        for line in content.split('\n'):
            parts = line.split(':')
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip().split()[0]
                if val.isdigit():
                    mem[key] = int(val)

        total = mem.get('MemTotal', 0)
        free = mem.get('MemFree', 0)
        available = mem.get('MemAvailable', 0)
        buffers = mem.get('Buffers', 0)
        cached = mem.get('Cached', 0)
        swap_total = mem.get('SwapTotal', 0)
        swap_free = mem.get('SwapFree', 0)
        shmem = mem.get('Shmem', 0)
        slab = mem.get('Slab', 0)
        huge_total = mem.get('HugePages_Total', 0)
        huge_free = mem.get('HugePages_Free', 0)

        used = total - available
        swap_used = swap_total - swap_free

        return {
            'total_kb': total, 'total_human': self._format_bytes(total),
            'used_kb': used, 'used_human': self._format_bytes(used),
            'free_kb': free, 'free_human': self._format_bytes(free),
            'available_kb': available, 'available_human': self._format_bytes(available),
            'buffers_kb': buffers, 'cached_kb': cached,
            'swap_total_kb': swap_total, 'swap_used_kb': swap_used,
            'swap_total_human': self._format_bytes(swap_total),
            'swap_used_human': self._format_bytes(swap_used),
            'shmem_kb': shmem, 'slab_kb': slab,
            'used_percent': round(used / total * 100, 1) if total else 0,
            'swap_percent': round(swap_used / swap_total * 100, 1) if swap_total else 0,
        }

    def get_process_memory(self, pid):
        status = self._read_file(f'/proc/{pid}/status')
        if not status:
            return None

        info = {'pid': pid}
        for line in status.split('\n'):
            parts = line.split(':')
            if len(parts) != 2:
                continue
            key = parts[0].strip()
            val = parts[1].strip()

            if key == 'Name':
                info['name'] = val
            elif key == 'VmRSS':
                v = val.split()[0]
                if v.isdigit():
                    info['rss_kb'] = int(v)
                    info['rss_human'] = self._format_bytes(int(v))
            elif key == 'VmSize':
                v = val.split()[0]
                if v.isdigit():
                    info['vsize_kb'] = int(v)
            elif key == 'VmSwap':
                v = val.split()[0]
                if v.isdigit():
                    info['swap_kb'] = int(v)
            elif key == 'RssAnon':
                v = val.split()[0]
                if v.isdigit():
                    info['rss_anon_kb'] = int(v)
            elif key == 'RssFile':
                v = val.split()[0]
                if v.isdigit():
                    info['rss_file_kb'] = int(v)
            elif key == 'RssShmem':
                v = val.split()[0]
                if v.isdigit():
                    info['rss_shmem_kb'] = int(v)
            elif key == 'Uid':
                info['uid'] = val.split()[0]

        smaps = self._read_file(f'/proc/{pid}/smaps_rollup')
        if smaps:
            for line in smaps.split('\n'):
                if line.startswith('Pss:'):
                    v = line.split(':')[1].strip().split()[0]
                    if v.isdigit():
                        info['pss_kb'] = int(v)
                        info['pss_human'] = self._format_bytes(int(v))

        return info

    def get_all_processes(self, sort_by='rss_kb', limit=30):
        processes = []
        try:
            for entry in os.listdir('/proc'):
                if entry.isdigit():
                    info = self.get_process_memory(int(entry))
                    if info and info.get('rss_kb', 0) > 0:
                        processes.append(info)
        except (FileNotFoundError, PermissionError):
            pass

        processes.sort(key=lambda x: x.get(sort_by, 0), reverse=True)
        return processes[:limit]

    def get_memory_by_name(self):
        processes = self.get_all_processes(limit=1000)
        grouped = {}
        for p in processes:
            name = p.get('name', 'unknown')
            if name not in grouped:
                grouped[name] = {'name': name, 'count': 0, 'total_rss_kb': 0, 'total_swap_kb': 0}
            grouped[name]['count'] += 1
            grouped[name]['total_rss_kb'] += p.get('rss_kb', 0)
            grouped[name]['total_swap_kb'] += p.get('swap_kb', 0)

        result = list(grouped.values())
        for r in result:
            r['total_rss_human'] = self._format_bytes(r['total_rss_kb'])
        result.sort(key=lambda x: x['total_rss_kb'], reverse=True)
        return result

    def get_shared_memory(self):
        segments = []
        try:
            import subprocess
            result = subprocess.run(['ipcs', '-m', '--human'], capture_output=True, text=True, timeout=10)
            for line in result.stdout.split('\n'):
                parts = line.split()
                if len(parts) >= 6 and parts[0].isdigit():
                    segments.append({'shmid': parts[0], 'owner': parts[2], 'size': parts[4], 'nattch': parts[5]})
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return segments

    def audit(self):
        issues = []
        sys_mem = self.get_system_memory()

        if sys_mem['used_percent'] > 90:
            issues.append({'severity': 'critical', 'message': f"System memory usage at {sys_mem['used_percent']}%"})
        elif sys_mem['used_percent'] > 80:
            issues.append({'severity': 'warning', 'message': f"System memory usage at {sys_mem['used_percent']}%"})

        if sys_mem['swap_percent'] > 50:
            issues.append({'severity': 'warning', 'message': f"Swap usage at {sys_mem['swap_percent']}%"})

        top = self.get_all_processes(limit=5)
        sys_total = sys_mem['total_kb']
        for p in top:
            pct = round(p.get('rss_kb', 0) / sys_total * 100, 1) if sys_total else 0
            if pct > 25:
                issues.append({'severity': 'warning', 'message': f"Process {p.get('name','')} (PID {p['pid']}) using {pct}% of system memory"})

        return issues

    def print_report(self):
        sys_mem = self.get_system_memory()
        top_procs = self.get_all_processes(limit=15)
        by_name = self.get_memory_by_name()[:10]
        issues = self.audit()

        print(f"\n{'='*60}")
        print(f"  Memory Profile Report")
        print(f"{'='*60}")

        print(f"\n  System Memory:")
        print(f"    Total:     {sys_mem['total_human']}")
        print(f"    Used:      {sys_mem['used_human']} ({sys_mem['used_percent']}%)")
        print(f"    Available: {sys_mem['available_human']}")
        print(f"    Buffers:   {self._format_bytes(sys_mem['buffers_kb'])}")
        print(f"    Cached:    {self._format_bytes(sys_mem['cached_kb'])}")
        if sys_mem['swap_total_kb']:
            print(f"    Swap:      {sys_mem['swap_used_human']} / {sys_mem['swap_total_human']} ({sys_mem['swap_percent']}%)")

        print(f"\n  Top Processes by RSS ({len(top_procs)}):")
        for p in top_procs:
            swap = f" swap={self._format_bytes(p['swap_kb'])}" if p.get('swap_kb', 0) > 0 else ''
            print(f"    {p.get('rss_human','N/A'):>10s}  PID {p['pid']:>6d}  {p.get('name','?')[:25]}{swap}")

        print(f"\n  Memory by Application ({len(by_name)}):")
        for g in by_name:
            print(f"    {g['total_rss_human']:>10s}  {g['name'][:25]:<25s} ({g['count']} procs)")

        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in issues:
                print(f"    [{i['severity'].upper():8s}] {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["MemoryProfiler"]
