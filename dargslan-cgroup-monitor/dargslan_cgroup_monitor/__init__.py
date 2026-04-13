"""
dargslan-cgroup-monitor — Linux Cgroup Resource Monitor

Track CPU, memory, and I/O limits for containers and system slices.
Supports cgroups v1 and v2. Zero external dependencies.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import os
import json


class CgroupMonitor:
    """Monitor Linux cgroup resource usage and limits."""

    def __init__(self):
        self.version = self._detect_version()

    def _detect_version(self):
        if os.path.exists('/sys/fs/cgroup/cgroup.controllers'):
            return 2
        if os.path.exists('/sys/fs/cgroup/cpu'):
            return 1
        return 0

    def _read_file(self, path):
        try:
            with open(path, 'r') as f:
                return f.read().strip()
        except (FileNotFoundError, PermissionError):
            return None

    @staticmethod
    def _format_bytes(b):
        if b is None: return 'N/A'
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if b < 1024: return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} PB"

    def list_cgroups_v2(self):
        cgroups = []
        base = '/sys/fs/cgroup'
        try:
            for root, dirs, files in os.walk(base):
                if 'cgroup.procs' in files:
                    procs = self._read_file(os.path.join(root, 'cgroup.procs'))
                    proc_count = len([p for p in (procs or '').split('\n') if p.strip()])
                    if proc_count == 0: continue
                    path = root.replace(base, '') or '/'
                    cg = {'path': path, 'procs': proc_count}

                    mem_current = self._read_file(os.path.join(root, 'memory.current'))
                    mem_max = self._read_file(os.path.join(root, 'memory.max'))
                    if mem_current and mem_current.isdigit():
                        cg['memory_bytes'] = int(mem_current)
                        cg['memory_human'] = self._format_bytes(int(mem_current))
                    if mem_max and mem_max != 'max' and mem_max.isdigit():
                        cg['memory_limit'] = int(mem_max)
                        cg['memory_limit_human'] = self._format_bytes(int(mem_max))
                        if cg.get('memory_bytes'):
                            cg['memory_percent'] = round(cg['memory_bytes'] / int(mem_max) * 100, 1)

                    cpu_stat = self._read_file(os.path.join(root, 'cpu.stat'))
                    if cpu_stat:
                        stats = {}
                        for line in cpu_stat.split('\n'):
                            parts = line.split()
                            if len(parts) == 2:
                                stats[parts[0]] = int(parts[1])
                        cg['cpu_usage_usec'] = stats.get('usage_usec', 0)

                    io_stat = self._read_file(os.path.join(root, 'io.stat'))
                    if io_stat and io_stat:
                        cg['io_stat'] = io_stat[:200]

                    cgroups.append(cg)
        except (FileNotFoundError, PermissionError):
            pass
        return sorted(cgroups, key=lambda x: x.get('memory_bytes', 0), reverse=True)

    def list_cgroups_v1(self):
        cgroups = []
        controllers = ['cpu', 'memory', 'blkio']
        for ctrl in controllers:
            base = f'/sys/fs/cgroup/{ctrl}'
            if not os.path.isdir(base): continue
            try:
                for root, dirs, files in os.walk(base):
                    if 'cgroup.procs' in files:
                        procs = self._read_file(os.path.join(root, 'cgroup.procs'))
                        proc_count = len([p for p in (procs or '').split('\n') if p.strip()])
                        if proc_count == 0: continue
                        path = root.replace(base, '') or '/'
                        cg = {'path': path, 'controller': ctrl, 'procs': proc_count}

                        if ctrl == 'memory':
                            usage = self._read_file(os.path.join(root, 'memory.usage_in_bytes'))
                            limit = self._read_file(os.path.join(root, 'memory.limit_in_bytes'))
                            if usage and usage.isdigit():
                                cg['memory_bytes'] = int(usage)
                                cg['memory_human'] = self._format_bytes(int(usage))
                            if limit and limit.isdigit() and int(limit) < 9223372036854775807:
                                cg['memory_limit'] = int(limit)
                                cg['memory_limit_human'] = self._format_bytes(int(limit))

                        cgroups.append(cg)
            except (FileNotFoundError, PermissionError):
                continue
        return cgroups

    def list_cgroups(self):
        if self.version == 2:
            return self.list_cgroups_v2()
        elif self.version == 1:
            return self.list_cgroups_v1()
        return []

    def get_system_slices(self):
        cgroups = self.list_cgroups()
        slices = [cg for cg in cgroups if '.slice' in cg.get('path', '') or '.service' in cg.get('path', '')]
        return slices

    def get_container_cgroups(self):
        cgroups = self.list_cgroups()
        containers = [cg for cg in cgroups if any(k in cg.get('path', '') for k in ['docker', 'containerd', 'podman', 'cri-containerd', 'lxc'])]
        return containers

    def audit(self):
        issues = []
        cgroups = self.list_cgroups()

        for cg in cgroups:
            if cg.get('memory_percent', 0) > 90:
                issues.append({'severity': 'critical', 'cgroup': cg['path'],
                    'message': f"Memory usage at {cg['memory_percent']}%"})
            elif cg.get('memory_percent', 0) > 75:
                issues.append({'severity': 'warning', 'cgroup': cg['path'],
                    'message': f"Memory usage at {cg['memory_percent']}%"})

            if cg.get('memory_bytes') and not cg.get('memory_limit'):
                if 'docker' in cg.get('path', '') or 'containerd' in cg.get('path', ''):
                    issues.append({'severity': 'info', 'cgroup': cg['path'],
                        'message': 'Container has no memory limit set'})

        return issues

    def print_report(self):
        cgroups = self.list_cgroups()
        issues = self.audit()

        print(f"\n{'='*60}")
        print(f"  Cgroup Resource Monitor (v{self.version})")
        print(f"{'='*60}")
        print(f"\n  Active cgroups: {len(cgroups)}")

        for cg in cgroups[:20]:
            mem = cg.get('memory_human', 'N/A')
            limit = cg.get('memory_limit_human', 'no limit')
            pct = f" ({cg['memory_percent']}%)" if 'memory_percent' in cg else ''
            print(f"\n  {cg['path']} ({cg['procs']} procs)")
            print(f"    Memory: {mem} / {limit}{pct}")

        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in issues:
                print(f"    [{i['severity'].upper():8s}] {i['cgroup']}: {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["CgroupMonitor"]
