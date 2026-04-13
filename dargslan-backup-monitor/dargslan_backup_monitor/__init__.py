"""
dargslan-backup-monitor — Linux Backup Monitor

Monitor backup status, check freshness, verify integrity.
Supports common backup directories, tar/gz archives, and rsync patterns.
Zero external dependencies.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import os
import time
import hashlib
import json
import glob as globmod


def _human_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def _time_ago(seconds):
    if seconds < 3600:
        return f"{int(seconds/60)} minutes ago"
    elif seconds < 86400:
        return f"{seconds/3600:.1f} hours ago"
    else:
        return f"{seconds/86400:.1f} days ago"


class BackupMonitor:
    """Monitor backup files and directories."""

    BACKUP_EXTENSIONS = ['.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tar.xz',
                         '.zip', '.sql', '.sql.gz', '.dump', '.bak', '.backup']

    def __init__(self, backup_dirs=None):
        self.backup_dirs = backup_dirs or [
            '/backup', '/backups', '/var/backups',
            '/home/backup', '/opt/backup', '/mnt/backup',
        ]

    def find_backups(self, path=None):
        """Find backup files in configured or specified directories."""
        dirs = [path] if path else self.backup_dirs
        backups = []
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for root, _, files in os.walk(d):
                for f in files:
                    if any(f.endswith(ext) for ext in self.BACKUP_EXTENSIONS):
                        fpath = os.path.join(root, f)
                        try:
                            stat = os.stat(fpath)
                            age = time.time() - stat.st_mtime
                            backups.append({
                                'path': fpath,
                                'filename': f,
                                'size': stat.st_size,
                                'size_human': _human_size(stat.st_size),
                                'modified': time.ctime(stat.st_mtime),
                                'age_seconds': age,
                                'age_human': _time_ago(age),
                                'status': 'OK' if age < 86400 else ('WARNING' if age < 604800 else 'STALE'),
                            })
                        except (OSError, PermissionError):
                            continue
        backups.sort(key=lambda x: x['age_seconds'])
        return backups

    def check_freshness(self, path=None, max_age_hours=24):
        """Check if backups are fresh (within max_age_hours)."""
        backups = self.find_backups(path)
        max_age_sec = max_age_hours * 3600
        results = {
            'fresh': [],
            'stale': [],
            'total': len(backups),
        }
        for b in backups:
            if b['age_seconds'] <= max_age_sec:
                results['fresh'].append(b)
            else:
                results['stale'].append(b)
        results['all_fresh'] = len(results['stale']) == 0 and len(backups) > 0
        return results

    def verify_checksum(self, filepath, algorithm='sha256'):
        """Calculate checksum of a backup file."""
        if not os.path.isfile(filepath):
            return {'error': f'File not found: {filepath}'}

        h = hashlib.new(algorithm)
        try:
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    h.update(chunk)
            return {
                'file': filepath,
                'algorithm': algorithm,
                'checksum': h.hexdigest(),
                'size': os.path.getsize(filepath),
                'size_human': _human_size(os.path.getsize(filepath)),
            }
        except (OSError, PermissionError) as e:
            return {'error': str(e)}

    def backup_schedule_check(self, path=None):
        """Analyze backup frequency and consistency."""
        backups = self.find_backups(path)
        if len(backups) < 2:
            return {'status': 'insufficient_data', 'count': len(backups)}

        intervals = []
        for i in range(len(backups) - 1):
            diff = abs(backups[i+1]['age_seconds'] - backups[i]['age_seconds'])
            intervals.append(diff)

        avg_interval = sum(intervals) / len(intervals)
        return {
            'count': len(backups),
            'avg_interval_hours': round(avg_interval / 3600, 1),
            'newest': backups[0]['age_human'],
            'oldest': backups[-1]['age_human'],
            'total_size': sum(b['size'] for b in backups),
            'total_size_human': _human_size(sum(b['size'] for b in backups)),
        }

    def disk_usage_trend(self, path=None):
        """Analyze backup disk usage."""
        backups = self.find_backups(path)
        if not backups:
            return {'status': 'no_backups'}

        total = sum(b['size'] for b in backups)
        largest = max(backups, key=lambda x: x['size'])
        smallest = min(backups, key=lambda x: x['size'])

        return {
            'total_backups': len(backups),
            'total_size': total,
            'total_size_human': _human_size(total),
            'average_size_human': _human_size(total // len(backups)),
            'largest': {'file': largest['filename'], 'size': largest['size_human']},
            'smallest': {'file': smallest['filename'], 'size': smallest['size_human']},
        }

    def print_report(self, path=None, max_age_hours=24):
        """Print formatted backup status report."""
        backups = self.find_backups(path)
        freshness = self.check_freshness(path, max_age_hours)

        print(f"\n{'='*60}")
        print(f"  Backup Monitor Report")
        print(f"{'='*60}")

        if not backups:
            dirs = [path] if path else self.backup_dirs
            print(f"  No backup files found in: {', '.join(dirs)}")
            print(f"  Searched extensions: {', '.join(self.BACKUP_EXTENSIONS[:5])}")
        else:
            status_icon = {'OK': '[OK]', 'WARNING': '[WARN]', 'STALE': '[STALE]'}
            print(f"  Found {len(backups)} backup file(s)")
            print(f"  Fresh (< {max_age_hours}h): {len(freshness['fresh'])}")
            print(f"  Stale: {len(freshness['stale'])}")
            print()

            for b in backups[:20]:
                icon = status_icon.get(b['status'], '[?]')
                print(f"  {icon:8s} {b['size_human']:>10}  {b['age_human']:>20}  {b['filename']}")

            if len(backups) > 20:
                print(f"  ... and {len(backups)-20} more")

            total = sum(b['size'] for b in backups)
            print(f"\n  Total backup size: {_human_size(total)}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  Linux eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")

    def to_json(self, path=None):
        """Return backup status as JSON."""
        return json.dumps({
            'backups': self.find_backups(path),
            'freshness': self.check_freshness(path),
            'disk_usage': self.disk_usage_trend(path),
        }, indent=2, default=str)


__all__ = ["BackupMonitor"]
