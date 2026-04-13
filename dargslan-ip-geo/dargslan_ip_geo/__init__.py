"""
dargslan-ip-geo — IP Geolocation & WHOIS Lookup

Find country, ISP, abuse contact, and network info for any IP address.
Zero external dependencies — uses only Python standard library.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import socket
import json
import re
import urllib.request


class IPGeo:
    """IP geolocation and WHOIS lookup tool."""

    WHOIS_SERVERS = {
        'arin': 'whois.arin.net',
        'ripe': 'whois.ripe.net',
        'apnic': 'whois.apnic.net',
        'lacnic': 'whois.lacnic.net',
        'afrinic': 'whois.afrinic.net',
        'default': 'whois.iana.org',
    }

    def __init__(self, timeout=10):
        self.timeout = timeout

    def geolocate(self, ip):
        """Get geolocation data for an IP address using ip-api.com."""
        try:
            url = f'http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query'
            req = urllib.request.Request(url, headers={'User-Agent': 'dargslan-ip-geo/1.0'})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode())
                if data.get('status') == 'success':
                    return data
                return {'query': ip, 'status': 'fail', 'error': data.get('message', 'Unknown error')}
        except Exception as e:
            return {'query': ip, 'status': 'fail', 'error': str(e)}

    def whois(self, ip, server=None):
        """Perform WHOIS lookup for an IP address."""
        if not server:
            server = self.WHOIS_SERVERS['default']
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((server, 43))
            sock.send(f'{ip}\r\n'.encode())
            response = b''
            while True:
                data = sock.recv(4096)
                if not data: break
                response += data
            sock.close()
            text = response.decode(errors='replace')

            info = {}
            for line in text.split('\n'):
                line = line.strip()
                if ':' in line and not line.startswith('%') and not line.startswith('#'):
                    key, _, value = line.partition(':')
                    key = key.strip().lower()
                    value = value.strip()
                    if value and key not in info:
                        info[key] = value

            refer = info.get('refer', '')
            if refer and refer != server:
                return self.whois(ip, refer)

            return {'ip': ip, 'server': server, 'raw_length': len(text), 'parsed': info}
        except Exception as e:
            return {'ip': ip, 'server': server, 'error': str(e)}

    def reverse_dns(self, ip):
        """Perform reverse DNS lookup."""
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return {'ip': ip, 'hostname': hostname}
        except socket.herror:
            return {'ip': ip, 'hostname': None}
        except Exception as e:
            return {'ip': ip, 'hostname': None, 'error': str(e)}

    def lookup(self, ip):
        """Full lookup: geolocation + reverse DNS."""
        geo = self.geolocate(ip)
        rdns = self.reverse_dns(ip)
        geo['hostname'] = rdns.get('hostname')
        return geo

    def bulk_lookup(self, ips):
        """Lookup multiple IPs."""
        return [self.lookup(ip.strip()) for ip in ips if ip.strip()]

    def print_report(self, ip):
        """Print formatted IP report."""
        info = self.lookup(ip)
        print(f"\n{'='*60}")
        print(f"  IP Geolocation Report: {ip}")
        print(f"{'='*60}")

        if info.get('status') == 'fail':
            print(f"  Error: {info.get('error', 'Unknown')}")
        else:
            print(f"  Country:   {info.get('country', 'N/A')} ({info.get('countryCode', '')})")
            print(f"  Region:    {info.get('regionName', 'N/A')}")
            print(f"  City:      {info.get('city', 'N/A')}")
            print(f"  ZIP:       {info.get('zip', 'N/A')}")
            print(f"  Coords:    {info.get('lat', '')}, {info.get('lon', '')}")
            print(f"  Timezone:  {info.get('timezone', 'N/A')}")
            print(f"  ISP:       {info.get('isp', 'N/A')}")
            print(f"  Org:       {info.get('org', 'N/A')}")
            print(f"  AS:        {info.get('as', 'N/A')}")
            print(f"  Hostname:  {info.get('hostname') or 'N/A'}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["IPGeo"]
