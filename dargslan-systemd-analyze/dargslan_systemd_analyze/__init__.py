"""
dargslan-systemd-analyze — Systemd Boot Time Analyzer

Measure service startup times, find slow units, and optimize boot performance.
Zero external dependencies — uses systemd-analyze CLI.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import subprocess
import re
import json


class SystemdAnalyze:
    """Analyze systemd boot performance."""

    def __init__(self):
        pass

    def _run(self, args):
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=30)
            return result.stdout.strip() if result.returncode == 0 else ''
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ''

    def get_boot_time(self):
        output = self._run(['systemd-analyze', 'time'])
        info = {'raw': output}
        match = re.search(r'Startup finished in (.+)', output)
        if match:
            info['summary'] = match.group(1)
            firmware = re.search(r'([\d.]+)s \(firmware\)', output)
            loader = re.search(r'([\d.]+)s \(loader\)', output)
            kernel = re.search(r'([\d.]+)s \(kernel\)', output)
            initrd = re.search(r'([\d.]+)s \(initrd\)', output)
            userspace = re.search(r'([\d.]+)s \(userspace\)', output)
            if firmware: info['firmware_sec'] = float(firmware.group(1))
            if loader: info['loader_sec'] = float(loader.group(1))
            if kernel: info['kernel_sec'] = float(kernel.group(1))
            if initrd: info['initrd_sec'] = float(initrd.group(1))
            if userspace: info['userspace_sec'] = float(userspace.group(1))
        return info

    def get_blame(self, limit=30):
        output = self._run(['systemd-analyze', 'blame', '--no-pager'])
        units = []
        for line in output.split('\n'):
            line = line.strip()
            if not line:
                continue
            match = re.match(r'([\d.]+)(min|s|ms)\s+(.+)', line)
            if match:
                value = float(match.group(1))
                unit_type = match.group(2)
                name = match.group(3).strip()
                if unit_type == 'min':
                    sec = value * 60
                elif unit_type == 'ms':
                    sec = value / 1000
                else:
                    sec = value
                units.append({'name': name, 'time_sec': round(sec, 3), 'time_raw': f"{match.group(1)}{unit_type}"})
        return units[:limit]

    def get_critical_chain(self):
        output = self._run(['systemd-analyze', 'critical-chain', '--no-pager'])
        return output

    def get_calendar_timers(self):
        output = self._run(['systemctl', 'list-timers', '--all', '--no-pager', '--no-legend'])
        timers = []
        for line in output.split('\n'):
            if line.strip():
                timers.append(line.strip())
        return timers

    def get_unit_dependencies(self, unit):
        output = self._run(['systemctl', 'list-dependencies', unit, '--no-pager'])
        return output

    def get_default_target(self):
        output = self._run(['systemctl', 'get-default'])
        return output

    def get_slow_units(self, threshold_sec=5.0):
        blame = self.get_blame(limit=100)
        return [u for u in blame if u['time_sec'] >= threshold_sec]

    def audit(self):
        issues = []
        boot = self.get_boot_time()

        total = boot.get('userspace_sec', 0) + boot.get('kernel_sec', 0) + boot.get('initrd_sec', 0)
        if total > 60:
            issues.append({'severity': 'warning', 'message': f'Total boot time is {total:.1f}s (over 60s)'})
        if boot.get('initrd_sec', 0) > 10:
            issues.append({'severity': 'info', 'message': f'initrd takes {boot["initrd_sec"]:.1f}s — consider optimizing initramfs'})

        slow = self.get_slow_units(threshold_sec=10.0)
        for u in slow[:5]:
            issues.append({'severity': 'warning', 'message': f"Slow unit: {u['name']} ({u['time_raw']})"})

        very_slow = self.get_slow_units(threshold_sec=30.0)
        for u in very_slow[:3]:
            issues.append({'severity': 'critical', 'message': f"Very slow unit: {u['name']} ({u['time_raw']})"})

        return issues

    def print_report(self):
        boot = self.get_boot_time()
        blame = self.get_blame(limit=15)
        chain = self.get_critical_chain()
        issues = self.audit()

        print(f"\n{'='*60}")
        print(f"  Systemd Boot Time Analysis")
        print(f"{'='*60}")

        if boot.get('summary'):
            print(f"\n  Boot Time: {boot['summary']}")
            if boot.get('kernel_sec'): print(f"    Kernel:    {boot['kernel_sec']:.1f}s")
            if boot.get('initrd_sec'): print(f"    initrd:    {boot['initrd_sec']:.1f}s")
            if boot.get('userspace_sec'): print(f"    Userspace: {boot['userspace_sec']:.1f}s")
        else:
            print(f"\n  {boot.get('raw', 'Unable to get boot time')}")

        if blame:
            print(f"\n  Slowest Units (top {len(blame)}):")
            for u in blame:
                bar = '#' * min(int(u['time_sec']), 40)
                print(f"    {u['time_raw']:>8s} {u['name'][:40]:<40s} {bar}")

        if chain:
            print(f"\n  Critical Chain:")
            for line in chain.split('\n')[:15]:
                print(f"    {line}")

        print(f"\n  Default Target: {self.get_default_target()}")

        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in issues:
                print(f"    [{i['severity'].upper():8s}] {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["SystemdAnalyze"]
