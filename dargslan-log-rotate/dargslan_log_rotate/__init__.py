"""
dargslan-log-rotate — Linux Log Rotation Analyzer

Analyze logrotate configuration, find large/unrotated logs, check status.
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
import json
import re


def _human_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


class LogRotateAudit:
    """Analyze log rotation configuration and status."""

    def __init__(self):
        self.log_dirs = ['/var/log']
        self.logrotate_conf = '/etc/logrotate.conf'
        self.logrotate_d = '/etc/logrotate.d'

    def get_logrotate_configs(self):
        """Parse logrotate configuration files."""
        configs = []
        if os.path.isfile(self.logrotate_conf):
            try:
                with open(self.logrotate_conf, 'r') as f:
                    configs.append({
                        'file': self.logrotate_conf,
                        'content': f.read(),
                    })
            except PermissionError:
                pass

        if os.path.isdir(self.logrotate_d):
            try:
                for fname in sorted(os.listdir(self.logrotate_d)):
                    fpath = os.path.join(self.logrotate_d, fname)
                    if os.path.isfile(fpath):
                        try:
                            with open(fpath, 'r') as f:
                                configs.append({
                                    'file': fpath,
                                    'content': f.read(),
                                })
                        except PermissionError:
                            pass
            except PermissionError:
                pass
        return configs

    def parse_logrotate_entries(self):
        """Extract logrotate entries with their settings."""
        entries = []
        for config in self.get_logrotate_configs():
            content = config['content']
            blocks = re.findall(r'(/\S+(?:\s+/\S+)*)\s*\{([^}]+)\}', content, re.DOTALL)
            for paths_str, body in blocks:
                paths = paths_str.split()
                settings = {}
                for line in body.strip().split('\n'):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split(None, 1)
                    settings[parts[0]] = parts[1] if len(parts) > 1 else True

                for path in paths:
                    entries.append({
                        'path': path,
                        'config_file': config['file'],
                        'rotate': settings.get('rotate', 'not set'),
                        'frequency': next((k for k in ['daily', 'weekly', 'monthly', 'yearly']
                                           if k in settings), 'not set'),
                        'compress': 'compress' in settings,
                        'missingok': 'missingok' in settings,
                        'notifempty': 'notifempty' in settings,
                        'maxsize': settings.get('maxsize', settings.get('size', 'not set')),
                        'settings': settings,
                    })
        return entries

    def scan_log_files(self, path=None):
        """Scan log files and return their sizes and ages."""
        scan_dirs = [path] if path else self.log_dirs
        logs = []
        for d in scan_dirs:
            if not os.path.isdir(d):
                continue
            for root, dirs, files in os.walk(d):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    try:
                        stat = os.stat(fpath)
                        age = time.time() - stat.st_mtime
                        logs.append({
                            'path': fpath,
                            'filename': fname,
                            'size': stat.st_size,
                            'size_human': _human_size(stat.st_size),
                            'modified': time.ctime(stat.st_mtime),
                            'age_days': int(age / 86400),
                            'is_compressed': fname.endswith(('.gz', '.bz2', '.xz', '.zst')),
                            'is_rotated': bool(re.search(r'\.\d+', fname)),
                        })
                    except (OSError, PermissionError):
                        continue
        logs.sort(key=lambda x: x['size'], reverse=True)
        return logs

    def find_large_logs(self, min_size_mb=50, path=None):
        """Find log files exceeding size threshold."""
        min_bytes = min_size_mb * 1024 * 1024
        return [l for l in self.scan_log_files(path) if l['size'] >= min_bytes]

    def find_unrotated(self, max_age_days=30, min_size_mb=10, path=None):
        """Find logs that appear unrotated (old and large)."""
        min_bytes = min_size_mb * 1024 * 1024
        return [l for l in self.scan_log_files(path)
                if l['age_days'] > max_age_days and l['size'] >= min_bytes and not l['is_rotated']]

    def log_dir_usage(self, path=None):
        """Get total log directory usage."""
        logs = self.scan_log_files(path)
        total = sum(l['size'] for l in logs)
        compressed = sum(l['size'] for l in logs if l['is_compressed'])
        uncompressed = total - compressed
        return {
            'total_files': len(logs),
            'total_size': total,
            'total_size_human': _human_size(total),
            'compressed_size': compressed,
            'compressed_size_human': _human_size(compressed),
            'uncompressed_size': uncompressed,
            'uncompressed_size_human': _human_size(uncompressed),
        }

    def audit(self):
        """Run log rotation audit."""
        issues = []
        large = self.find_large_logs(50)
        for l in large:
            issues.append({
                'severity': 'warning',
                'category': 'large_log',
                'message': f"Large log file: {l['path']} ({l['size_human']})",
            })

        unrotated = self.find_unrotated(30, 10)
        for u in unrotated:
            issues.append({
                'severity': 'warning',
                'category': 'unrotated',
                'message': f"Possibly unrotated: {u['path']} ({u['size_human']}, {u['age_days']} days old)",
            })

        return issues

    def print_report(self):
        """Print formatted log rotation report."""
        usage = self.log_dir_usage()
        entries = self.parse_logrotate_entries()
        issues = self.audit()
        logs = self.scan_log_files()

        print(f"\n{'='*60}")
        print(f"  Log Rotation Report")
        print(f"{'='*60}")
        print(f"  Total log files:   {usage['total_files']}")
        print(f"  Total size:        {usage['total_size_human']}")
        print(f"  Compressed:        {usage['compressed_size_human']}")
        print(f"  Uncompressed:      {usage['uncompressed_size_human']}")

        if entries:
            print(f"\n  Logrotate Configs ({len(entries)}):")
            for e in entries[:15]:
                freq = e['frequency']
                comp = 'compressed' if e['compress'] else 'uncompressed'
                print(f"    {e['path'][:40]:40s} {freq:8s} rotate:{e['rotate']} {comp}")

        if logs:
            print(f"\n  Largest Log Files:")
            for l in logs[:10]:
                print(f"    {l['size_human']:>10}  {l['age_days']:>4}d  {l['path']}")

        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in issues:
                print(f"    [{i['severity'].upper()}] {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  Linux eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")

    def to_json(self):
        """Return log rotation info as JSON."""
        return json.dumps({
            'usage': self.log_dir_usage(),
            'configs': len(self.parse_logrotate_entries()),
            'issues': self.audit(),
            'top_files': self.scan_log_files()[:20],
        }, indent=2)


__all__ = ["LogRotateAudit"]
