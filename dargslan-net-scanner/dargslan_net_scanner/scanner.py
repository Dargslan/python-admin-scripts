"""
Network scanner — https://dargslan.com
"""

import socket
import subprocess
import ipaddress
import concurrent.futures
from typing import List, Dict, Optional


COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    993: "IMAPS", 995: "POP3S", 3306: "MySQL", 3389: "RDP",
    5432: "PostgreSQL", 5900: "VNC", 6379: "Redis", 8080: "HTTP-Alt",
    8443: "HTTPS-Alt", 9090: "Prometheus", 27017: "MongoDB",
}


class NetScanner:
    """Lightweight network scanner."""

    def __init__(self, timeout: float = 1.0, threads: int = 50):
        self.timeout = timeout
        self.threads = threads

    def ping(self, host: str) -> bool:
        """Check if host is reachable via ping."""
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", str(host)],
                capture_output=True, timeout=3
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def ping_sweep(self, subnet: str) -> List[str]:
        """Ping sweep a subnet, return list of alive hosts."""
        network = ipaddress.ip_network(subnet, strict=False)
        hosts = [str(ip) for ip in network.hosts()]
        alive = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as ex:
            futures = {ex.submit(self.ping, h): h for h in hosts}
            for future in concurrent.futures.as_completed(futures):
                if future.result():
                    alive.append(futures[future])

        return sorted(alive, key=lambda x: ipaddress.ip_address(x))

    def scan_port(self, host: str, port: int) -> Optional[Dict]:
        """Scan a single TCP port."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                service = COMMON_PORTS.get(port, "unknown")
                return {"port": port, "state": "open", "service": service}
        except (socket.error, OSError):
            pass
        return None

    def port_scan(self, host: str, ports: List[int] = None) -> List[Dict]:
        """Scan multiple TCP ports on a host."""
        if ports is None:
            ports = list(COMMON_PORTS.keys())

        open_ports = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as ex:
            futures = {ex.submit(self.scan_port, host, p): p for p in ports}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    open_ports.append(result)

        return sorted(open_ports, key=lambda x: x["port"])

    def quick_scan(self, host: str) -> List[Dict]:
        """Quick scan of most common ports."""
        return self.port_scan(host, list(COMMON_PORTS.keys()))

    def scan_host(self, host: str) -> Dict:
        """Full host scan with ping and port scan."""
        is_alive = self.ping(host)
        ports = self.quick_scan(host) if is_alive else []
        try:
            hostname = socket.getfqdn(host)
        except socket.error:
            hostname = host

        return {
            "host": host,
            "hostname": hostname,
            "alive": is_alive,
            "open_ports": ports,
            "port_count": len(ports),
        }

    def print_scan(self, host: str, ports: List[int] = None):
        """Print formatted scan results."""
        print(f"\n{'=' * 50}")
        print(f"  DARGSLAN NETWORK SCAN: {host}")
        print(f"{'=' * 50}")

        is_alive = self.ping(host)
        print(f"\n  Host: {'UP' if is_alive else 'DOWN'}")

        if is_alive:
            results = self.port_scan(host, ports)
            if results:
                print(f"\n  {'PORT':>7s}  {'STATE':8s}  SERVICE")
                print(f"  {'-' * 35}")
                for r in results:
                    print(f"  {r['port']:>7d}  {r['state']:8s}  {r['service']}")
            else:
                print("  No open ports found")

        print(f"\n{'-' * 50}")
        print("  dargslan.com — Linux & DevOps eBooks")
        print(f"{'=' * 50}\n")
