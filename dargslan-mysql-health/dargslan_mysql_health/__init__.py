"""
dargslan-mysql-health — MySQL/MariaDB Health Checker

Monitor MySQL/MariaDB server health, connections, slow queries, and replication.
Zero external dependencies — uses only Python standard library.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import subprocess
import json
import os
import re


class MySQLHealth:
    """Check MySQL/MariaDB server health and performance."""

    def __init__(self, host='localhost', port=3306, user=None, password=None, socket_path=None):
        self.host = host
        self.port = port
        self.user = user or os.environ.get('MYSQL_USER', 'root')
        self.password = password or os.environ.get('MYSQL_PASSWORD', '')
        self.socket_path = socket_path

    def _run_query(self, query):
        cmd = ['mysql', '-u', self.user, '-h', self.host, '-P', str(self.port),
               '--batch', '--skip-column-names', '-e', query]
        if self.password:
            cmd.extend(['-p' + self.password])
        if self.socket_path:
            cmd.extend(['-S', self.socket_path])
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                return result.stdout.strip()
            return ''
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ''

    def _run_query_dict(self, query):
        cmd = ['mysql', '-u', self.user, '-h', self.host, '-P', str(self.port),
               '--batch', '-e', query]
        if self.password:
            cmd.extend(['-p' + self.password])
        if self.socket_path:
            cmd.extend(['-S', self.socket_path])
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode != 0 or not result.stdout.strip():
                return []
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                return []
            headers = lines[0].split('\t')
            rows = []
            for line in lines[1:]:
                values = line.split('\t')
                rows.append(dict(zip(headers, values)))
            return rows
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []

    def is_running(self):
        """Check if MySQL is running."""
        try:
            result = subprocess.run(['mysqladmin', '-u', self.user, '-h', self.host, 'ping'],
                                  capture_output=True, text=True, timeout=10)
            return 'alive' in result.stdout.lower()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def server_info(self):
        """Get MySQL server version and basic info."""
        version = self._run_query("SELECT VERSION()")
        uptime = self._run_query("SHOW STATUS LIKE 'Uptime'")
        uptime_val = uptime.split('\t')[1] if '\t' in uptime else '0'
        return {
            'version': version,
            'uptime_seconds': int(uptime_val),
            'uptime_human': f"{int(uptime_val)//86400}d {(int(uptime_val)%86400)//3600}h",
        }

    def connection_status(self):
        """Get connection statistics."""
        max_conn = self._run_query("SHOW VARIABLES LIKE 'max_connections'")
        threads = self._run_query("SHOW STATUS LIKE 'Threads_connected'")
        max_used = self._run_query("SHOW STATUS LIKE 'Max_used_connections'")

        max_val = int(max_conn.split('\t')[1]) if '\t' in max_conn else 0
        current = int(threads.split('\t')[1]) if '\t' in threads else 0
        max_u = int(max_used.split('\t')[1]) if '\t' in max_used else 0

        return {
            'max_connections': max_val,
            'current_connections': current,
            'max_used_connections': max_u,
            'usage_percent': round(current / max_val * 100, 1) if max_val else 0,
        }

    def slow_queries(self):
        """Get slow query information."""
        slow_count = self._run_query("SHOW STATUS LIKE 'Slow_queries'")
        slow_log = self._run_query("SHOW VARIABLES LIKE 'slow_query_log'")
        long_time = self._run_query("SHOW VARIABLES LIKE 'long_query_time'")

        return {
            'slow_query_count': int(slow_count.split('\t')[1]) if '\t' in slow_count else 0,
            'slow_log_enabled': 'ON' in (slow_log.split('\t')[1] if '\t' in slow_log else ''),
            'long_query_time': float(long_time.split('\t')[1]) if '\t' in long_time else 10,
        }

    def database_sizes(self):
        """Get database sizes."""
        query = """SELECT table_schema AS db,
                   ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size_mb
                   FROM information_schema.tables
                   GROUP BY table_schema ORDER BY size_mb DESC"""
        rows = self._run_query_dict(query)
        return [{'database': r['db'], 'size_mb': float(r.get('size_mb', 0))} for r in rows]

    def replication_status(self):
        """Check replication status (if configured)."""
        rows = self._run_query_dict("SHOW SLAVE STATUS")
        if not rows:
            return {'configured': False}
        r = rows[0]
        return {
            'configured': True,
            'io_running': r.get('Slave_IO_Running', 'No'),
            'sql_running': r.get('Slave_SQL_Running', 'No'),
            'seconds_behind': int(r.get('Seconds_Behind_Master', 0) or 0),
            'last_error': r.get('Last_Error', ''),
        }

    def audit(self):
        """Run health audit and return issues."""
        issues = []
        conn = self.connection_status()
        if conn['usage_percent'] > 80:
            issues.append({'severity': 'warning', 'message': f"Connection usage at {conn['usage_percent']}%"})
        if conn['usage_percent'] > 95:
            issues.append({'severity': 'critical', 'message': f"Connection usage critically high: {conn['usage_percent']}%"})

        slow = self.slow_queries()
        if not slow['slow_log_enabled']:
            issues.append({'severity': 'info', 'message': 'Slow query log is disabled'})
        if slow['slow_query_count'] > 1000:
            issues.append({'severity': 'warning', 'message': f"{slow['slow_query_count']} slow queries recorded"})

        repl = self.replication_status()
        if repl['configured']:
            if repl['io_running'] != 'Yes' or repl['sql_running'] != 'Yes':
                issues.append({'severity': 'critical', 'message': 'Replication is broken!'})
            if repl.get('seconds_behind', 0) > 60:
                issues.append({'severity': 'warning', 'message': f"Replication lag: {repl['seconds_behind']}s behind master"})

        return issues

    def print_report(self):
        """Print formatted MySQL health report."""
        info = self.server_info()
        conn = self.connection_status()
        slow = self.slow_queries()
        issues = self.audit()

        print(f"\n{'='*60}")
        print(f"  MySQL/MariaDB Health Report")
        print(f"{'='*60}")
        print(f"  Version: {info['version']}")
        print(f"  Uptime: {info['uptime_human']}")
        print(f"\n  Connections: {conn['current_connections']}/{conn['max_connections']} ({conn['usage_percent']}%)")
        print(f"  Max Used: {conn['max_used_connections']}")
        print(f"\n  Slow Queries: {slow['slow_query_count']}")
        print(f"  Slow Log: {'ON' if slow['slow_log_enabled'] else 'OFF'}")

        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in issues:
                print(f"    [{i['severity'].upper()}] {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["MySQLHealth"]
