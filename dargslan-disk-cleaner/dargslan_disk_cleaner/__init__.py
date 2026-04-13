"""
dargslan-disk-cleaner — Linux Disk Usage Analyzer & Cleaner

Find large files, analyze disk usage, and identify cleanup opportunities.
Zero external dependencies.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import os
import shutil
import time
import json


def _human_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


class DiskCleaner:
    """Analyze disk usage and find cleanup opportunities."""

    def __init__(self):
        self.temp_dirs = ['/tmp', '/var/tmp', '/var/cache/apt/archives']
        self.log_dirs = ['/var/log']

    def disk_usage(self):
        """Get disk usage for all mounted filesystems."""
        results = []
        seen = set()
        try:
            with open('/proc/mounts', 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) < 2:
                        continue
                    mount = parts[1]
                    if mount in seen or parts[0] == 'none':
                        continue
                    try:
                        stat = shutil.disk_usage(mount)
                        seen.add(mount)
                        results.append({
                            'mount': mount,
                            'total': stat.total,
                            'used': stat.used,
                            'free': stat.free,
                            'percent_used': round((stat.used / stat.total) * 100, 1) if stat.total > 0 else 0,
                            'total_human': _human_size(stat.total),
                            'used_human': _human_size(stat.used),
                            'free_human': _human_size(stat.free),
                        })
                    except (PermissionError, OSError):
                        continue
        except FileNotFoundError:
            stat = shutil.disk_usage('/')
            results.append({
                'mount': '/',
                'total': stat.total,
                'used': stat.used,
                'free': stat.free,
                'percent_used': round((stat.used / stat.total) * 100, 1),
                'total_human': _human_size(stat.total),
                'used_human': _human_size(stat.used),
                'free_human': _human_size(stat.free),
            })
        return results

    def find_large_files(self, path='/', min_size_mb=100, max_results=20):
        """Find files larger than min_size_mb."""
        min_bytes = min_size_mb * 1024 * 1024
        large_files = []
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '__pycache__', '.cache')]
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    size = os.path.getsize(fpath)
                    if size >= min_bytes:
                        large_files.append({
                            'path': fpath,
                            'size': size,
                            'size_human': _human_size(size),
                            'modified': time.ctime(os.path.getmtime(fpath)),
                        })
                except (OSError, PermissionError):
                    continue
        large_files.sort(key=lambda x: x['size'], reverse=True)
        return large_files[:max_results]

    def find_old_files(self, path, days=90, max_results=50):
        """Find files not modified in the last N days."""
        cutoff = time.time() - (days * 86400)
        old_files = []
        for root, dirs, files in os.walk(path):
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    mtime = os.path.getmtime(fpath)
                    if mtime < cutoff:
                        old_files.append({
                            'path': fpath,
                            'size': os.path.getsize(fpath),
                            'size_human': _human_size(os.path.getsize(fpath)),
                            'modified': time.ctime(mtime),
                            'days_old': int((time.time() - mtime) / 86400),
                        })
                except (OSError, PermissionError):
                    continue
        old_files.sort(key=lambda x: x['size'], reverse=True)
        return old_files[:max_results]

    def dir_sizes(self, path='/', depth=1):
        """Get directory sizes at given depth."""
        results = []
        try:
            for entry in os.scandir(path):
                if entry.is_dir(follow_symlinks=False):
                    total = 0
                    try:
                        for root, dirs, files in os.walk(entry.path):
                            for f in files:
                                try:
                                    total += os.path.getsize(os.path.join(root, f))
                                except (OSError, PermissionError):
                                    pass
                        results.append({
                            'path': entry.path,
                            'size': total,
                            'size_human': _human_size(total),
                        })
                    except PermissionError:
                        continue
        except PermissionError:
            pass
        results.sort(key=lambda x: x['size'], reverse=True)
        return results

    def temp_usage(self):
        """Analyze temp directory usage."""
        results = []
        for d in self.temp_dirs:
            if os.path.isdir(d):
                total = 0
                count = 0
                for root, dirs, files in os.walk(d):
                    for f in files:
                        try:
                            total += os.path.getsize(os.path.join(root, f))
                            count += 1
                        except (OSError, PermissionError):
                            pass
                results.append({
                    'directory': d,
                    'size': total,
                    'size_human': _human_size(total),
                    'file_count': count,
                })
        return results

    def find_duplicates(self, path, min_size_mb=1):
        """Find potential duplicate files by size."""
        min_bytes = min_size_mb * 1024 * 1024
        size_map = {}
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules')]
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    size = os.path.getsize(fpath)
                    if size >= min_bytes:
                        size_map.setdefault(size, []).append(fpath)
                except (OSError, PermissionError):
                    pass
        return {_human_size(k): v for k, v in size_map.items() if len(v) > 1}

    def print_report(self, path='/'):
        """Print a formatted disk usage report."""
        print(f"\n{'='*60}")
        print(f"  Disk Usage Report")
        print(f"{'='*60}")

        for du in self.disk_usage():
            bar_len = 30
            filled = int(bar_len * du['percent_used'] / 100)
            bar = '#' * filled + '-' * (bar_len - filled)
            warn = ' [!]' if du['percent_used'] > 85 else ''
            print(f"  {du['mount']}")
            print(f"    [{bar}] {du['percent_used']}%{warn}")
            print(f"    Used: {du['used_human']} / {du['total_human']} (Free: {du['free_human']})")

        temps = self.temp_usage()
        if temps:
            print(f"\n  Temp Directories:")
            for t in temps:
                print(f"    {t['directory']}: {t['size_human']} ({t['file_count']} files)")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  Linux eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")

    def to_json(self):
        """Return full disk report as JSON."""
        return json.dumps({
            'filesystems': self.disk_usage(),
            'temp_dirs': self.temp_usage(),
        }, indent=2)


__all__ = ["DiskCleaner"]
