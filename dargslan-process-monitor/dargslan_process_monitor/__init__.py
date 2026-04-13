"""
dargslan-process-monitor — Linux Process Monitor

Monitor processes, detect zombies, track resource-hungry processes.
Zero external dependencies — reads from /proc filesystem.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import os
import json


def _human_size(kb):
    if kb < 1024:
        return f"{kb} KB"
    elif kb < 1048576:
        return f"{kb/1024:.1f} MB"
    else:
        return f"{kb/1048576:.1f} GB"


class ProcessMonitor:
    """Monitor Linux processes via /proc filesystem."""

    def list_processes(self):
        """List all running processes with details."""
        processes = []
        for pid_dir in os.listdir('/proc'):
            if not pid_dir.isdigit():
                continue
            pid = int(pid_dir)
            info = self._get_process_info(pid)
            if info:
                processes.append(info)
        return processes

    def _get_process_info(self, pid):
        """Get detailed info for a single process."""
        try:
            with open(f'/proc/{pid}/stat', 'r') as f:
                stat = f.read().split()

            comm_start = stat[1].find('(')
            comm_end = stat[1].rfind(')')
            name = stat[1][comm_start+1:comm_end] if comm_start >= 0 else stat[1]

            state_map = {'R': 'Running', 'S': 'Sleeping', 'D': 'Disk Sleep',
                         'Z': 'Zombie', 'T': 'Stopped', 'I': 'Idle', 'X': 'Dead'}
            state_char = stat[2]

            mem_kb = 0
            try:
                with open(f'/proc/{pid}/status', 'r') as f:
                    for line in f:
                        if line.startswith('VmRSS:'):
                            mem_kb = int(line.split()[1])
                            break
            except (FileNotFoundError, PermissionError):
                pass

            try:
                with open(f'/proc/{pid}/cmdline', 'r') as f:
                    cmdline = f.read().replace('\x00', ' ').strip()
            except (FileNotFoundError, PermissionError):
                cmdline = name

            utime = int(stat[13])
            stime = int(stat[14])
            total_time = utime + stime

            return {
                'pid': pid,
                'name': name,
                'state': state_char,
                'state_name': state_map.get(state_char, 'Unknown'),
                'ppid': int(stat[3]),
                'threads': int(stat[19]),
                'mem_kb': mem_kb,
                'mem_human': _human_size(mem_kb),
                'cpu_ticks': total_time,
                'cmdline': cmdline[:200],
            }
        except (FileNotFoundError, PermissionError, IndexError, ValueError):
            return None

    def find_zombies(self):
        """Find zombie processes."""
        return [p for p in self.list_processes() if p['state'] == 'Z']

    def top_memory(self, n=10):
        """Get top N processes by memory usage."""
        procs = self.list_processes()
        procs.sort(key=lambda x: x['mem_kb'], reverse=True)
        return procs[:n]

    def top_cpu(self, n=10):
        """Get top N processes by CPU ticks."""
        procs = self.list_processes()
        procs.sort(key=lambda x: x['cpu_ticks'], reverse=True)
        return procs[:n]

    def find_by_name(self, name):
        """Find processes by name (partial match)."""
        name_lower = name.lower()
        return [p for p in self.list_processes() if name_lower in p['name'].lower() or name_lower in p['cmdline'].lower()]

    def process_count(self):
        """Get process count by state."""
        procs = self.list_processes()
        counts = {}
        for p in procs:
            state = p['state_name']
            counts[state] = counts.get(state, 0) + 1
        counts['total'] = len(procs)
        return counts

    def print_summary(self):
        """Print formatted process summary."""
        counts = self.process_count()
        zombies = self.find_zombies()
        top_mem = self.top_memory(5)

        print(f"\n{'='*60}")
        print(f"  Process Monitor — {counts.get('total', 0)} processes")
        print(f"{'='*60}")

        for state, count in sorted(counts.items()):
            if state != 'total':
                print(f"  {state:20s}: {count}")

        if zombies:
            print(f"\n  [!] ZOMBIE PROCESSES ({len(zombies)}):")
            for z in zombies:
                print(f"    PID {z['pid']:>6}  PPID {z['ppid']:>6}  {z['name']}")

        print(f"\n  Top Memory Consumers:")
        for p in top_mem:
            print(f"    PID {p['pid']:>6}  {p['mem_human']:>10}  {p['name']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  Linux eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")

    def to_json(self):
        """Return process info as JSON."""
        return json.dumps({
            'counts': self.process_count(),
            'zombies': self.find_zombies(),
            'top_memory': self.top_memory(10),
            'top_cpu': self.top_cpu(10),
        }, indent=2)


__all__ = ["ProcessMonitor"]
