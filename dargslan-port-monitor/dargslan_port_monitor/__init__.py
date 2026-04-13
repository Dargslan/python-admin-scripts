"""
dargslan-port-monitor — Linux Open Port Monitor

Monitor open ports, detect listening services, find unexpected listeners.
Zero external dependencies — reads from /proc/net and uses ss/netstat.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import subprocess
import socket
import json
import os


class PortMonitor:
    """Monitor open ports and listening services."""

    WELL_KNOWN = {
        22: 'SSH', 25: 'SMTP', 53: 'DNS', 80: 'HTTP', 443: 'HTTPS',
        110: 'POP3', 143: 'IMAP', 3306: 'MySQL', 5432: 'PostgreSQL',
        6379: 'Redis', 27017: 'MongoDB', 8080: 'HTTP-Alt', 8443: 'HTTPS-Alt',
        9090: 'Prometheus', 3000: 'Grafana/Dev', 5000: 'Dev', 8000: 'Dev',
        2222: 'SSH-Alt', 993: 'IMAPS', 995: 'POP3S', 587: 'SMTP-Submit',
        11211: 'Memcached', 9200: 'Elasticsearch', 5601: 'Kibana',
        2379: 'etcd', 6443: 'K8s-API', 10250: 'Kubelet',
    }

    def get_listening_ports(self):
        """Get all listening ports using ss or /proc/net."""
        ports = self._try_ss()
        if not ports:
            ports = self._try_proc_net()
        return ports

    def _try_ss(self):
        """Get listening ports via ss command."""
        ports = []
        try:
            result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return []
            for line in result.stdout.strip().split('\n')[1:]:
                parts = line.split()
                if len(parts) >= 4:
                    local = parts[3]
                    if ':' in local:
                        addr, port_str = local.rsplit(':', 1)
                        try:
                            port = int(port_str)
                        except ValueError:
                            continue
                        addr = addr.strip('[]')
                        process = ''
                        if len(parts) >= 6:
                            proc_info = parts[5] if len(parts) > 5 else parts[-1]
                            if 'users:' in proc_info:
                                start = proc_info.find('"')
                                end = proc_info.find('"', start + 1)
                                if start >= 0 and end >= 0:
                                    process = proc_info[start+1:end]

                        ports.append({
                            'port': port,
                            'address': addr,
                            'protocol': 'tcp',
                            'process': process,
                            'service': self.WELL_KNOWN.get(port, ''),
                            'exposed': addr in ('0.0.0.0', '*', '::'),
                        })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return ports

    def _try_proc_net(self):
        """Get listening ports from /proc/net/tcp."""
        ports = []
        try:
            with open('/proc/net/tcp', 'r') as f:
                for line in f.readlines()[1:]:
                    parts = line.strip().split()
                    if len(parts) >= 4 and parts[3] == '0A':
                        local = parts[1]
                        addr_hex, port_hex = local.split(':')
                        port = int(port_hex, 16)
                        addr_int = int(addr_hex, 16)
                        addr = socket.inet_ntoa(addr_int.to_bytes(4, 'little'))
                        ports.append({
                            'port': port,
                            'address': addr,
                            'protocol': 'tcp',
                            'process': '',
                            'service': self.WELL_KNOWN.get(port, ''),
                            'exposed': addr == '0.0.0.0',
                        })
        except (FileNotFoundError, PermissionError):
            pass
        return ports

    def get_udp_ports(self):
        """Get listening UDP ports."""
        ports = []
        try:
            result = subprocess.run(['ss', '-ulnp'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return []
            for line in result.stdout.strip().split('\n')[1:]:
                parts = line.split()
                if len(parts) >= 4:
                    local = parts[3]
                    if ':' in local:
                        addr, port_str = local.rsplit(':', 1)
                        try:
                            port = int(port_str)
                        except ValueError:
                            continue
                        ports.append({
                            'port': port,
                            'address': addr.strip('[]'),
                            'protocol': 'udp',
                            'service': self.WELL_KNOWN.get(port, ''),
                        })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return ports

    def check_port(self, host, port, timeout=3):
        """Check if a specific port is open."""
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return {'host': host, 'port': port, 'open': True, 'service': self.WELL_KNOWN.get(port, '')}
        except (socket.timeout, ConnectionRefusedError, OSError):
            return {'host': host, 'port': port, 'open': False}

    def find_unexpected(self, expected_ports=None):
        """Find ports that are not in the expected list."""
        if expected_ports is None:
            expected_ports = [22, 80, 443]
        listening = self.get_listening_ports()
        return [p for p in listening if p['port'] not in expected_ports and p['exposed']]

    def find_exposed(self):
        """Find ports listening on all interfaces (0.0.0.0 or ::)."""
        return [p for p in self.get_listening_ports() if p['exposed']]

    def port_count(self):
        """Get port statistics."""
        tcp = self.get_listening_ports()
        udp = self.get_udp_ports()
        exposed = [p for p in tcp if p['exposed']]
        return {
            'tcp_listening': len(tcp),
            'udp_listening': len(udp),
            'exposed': len(exposed),
            'total': len(tcp) + len(udp),
        }

    def print_report(self):
        """Print formatted port report."""
        tcp = self.get_listening_ports()
        udp = self.get_udp_ports()

        print(f"\n{'='*60}")
        print(f"  Port Monitor Report")
        print(f"{'='*60}")
        print(f"  TCP listening: {len(tcp)}")
        print(f"  UDP listening: {len(udp)}")

        if tcp:
            print(f"\n  TCP Listening Ports:")
            tcp.sort(key=lambda x: x['port'])
            for p in tcp:
                exposed = '[EXPOSED]' if p['exposed'] else '[local]'
                svc = f" ({p['service']})" if p['service'] else ''
                proc = f" [{p['process']}]" if p.get('process') else ''
                print(f"    {exposed:10s} {p['address']:>15}:{p['port']:<6}{svc}{proc}")

        if udp:
            print(f"\n  UDP Listening Ports:")
            for p in udp:
                svc = f" ({p['service']})" if p['service'] else ''
                print(f"    {p['address']:>15}:{p['port']:<6}{svc}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  Linux eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")

    def to_json(self):
        """Return port info as JSON."""
        return json.dumps({
            'tcp': self.get_listening_ports(),
            'udp': self.get_udp_ports(),
            'stats': self.port_count(),
        }, indent=2)


__all__ = ["PortMonitor"]
