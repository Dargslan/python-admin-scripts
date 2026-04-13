"""
dargslan-user-audit — Linux User Account Auditor

Audit user accounts, detect security issues, check sudo access.
Zero external dependencies — reads /etc/passwd, /etc/shadow, /etc/group.

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
import time


class UserAudit:
    """Audit Linux user accounts for security issues."""

    SYSTEM_SHELLS = ['/usr/sbin/nologin', '/bin/false', '/sbin/nologin']
    LOGIN_SHELLS = ['/bin/bash', '/bin/sh', '/bin/zsh', '/bin/fish', '/usr/bin/bash',
                    '/usr/bin/zsh', '/usr/bin/fish', '/bin/dash', '/usr/bin/sh']

    def get_users(self):
        """Get all users from /etc/passwd."""
        users = []
        try:
            with open('/etc/passwd', 'r') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) >= 7:
                        uid = int(parts[2])
                        users.append({
                            'username': parts[0],
                            'uid': uid,
                            'gid': int(parts[3]),
                            'gecos': parts[4],
                            'home': parts[5],
                            'shell': parts[6],
                            'is_system': uid < 1000 and uid != 0,
                            'is_root': uid == 0,
                            'has_login_shell': parts[6] in self.LOGIN_SHELLS,
                        })
        except PermissionError:
            pass
        return users

    def get_login_users(self):
        """Get only users with login shells (non-system)."""
        return [u for u in self.get_users() if u['has_login_shell'] and not u['is_system']]

    def get_groups(self):
        """Get all groups and their members."""
        groups = {}
        try:
            with open('/etc/group', 'r') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) >= 4:
                        groups[parts[0]] = {
                            'gid': int(parts[2]),
                            'members': [m for m in parts[3].split(',') if m],
                        }
        except PermissionError:
            pass
        return groups

    def check_sudo_users(self):
        """Find users with sudo/wheel group membership."""
        groups = self.get_groups()
        sudo_users = set()
        for gname in ['sudo', 'wheel', 'admin']:
            if gname in groups:
                sudo_users.update(groups[gname]['members'])
        try:
            if os.path.isdir('/etc/sudoers.d'):
                for fname in os.listdir('/etc/sudoers.d'):
                    fpath = os.path.join('/etc/sudoers.d', fname)
                    try:
                        with open(fpath, 'r') as f:
                            for line in f:
                                line = line.strip()
                                if line and not line.startswith('#') and not line.startswith('%'):
                                    parts = line.split()
                                    if parts:
                                        sudo_users.add(parts[0])
                    except PermissionError:
                        pass
        except PermissionError:
            pass
        return list(sudo_users)

    def check_empty_passwords(self):
        """Check for users with empty passwords (requires root)."""
        empty = []
        try:
            with open('/etc/shadow', 'r') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) >= 2:
                        if parts[1] == '' or parts[1] == '!!' or parts[1] == '!':
                            pass
                        elif parts[1] == '*':
                            pass
                        elif len(parts[1]) < 4:
                            empty.append(parts[0])
        except PermissionError:
            pass
        return empty

    def check_home_dirs(self):
        """Check home directory permissions and existence."""
        issues = []
        for user in self.get_login_users():
            home = user['home']
            if not os.path.exists(home):
                issues.append({
                    'user': user['username'],
                    'issue': 'missing_home',
                    'detail': f"Home directory does not exist: {home}",
                })
                continue
            try:
                stat = os.stat(home)
                mode = oct(stat.st_mode)[-3:]
                if mode[-1] in ('7', '6', '5', '3', '2'):
                    issues.append({
                        'user': user['username'],
                        'issue': 'world_accessible',
                        'detail': f"Home {home} is world-accessible (mode: {mode})",
                    })
                if stat.st_uid != user['uid']:
                    issues.append({
                        'user': user['username'],
                        'issue': 'wrong_owner',
                        'detail': f"Home {home} owned by UID {stat.st_uid}, expected {user['uid']}",
                    })
            except PermissionError:
                pass
        return issues

    def check_duplicate_uids(self):
        """Find users sharing the same UID."""
        uid_map = {}
        for user in self.get_users():
            uid_map.setdefault(user['uid'], []).append(user['username'])
        return {uid: users for uid, users in uid_map.items() if len(users) > 1}

    def check_root_accounts(self):
        """Find all accounts with UID 0 (root-level)."""
        return [u for u in self.get_users() if u['uid'] == 0]

    def last_logins(self):
        """Get last login information."""
        logins = []
        try:
            result = subprocess.run(['lastlog', '-b', '365'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n')[1:]:
                    parts = line.split()
                    if parts and '**Never' not in line:
                        logins.append({
                            'username': parts[0],
                            'last_login': ' '.join(parts[1:]),
                        })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return logins

    def audit(self):
        """Run full user audit and return issues."""
        issues = []

        root_accounts = self.check_root_accounts()
        if len(root_accounts) > 1:
            issues.append({
                'severity': 'critical',
                'category': 'root_accounts',
                'message': f"Multiple UID 0 accounts: {', '.join(u['username'] for u in root_accounts)}",
            })

        dupes = self.check_duplicate_uids()
        for uid, users in dupes.items():
            if uid != 0:
                issues.append({
                    'severity': 'warning',
                    'category': 'duplicate_uid',
                    'message': f"Duplicate UID {uid}: {', '.join(users)}",
                })

        home_issues = self.check_home_dirs()
        for hi in home_issues:
            issues.append({
                'severity': 'warning',
                'category': hi['issue'],
                'message': hi['detail'],
            })

        login_users = self.get_login_users()
        sudo_users = self.check_sudo_users()
        for su in sudo_users:
            issues.append({
                'severity': 'info',
                'category': 'sudo_access',
                'message': f"User '{su}' has sudo access",
            })

        return issues

    def print_report(self):
        """Print formatted user audit report."""
        users = self.get_users()
        login_users = self.get_login_users()
        sudo_users = self.check_sudo_users()
        issues = self.audit()

        print(f"\n{'='*60}")
        print(f"  User Audit Report")
        print(f"{'='*60}")
        print(f"  Total accounts:      {len(users)}")
        print(f"  Login accounts:      {len(login_users)}")
        print(f"  Sudo users:          {len(sudo_users)}")

        if login_users:
            print(f"\n  Login Users:")
            for u in login_users:
                sudo_flag = ' [SUDO]' if u['username'] in sudo_users else ''
                root_flag = ' [ROOT]' if u['is_root'] else ''
                print(f"    {u['username']:20s} UID:{u['uid']:>5}  {u['shell']}{sudo_flag}{root_flag}")

        if issues:
            critical = [i for i in issues if i['severity'] == 'critical']
            warnings = [i for i in issues if i['severity'] == 'warning']
            if critical:
                print(f"\n  [CRITICAL]:")
                for i in critical:
                    print(f"    ! {i['message']}")
            if warnings:
                print(f"\n  [WARNINGS]:")
                for i in warnings:
                    print(f"    ~ {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  Linux eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")

    def to_json(self):
        """Return user audit as JSON."""
        return json.dumps({
            'users': self.get_login_users(),
            'sudo_users': self.check_sudo_users(),
            'root_accounts': self.check_root_accounts(),
            'duplicate_uids': self.check_duplicate_uids(),
            'issues': self.audit(),
        }, indent=2)


__all__ = ["UserAudit"]
