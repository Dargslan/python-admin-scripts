"""
dargslan-tcp-monitor — TCP Connection Monitor

Track ESTABLISHED, TIME_WAIT, connection states, and per-IP statistics.
Zero external dependencies — reads /proc/net/tcp directly.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import os
import socket
import struct
import json


TCP_STATES = {
    '01': 'ESTABLISHED', '02': 'SYN_SENT', '03': 'SYN_RECV',
    '04': 'FIN_WAIT1', '05': 'FIN_WAIT2', '06': 'TIME_WAIT',
    '07': 'CLOSE', '08': 'CLOSE_WAIT', '09': 'LAST_ACK',
    '0A': 'LISTEN', '0B': 'CLOSING',
}


class TCPMonitor:
    """Monitor TCP connections and statistics."""

    def __init__(self):
        pass

    def _read_file(self, path):
        try:
            with open(path, 'r') as f:
                return f.read()
        except (FileNotFoundError, PermissionError):
            return ''

    @staticmethod
    def _hex_to_ip(hex_str):
        try:
            ip_int = int(hex_str, 16)
            ip = socket.inet_ntoa(struct.pack('<I', ip_int))
            return ip
        except (ValueError, struct.error):
            return hex_str

    @staticmethod
    def _hex_to_port(hex_str):
        try:
            return int(hex_str, 16)
        except ValueError:
            return 0

    def _parse_tcp_file(self, path):
        content = self._read_file(path)
        connections = []
        for line in content.split('\n')[1:]:
            parts = line.split()
            if len(parts) < 10:
                continue
            local = parts[1].split(':')
            remote = parts[2].split(':')
            state_hex = parts[3]

            conn = {
                'local_ip': self._hex_to_ip(local[0]),
                'local_port': self._hex_to_port(local[1]),
                'remote_ip': self._hex_to_ip(remote[0]),
                'remote_port': self._hex_to_port(remote[1]),
                'state': TCP_STATES.get(state_hex, state_hex),
                'uid': int(parts[7]) if parts[7].isdigit() else 0,
                'inode': parts[9],
            }
            connections.append(conn)
        return connections

    def get_connections(self, include_v6=True):
        conns = self._parse_tcp_file('/proc/net/tcp')
        if include_v6:
            conns6 = self._parse_tcp_file('/proc/net/tcp6')
            conns.extend(conns6)
        return conns

    def get_state_counts(self):
        conns = self.get_connections()
        counts = {}
        for c in conns:
            state = c['state']
            counts[state] = counts.get(state, 0) + 1
        return counts

    def get_listening_ports(self):
        conns = self.get_connections()
        listening = [c for c in conns if c['state'] == 'LISTEN']
        seen = set()
        unique = []
        for l in listening:
            key = (l['local_ip'], l['local_port'])
            if key not in seen:
                seen.add(key)
                unique.append(l)
        unique.sort(key=lambda x: x['local_port'])
        return unique

    def get_established(self):
        conns = self.get_connections()
        return [c for c in conns if c['state'] == 'ESTABLISHED']

    def get_connections_per_ip(self, state=None):
        conns = self.get_connections()
        if state:
            conns = [c for c in conns if c['state'] == state]
        ip_counts = {}
        for c in conns:
            ip = c['remote_ip']
            if ip == '0.0.0.0' or ip == '::':
                continue
            ip_counts[ip] = ip_counts.get(ip, 0) + 1
        result = [{'ip': ip, 'count': count} for ip, count in ip_counts.items()]
        result.sort(key=lambda x: x['count'], reverse=True)
        return result

    def get_connections_per_port(self):
        conns = self.get_connections()
        established = [c for c in conns if c['state'] == 'ESTABLISHED']
        port_counts = {}
        for c in established:
            port = c['local_port']
            port_counts[port] = port_counts.get(port, 0) + 1
        result = [{'port': port, 'count': count} for port, count in port_counts.items()]
        result.sort(key=lambda x: x['count'], reverse=True)
        return result

    def get_time_wait_count(self):
        conns = self.get_connections()
        return len([c for c in conns if c['state'] == 'TIME_WAIT'])

    def get_tcp_stats(self):
        content = self._read_file('/proc/net/snmp')
        stats = {}
        lines = content.split('\n')
        for i in range(0, len(lines) - 1, 2):
            if lines[i].startswith('Tcp:'):
                keys = lines[i].split()[1:]
                vals = lines[i + 1].split()[1:]
                for k, v in zip(keys, vals):
                    if v.lstrip('-').isdigit():
                        stats[k] = int(v)
        return stats

    def audit(self):
        issues = []
        states = self.get_state_counts()
        total = sum(states.values())

        tw = states.get('TIME_WAIT', 0)
        if tw > 5000:
            issues.append({'severity': 'critical', 'message': f'{tw} connections in TIME_WAIT (may exhaust ephemeral ports)'})
        elif tw > 1000:
            issues.append({'severity': 'warning', 'message': f'{tw} connections in TIME_WAIT'})

        cw = states.get('CLOSE_WAIT', 0)
        if cw > 100:
            issues.append({'severity': 'warning', 'message': f'{cw} connections in CLOSE_WAIT (possible application bug — not closing sockets)'})

        per_ip = self.get_connections_per_ip()
        for entry in per_ip[:3]:
            if entry['count'] > 200:
                issues.append({'severity': 'warning', 'message': f"IP {entry['ip']} has {entry['count']} connections (possible abuse)"})

        if total > 10000:
            issues.append({'severity': 'warning', 'message': f'Total TCP connections: {total} (high load)'})

        return issues

    def print_report(self):
        states = self.get_state_counts()
        listening = self.get_listening_ports()
        per_ip = self.get_connections_per_ip()[:10]
        per_port = self.get_connections_per_port()[:10]
        issues = self.audit()

        print(f"\n{'='*60}")
        print(f"  TCP Connection Monitor")
        print(f"{'='*60}")

        total = sum(states.values())
        print(f"\n  Total Connections: {total}")
        print(f"\n  Connection States:")
        for state, count in sorted(states.items(), key=lambda x: -x[1]):
            bar = '#' * min(count // 10, 30)
            print(f"    {state:15s} {count:>6d} {bar}")

        if listening:
            print(f"\n  Listening Ports ({len(listening)}):")
            for l in listening[:15]:
                print(f"    {l['local_ip']:>15s}:{l['local_port']:<6d}")

        if per_ip:
            print(f"\n  Top IPs by Connections:")
            for entry in per_ip:
                print(f"    {entry['ip']:>15s}  {entry['count']} connections")

        if per_port:
            print(f"\n  Established by Local Port:")
            for entry in per_port:
                print(f"    Port {entry['port']:>5d}  {entry['count']} connections")

        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in issues:
                print(f"    [{i['severity'].upper():8s}] {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["TCPMonitor"]
