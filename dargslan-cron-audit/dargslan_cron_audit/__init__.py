"""
dargslan-cron-audit — Linux Crontab Auditor

Audit crontab entries, detect issues, validate schedules.
Zero external dependencies.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import os
import subprocess
import json
import re


class CronAudit:
    """Audit and analyze crontab entries on Linux."""

    SCHEDULE_LABELS = {
        '@reboot': 'At system boot',
        '@yearly': 'Once a year (Jan 1, 00:00)',
        '@annually': 'Once a year (Jan 1, 00:00)',
        '@monthly': 'Once a month (1st, 00:00)',
        '@weekly': 'Once a week (Sunday, 00:00)',
        '@daily': 'Once a day (00:00)',
        '@midnight': 'Once a day (00:00)',
        '@hourly': 'Once an hour (:00)',
    }

    def get_user_crontab(self, user=None):
        """Get crontab entries for a user (current user if None)."""
        try:
            cmd = ['crontab', '-l']
            if user:
                cmd = ['crontab', '-l', '-u', user]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return []
            return self._parse_crontab(result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def get_system_crontabs(self):
        """Get all system crontab files."""
        entries = []
        cron_dirs = ['/etc/cron.d', '/etc/cron.daily', '/etc/cron.hourly',
                     '/etc/cron.weekly', '/etc/cron.monthly']

        if os.path.isfile('/etc/crontab'):
            try:
                with open('/etc/crontab', 'r') as f:
                    parsed = self._parse_crontab(f.read(), system=True)
                    for e in parsed:
                        e['source'] = '/etc/crontab'
                    entries.extend(parsed)
            except PermissionError:
                pass

        for cron_dir in cron_dirs:
            if os.path.isdir(cron_dir):
                try:
                    for fname in os.listdir(cron_dir):
                        fpath = os.path.join(cron_dir, fname)
                        if os.path.isfile(fpath) and not fname.startswith('.'):
                            try:
                                with open(fpath, 'r') as f:
                                    parsed = self._parse_crontab(f.read(), system=True)
                                    for e in parsed:
                                        e['source'] = fpath
                                    entries.extend(parsed)
                            except PermissionError:
                                pass
                except PermissionError:
                    pass

        return entries

    def _parse_crontab(self, content, system=False):
        """Parse crontab content into structured entries."""
        entries = []
        for line_num, line in enumerate(content.strip().split('\n'), 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if '=' in line and not any(line.startswith(s) for s in ['*', '@'] + [str(i) for i in range(10)]):
                continue

            entry = self._parse_line(line, line_num, system)
            if entry:
                entries.append(entry)
        return entries

    def _parse_line(self, line, line_num, system=False):
        """Parse a single crontab line."""
        for special, desc in self.SCHEDULE_LABELS.items():
            if line.startswith(special):
                rest = line[len(special):].strip()
                if system:
                    parts = rest.split(None, 1)
                    user = parts[0] if parts else 'root'
                    command = parts[1] if len(parts) > 1 else ''
                else:
                    user = None
                    command = rest
                return {
                    'line': line_num,
                    'schedule': special,
                    'schedule_human': desc,
                    'command': command,
                    'user': user,
                    'raw': line,
                }

        parts = line.split(None, 5 if not system else 6)
        if len(parts) < (6 if not system else 7):
            return None

        schedule = ' '.join(parts[:5])
        if system:
            user = parts[5]
            command = parts[6] if len(parts) > 6 else ''
        else:
            user = None
            command = parts[5]

        return {
            'line': line_num,
            'schedule': schedule,
            'schedule_human': self._describe_schedule(schedule),
            'command': command,
            'user': user,
            'raw': line,
        }

    def _describe_schedule(self, schedule):
        """Human-readable description of a cron schedule."""
        parts = schedule.split()
        if len(parts) != 5:
            return schedule

        minute, hour, dom, month, dow = parts

        if schedule == '* * * * *':
            return 'Every minute'
        if schedule == '*/5 * * * *':
            return 'Every 5 minutes'
        if schedule == '*/15 * * * *':
            return 'Every 15 minutes'
        if schedule == '0 * * * *':
            return 'Every hour'
        if schedule == '0 0 * * *':
            return 'Daily at midnight'
        if schedule == '0 0 * * 0':
            return 'Weekly (Sunday midnight)'
        if schedule == '0 0 1 * *':
            return 'Monthly (1st at midnight)'

        desc = []
        if minute != '*':
            desc.append(f"min:{minute}")
        if hour != '*':
            desc.append(f"hour:{hour}")
        if dom != '*':
            desc.append(f"day:{dom}")
        if month != '*':
            desc.append(f"month:{month}")
        if dow != '*':
            desc.append(f"dow:{dow}")
        return ', '.join(desc) if desc else 'Custom schedule'

    def audit(self, entries=None):
        """Audit crontab entries for potential issues."""
        if entries is None:
            entries = self.get_user_crontab() + self.get_system_crontabs()

        issues = []
        for entry in entries:
            cmd = entry.get('command', '')

            if '>' not in cmd and '|' not in cmd and 'logger' not in cmd:
                issues.append({
                    'severity': 'warning',
                    'entry': entry,
                    'message': 'No output redirection — cron mail may accumulate',
                })

            if cmd.startswith('/') or cmd.startswith('~'):
                bin_path = cmd.split()[0]
                if not os.path.exists(bin_path) and bin_path.startswith('/'):
                    issues.append({
                        'severity': 'error',
                        'entry': entry,
                        'message': f'Command not found: {bin_path}',
                    })

            if entry.get('schedule') == '* * * * *':
                issues.append({
                    'severity': 'warning',
                    'entry': entry,
                    'message': 'Runs every minute — high frequency job',
                })

            if entry.get('user') == 'root':
                issues.append({
                    'severity': 'info',
                    'entry': entry,
                    'message': 'Runs as root — ensure this is intentional',
                })

            if 'rm -rf' in cmd or 'rm -r /' in cmd:
                issues.append({
                    'severity': 'critical',
                    'entry': entry,
                    'message': 'Dangerous recursive delete detected',
                })

            if 'chmod 777' in cmd:
                issues.append({
                    'severity': 'warning',
                    'entry': entry,
                    'message': 'chmod 777 — overly permissive permissions',
                })

        return issues

    def print_report(self):
        """Print formatted cron audit report."""
        user_entries = self.get_user_crontab()
        sys_entries = self.get_system_crontabs()
        all_entries = user_entries + sys_entries
        issues = self.audit(all_entries)

        print(f"\n{'='*60}")
        print(f"  Cron Audit Report")
        print(f"{'='*60}")
        print(f"  User crontab entries: {len(user_entries)}")
        print(f"  System crontab entries: {len(sys_entries)}")
        print(f"  Total: {len(all_entries)}")

        if all_entries:
            print(f"\n  Entries:")
            for e in all_entries:
                src = f" [{e.get('source', 'user')}]" if e.get('source') else ''
                user = f" (as {e['user']})" if e.get('user') else ''
                print(f"    {e['schedule_human']}: {e['command'][:60]}{user}{src}")

        if issues:
            critical = [i for i in issues if i['severity'] == 'critical']
            errors = [i for i in issues if i['severity'] == 'error']
            warnings = [i for i in issues if i['severity'] == 'warning']

            print(f"\n  Issues Found: {len(issues)}")
            if critical:
                print(f"    [CRITICAL] {len(critical)}")
                for i in critical:
                    print(f"      ! {i['message']}: {i['entry']['command'][:50]}")
            if errors:
                print(f"    [ERROR] {len(errors)}")
                for i in errors:
                    print(f"      x {i['message']}")
            if warnings:
                print(f"    [WARNING] {len(warnings)}")
                for i in warnings:
                    print(f"      ~ {i['message']}")
        else:
            print(f"\n  No issues found.")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  Linux eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")

    def to_json(self):
        """Return cron audit as JSON."""
        entries = self.get_user_crontab() + self.get_system_crontabs()
        return json.dumps({
            'entries': entries,
            'issues': self.audit(entries),
            'total': len(entries),
        }, indent=2)


__all__ = ["CronAudit"]
