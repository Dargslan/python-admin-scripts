"""
dargslan-ssl-checker — SSL/TLS Certificate Checker

Check SSL certificate expiry, cipher suites, and security issues.
Zero external dependencies — uses only Python standard library.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import ssl
import socket
import datetime
import json


class SSLChecker:
    """Check SSL/TLS certificates for domains."""

    def __init__(self, timeout=10):
        self.timeout = timeout

    def get_cert_info(self, hostname, port=443):
        """Get SSL certificate information for a hostname."""
        context = ssl.create_default_context()
        try:
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    protocol = ssock.version()

                    not_before = datetime.datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                    not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_left = (not_after - datetime.datetime.utcnow()).days

                    subject = dict(x[0] for x in cert.get('subject', []))
                    issuer = dict(x[0] for x in cert.get('issuer', []))
                    san = [entry[1] for entry in cert.get('subjectAltName', [])]

                    return {
                        'hostname': hostname,
                        'port': port,
                        'common_name': subject.get('commonName', 'N/A'),
                        'issuer': issuer.get('organizationName', issuer.get('commonName', 'N/A')),
                        'not_before': not_before.isoformat(),
                        'not_after': not_after.isoformat(),
                        'days_until_expiry': days_left,
                        'expired': days_left < 0,
                        'expiring_soon': 0 <= days_left <= 30,
                        'serial_number': cert.get('serialNumber', 'N/A'),
                        'san': san,
                        'protocol': protocol,
                        'cipher': cipher[0] if cipher else 'N/A',
                        'cipher_bits': cipher[2] if cipher and len(cipher) > 2 else 'N/A',
                        'status': 'EXPIRED' if days_left < 0 else ('WARNING' if days_left <= 30 else 'OK'),
                    }
        except ssl.SSLCertVerificationError as e:
            return {'hostname': hostname, 'port': port, 'status': 'INVALID', 'error': str(e)}
        except socket.timeout:
            return {'hostname': hostname, 'port': port, 'status': 'TIMEOUT', 'error': 'Connection timed out'}
        except socket.gaierror:
            return {'hostname': hostname, 'port': port, 'status': 'DNS_ERROR', 'error': 'DNS resolution failed'}
        except Exception as e:
            return {'hostname': hostname, 'port': port, 'status': 'ERROR', 'error': str(e)}

    def check_multiple(self, hostnames, port=443):
        """Check SSL certificates for multiple hostnames."""
        results = []
        for hostname in hostnames:
            results.append(self.get_cert_info(hostname.strip(), port))
        return results

    def check_expiring(self, hostnames, days_threshold=30, port=443):
        """Find certificates expiring within the threshold."""
        results = self.check_multiple(hostnames, port)
        return [r for r in results if r.get('days_until_expiry', 0) <= days_threshold or r.get('status') != 'OK']

    def print_report(self, hostname, port=443):
        """Print a formatted SSL certificate report."""
        info = self.get_cert_info(hostname, port)

        if info['status'] in ('ERROR', 'TIMEOUT', 'DNS_ERROR', 'INVALID'):
            print(f"\n{'='*60}")
            print(f"  SSL CHECK FAILED: {hostname}:{port}")
            print(f"  Status: {info['status']}")
            print(f"  Error: {info.get('error', 'Unknown')}")
            print(f"{'='*60}")
            return info

        status_icon = {'OK': '[OK]', 'WARNING': '[WARN]', 'EXPIRED': '[EXPIRED]'}
        icon = status_icon.get(info['status'], '[?]')

        print(f"\n{'='*60}")
        print(f"  SSL Certificate Report: {hostname}")
        print(f"{'='*60}")
        print(f"  Status:         {icon} {info['status']}")
        print(f"  Common Name:    {info['common_name']}")
        print(f"  Issuer:         {info['issuer']}")
        print(f"  Valid From:     {info['not_before']}")
        print(f"  Valid Until:    {info['not_after']}")
        print(f"  Days Left:      {info['days_until_expiry']}")
        print(f"  Protocol:       {info['protocol']}")
        print(f"  Cipher:         {info['cipher']} ({info['cipher_bits']} bits)")
        print(f"  Serial:         {info['serial_number']}")
        if info['san']:
            print(f"  SANs:           {', '.join(info['san'][:5])}")
            if len(info['san']) > 5:
                print(f"                  ... and {len(info['san'])-5} more")
        print(f"{'='*60}")
        print(f"  More security tools: https://dargslan.com")
        print(f"  Linux eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")
        return info

    def to_json(self, hostname, port=443):
        """Return SSL certificate info as JSON string."""
        return json.dumps(self.get_cert_info(hostname, port), indent=2)


__all__ = ["SSLChecker"]
