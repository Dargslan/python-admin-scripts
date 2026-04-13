"""
dargslan-apache-analyzer — Apache HTTP Server Configuration Analyzer

Analyze Apache configuration for security issues, VirtualHosts, SSL, and modules.
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
import glob as globmod


class ApacheAnalyzer:
    """Analyze Apache HTTP Server configuration."""

    SECURITY_HEADERS = [
        'X-Frame-Options', 'X-Content-Type-Options', 'X-XSS-Protection',
        'Strict-Transport-Security', 'Content-Security-Policy', 'Referrer-Policy',
    ]

    def __init__(self, config_path=None):
        self.config_path = config_path or self._find_config()

    def _find_config(self):
        paths = ['/etc/apache2/apache2.conf', '/etc/httpd/conf/httpd.conf',
                 '/usr/local/apache2/conf/httpd.conf', '/etc/apache2/httpd.conf']
        for p in paths:
            if os.path.exists(p): return p
        return '/etc/apache2/apache2.conf'

    def _read_config(self, path=None):
        path = path or self.config_path
        try:
            with open(path, 'r') as f: return f.read()
        except (FileNotFoundError, PermissionError): return ''

    def _find_includes(self, config_text):
        base_dir = os.path.dirname(self.config_path)
        includes = []
        for match in re.finditer(r'(?:Include|IncludeOptional)\s+(.+)', config_text):
            pattern = match.group(1).strip()
            if not os.path.isabs(pattern):
                pattern = os.path.join(base_dir, pattern)
            for path in globmod.glob(pattern):
                if os.path.isfile(path): includes.append(path)
        return includes

    def get_vhosts(self):
        """Parse VirtualHost blocks."""
        all_configs = [self.config_path]
        main_config = self._read_config()
        all_configs.extend(self._find_includes(main_config))

        vhosts = []
        for conf_path in all_configs:
            content = self._read_config(conf_path)
            if not content: continue
            for match in re.finditer(r'<VirtualHost\s+([^>]+)>', content):
                start = match.start()
                end_match = re.search(r'</VirtualHost>', content[start:])
                if not end_match: continue
                block = content[start:start + end_match.end()]

                server_name = re.search(r'ServerName\s+(\S+)', block)
                doc_root = re.search(r'DocumentRoot\s+(\S+)', block)
                ssl = 'SSLEngine on' in block or ':443' in match.group(1)

                vhosts.append({
                    'file': conf_path,
                    'address': match.group(1).strip(),
                    'server_name': server_name.group(1) if server_name else '_',
                    'document_root': doc_root.group(1).strip('"') if doc_root else None,
                    'ssl': ssl,
                    'block': block,
                })
        return vhosts

    def get_loaded_modules(self):
        """Get loaded Apache modules."""
        try:
            for cmd in [['apache2ctl', '-M'], ['httpd', '-M'], ['apachectl', '-M']]:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        modules = []
                        for line in result.stdout.split('\n'):
                            line = line.strip()
                            if '_module' in line:
                                modules.append(line.split()[0])
                        return modules
                except FileNotFoundError: continue
        except subprocess.TimeoutExpired: pass
        return []

    def check_security(self):
        """Check Apache security configuration."""
        issues = []
        main_config = self._read_config()
        all_content = main_config
        for inc in self._find_includes(main_config):
            all_content += '\n' + self._read_config(inc)

        if 'ServerTokens Prod' not in all_content and 'ServerTokens ProductOnly' not in all_content:
            issues.append({'severity': 'warning', 'message': 'ServerTokens not set to Prod (version disclosure)'})

        if 'ServerSignature Off' not in all_content:
            issues.append({'severity': 'warning', 'message': 'ServerSignature not disabled'})

        if 'TraceEnable Off' not in all_content:
            issues.append({'severity': 'warning', 'message': 'TRACE method not disabled'})

        modules = self.get_loaded_modules()
        security_modules = ['security2_module', 'headers_module', 'ssl_module']
        for mod in security_modules:
            if mod not in modules:
                sev = 'info' if mod != 'ssl_module' else 'warning'
                issues.append({'severity': sev, 'message': f'Module not loaded: {mod}'})

        for vhost in self.get_vhosts():
            block = vhost['block']
            for header in self.SECURITY_HEADERS:
                if header.lower() not in block.lower():
                    issues.append({'severity': 'info', 'server': vhost['server_name'],
                        'message': f"Missing: {header}"})

            if vhost['ssl']:
                if 'SSLProtocol' in block:
                    proto_match = re.search(r'SSLProtocol\s+(.+)', block)
                    if proto_match:
                        protos = proto_match.group(1)
                        if 'SSLv3' in protos or '+TLSv1 ' in protos:
                            issues.append({'severity': 'critical', 'server': vhost['server_name'],
                                'message': f'Insecure SSL protocol: {protos.strip()}'})

            if 'Options Indexes' in block or 'Options +Indexes' in block:
                issues.append({'severity': 'high', 'server': vhost['server_name'],
                    'message': 'Directory listing enabled'})

        return issues

    def test_config(self):
        """Test Apache configuration syntax."""
        for cmd in [['apache2ctl', '-t'], ['httpd', '-t'], ['apachectl', '-t']]:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                return {'valid': result.returncode == 0, 'output': result.stderr.strip()}
            except FileNotFoundError: continue
        return {'valid': None, 'output': 'Apache not found'}

    def print_report(self):
        """Print formatted Apache analysis report."""
        vhosts = self.get_vhosts()
        modules = self.get_loaded_modules()
        issues = self.check_security()

        print(f"\n{'='*60}")
        print(f"  Apache Configuration Analysis")
        print(f"  Config: {self.config_path}")
        print(f"{'='*60}")
        print(f"\n  VirtualHosts ({len(vhosts)}):")
        for v in vhosts:
            ssl = " [SSL]" if v['ssl'] else ""
            print(f"    {v['server_name']}{ssl} -> {v['address']}")

        print(f"\n  Loaded Modules: {len(modules)}")

        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in sorted(issues, key=lambda x: {'critical':0,'high':1,'warning':2,'info':3}.get(x['severity'],4)):
                srv = f" ({i['server']})" if 'server' in i else ""
                print(f"    [{i['severity'].upper():8s}]{srv} {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["ApacheAnalyzer"]
