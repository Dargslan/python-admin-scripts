"""
dargslan-cert-manager — SSL/TLS Certificate Inventory Manager

Track expiry dates, issuer info, and certificate chain across servers.
Zero external dependencies — uses openssl CLI.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import subprocess
import ssl
import socket
import json
import os
import re
from datetime import datetime


class CertManager:
    """Manage and monitor SSL/TLS certificates."""

    def __init__(self, timeout=10):
        self.timeout = timeout

    def check_remote(self, hostname, port=443):
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            conn = ctx.wrap_socket(socket.socket(), server_hostname=hostname)
            conn.settimeout(self.timeout)
            conn.connect((hostname, port))
            der_cert = conn.getpeercert(True)
            pem_cert = ssl.DER_cert_to_PEM_cert(der_cert)
            conn.close()

            info = self._parse_cert_openssl(pem_cert)
            info['hostname'] = hostname
            info['port'] = port

            if info.get('not_after'):
                try:
                    expiry = datetime.strptime(info['not_after'], '%b %d %H:%M:%S %Y %Z')
                    info['days_until_expiry'] = (expiry - datetime.utcnow()).days
                    info['expired'] = info['days_until_expiry'] < 0
                except (ValueError, TypeError):
                    pass

            return info
        except Exception as e:
            return {'hostname': hostname, 'port': port, 'error': str(e)}

    def _parse_cert_openssl(self, pem_cert):
        try:
            proc = subprocess.run(
                ['openssl', 'x509', '-noout', '-subject', '-issuer', '-dates', '-serial',
                 '-ext', 'subjectAltName', '-fingerprint'],
                input=pem_cert, capture_output=True, text=True, timeout=10
            )
            output = proc.stdout
            info = {}

            subject = re.search(r'subject\s*=\s*(.+)', output)
            if subject: info['subject'] = subject.group(1).strip()

            issuer = re.search(r'issuer\s*=\s*(.+)', output)
            if issuer: info['issuer'] = issuer.group(1).strip()

            not_before = re.search(r'notBefore\s*=\s*(.+)', output)
            if not_before: info['not_before'] = not_before.group(1).strip()

            not_after = re.search(r'notAfter\s*=\s*(.+)', output)
            if not_after: info['not_after'] = not_after.group(1).strip()

            serial = re.search(r'serial\s*=\s*(.+)', output)
            if serial: info['serial'] = serial.group(1).strip()

            fingerprint = re.search(r'SHA1 Fingerprint\s*=\s*(.+)', output)
            if fingerprint: info['fingerprint'] = fingerprint.group(1).strip()

            san = re.search(r'DNS:([^\n]+)', output)
            if san:
                info['san'] = [d.strip().replace('DNS:', '') for d in san.group(0).split(',')]

            return info
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {}

    def check_file(self, cert_path):
        try:
            result = subprocess.run(
                ['openssl', 'x509', '-noout', '-subject', '-issuer', '-dates', '-serial', '-fingerprint', '-in', cert_path],
                capture_output=True, text=True, timeout=10
            )
            output = result.stdout
            info = {'file': cert_path}

            for field, pattern in [('subject', r'subject\s*=\s*(.+)'), ('issuer', r'issuer\s*=\s*(.+)'),
                                    ('not_before', r'notBefore\s*=\s*(.+)'), ('not_after', r'notAfter\s*=\s*(.+)'),
                                    ('serial', r'serial\s*=\s*(.+)')]:
                match = re.search(pattern, output)
                if match: info[field] = match.group(1).strip()

            if info.get('not_after'):
                try:
                    expiry = datetime.strptime(info['not_after'], '%b %d %H:%M:%S %Y %Z')
                    info['days_until_expiry'] = (expiry - datetime.utcnow()).days
                    info['expired'] = info['days_until_expiry'] < 0
                except (ValueError, TypeError):
                    pass

            return info
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            return {'file': cert_path, 'error': str(e)}

    def find_local_certs(self):
        certs = []
        search_dirs = ['/etc/ssl/certs', '/etc/pki/tls/certs', '/etc/letsencrypt/live']
        for d in search_dirs:
            if not os.path.isdir(d): continue
            try:
                for root, dirs, files in os.walk(d):
                    for f in files:
                        if f.endswith(('.pem', '.crt', '.cert')) and not f.startswith('.'):
                            certs.append(os.path.join(root, f))
            except PermissionError:
                continue
        return certs[:50]

    def bulk_check(self, hosts):
        results = []
        for host in hosts:
            host = host.strip()
            if ':' in host:
                hostname, port = host.rsplit(':', 1)
                port = int(port)
            else:
                hostname, port = host, 443
            results.append(self.check_remote(hostname, port))
        return results

    def audit(self, hosts=None):
        issues = []
        if hosts:
            for result in self.bulk_check(hosts):
                if result.get('error'):
                    issues.append({'severity': 'critical', 'host': result.get('hostname',''),
                        'message': f"Cannot connect: {result['error']}"})
                elif result.get('expired'):
                    issues.append({'severity': 'critical', 'host': result.get('hostname',''),
                        'message': f"Certificate EXPIRED ({abs(result['days_until_expiry'])} days ago)"})
                elif result.get('days_until_expiry', 999) < 7:
                    issues.append({'severity': 'critical', 'host': result.get('hostname',''),
                        'message': f"Expires in {result['days_until_expiry']} days"})
                elif result.get('days_until_expiry', 999) < 30:
                    issues.append({'severity': 'warning', 'host': result.get('hostname',''),
                        'message': f"Expires in {result['days_until_expiry']} days"})

        for cert_path in self.find_local_certs()[:20]:
            info = self.check_file(cert_path)
            if info.get('expired'):
                issues.append({'severity': 'warning', 'file': cert_path,
                    'message': f"Local cert expired ({abs(info.get('days_until_expiry',0))} days ago)"})
            elif info.get('days_until_expiry', 999) < 14:
                issues.append({'severity': 'warning', 'file': cert_path,
                    'message': f"Local cert expires in {info['days_until_expiry']} days"})

        return issues

    def print_report(self, hosts=None):
        print(f"\n{'='*60}")
        print(f"  SSL/TLS Certificate Inventory")
        print(f"{'='*60}")

        if hosts:
            print(f"\n  Remote Certificates ({len(hosts)}):")
            for result in self.bulk_check(hosts):
                if result.get('error'):
                    print(f"    [FAIL] {result.get('hostname','')}: {result['error']}")
                else:
                    days = result.get('days_until_expiry', '?')
                    status = 'EXPIRED' if result.get('expired') else f'{days}d'
                    icon = '[!!]' if result.get('expired') or (isinstance(days, int) and days < 30) else '[OK]'
                    print(f"    {icon} {result.get('hostname','')}:{result.get('port',443)} — {status}")
                    print(f"        Issuer: {result.get('issuer','N/A')[:60]}")
                    print(f"        Expires: {result.get('not_after','N/A')}")

        local = self.find_local_certs()
        if local:
            print(f"\n  Local Certificates ({len(local)}):")
            for cert in local[:10]:
                info = self.check_file(cert)
                days = info.get('days_until_expiry', '?')
                status = 'EXPIRED' if info.get('expired') else f'{days}d'
                print(f"    [{status:8s}] {cert}")

        issues = self.audit(hosts)
        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in issues:
                target = i.get('host') or i.get('file', '')
                print(f"    [{i['severity'].upper():8s}] {target}: {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["CertManager"]
