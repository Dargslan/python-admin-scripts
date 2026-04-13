"""
dargslan-redis-health — Redis Server Health Checker

Monitor Redis memory, persistence, replication, slow log, and clients.
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
import os


class RedisHealth:
    """Check Redis server health and performance."""

    def __init__(self, host='localhost', port=6379, password=None, timeout=5):
        self.host = host
        self.port = port
        self.password = password or os.environ.get('REDIS_PASSWORD', '')
        self.timeout = timeout

    def _send_command(self, *args):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))

            if self.password:
                auth_cmd = f"*2\r\n$4\r\nAUTH\r\n${len(self.password)}\r\n{self.password}\r\n"
                sock.send(auth_cmd.encode())
                sock.recv(1024)

            cmd_parts = [f"${len(str(a))}\r\n{a}" for a in args]
            cmd = f"*{len(args)}\r\n" + "\r\n".join(cmd_parts) + "\r\n"
            sock.send(cmd.encode())

            response = b''
            while True:
                data = sock.recv(4096)
                if not data: break
                response += data
                if b'\r\n' in data and len(data) < 4096: break

            sock.close()
            return response.decode(errors='replace')
        except Exception as e:
            return f'-ERR {e}'

    def _parse_info(self, raw):
        info = {}
        for line in raw.split('\r\n'):
            if ':' in line and not line.startswith('#') and not line.startswith('$'):
                key, _, value = line.partition(':')
                info[key.strip()] = value.strip()
        return info

    def get_info(self, section=None):
        """Get Redis INFO output."""
        if section:
            raw = self._send_command('INFO', section)
        else:
            raw = self._send_command('INFO')
        return self._parse_info(raw)

    def is_alive(self):
        """Ping Redis server."""
        response = self._send_command('PING')
        return 'PONG' in response

    def memory_info(self):
        """Get memory usage information."""
        info = self.get_info('memory')
        return {
            'used_memory': int(info.get('used_memory', 0)),
            'used_memory_human': info.get('used_memory_human', 'N/A'),
            'used_memory_peak_human': info.get('used_memory_peak_human', 'N/A'),
            'maxmemory': int(info.get('maxmemory', 0)),
            'maxmemory_human': info.get('maxmemory_human', 'N/A'),
            'maxmemory_policy': info.get('maxmemory_policy', 'N/A'),
            'mem_fragmentation_ratio': float(info.get('mem_fragmentation_ratio', 0)),
        }

    def persistence_info(self):
        """Get persistence (RDB/AOF) status."""
        info = self.get_info('persistence')
        return {
            'rdb_last_save_time': int(info.get('rdb_last_save_time', 0)),
            'rdb_last_bgsave_status': info.get('rdb_last_bgsave_status', 'N/A'),
            'rdb_changes_since_last_save': int(info.get('rdb_changes_since_last_save', 0)),
            'aof_enabled': info.get('aof_enabled', '0') == '1',
            'aof_last_bgrewrite_status': info.get('aof_last_bgrewrite_status', 'N/A'),
        }

    def replication_info(self):
        """Get replication status."""
        info = self.get_info('replication')
        return {
            'role': info.get('role', 'unknown'),
            'connected_slaves': int(info.get('connected_slaves', 0)),
            'master_link_status': info.get('master_link_status', 'N/A'),
        }

    def client_info(self):
        """Get client connection info."""
        info = self.get_info('clients')
        return {
            'connected_clients': int(info.get('connected_clients', 0)),
            'blocked_clients': int(info.get('blocked_clients', 0)),
            'maxclients': int(info.get('maxclients', 0)) if info.get('maxclients') else 10000,
        }

    def server_info(self):
        """Get basic server info."""
        info = self.get_info('server')
        return {
            'redis_version': info.get('redis_version', 'N/A'),
            'uptime_in_days': int(info.get('uptime_in_days', 0)),
            'tcp_port': int(info.get('tcp_port', self.port)),
        }

    def audit(self):
        """Run Redis health audit."""
        issues = []
        mem = self.memory_info()
        pers = self.persistence_info()
        repl = self.replication_info()
        clients = self.client_info()

        if mem['maxmemory'] > 0:
            usage = mem['used_memory'] / mem['maxmemory'] * 100
            if usage > 90:
                issues.append({'severity': 'critical', 'message': f"Memory usage at {usage:.0f}%"})
            elif usage > 75:
                issues.append({'severity': 'warning', 'message': f"Memory usage at {usage:.0f}%"})
        elif mem['maxmemory'] == 0:
            issues.append({'severity': 'warning', 'message': 'maxmemory not set (unbounded memory usage)'})

        if mem['mem_fragmentation_ratio'] > 1.5:
            issues.append({'severity': 'warning', 'message': f"High memory fragmentation: {mem['mem_fragmentation_ratio']}"})

        if pers['rdb_last_bgsave_status'] != 'ok':
            issues.append({'severity': 'critical', 'message': f"Last RDB save failed: {pers['rdb_last_bgsave_status']}"})

        if not pers['aof_enabled']:
            issues.append({'severity': 'info', 'message': 'AOF persistence disabled'})

        if repl['role'] == 'slave' and repl.get('master_link_status') != 'up':
            issues.append({'severity': 'critical', 'message': 'Replication link down'})

        max_c = clients.get('maxclients', 10000)
        if max_c and clients['connected_clients'] / max_c > 0.8:
            issues.append({'severity': 'warning', 'message': f"Client connections high: {clients['connected_clients']}/{max_c}"})

        return issues

    def print_report(self):
        """Print formatted Redis health report."""
        srv = self.server_info()
        mem = self.memory_info()
        pers = self.persistence_info()
        repl = self.replication_info()
        clients = self.client_info()
        issues = self.audit()

        print(f"\n{'='*60}")
        print(f"  Redis Health Report")
        print(f"{'='*60}")
        print(f"  Version: {srv['redis_version']}")
        print(f"  Uptime: {srv['uptime_in_days']} days")
        print(f"  Role: {repl['role']}")
        print(f"\n  Memory: {mem['used_memory_human']} / {mem['maxmemory_human']}")
        print(f"  Peak: {mem['used_memory_peak_human']}")
        print(f"  Fragmentation: {mem['mem_fragmentation_ratio']}")
        print(f"  Policy: {mem['maxmemory_policy']}")
        print(f"\n  Clients: {clients['connected_clients']} (blocked: {clients['blocked_clients']})")
        print(f"\n  RDB Status: {pers['rdb_last_bgsave_status']}")
        print(f"  AOF: {'enabled' if pers['aof_enabled'] else 'disabled'}")

        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in issues:
                print(f"    [{i['severity'].upper():8s}] {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["RedisHealth"]
