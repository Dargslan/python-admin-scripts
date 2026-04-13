"""
dargslan-package-audit — Linux Package Auditor

Find outdated, security-pending, and orphaned packages on apt/dnf/pacman systems.
Zero external dependencies — uses only Python standard library.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import subprocess
import os
import json
import re


class PackageAudit:
    """Audit installed Linux packages for security and maintenance."""

    def __init__(self, manager=None):
        self.manager = manager or self._detect_manager()

    def _detect_manager(self):
        for mgr, cmd in [('apt', 'apt'), ('dnf', 'dnf'), ('yum', 'yum'), ('pacman', 'pacman'), ('zypper', 'zypper'), ('apk', 'apk')]:
            try:
                subprocess.run([cmd, '--version'], capture_output=True, timeout=5)
                return mgr
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        return 'unknown'

    def _run(self, args):
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=60)
            return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ''

    def count_installed(self):
        """Count total installed packages."""
        if self.manager == 'apt':
            output = self._run(['dpkg', '-l'])
            return len([l for l in output.split('\n') if l.startswith('ii')])
        elif self.manager in ('dnf', 'yum'):
            output = self._run(['rpm', '-qa'])
            return len([l for l in output.split('\n') if l.strip()])
        elif self.manager == 'pacman':
            output = self._run(['pacman', '-Q'])
            return len([l for l in output.split('\n') if l.strip()])
        elif self.manager == 'apk':
            output = self._run(['apk', 'list', '--installed'])
            return len([l for l in output.split('\n') if l.strip()])
        return 0

    def check_upgradable(self):
        """Find packages with available updates."""
        packages = []
        if self.manager == 'apt':
            output = self._run(['apt', 'list', '--upgradable'])
            for line in output.split('\n'):
                if '/' in line and 'Listing' not in line:
                    name = line.split('/')[0]
                    packages.append({'name': name, 'line': line.strip()})
        elif self.manager in ('dnf', 'yum'):
            output = self._run([self.manager, 'check-update', '-q'])
            for line in output.split('\n'):
                parts = line.split()
                if len(parts) >= 2 and not line.startswith('Last') and not line.startswith('Obsoleting'):
                    packages.append({'name': parts[0], 'version': parts[1] if len(parts) > 1 else ''})
        elif self.manager == 'pacman':
            output = self._run(['pacman', '-Qu'])
            for line in output.split('\n'):
                parts = line.split()
                if len(parts) >= 4:
                    packages.append({'name': parts[0], 'current': parts[1], 'available': parts[3]})
        return packages

    def check_security_updates(self):
        """Find packages with security updates."""
        packages = []
        if self.manager == 'apt':
            output = self._run(['apt', 'list', '--upgradable'])
            for line in output.split('\n'):
                if 'security' in line.lower():
                    name = line.split('/')[0] if '/' in line else line.split()[0]
                    packages.append({'name': name, 'type': 'security'})
        elif self.manager in ('dnf', 'yum'):
            output = self._run([self.manager, 'updateinfo', 'list', 'security', '-q'])
            for line in output.split('\n'):
                parts = line.split()
                if len(parts) >= 3:
                    packages.append({'name': parts[-1], 'advisory': parts[0], 'severity': parts[1] if len(parts) > 2 else ''})
        return packages

    def check_auto_removable(self):
        """Find orphaned/auto-removable packages."""
        packages = []
        if self.manager == 'apt':
            output = self._run(['apt', 'autoremove', '--dry-run'])
            for line in output.split('\n'):
                if line.strip().startswith('Remv '):
                    name = line.split()[1]
                    packages.append({'name': name})
        elif self.manager in ('dnf', 'yum'):
            output = self._run([self.manager, 'autoremove', '--assumeno'])
            capturing = False
            for line in output.split('\n'):
                if 'Removing:' in line: capturing = True; continue
                if capturing and line.strip() and not line.startswith('Transaction') and not line.startswith('Is this'):
                    parts = line.split()
                    if parts: packages.append({'name': parts[0]})
        elif self.manager == 'pacman':
            output = self._run(['pacman', '-Qdtq'])
            for line in output.split('\n'):
                if line.strip(): packages.append({'name': line.strip()})
        return packages

    def audit(self):
        """Run full package audit."""
        issues = []
        upgradable = self.check_upgradable()
        security = self.check_security_updates()
        removable = self.check_auto_removable()

        if security:
            issues.append({'severity': 'critical', 'message': f'{len(security)} security updates available'})
        if len(upgradable) > 50:
            issues.append({'severity': 'warning', 'message': f'{len(upgradable)} packages need updating'})
        elif upgradable:
            issues.append({'severity': 'info', 'message': f'{len(upgradable)} packages can be updated'})
        if len(removable) > 10:
            issues.append({'severity': 'info', 'message': f'{len(removable)} orphaned packages can be removed'})
        return issues

    def print_report(self):
        """Print formatted package audit report."""
        total = self.count_installed()
        upgradable = self.check_upgradable()
        security = self.check_security_updates()
        removable = self.check_auto_removable()
        issues = self.audit()

        print(f"\n{'='*60}")
        print(f"  Linux Package Audit Report")
        print(f"  Package Manager: {self.manager}")
        print(f"{'='*60}")
        print(f"\n  Installed Packages: {total}")
        print(f"  Upgradable: {len(upgradable)}")
        print(f"  Security Updates: {len(security)}")
        print(f"  Auto-removable: {len(removable)}")

        if security:
            print(f"\n  Security Updates:")
            for s in security[:10]:
                print(f"    [!!] {s['name']}")

        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in issues:
                print(f"    [{i['severity'].upper():8s}] {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["PackageAudit"]
