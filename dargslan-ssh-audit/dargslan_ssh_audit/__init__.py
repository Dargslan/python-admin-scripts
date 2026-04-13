"""
dargslan-ssh-audit — SSH Server Configuration Auditor

Audit SSH server configuration for security issues and best practices.
Zero external dependencies — uses only Python standard library.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import os
import re
import json
import subprocess


class SSHAudit:
    """Audit SSH server configuration for security issues."""

    WEAK_CIPHERS = ['3des-cbc', 'aes128-cbc', 'aes192-cbc', 'aes256-cbc', 'blowfish-cbc', 'cast128-cbc']
    WEAK_MACS = ['hmac-md5', 'hmac-sha1', 'hmac-md5-96', 'hmac-sha1-96']
    WEAK_KEX = ['diffie-hellman-group1-sha1', 'diffie-hellman-group14-sha1', 'diffie-hellman-group-exchange-sha1']

    def __init__(self, config_path=None):
        self.config_path = config_path or '/etc/ssh/sshd_config'

    def _read_config(self):
        try:
            with open(self.config_path, 'r') as f:
                return f.read()
        except (FileNotFoundError, PermissionError):
            return ''

    def _get_setting(self, config, key, default=None):
        match = re.search(rf'^\s*{key}\s+(.+)', config, re.MULTILINE | re.IGNORECASE)
        return match.group(1).strip() if match else default

    def check_root_login(self):
        config = self._read_config()
        value = self._get_setting(config, 'PermitRootLogin', 'prohibit-password')
        secure = value.lower() in ('no', 'prohibit-password', 'forced-commands-only')
        return {'setting': 'PermitRootLogin', 'value': value, 'secure': secure,
                'recommendation': 'Set to "no" or "prohibit-password"' if not secure else 'OK'}

    def check_password_auth(self):
        config = self._read_config()
        value = self._get_setting(config, 'PasswordAuthentication', 'yes')
        secure = value.lower() == 'no'
        return {'setting': 'PasswordAuthentication', 'value': value, 'secure': secure,
                'recommendation': 'Set to "no" — use key-based authentication' if not secure else 'OK'}

    def check_empty_passwords(self):
        config = self._read_config()
        value = self._get_setting(config, 'PermitEmptyPasswords', 'no')
        secure = value.lower() == 'no'
        return {'setting': 'PermitEmptyPasswords', 'value': value, 'secure': secure,
                'recommendation': 'Must be "no"' if not secure else 'OK'}

    def check_protocol(self):
        config = self._read_config()
        value = self._get_setting(config, 'Protocol', '2')
        secure = value.strip() == '2'
        return {'setting': 'Protocol', 'value': value, 'secure': secure,
                'recommendation': 'Set to "2" — SSHv1 is insecure' if not secure else 'OK'}

    def check_max_auth_tries(self):
        config = self._read_config()
        value = self._get_setting(config, 'MaxAuthTries', '6')
        tries = int(value) if value.isdigit() else 6
        secure = tries <= 4
        return {'setting': 'MaxAuthTries', 'value': value, 'secure': secure,
                'recommendation': 'Set to 3 or 4 to limit brute force' if not secure else 'OK'}

    def check_x11_forwarding(self):
        config = self._read_config()
        value = self._get_setting(config, 'X11Forwarding', 'no')
        secure = value.lower() == 'no'
        return {'setting': 'X11Forwarding', 'value': value, 'secure': secure,
                'recommendation': 'Disable unless required' if not secure else 'OK'}

    def check_ciphers(self):
        config = self._read_config()
        value = self._get_setting(config, 'Ciphers', '')
        if not value:
            return {'setting': 'Ciphers', 'value': 'default', 'weak': [], 'recommendation': 'Explicitly set strong ciphers'}
        ciphers = [c.strip() for c in value.split(',')]
        weak = [c for c in ciphers if c in self.WEAK_CIPHERS]
        return {'setting': 'Ciphers', 'value': value, 'weak': weak,
                'recommendation': f'Remove weak ciphers: {", ".join(weak)}' if weak else 'OK'}

    def check_macs(self):
        config = self._read_config()
        value = self._get_setting(config, 'MACs', '')
        if not value:
            return {'setting': 'MACs', 'value': 'default', 'weak': [], 'recommendation': 'Explicitly set strong MACs'}
        macs = [m.strip() for m in value.split(',')]
        weak = [m for m in macs if m in self.WEAK_MACS]
        return {'setting': 'MACs', 'value': value, 'weak': weak,
                'recommendation': f'Remove weak MACs: {", ".join(weak)}' if weak else 'OK'}

    def check_host_keys(self):
        config = self._read_config()
        keys = re.findall(r'^\s*HostKey\s+(.+)', config, re.MULTILINE)
        key_files = []
        for k in keys:
            k = k.strip()
            exists = os.path.exists(k)
            key_type = 'unknown'
            if 'ed25519' in k: key_type = 'ed25519'
            elif 'ecdsa' in k: key_type = 'ecdsa'
            elif 'rsa' in k: key_type = 'rsa'
            elif 'dsa' in k: key_type = 'dsa'
            key_files.append({'path': k, 'type': key_type, 'exists': exists, 'weak': key_type == 'dsa'})
        return key_files

    def check_authorized_keys(self):
        issues = []
        for user_dir in ['/root'] + [f'/home/{d}' for d in os.listdir('/home') if os.path.isdir(f'/home/{d}')]:
            ak_path = os.path.join(user_dir, '.ssh', 'authorized_keys')
            if os.path.exists(ak_path):
                try:
                    stat = os.stat(ak_path)
                    perms = oct(stat.st_mode)[-3:]
                    if perms not in ('600', '644', '400'):
                        issues.append({'file': ak_path, 'issue': f'Insecure permissions: {perms}', 'severity': 'warning'})
                    with open(ak_path, 'r') as f:
                        lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]
                        if len(lines) > 20:
                            issues.append({'file': ak_path, 'issue': f'Too many keys: {len(lines)}', 'severity': 'info'})
                        for line in lines:
                            if 'ssh-dss' in line:
                                issues.append({'file': ak_path, 'issue': 'DSA key found (deprecated)', 'severity': 'warning'})
                except PermissionError:
                    pass
        return issues

    def check_login_grace_time(self):
        config = self._read_config()
        value = self._get_setting(config, 'LoginGraceTime', '120')
        return {'setting': 'LoginGraceTime', 'value': value,
                'recommendation': 'Set to 60 or less' if value and int(re.sub(r'[^0-9]', '', value) or '120') > 60 else 'OK'}

    def audit(self):
        issues = []
        for check in [self.check_root_login, self.check_password_auth, self.check_empty_passwords,
                       self.check_protocol, self.check_max_auth_tries, self.check_x11_forwarding]:
            result = check()
            if not result.get('secure', True):
                sev = 'critical' if result['setting'] in ('PermitEmptyPasswords', 'Protocol') else 'warning'
                issues.append({'severity': sev, 'setting': result['setting'], 'value': result['value'],
                               'message': result['recommendation']})

        cipher_check = self.check_ciphers()
        if cipher_check.get('weak'):
            issues.append({'severity': 'high', 'setting': 'Ciphers', 'message': cipher_check['recommendation']})

        mac_check = self.check_macs()
        if mac_check.get('weak'):
            issues.append({'severity': 'high', 'setting': 'MACs', 'message': mac_check['recommendation']})

        for key in self.check_host_keys():
            if key.get('weak'):
                issues.append({'severity': 'warning', 'setting': 'HostKey', 'message': f'Weak DSA key: {key["path"]}'})

        for ak_issue in self.check_authorized_keys():
            issues.append({'severity': ak_issue['severity'], 'setting': 'authorized_keys', 'message': ak_issue['issue']})

        return issues

    def print_report(self):
        issues = self.audit()
        print(f"\n{'='*60}")
        print(f"  SSH Server Security Audit")
        print(f"  Config: {self.config_path}")
        print(f"{'='*60}")

        for check in [self.check_root_login, self.check_password_auth, self.check_empty_passwords,
                       self.check_max_auth_tries, self.check_x11_forwarding]:
            r = check()
            icon = '[OK]' if r.get('secure') else '[!!]'
            print(f"  {icon} {r['setting']}: {r['value']}")

        keys = self.check_host_keys()
        if keys:
            print(f"\n  Host Keys ({len(keys)}):")
            for k in keys:
                weak = " [WEAK]" if k['weak'] else ""
                print(f"    {k['type']}: {k['path']}{weak}")

        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in issues:
                print(f"    [{i['severity'].upper():8s}] {i.get('setting','')}: {i['message']}")
        else:
            print("\n  No security issues found.")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["SSHAudit"]
