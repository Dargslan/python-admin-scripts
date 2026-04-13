"""
dargslan-nginx-analyzer — Nginx Configuration Analyzer

Analyze Nginx configuration for security issues and best practices.
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


class NginxAnalyzer:
    """Analyze Nginx configuration for security and best practices."""

    SECURITY_HEADERS = [
        'X-Frame-Options', 'X-Content-Type-Options', 'X-XSS-Protection',
        'Strict-Transport-Security', 'Content-Security-Policy',
        'Referrer-Policy', 'Permissions-Policy',
    ]

    def __init__(self, config_path=None):
        self.config_path = config_path or self._find_config()

    def _find_config(self):
        paths = ['/etc/nginx/nginx.conf', '/usr/local/nginx/conf/nginx.conf', '/opt/nginx/conf/nginx.conf']
        for p in paths:
            if os.path.exists(p):
                return p
        return '/etc/nginx/nginx.conf'

    def _read_config(self, path=None):
        path = path or self.config_path
        try:
            with open(path, 'r') as f:
                return f.read()
        except (FileNotFoundError, PermissionError):
            return ''

    def _find_includes(self, config_text, base_dir=None):
        if base_dir is None:
            base_dir = os.path.dirname(self.config_path)
        includes = []
        for match in re.finditer(r'include\s+([^;]+);', config_text):
            pattern = match.group(1).strip()
            if not os.path.isabs(pattern):
                pattern = os.path.join(base_dir, pattern)
            import glob
            for path in glob.glob(pattern):
                if os.path.isfile(path):
                    includes.append(path)
        return includes

    def get_server_blocks(self):
        """Parse server blocks from nginx config."""
        all_configs = [self.config_path]
        main_config = self._read_config()
        all_configs.extend(self._find_includes(main_config))

        servers = []
        for conf_path in all_configs:
            content = self._read_config(conf_path)
            if not content:
                continue
            for match in re.finditer(r'server\s*\{', content):
                start = match.start()
                depth = 0
                end = start
                for i in range(start, len(content)):
                    if content[i] == '{':
                        depth += 1
                    elif content[i] == '}':
                        depth -= 1
                        if depth == 0:
                            end = i + 1
                            break

                block = content[start:end]
                server_name = re.search(r'server_name\s+([^;]+);', block)
                listen = re.findall(r'listen\s+([^;]+);', block)
                ssl = any('ssl' in l for l in listen) or 'ssl_certificate' in block
                root = re.search(r'root\s+([^;]+);', block)

                servers.append({
                    'file': conf_path,
                    'server_name': server_name.group(1).strip() if server_name else '_',
                    'listen': [l.strip() for l in listen],
                    'ssl': ssl,
                    'root': root.group(1).strip() if root else None,
                    'block': block,
                })
        return servers

    def check_ssl_config(self):
        """Check SSL/TLS configuration."""
        issues = []
        servers = self.get_server_blocks()

        for s in servers:
            if not s['ssl']:
                continue
            block = s['block']

            if 'ssl_protocols' in block:
                protos = re.search(r'ssl_protocols\s+([^;]+);', block)
                if protos:
                    proto_list = protos.group(1)
                    if 'SSLv3' in proto_list or 'TLSv1 ' in proto_list or 'TLSv1.0' in proto_list:
                        issues.append({'severity': 'critical', 'server': s['server_name'],
                            'message': f"Insecure SSL protocol enabled: {proto_list.strip()}"})
            else:
                issues.append({'severity': 'warning', 'server': s['server_name'],
                    'message': 'ssl_protocols not explicitly set'})

            if 'ssl_ciphers' not in block:
                issues.append({'severity': 'warning', 'server': s['server_name'],
                    'message': 'ssl_ciphers not explicitly configured'})

            if 'ssl_prefer_server_ciphers' not in block:
                issues.append({'severity': 'info', 'server': s['server_name'],
                    'message': 'ssl_prefer_server_ciphers not set'})

        return issues

    def check_security_headers(self):
        """Check for missing security headers."""
        servers = self.get_server_blocks()
        issues = []
        for s in servers:
            block = s['block']
            for header in self.SECURITY_HEADERS:
                if header.lower() not in block.lower():
                    issues.append({
                        'severity': 'warning' if header in ['Strict-Transport-Security', 'Content-Security-Policy'] else 'info',
                        'server': s['server_name'],
                        'message': f"Missing security header: {header}",
                    })
        return issues

    def check_common_issues(self):
        """Check for common Nginx misconfigurations."""
        issues = []
        servers = self.get_server_blocks()

        for s in servers:
            block = s['block']

            if 'server_tokens' not in block and 'server_tokens off' not in self._read_config():
                issues.append({'severity': 'warning', 'server': s['server_name'],
                    'message': 'server_tokens not disabled (version disclosure)'})

            if 'autoindex on' in block:
                issues.append({'severity': 'high', 'server': s['server_name'],
                    'message': 'Directory listing enabled (autoindex on)'})

            if re.search(r'location\s+~\s+/\.', block) is None and 'location ~ /\\.' not in block:
                has_dotfile_block = 'location ~ /.' in block or 'deny all' in block
                if not has_dotfile_block:
                    issues.append({'severity': 'info', 'server': s['server_name'],
                        'message': 'No explicit block for dotfiles (.env, .git)'})

        return issues

    def test_config(self):
        """Run nginx -t to validate configuration."""
        try:
            result = subprocess.run(['nginx', '-t'], capture_output=True, text=True, timeout=10)
            return {
                'valid': result.returncode == 0,
                'output': result.stderr.strip(),
            }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {'valid': None, 'output': 'nginx not found or timed out'}

    def audit(self):
        """Run full Nginx audit."""
        issues = []
        issues.extend(self.check_ssl_config())
        issues.extend(self.check_security_headers())
        issues.extend(self.check_common_issues())
        return issues

    def print_report(self):
        """Print formatted Nginx analysis report."""
        servers = self.get_server_blocks()
        issues = self.audit()

        print(f"\n{'='*60}")
        print(f"  Nginx Configuration Analysis")
        print(f"  Config: {self.config_path}")
        print(f"{'='*60}")

        print(f"\n  Server Blocks ({len(servers)}):")
        for s in servers:
            ssl_badge = " [SSL]" if s['ssl'] else ""
            print(f"    {s['server_name']}{ssl_badge} -> {', '.join(s['listen'])}")

        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in sorted(issues, key=lambda x: {'critical':0,'high':1,'warning':2,'info':3}.get(x['severity'],4)):
                icon = {'critical':'!!','high':'!','warning':'~','info':'i'}.get(i['severity'],'?')
                print(f"  [{icon}] {i['server']}: {i['message']}")
        else:
            print("\n  No issues found.")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["NginxAnalyzer"]
