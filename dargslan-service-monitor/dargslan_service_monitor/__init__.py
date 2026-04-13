"""
dargslan-service-monitor — Systemd Service Monitor

Monitor systemd services, detect failed units, check service status.
Zero external dependencies — uses systemctl commands.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import subprocess
import json


class ServiceMonitor:
    """Monitor systemd services."""

    def _run(self, cmd, timeout=15):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result.stdout.strip(), result.returncode
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return '', 1

    def list_services(self):
        """List all systemd services with their status."""
        output, rc = self._run(['systemctl', 'list-units', '--type=service', '--all', '--no-pager', '--no-legend'])
        services = []
        if rc != 0 or not output:
            return services
        for line in output.split('\n'):
            parts = line.split()
            if len(parts) >= 4:
                name = parts[0].replace('.service', '')
                services.append({
                    'name': name,
                    'load': parts[1],
                    'active': parts[2],
                    'sub': parts[3],
                    'description': ' '.join(parts[4:]) if len(parts) > 4 else '',
                })
        return services

    def get_failed(self):
        """Get failed services."""
        output, rc = self._run(['systemctl', 'list-units', '--type=service', '--state=failed', '--no-pager', '--no-legend'])
        failed = []
        if not output:
            return failed
        for line in output.split('\n'):
            parts = line.split()
            if len(parts) >= 4:
                failed.append({
                    'name': parts[0].replace('.service', ''),
                    'load': parts[1],
                    'active': parts[2],
                    'sub': parts[3],
                    'description': ' '.join(parts[4:]) if len(parts) > 4 else '',
                })
        return failed

    def get_running(self):
        """Get running services."""
        return [s for s in self.list_services() if s['active'] == 'active' and s['sub'] == 'running']

    def get_enabled(self):
        """Get enabled services (start at boot)."""
        output, rc = self._run(['systemctl', 'list-unit-files', '--type=service', '--state=enabled', '--no-pager', '--no-legend'])
        enabled = []
        if not output:
            return enabled
        for line in output.split('\n'):
            parts = line.split()
            if len(parts) >= 2:
                enabled.append({
                    'name': parts[0].replace('.service', ''),
                    'state': parts[1],
                })
        return enabled

    def service_status(self, name):
        """Get detailed status of a specific service."""
        if not name.endswith('.service'):
            name += '.service'
        output, rc = self._run(['systemctl', 'show', name,
                                '--property=ActiveState,SubState,LoadState,MainPID,MemoryCurrent,CPUUsageNSec,ExecMainStartTimestamp,Description'])
        info = {'name': name.replace('.service', ''), 'found': rc == 0}
        if output:
            for line in output.split('\n'):
                if '=' in line:
                    key, val = line.split('=', 1)
                    info[key] = val
        return info

    def check_critical_services(self, services=None):
        """Check if critical services are running."""
        if services is None:
            services = ['sshd', 'ssh', 'nginx', 'apache2', 'httpd', 'mysql', 'mariadb',
                        'postgresql', 'docker', 'containerd', 'cron', 'rsyslog', 'firewalld', 'ufw']
        results = []
        running = {s['name'] for s in self.get_running()}
        for svc in services:
            results.append({
                'name': svc,
                'running': svc in running,
                'status': 'OK' if svc in running else 'DOWN',
            })
        return results

    def service_count(self):
        """Get service count by status."""
        services = self.list_services()
        counts = {'total': len(services)}
        for s in services:
            state = s['active']
            counts[state] = counts.get(state, 0) + 1
        return counts

    def print_report(self):
        """Print formatted service report."""
        counts = self.service_count()
        failed = self.get_failed()
        running = self.get_running()

        print(f"\n{'='*60}")
        print(f"  Systemd Service Monitor")
        print(f"{'='*60}")
        print(f"  Total services: {counts.get('total', 0)}")
        print(f"  Active:         {counts.get('active', 0)}")
        print(f"  Inactive:       {counts.get('inactive', 0)}")
        print(f"  Failed:         {counts.get('failed', 0)}")

        if failed:
            print(f"\n  [!] FAILED SERVICES ({len(failed)}):")
            for f_ in failed:
                print(f"    x {f_['name']:30s} {f_['description']}")

        print(f"\n  Running ({len(running)}):")
        for r in running[:20]:
            print(f"    + {r['name']:30s} {r['description'][:30]}")
        if len(running) > 20:
            print(f"    ... and {len(running)-20} more")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  Linux eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")

    def to_json(self):
        """Return service status as JSON."""
        return json.dumps({
            'counts': self.service_count(),
            'failed': self.get_failed(),
            'running': self.get_running(),
        }, indent=2)


__all__ = ["ServiceMonitor"]
