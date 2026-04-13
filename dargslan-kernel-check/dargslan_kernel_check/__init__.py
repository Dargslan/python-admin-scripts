"""
dargslan-kernel-check — Linux Kernel Parameter Checker

Audit sysctl hardening, compare live vs saved settings, and security recommendations.
Zero external dependencies — uses only Python standard library.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import os
import json
import subprocess


class KernelCheck:
    """Audit Linux kernel parameters for security hardening."""

    SECURITY_PARAMS = {
        'net.ipv4.ip_forward': {'recommended': '0', 'description': 'IP forwarding (disable unless router)', 'severity': 'warning'},
        'net.ipv4.conf.all.accept_redirects': {'recommended': '0', 'description': 'ICMP redirects', 'severity': 'warning'},
        'net.ipv4.conf.default.accept_redirects': {'recommended': '0', 'description': 'Default ICMP redirects', 'severity': 'warning'},
        'net.ipv4.conf.all.send_redirects': {'recommended': '0', 'description': 'Send ICMP redirects', 'severity': 'warning'},
        'net.ipv4.conf.all.accept_source_route': {'recommended': '0', 'description': 'Source routing', 'severity': 'warning'},
        'net.ipv4.conf.all.log_martians': {'recommended': '1', 'description': 'Log martian packets', 'severity': 'info'},
        'net.ipv4.icmp_echo_ignore_broadcasts': {'recommended': '1', 'description': 'Ignore broadcast pings', 'severity': 'warning'},
        'net.ipv4.icmp_ignore_bogus_error_responses': {'recommended': '1', 'description': 'Ignore bogus ICMP errors', 'severity': 'info'},
        'net.ipv4.tcp_syncookies': {'recommended': '1', 'description': 'SYN flood protection', 'severity': 'critical'},
        'net.ipv4.conf.all.rp_filter': {'recommended': '1', 'description': 'Reverse path filtering', 'severity': 'warning'},
        'net.ipv4.conf.default.rp_filter': {'recommended': '1', 'description': 'Default reverse path filtering', 'severity': 'warning'},
        'kernel.randomize_va_space': {'recommended': '2', 'description': 'ASLR (Address Space Layout Randomization)', 'severity': 'critical'},
        'kernel.exec-shield': {'recommended': '1', 'description': 'Exec-Shield protection', 'severity': 'warning'},
        'kernel.sysrq': {'recommended': '0', 'description': 'Magic SysRq key (disable in production)', 'severity': 'info'},
        'kernel.core_uses_pid': {'recommended': '1', 'description': 'Core dumps with PID', 'severity': 'info'},
        'kernel.dmesg_restrict': {'recommended': '1', 'description': 'Restrict dmesg access', 'severity': 'warning'},
        'kernel.kptr_restrict': {'recommended': '2', 'description': 'Restrict kernel pointer access', 'severity': 'warning'},
        'net.ipv6.conf.all.accept_redirects': {'recommended': '0', 'description': 'IPv6 ICMP redirects', 'severity': 'warning'},
        'net.ipv6.conf.default.accept_redirects': {'recommended': '0', 'description': 'IPv6 default ICMP redirects', 'severity': 'warning'},
        'fs.suid_dumpable': {'recommended': '0', 'description': 'SUID core dumps', 'severity': 'warning'},
    }

    def __init__(self):
        pass

    def _get_sysctl(self, param):
        path = f'/proc/sys/{param.replace(".", "/")}'
        try:
            with open(path, 'r') as f:
                return f.read().strip()
        except (FileNotFoundError, PermissionError):
            return None

    def get_kernel_version(self):
        """Get running kernel version."""
        try:
            with open('/proc/version', 'r') as f:
                return f.read().strip()
        except (FileNotFoundError, PermissionError):
            return 'unknown'

    def check_all_params(self):
        """Check all security-relevant kernel parameters."""
        results = []
        for param, config in self.SECURITY_PARAMS.items():
            current = self._get_sysctl(param)
            if current is None: continue
            compliant = current == config['recommended']
            results.append({
                'param': param,
                'current': current,
                'recommended': config['recommended'],
                'compliant': compliant,
                'description': config['description'],
                'severity': config['severity'],
            })
        return results

    def get_saved_settings(self):
        """Read sysctl settings from config files."""
        saved = {}
        config_files = ['/etc/sysctl.conf']
        sysctl_d = '/etc/sysctl.d'
        if os.path.isdir(sysctl_d):
            for f in sorted(os.listdir(sysctl_d)):
                if f.endswith('.conf'):
                    config_files.append(os.path.join(sysctl_d, f))

        for conf_file in config_files:
            try:
                with open(conf_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, _, value = line.partition('=')
                            saved[key.strip()] = {'value': value.strip(), 'file': conf_file}
            except (FileNotFoundError, PermissionError):
                continue
        return saved

    def compare_live_vs_saved(self):
        """Compare live sysctl values with saved config."""
        saved = self.get_saved_settings()
        diffs = []
        for param, config in saved.items():
            live = self._get_sysctl(param)
            if live is not None and live != config['value']:
                diffs.append({
                    'param': param,
                    'live': live,
                    'saved': config['value'],
                    'file': config['file'],
                })
        return diffs

    def get_score(self):
        """Calculate security hardening score."""
        results = self.check_all_params()
        if not results: return 0
        compliant = sum(1 for r in results if r['compliant'])
        return round(compliant / len(results) * 100)

    def audit(self):
        """Run kernel security audit."""
        issues = []
        results = self.check_all_params()
        for r in results:
            if not r['compliant']:
                issues.append({
                    'severity': r['severity'],
                    'param': r['param'],
                    'message': f"{r['description']}: current={r['current']}, recommended={r['recommended']}",
                })

        diffs = self.compare_live_vs_saved()
        for d in diffs:
            issues.append({
                'severity': 'info',
                'param': d['param'],
                'message': f"Live ({d['live']}) differs from saved ({d['saved']}) in {d['file']}",
            })

        return issues

    def print_report(self):
        """Print formatted kernel audit report."""
        results = self.check_all_params()
        score = self.get_score()
        issues = self.audit()

        print(f"\n{'='*60}")
        print(f"  Kernel Security Hardening Report")
        print(f"  Score: {score}/100")
        print(f"{'='*60}")

        for r in results:
            icon = '[OK]' if r['compliant'] else '[!!]'
            print(f"  {icon} {r['param']}: {r['current']} (rec: {r['recommended']})")

        diffs = self.compare_live_vs_saved()
        if diffs:
            print(f"\n  Live vs Saved Differences ({len(diffs)}):")
            for d in diffs:
                print(f"    {d['param']}: live={d['live']}, saved={d['saved']}")

        if issues:
            non_compliant = [i for i in issues if i['severity'] != 'info']
            if non_compliant:
                print(f"\n  Non-compliant ({len(non_compliant)}):")
                for i in sorted(non_compliant, key=lambda x: {'critical':0,'high':1,'warning':2}.get(x['severity'],3)):
                    print(f"    [{i['severity'].upper():8s}] {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["KernelCheck"]
