"""
dargslan-postgres-health — PostgreSQL Health Checker

Monitor connections, bloat, vacuum status, locks, and replication lag.
Zero external dependencies — uses only Python standard library + psql CLI.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import subprocess
import os
import json


class PostgresHealth:
    """Check PostgreSQL server health and performance."""

    def __init__(self, host='localhost', port=5432, user=None, dbname=None, password=None):
        self.host = host
        self.port = port
        self.user = user or os.environ.get('PGUSER', 'postgres')
        self.dbname = dbname or os.environ.get('PGDATABASE', 'postgres')
        self.password = password or os.environ.get('PGPASSWORD', '')

    def _run_query(self, query):
        env = os.environ.copy()
        if self.password: env['PGPASSWORD'] = self.password
        cmd = ['psql', '-h', self.host, '-p', str(self.port), '-U', self.user,
               '-d', self.dbname, '-t', '-A', '-c', query]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15, env=env)
            return result.stdout.strip() if result.returncode == 0 else ''
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ''

    def _query_rows(self, query):
        env = os.environ.copy()
        if self.password: env['PGPASSWORD'] = self.password
        cmd = ['psql', '-h', self.host, '-p', str(self.port), '-U', self.user,
               '-d', self.dbname, '-t', '-A', '-F', '\t', '-c', query]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15, env=env)
            if result.returncode != 0: return []
            rows = []
            for line in result.stdout.strip().split('\n'):
                if line.strip(): rows.append(line.split('\t'))
            return rows
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []

    def server_info(self):
        """Get PostgreSQL version and uptime."""
        version = self._run_query("SELECT version()")
        uptime = self._run_query("SELECT now() - pg_postmaster_start_time()")
        return {'version': version, 'uptime': uptime}

    def connection_status(self):
        """Get connection statistics."""
        max_conn = self._run_query("SHOW max_connections")
        active = self._run_query("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
        total = self._run_query("SELECT count(*) FROM pg_stat_activity")
        idle = self._run_query("SELECT count(*) FROM pg_stat_activity WHERE state = 'idle'")

        max_c = int(max_conn) if max_conn and max_conn.isdigit() else 100
        total_c = int(total) if total and total.isdigit() else 0

        return {
            'max_connections': max_c,
            'total_connections': total_c,
            'active': int(active) if active and active.isdigit() else 0,
            'idle': int(idle) if idle and idle.isdigit() else 0,
            'usage_percent': round(total_c / max_c * 100, 1) if max_c else 0,
        }

    def database_sizes(self):
        """Get database sizes."""
        rows = self._query_rows("SELECT datname, pg_database_size(datname)/1024/1024 as size_mb FROM pg_database WHERE datistemplate = false ORDER BY size_mb DESC")
        return [{'database': r[0], 'size_mb': float(r[1])} for r in rows if len(r) >= 2]

    def table_bloat(self):
        """Check for table bloat (simplified)."""
        rows = self._query_rows("""SELECT schemaname||'.'||relname, n_dead_tup, n_live_tup,
            CASE WHEN n_live_tup > 0 THEN round(n_dead_tup::numeric/n_live_tup*100,1) ELSE 0 END as dead_pct
            FROM pg_stat_user_tables WHERE n_dead_tup > 1000 ORDER BY n_dead_tup DESC LIMIT 10""")
        return [{'table': r[0], 'dead_tuples': int(r[1]), 'live_tuples': int(r[2]),
                 'dead_percent': float(r[3])} for r in rows if len(r) >= 4]

    def vacuum_status(self):
        """Check last vacuum/analyze times."""
        rows = self._query_rows("""SELECT schemaname||'.'||relname, last_vacuum, last_autovacuum,
            last_analyze, last_autoanalyze
            FROM pg_stat_user_tables ORDER BY COALESCE(last_autovacuum, '1970-01-01'::timestamp) LIMIT 10""")
        return [{'table': r[0], 'last_vacuum': r[1] or 'never', 'last_autovacuum': r[2] or 'never',
                 'last_analyze': r[3] or 'never'} for r in rows if len(r) >= 5]

    def active_locks(self):
        """Check for blocking locks."""
        count = self._run_query("SELECT count(*) FROM pg_locks WHERE NOT granted")
        return int(count) if count and count.isdigit() else 0

    def replication_status(self):
        """Check replication status."""
        rows = self._query_rows("SELECT client_addr, state, sent_lsn, replay_lsn FROM pg_stat_replication")
        if not rows:
            return {'configured': False}
        replicas = [{'client': r[0], 'state': r[1], 'sent_lsn': r[2], 'replay_lsn': r[3]}
                    for r in rows if len(r) >= 4]
        return {'configured': True, 'replicas': replicas}

    def long_running_queries(self):
        """Find long-running queries."""
        rows = self._query_rows("""SELECT pid, now()-query_start as duration, state, left(query,80)
            FROM pg_stat_activity WHERE state != 'idle' AND query_start < now()-interval '30 seconds'
            ORDER BY duration DESC LIMIT 5""")
        return [{'pid': int(r[0]), 'duration': r[1], 'state': r[2], 'query': r[3]}
                for r in rows if len(r) >= 4]

    def audit(self):
        """Run PostgreSQL health audit."""
        issues = []
        conn = self.connection_status()
        if conn['usage_percent'] > 80:
            issues.append({'severity': 'warning', 'message': f"Connection usage at {conn['usage_percent']}%"})
        if conn['usage_percent'] > 95:
            issues.append({'severity': 'critical', 'message': f"Connection usage critical: {conn['usage_percent']}%"})

        bloat = self.table_bloat()
        for t in bloat:
            if t['dead_percent'] > 20:
                issues.append({'severity': 'warning', 'message': f"Table {t['table']} has {t['dead_percent']}% dead tuples"})

        locks = self.active_locks()
        if locks > 5:
            issues.append({'severity': 'warning', 'message': f"{locks} waiting locks detected"})

        long_q = self.long_running_queries()
        if long_q:
            issues.append({'severity': 'info', 'message': f"{len(long_q)} long-running queries detected"})

        return issues

    def print_report(self):
        """Print formatted PostgreSQL health report."""
        srv = self.server_info()
        conn = self.connection_status()
        issues = self.audit()

        print(f"\n{'='*60}")
        print(f"  PostgreSQL Health Report")
        print(f"{'='*60}")
        print(f"  Version: {srv['version'][:60]}")
        print(f"  Uptime: {srv['uptime']}")
        print(f"\n  Connections: {conn['total_connections']}/{conn['max_connections']} ({conn['usage_percent']}%)")
        print(f"  Active: {conn['active']}, Idle: {conn['idle']}")
        print(f"  Waiting Locks: {self.active_locks()}")

        dbs = self.database_sizes()
        if dbs:
            print(f"\n  Databases:")
            for db in dbs[:5]:
                print(f"    {db['database']:30s} {db['size_mb']:>10.1f} MB")

        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in issues:
                print(f"    [{i['severity'].upper():8s}] {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["PostgresHealth"]
