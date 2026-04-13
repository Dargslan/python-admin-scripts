"""
dargslan-nfs-health — NFS Mount Health Checker

Detect stale mounts, measure latency, audit exports, and monitor NFS statistics.
Zero external dependencies — uses only Python standard library.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import os
import subprocess
import time
import json


class NFSHealth:
    """Check NFS mount health and performance."""

    def __init__(self):
        pass

    def _run(self, args):
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=15)
            return result.stdout.strip() if result.returncode == 0 else ''
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ''

    def get_nfs_mounts(self):
        mounts = []
        try:
            with open('/proc/mounts', 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 4 and ('nfs' in parts[2] or 'nfs4' in parts[2]):
                        mounts.append({
                            'source': parts[0],
                            'mountpoint': parts[1],
                            'fstype': parts[2],
                            'options': parts[3],
                        })
        except (FileNotFoundError, PermissionError):
            pass
        return mounts

    def check_mount_health(self, mountpoint):
        start = time.time()
        try:
            os.statvfs(mountpoint)
            latency_ms = (time.time() - start) * 1000
            return {'mountpoint': mountpoint, 'accessible': True, 'latency_ms': round(latency_ms, 2), 'stale': False}
        except OSError as e:
            return {'mountpoint': mountpoint, 'accessible': False, 'stale': 'Stale' in str(e) or 'errno 116' in str(e),
                    'error': str(e)}
        except Exception as e:
            return {'mountpoint': mountpoint, 'accessible': False, 'error': str(e)}

    def check_all_mounts(self):
        results = []
        for mount in self.get_nfs_mounts():
            health = self.check_mount_health(mount['mountpoint'])
            health['source'] = mount['source']
            health['fstype'] = mount['fstype']
            health['options'] = mount['options']
            results.append(health)
        return results

    def get_nfs_stats(self):
        try:
            with open('/proc/net/rpc/nfs', 'r') as f:
                content = f.read()
            stats = {}
            for line in content.split('\n'):
                parts = line.split()
                if len(parts) >= 2:
                    stats[parts[0]] = [int(x) if x.isdigit() else x for x in parts[1:]]
            return stats
        except (FileNotFoundError, PermissionError):
            return {}

    def get_nfsd_stats(self):
        try:
            with open('/proc/net/rpc/nfsd', 'r') as f:
                content = f.read()
            stats = {}
            for line in content.split('\n'):
                parts = line.split()
                if len(parts) >= 2:
                    stats[parts[0]] = [int(x) if x.isdigit() else x for x in parts[1:]]
            return stats
        except (FileNotFoundError, PermissionError):
            return {}

    def get_exports(self):
        exports = []
        try:
            with open('/etc/exports', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split()
                        if parts:
                            export = {'path': parts[0], 'clients': parts[1:]}
                            exports.append(export)
        except (FileNotFoundError, PermissionError):
            pass
        return exports

    def get_active_exports(self):
        output = self._run(['exportfs', '-v'])
        exports = []
        for line in output.split('\n'):
            if line.strip():
                exports.append(line.strip())
        return exports

    def measure_throughput(self, mountpoint, size_kb=1024):
        test_file = os.path.join(mountpoint, '.dargslan_nfs_test')
        try:
            data = os.urandom(size_kb * 1024)
            start = time.time()
            with open(test_file, 'wb') as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            write_time = time.time() - start

            start = time.time()
            with open(test_file, 'rb') as f:
                f.read()
            read_time = time.time() - start

            os.unlink(test_file)
            return {
                'mountpoint': mountpoint,
                'size_kb': size_kb,
                'write_mbps': round(size_kb / 1024 / write_time, 2) if write_time > 0 else 0,
                'read_mbps': round(size_kb / 1024 / read_time, 2) if read_time > 0 else 0,
            }
        except (OSError, PermissionError) as e:
            return {'mountpoint': mountpoint, 'error': str(e)}

    def audit(self):
        issues = []
        mounts = self.check_all_mounts()

        for m in mounts:
            if m.get('stale'):
                issues.append({'severity': 'critical', 'message': f"Stale NFS mount: {m['mountpoint']} ({m['source']})"})
            elif not m.get('accessible'):
                issues.append({'severity': 'critical', 'message': f"Inaccessible NFS mount: {m['mountpoint']}"})
            elif m.get('latency_ms', 0) > 100:
                issues.append({'severity': 'warning', 'message': f"High NFS latency: {m['mountpoint']} ({m['latency_ms']}ms)"})

            opts = m.get('options', '')
            if 'noac' not in opts and 'actimeo=0' not in opts:
                pass
            if 'hard' not in opts and 'soft' in opts:
                issues.append({'severity': 'info', 'message': f"Soft mount (may cause data corruption): {m['mountpoint']}"})

        return issues

    def print_report(self):
        mounts = self.check_all_mounts()
        exports = self.get_exports()
        issues = self.audit()

        print(f"\n{'='*60}")
        print(f"  NFS Health Report")
        print(f"{'='*60}")

        if mounts:
            print(f"\n  NFS Mounts ({len(mounts)}):")
            for m in mounts:
                status = 'OK' if m.get('accessible') else 'STALE' if m.get('stale') else 'FAIL'
                latency = f" ({m['latency_ms']}ms)" if 'latency_ms' in m else ''
                print(f"    [{status:5s}] {m['source']} -> {m['mountpoint']}{latency}")
        else:
            print("\n  No NFS mounts found.")

        if exports:
            print(f"\n  Exports ({len(exports)}):")
            for e in exports:
                print(f"    {e['path']} -> {' '.join(e['clients'])}")

        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in issues:
                print(f"    [{i['severity'].upper():8s}] {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["NFSHealth"]
