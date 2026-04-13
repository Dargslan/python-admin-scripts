"""
dargslan-disk-benchmark — Linux Disk I/O Benchmark Tool

Measure read/write speed, IOPS, and latency for any filesystem path.
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
import tempfile
import struct


class DiskBenchmark:
    """Benchmark disk I/O performance."""

    def __init__(self, path=None):
        self.path = path or tempfile.gettempdir()

    @staticmethod
    def _format_bytes(b):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} PB"

    def sequential_write(self, size_mb=100, block_size_kb=1024):
        test_file = os.path.join(self.path, '.dargslan_bench_write')
        block = os.urandom(block_size_kb * 1024)
        blocks = (size_mb * 1024) // block_size_kb
        try:
            start = time.time()
            with open(test_file, 'wb') as f:
                for _ in range(blocks):
                    f.write(block)
                f.flush()
                os.fsync(f.fileno())
            elapsed = time.time() - start
            speed_mbps = size_mb / elapsed if elapsed > 0 else 0
            return {
                'test': 'sequential_write',
                'size_mb': size_mb,
                'block_size_kb': block_size_kb,
                'elapsed_sec': round(elapsed, 3),
                'speed_mbps': round(speed_mbps, 2),
                'speed_human': f"{speed_mbps:.1f} MB/s",
            }
        finally:
            try:
                os.unlink(test_file)
            except OSError:
                pass

    def sequential_read(self, size_mb=100, block_size_kb=1024):
        test_file = os.path.join(self.path, '.dargslan_bench_read')
        block = os.urandom(block_size_kb * 1024)
        blocks = (size_mb * 1024) // block_size_kb
        try:
            with open(test_file, 'wb') as f:
                for _ in range(blocks):
                    f.write(block)
                f.flush()
                os.fsync(f.fileno())

            os.sync()
            try:
                with open('/proc/sys/vm/drop_caches', 'w') as f:
                    f.write('3')
            except (PermissionError, FileNotFoundError):
                pass

            start = time.time()
            with open(test_file, 'rb') as f:
                while f.read(block_size_kb * 1024):
                    pass
            elapsed = time.time() - start
            speed_mbps = size_mb / elapsed if elapsed > 0 else 0
            return {
                'test': 'sequential_read',
                'size_mb': size_mb,
                'block_size_kb': block_size_kb,
                'elapsed_sec': round(elapsed, 3),
                'speed_mbps': round(speed_mbps, 2),
                'speed_human': f"{speed_mbps:.1f} MB/s",
            }
        finally:
            try:
                os.unlink(test_file)
            except OSError:
                pass

    def random_write_iops(self, count=1000, block_size=4096):
        test_file = os.path.join(self.path, '.dargslan_bench_riops')
        file_size = count * block_size
        try:
            with open(test_file, 'wb') as f:
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())

            import random
            data = os.urandom(block_size)
            positions = [random.randint(0, count - 1) * block_size for _ in range(count)]

            start = time.time()
            with open(test_file, 'r+b') as f:
                for pos in positions:
                    f.seek(pos)
                    f.write(data)
                f.flush()
                os.fsync(f.fileno())
            elapsed = time.time() - start
            iops = count / elapsed if elapsed > 0 else 0
            return {
                'test': 'random_write_iops',
                'operations': count,
                'block_size': block_size,
                'elapsed_sec': round(elapsed, 3),
                'iops': round(iops, 0),
            }
        finally:
            try:
                os.unlink(test_file)
            except OSError:
                pass

    def random_read_iops(self, count=1000, block_size=4096):
        test_file = os.path.join(self.path, '.dargslan_bench_rriops')
        file_size = count * block_size
        try:
            with open(test_file, 'wb') as f:
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())

            import random
            positions = [random.randint(0, count - 1) * block_size for _ in range(count)]

            start = time.time()
            with open(test_file, 'rb') as f:
                for pos in positions:
                    f.seek(pos)
                    f.read(block_size)
            elapsed = time.time() - start
            iops = count / elapsed if elapsed > 0 else 0
            return {
                'test': 'random_read_iops',
                'operations': count,
                'block_size': block_size,
                'elapsed_sec': round(elapsed, 3),
                'iops': round(iops, 0),
            }
        finally:
            try:
                os.unlink(test_file)
            except OSError:
                pass

    def latency_test(self, count=100):
        test_file = os.path.join(self.path, '.dargslan_bench_lat')
        latencies = []
        try:
            for _ in range(count):
                data = os.urandom(512)
                start = time.time()
                with open(test_file, 'wb') as f:
                    f.write(data)
                    f.flush()
                    os.fsync(f.fileno())
                lat = (time.time() - start) * 1000
                latencies.append(lat)

            latencies.sort()
            return {
                'test': 'latency',
                'operations': count,
                'avg_ms': round(sum(latencies) / len(latencies), 3),
                'min_ms': round(latencies[0], 3),
                'max_ms': round(latencies[-1], 3),
                'p50_ms': round(latencies[len(latencies) // 2], 3),
                'p95_ms': round(latencies[int(len(latencies) * 0.95)], 3),
                'p99_ms': round(latencies[int(len(latencies) * 0.99)], 3),
            }
        finally:
            try:
                os.unlink(test_file)
            except OSError:
                pass

    def get_disk_info(self):
        try:
            stat = os.statvfs(self.path)
            total = stat.f_frsize * stat.f_blocks
            free = stat.f_frsize * stat.f_bavail
            used = total - free
            return {
                'path': self.path,
                'total': total,
                'used': used,
                'free': free,
                'total_human': self._format_bytes(total),
                'used_human': self._format_bytes(used),
                'free_human': self._format_bytes(free),
                'used_percent': round(used / total * 100, 1) if total else 0,
            }
        except OSError as e:
            return {'path': self.path, 'error': str(e)}

    def full_benchmark(self, size_mb=50):
        results = {
            'path': self.path,
            'disk_info': self.get_disk_info(),
            'tests': [],
        }
        results['tests'].append(self.sequential_write(size_mb=size_mb))
        results['tests'].append(self.sequential_read(size_mb=size_mb))
        results['tests'].append(self.random_write_iops(count=500))
        results['tests'].append(self.random_read_iops(count=500))
        results['tests'].append(self.latency_test(count=50))
        return results

    def print_report(self, size_mb=50):
        results = self.full_benchmark(size_mb=size_mb)
        di = results['disk_info']

        print(f"\n{'='*60}")
        print(f"  Disk I/O Benchmark Report")
        print(f"  Path: {self.path}")
        print(f"{'='*60}")

        if not di.get('error'):
            print(f"\n  Disk: {di['total_human']} total, {di['used_human']} used ({di['used_percent']}%), {di['free_human']} free")

        for t in results['tests']:
            print(f"\n  {t['test'].replace('_', ' ').title()}:")
            if 'speed_human' in t:
                print(f"    Speed: {t['speed_human']}")
                print(f"    Time:  {t['elapsed_sec']}s ({t['size_mb']} MB)")
            elif 'iops' in t:
                print(f"    IOPS:  {t['iops']}")
                print(f"    Time:  {t['elapsed_sec']}s ({t['operations']} ops)")
            elif 'avg_ms' in t:
                print(f"    Avg:   {t['avg_ms']}ms")
                print(f"    P50:   {t['p50_ms']}ms | P95: {t['p95_ms']}ms | P99: {t['p99_ms']}ms")
                print(f"    Min:   {t['min_ms']}ms | Max: {t['max_ms']}ms")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["DiskBenchmark"]
