"""
dargslan-security-scan — Linux Security Scanner

Basic security scanner: SSH config, file permissions, SUID binaries,
world-writable files, kernel parameters, and more.
Zero external dependencies.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import os
import stat
import subprocess
import json
import re


class SecurityScanner:
    """Basic Linux security scanner."""

    def check_ssh_config(self):
        """Check SSH server configuration for security issues."""
        issues = []
        ssh_config = '/etc/ssh/sshd_config'
        if not os.path.isfile(ssh_config):
            return [{'check': 'ssh_config', 'severity': 'info', 'message': 'sshd_config not found'}]

        try:
            with open(ssh_config, 'r') as f:
                content = f.read()

            checks = {
                'PermitRootLogin': {'bad': ['yes'], 'message': 'Root login is permitted'},
                'PasswordAuthentication': {'bad': ['yes'], 'message': 'Password authentication enabled (key-only recommended)'},
                'PermitEmptyPasswords': {'bad': ['yes'], 'message': 'Empty passwords are permitted'},
                'X11Forwarding': {'bad': ['yes'], 'message': 'X11 forwarding enabled'},
                'MaxAuthTries': {'max': 6, 'message': 'MaxAuthTries is high'},
            }

            for key, check in checks.items():
                match = re.search(rf'^{key}\s+(\S+)', content, re.MULTILINE | re.IGNORECASE)
                if match:
                    val = match.group(1).lower()
                    if 'bad' in check and val in check['bad']:
                        issues.append({
                            'check': f'ssh_{key}',
                            'severity': 'warning',
                            'message': check['message'],
                            'current': val,
                        })
                    if 'max' in check:
                        try:
                            if int(val) > check['max']:
                                issues.append({
                                    'check': f'ssh_{key}',
                                    'severity': 'info',
                                    'message': f"{check['message']} ({val})",
                                    'current': val,
                                })
                        except ValueError:
                            pass

            port_match = re.search(r'^Port\s+(\d+)', content, re.MULTILINE)
            if port_match and port_match.group(1) == '22':
                issues.append({
                    'check': 'ssh_port',
                    'severity': 'info',
                    'message': 'SSH running on default port 22',
                })

        except PermissionError:
            issues.append({'check': 'ssh_config', 'severity': 'error', 'message': 'Cannot read sshd_config (permission denied)'})

        if not issues:
            issues.append({'check': 'ssh_config', 'severity': 'ok', 'message': 'SSH configuration looks good'})
        return issues

    def find_suid_files(self, paths=None):
        """Find SUID/SGID binaries."""
        if paths is None:
            paths = ['/usr/bin', '/usr/sbin', '/usr/local/bin', '/usr/local/sbin']
        suid_files = []
        known_suid = {'sudo', 'su', 'passwd', 'chsh', 'chfn', 'mount', 'umount',
                      'ping', 'newgrp', 'gpasswd', 'pkexec', 'crontab'}

        for search_path in paths:
            if not os.path.isdir(search_path):
                continue
            try:
                for fname in os.listdir(search_path):
                    fpath = os.path.join(search_path, fname)
                    try:
                        st = os.stat(fpath)
                        mode = st.st_mode
                        if mode & stat.S_ISUID or mode & stat.S_ISGID:
                            suid_files.append({
                                'path': fpath,
                                'mode': oct(mode)[-4:],
                                'suid': bool(mode & stat.S_ISUID),
                                'sgid': bool(mode & stat.S_ISGID),
                                'known': fname in known_suid,
                                'owner_uid': st.st_uid,
                            })
                    except (OSError, PermissionError):
                        continue
            except PermissionError:
                continue
        return suid_files

    def find_world_writable(self, paths=None):
        """Find world-writable files and directories."""
        if paths is None:
            paths = ['/etc', '/var']
        writable = []
        for search_path in paths:
            if not os.path.isdir(search_path):
                continue
            for root, dirs, files in os.walk(search_path):
                for name in files + dirs:
                    fpath = os.path.join(root, name)
                    try:
                        st = os.stat(fpath)
                        if st.st_mode & stat.S_IWOTH:
                            if not os.path.islink(fpath):
                                writable.append({
                                    'path': fpath,
                                    'mode': oct(st.st_mode)[-4:],
                                    'is_dir': os.path.isdir(fpath),
                                    'has_sticky': bool(st.st_mode & stat.S_ISVTX),
                                })
                    except (OSError, PermissionError):
                        continue
        return writable

    def check_kernel_params(self):
        """Check security-related kernel parameters."""
        params = {
            'net.ipv4.ip_forward': {'secure': '0', 'message': 'IP forwarding enabled'},
            'net.ipv4.conf.all.accept_redirects': {'secure': '0', 'message': 'ICMP redirects accepted'},
            'net.ipv4.conf.all.send_redirects': {'secure': '0', 'message': 'ICMP redirects sent'},
            'net.ipv4.conf.all.accept_source_route': {'secure': '0', 'message': 'Source routing accepted'},
            'net.ipv4.conf.all.log_martians': {'secure': '1', 'message': 'Martian packets not logged'},
            'net.ipv4.tcp_syncookies': {'secure': '1', 'message': 'SYN cookies disabled'},
            'kernel.randomize_va_space': {'secure': '2', 'message': 'ASLR not fully enabled'},
        }
        results = []
        for param, check in params.items():
            path = '/proc/sys/' + param.replace('.', '/')
            try:
                with open(path, 'r') as f:
                    value = f.read().strip()
                    secure = value == check['secure']
                    results.append({
                        'param': param,
                        'value': value,
                        'expected': check['secure'],
                        'secure': secure,
                        'message': check['message'] if not secure else 'OK',
                        'severity': 'warning' if not secure else 'ok',
                    })
            except (FileNotFoundError, PermissionError):
                pass
        return results

    def check_important_perms(self):
        """Check permissions on important files."""
        files_to_check = {
            '/etc/passwd': '0644',
            '/etc/shadow': '0640',
            '/etc/group': '0644',
            '/etc/gshadow': '0640',
            '/etc/ssh/sshd_config': '0600',
            '/etc/crontab': '0644',
        }
        issues = []
        for fpath, expected in files_to_check.items():
            if not os.path.exists(fpath):
                continue
            try:
                actual = oct(os.stat(fpath).st_mode)[-4:]
                if actual != expected:
                    issues.append({
                        'file': fpath,
                        'expected': expected,
                        'actual': actual,
                        'severity': 'warning',
                        'message': f"{fpath} has mode {actual} (expected {expected})",
                    })
            except PermissionError:
                pass
        return issues

    def full_scan(self):
        """Run all security checks."""
        return {
            'ssh': self.check_ssh_config(),
            'suid': self.find_suid_files(),
            'world_writable': self.find_world_writable(),
            'kernel': self.check_kernel_params(),
            'permissions': self.check_important_perms(),
        }

    def score(self):
        """Calculate a simple security score (0-100)."""
        total = 0
        passed = 0

        ssh = self.check_ssh_config()
        total += len(ssh)
        passed += sum(1 for i in ssh if i['severity'] == 'ok')

        kernel = self.check_kernel_params()
        total += len(kernel)
        passed += sum(1 for k in kernel if k['secure'])

        perms = self.check_important_perms()
        total += max(len(perms), 1)
        if not perms:
            passed += 1

        suid = self.find_suid_files()
        unknown = [s for s in suid if not s['known']]
        total += 1
        if not unknown:
            passed += 1

        return round((passed / total) * 100) if total > 0 else 0

    def print_report(self):
        """Print formatted security scan report."""
        ssh = self.check_ssh_config()
        suid = self.find_suid_files()
        kernel = self.check_kernel_params()
        perms = self.check_important_perms()
        sc = self.score()

        print(f"\n{'='*60}")
        print(f"  Security Scan Report — Score: {sc}/100")
        print(f"{'='*60}")

        print(f"\n  SSH Configuration:")
        for i in ssh:
            icon = '[OK]' if i['severity'] == 'ok' else '[!!]'
            print(f"    {icon} {i['message']}")

        print(f"\n  Kernel Parameters:")
        for k in kernel:
            icon = '[OK]' if k['secure'] else '[!!]'
            print(f"    {icon} {k['param']} = {k['value']} (expected: {k['expected']})")

        if perms:
            print(f"\n  File Permission Issues:")
            for p in perms:
                print(f"    [!!] {p['message']}")
        else:
            print(f"\n  File Permissions: [OK] All checked files have correct permissions")

        unknown_suid = [s for s in suid if not s['known']]
        if unknown_suid:
            print(f"\n  Unknown SUID/SGID Binaries ({len(unknown_suid)}):")
            for s in unknown_suid[:10]:
                flags = []
                if s['suid']:
                    flags.append('SUID')
                if s['sgid']:
                    flags.append('SGID')
                print(f"    [!!] {s['path']} ({', '.join(flags)}) mode:{s['mode']}")
        else:
            print(f"\n  SUID/SGID: [OK] Only known system binaries found ({len(suid)} total)")

        print(f"\n{'='*60}")
        print(f"  More security tools: https://dargslan.com")
        print(f"  Linux eBooks: https://dargslan.com/books")
        print(f"  Cheat Sheets: https://dargslan.com/cheat-sheets")
        print(f"{'='*60}\n")

    def to_json(self):
        """Return security scan as JSON."""
        result = self.full_scan()
        result['score'] = self.score()
        return json.dumps(result, indent=2)


__all__ = ["SecurityScanner"]
