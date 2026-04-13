"""
dargslan-journald-analyzer — Systemd Journal Log Analyzer

Find boot errors, service failures, kernel warnings, and security events.
Zero external dependencies — uses journalctl CLI.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import subprocess
import json
import re
from datetime import datetime


class JournaldAnalyzer:
    """Analyze systemd journal logs for issues."""

    def __init__(self):
        pass

    def _run_journalctl(self, args):
        try:
            cmd = ['journalctl', '--no-pager'] + args
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout.strip() if result.returncode == 0 else ''
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ''

    def get_boot_errors(self, boot=0):
        output = self._run_journalctl(['-b', str(boot), '-p', 'err', '--output=short-precise'])
        errors = []
        for line in output.split('\n'):
            if line.strip():
                errors.append(line.strip())
        return errors

    def get_service_failures(self):
        output = self._run_journalctl(['-b', '0', '-p', 'err', '-u', '*.service', '--output=short'])
        failures = []
        for line in output.split('\n'):
            if line.strip() and ('failed' in line.lower() or 'error' in line.lower()):
                failures.append(line.strip())
        return failures

    def get_kernel_warnings(self, boot=0):
        output = self._run_journalctl(['-b', str(boot), '-k', '-p', 'warning', '--output=short'])
        warnings = []
        for line in output.split('\n'):
            if line.strip():
                warnings.append(line.strip())
        return warnings

    def get_security_events(self):
        output = self._run_journalctl(['-b', '0', '--output=short', '-g',
            'authentication failure|Failed password|session opened|session closed|sudo|segfault|COMMAND='])
        events = []
        for line in output.split('\n'):
            if line.strip():
                event_type = 'unknown'
                if 'Failed password' in line or 'authentication failure' in line:
                    event_type = 'auth_failure'
                elif 'session opened' in line:
                    event_type = 'login'
                elif 'sudo' in line or 'COMMAND=' in line:
                    event_type = 'sudo'
                elif 'segfault' in line:
                    event_type = 'crash'
                events.append({'type': event_type, 'line': line.strip()})
        return events

    def get_disk_usage(self):
        output = self._run_journalctl(['--disk-usage'])
        return output

    def get_boot_list(self):
        output = self._run_journalctl(['--list-boots', '--no-pager'])
        boots = []
        for line in output.split('\n'):
            if line.strip():
                boots.append(line.strip())
        return boots

    def get_failed_units(self):
        try:
            result = subprocess.run(['systemctl', '--failed', '--no-pager', '--no-legend'],
                                   capture_output=True, text=True, timeout=10)
            units = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if parts:
                        units.append({'unit': parts[0], 'line': line.strip()})
            return units
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []

    def get_oom_kills(self, boot=0):
        output = self._run_journalctl(['-b', str(boot), '-k', '-g', 'oom-kill|Out of memory|Killed process'])
        kills = []
        for line in output.split('\n'):
            if line.strip():
                kills.append(line.strip())
        return kills

    def get_recent_critical(self, hours=24):
        output = self._run_journalctl([f'--since={hours} hours ago', '-p', 'crit', '--output=short'])
        lines = []
        for line in output.split('\n'):
            if line.strip():
                lines.append(line.strip())
        return lines

    def audit(self):
        issues = []
        errors = self.get_boot_errors()
        if len(errors) > 20:
            issues.append({'severity': 'warning', 'message': f'{len(errors)} boot errors in current session'})

        failed = self.get_failed_units()
        if failed:
            issues.append({'severity': 'critical', 'message': f'{len(failed)} systemd units in failed state'})
            for u in failed[:5]:
                issues.append({'severity': 'high', 'message': f"Failed unit: {u['unit']}"})

        oom = self.get_oom_kills()
        if oom:
            issues.append({'severity': 'critical', 'message': f'{len(oom)} OOM kills detected this boot'})

        critical = self.get_recent_critical(hours=24)
        if critical:
            issues.append({'severity': 'critical', 'message': f'{len(critical)} critical log entries in last 24h'})

        kernel_warns = self.get_kernel_warnings()
        if len(kernel_warns) > 50:
            issues.append({'severity': 'info', 'message': f'{len(kernel_warns)} kernel warnings this boot'})

        return issues

    def print_report(self):
        errors = self.get_boot_errors()
        failed = self.get_failed_units()
        oom = self.get_oom_kills()
        issues = self.audit()
        disk = self.get_disk_usage()

        print(f"\n{'='*60}")
        print(f"  Systemd Journal Analysis Report")
        print(f"{'='*60}")
        print(f"\n  Boot Errors: {len(errors)}")
        print(f"  Failed Units: {len(failed)}")
        print(f"  OOM Kills: {len(oom)}")
        print(f"  Journal Disk: {disk}")

        if failed:
            print(f"\n  Failed Units:")
            for u in failed[:10]:
                print(f"    [!!] {u['unit']}")

        if oom:
            print(f"\n  OOM Kills:")
            for o in oom[:5]:
                print(f"    {o}")

        if errors:
            print(f"\n  Recent Errors (last 10):")
            for e in errors[-10:]:
                print(f"    {e[:100]}")

        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in issues:
                print(f"    [{i['severity'].upper():8s}] {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["JournaldAnalyzer"]
