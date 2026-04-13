"""
dargslan-git-audit — Git Repository Security Auditor

Scan for secrets in commits, large files, .gitignore gaps, and sensitive data leaks.
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
import subprocess
import json


class GitAudit:
    """Audit Git repositories for security issues."""

    SECRET_PATTERNS = [
        (r'(?:password|passwd|pwd)\s*[:=]\s*["\']?[A-Za-z0-9!@#$%^&*]{8,}', 'password'),
        (r'(?:api[_-]?key|apikey)\s*[:=]\s*["\']?[A-Za-z0-9]{16,}', 'api_key'),
        (r'(?:secret[_-]?key|secretkey)\s*[:=]\s*["\']?[A-Za-z0-9]{16,}', 'secret_key'),
        (r'(?:access[_-]?token|auth[_-]?token)\s*[:=]\s*["\']?[A-Za-z0-9_\-]{20,}', 'token'),
        (r'AKIA[0-9A-Z]{16}', 'aws_access_key'),
        (r'(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}', 'github_token'),
        (r'sk-[A-Za-z0-9]{48,}', 'openai_key'),
        (r'-----BEGIN (?:RSA |DSA |EC )?PRIVATE KEY-----', 'private_key'),
        (r'(?:mysql|postgres|mongodb)://[^:]+:[^@]+@', 'database_url'),
        (r'Bearer\s+[A-Za-z0-9\-._~+/]+=*', 'bearer_token'),
    ]

    SENSITIVE_FILES = [
        '.env', '.env.local', '.env.production', 'id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519',
        '*.pem', '*.key', '*.p12', '*.pfx', '*.jks', 'credentials.json', 'service-account.json',
        'wp-config.php', 'config.php', 'secrets.yml', 'secrets.yaml', '.htpasswd',
    ]

    def __init__(self, repo_path=None):
        self.repo_path = repo_path or os.getcwd()

    def _run_git(self, args):
        try:
            result = subprocess.run(['git'] + args, capture_output=True, text=True,
                                   timeout=30, cwd=self.repo_path)
            return result.stdout.strip() if result.returncode == 0 else ''
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ''

    def is_git_repo(self):
        """Check if current directory is a Git repo."""
        return os.path.isdir(os.path.join(self.repo_path, '.git'))

    def scan_staged_secrets(self):
        """Scan staged files for secrets."""
        diff = self._run_git(['diff', '--cached', '--diff-filter=ACMR'])
        return self._scan_content(diff, 'staged')

    def scan_working_secrets(self):
        """Scan working directory for secrets."""
        issues = []
        tracked = self._run_git(['ls-files'])
        for filepath in tracked.split('\n'):
            if not filepath.strip(): continue
            full_path = os.path.join(self.repo_path, filepath)
            try:
                if os.path.getsize(full_path) > 1048576: continue
                with open(full_path, 'r', errors='replace') as f:
                    content = f.read()
                for pattern, secret_type in self.SECRET_PATTERNS:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches[:3]:
                        issues.append({
                            'file': filepath,
                            'type': secret_type,
                            'severity': 'critical',
                            'preview': match[:30] + '...' if len(match) > 30 else match,
                        })
            except (FileNotFoundError, PermissionError, UnicodeDecodeError):
                continue
        return issues

    def _scan_content(self, content, source):
        issues = []
        for pattern, secret_type in self.SECRET_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches[:5]:
                issues.append({
                    'source': source,
                    'type': secret_type,
                    'severity': 'critical',
                    'preview': match[:30] + '...',
                })
        return issues

    def check_gitignore(self):
        """Check for missing .gitignore entries."""
        gitignore_path = os.path.join(self.repo_path, '.gitignore')
        missing = []
        gitignore_content = ''
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()

        recommended = ['.env', '.env.*', '*.pem', '*.key', 'id_rsa', 'id_dsa',
                       'node_modules/', '__pycache__/', '*.pyc', '.DS_Store',
                       'credentials.json', '*.log', 'dist/', 'build/']

        for entry in recommended:
            if entry not in gitignore_content:
                exists = False
                tracked = self._run_git(['ls-files', '--', entry.rstrip('/')])
                if tracked: exists = True
                missing.append({'pattern': entry, 'tracked': exists})

        return missing

    def find_large_files(self, threshold_mb=10):
        """Find large files in repository history."""
        output = self._run_git(['rev-list', '--objects', '--all'])
        large_files = []
        if not output: return large_files

        for line in output.split('\n')[:500]:
            parts = line.split(None, 1)
            if len(parts) < 2: continue
            obj_hash, path = parts
            size_output = self._run_git(['cat-file', '-s', obj_hash])
            if size_output and size_output.isdigit():
                size_bytes = int(size_output)
                if size_bytes > threshold_mb * 1024 * 1024:
                    large_files.append({
                        'path': path,
                        'size_mb': round(size_bytes / 1024 / 1024, 2),
                        'hash': obj_hash[:8],
                    })
        return sorted(large_files, key=lambda x: x['size_mb'], reverse=True)[:20]

    def check_sensitive_files(self):
        """Check for tracked sensitive files."""
        tracked = self._run_git(['ls-files'])
        found = []
        for filepath in tracked.split('\n'):
            basename = os.path.basename(filepath)
            for pattern in self.SENSITIVE_FILES:
                if pattern.startswith('*.'):
                    if basename.endswith(pattern[1:]):
                        found.append({'file': filepath, 'pattern': pattern, 'severity': 'high'})
                        break
                elif basename == pattern:
                    found.append({'file': filepath, 'pattern': pattern, 'severity': 'critical'})
                    break
        return found

    def repo_stats(self):
        """Get repository statistics."""
        commit_count = self._run_git(['rev-list', '--count', 'HEAD'])
        branch_count = self._run_git(['branch', '-a', '--list'])
        contributor_count = self._run_git(['shortlog', '-sn', '--all'])

        return {
            'commits': int(commit_count) if commit_count and commit_count.isdigit() else 0,
            'branches': len([b for b in branch_count.split('\n') if b.strip()]) if branch_count else 0,
            'contributors': len([c for c in contributor_count.split('\n') if c.strip()]) if contributor_count else 0,
        }

    def audit(self):
        """Run full Git security audit."""
        issues = []

        for s in self.scan_working_secrets():
            issues.append({'severity': 'critical', 'category': 'secret',
                          'message': f"Secret ({s['type']}) in {s['file']}"})

        for f in self.check_sensitive_files():
            issues.append({'severity': f['severity'], 'category': 'sensitive_file',
                          'message': f"Sensitive file tracked: {f['file']}"})

        gitignore_gaps = self.check_gitignore()
        tracked_gaps = [g for g in gitignore_gaps if g['tracked']]
        if tracked_gaps:
            issues.append({'severity': 'warning', 'category': 'gitignore',
                          'message': f"{len(tracked_gaps)} sensitive patterns tracked but not in .gitignore"})

        return issues

    def print_report(self):
        """Print formatted Git audit report."""
        stats = self.repo_stats()
        issues = self.audit()

        print(f"\n{'='*60}")
        print(f"  Git Repository Security Audit")
        print(f"  Path: {self.repo_path}")
        print(f"{'='*60}")
        print(f"\n  Commits: {stats['commits']}")
        print(f"  Branches: {stats['branches']}")
        print(f"  Contributors: {stats['contributors']}")

        secrets = self.scan_working_secrets()
        if secrets:
            print(f"\n  Secrets Found ({len(secrets)}):")
            for s in secrets[:10]:
                print(f"    [CRITICAL] {s['file']}: {s['type']}")

        sensitive = self.check_sensitive_files()
        if sensitive:
            print(f"\n  Sensitive Files ({len(sensitive)}):")
            for f in sensitive[:10]:
                print(f"    [{f['severity'].upper()}] {f['file']}")

        if issues:
            print(f"\n  Total Issues ({len(issues)}):")
            for i in issues:
                print(f"    [{i['severity'].upper():8s}] {i['message']}")
        else:
            print("\n  No security issues found.")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["GitAudit"]
