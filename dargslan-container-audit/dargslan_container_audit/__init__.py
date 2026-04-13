"""
dargslan-container-audit — Container Security Auditor

Audit Docker/Podman containers for security issues and best practices.
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


class ContainerAudit:
    """Audit Docker/Podman containers for security issues."""

    DANGEROUS_CAPABILITIES = [
        'SYS_ADMIN', 'NET_ADMIN', 'SYS_PTRACE', 'SYS_RAWIO',
        'DAC_OVERRIDE', 'SETUID', 'SETGID', 'NET_RAW',
    ]

    def __init__(self, runtime=None):
        if runtime:
            self.runtime = runtime
        elif self._cmd_exists('docker'):
            self.runtime = 'docker'
        elif self._cmd_exists('podman'):
            self.runtime = 'podman'
        else:
            self.runtime = 'docker'

    def _cmd_exists(self, cmd):
        try:
            subprocess.run([cmd, '--version'], capture_output=True, timeout=5)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _run(self, args):
        try:
            result = subprocess.run(
                [self.runtime] + args,
                capture_output=True, text=True, timeout=30
            )
            return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ''

    def _run_json(self, args):
        output = self._run(args)
        if not output:
            return []
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return []

    def list_containers(self, all_containers=True):
        """List all containers with status."""
        fmt = '{"id":"{{.ID}}","name":"{{.Names}}","image":"{{.Image}}","status":"{{.Status}}","state":"{{.State}}","ports":"{{.Ports}}"}'
        args = ['ps', '--format', fmt]
        if all_containers:
            args.append('-a')
        output = self._run(args)
        if not output:
            return []
        containers = []
        for line in output.strip().split('\n'):
            if line.strip():
                try:
                    containers.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return containers

    def inspect_container(self, container_id):
        """Get detailed container inspection data."""
        data = self._run_json(['inspect', container_id])
        return data[0] if data else {}

    def check_privileged(self):
        """Find containers running in privileged mode."""
        containers = self.list_containers()
        privileged = []
        for c in containers:
            info = self.inspect_container(c['id'])
            if info:
                host_config = info.get('HostConfig', {})
                if host_config.get('Privileged', False):
                    privileged.append({
                        'name': c.get('name', c['id']),
                        'image': c.get('image', 'unknown'),
                        'issue': 'Running in privileged mode',
                    })
        return privileged

    def check_root_containers(self):
        """Find containers running as root user."""
        containers = self.list_containers()
        root_containers = []
        for c in containers:
            info = self.inspect_container(c['id'])
            if info:
                config = info.get('Config', {})
                user = config.get('User', '')
                if not user or user == 'root' or user == '0':
                    root_containers.append({
                        'name': c.get('name', c['id']),
                        'image': c.get('image', 'unknown'),
                        'user': user or 'root (default)',
                    })
        return root_containers

    def check_capabilities(self):
        """Check containers for dangerous capabilities."""
        containers = self.list_containers()
        issues = []
        for c in containers:
            info = self.inspect_container(c['id'])
            if info:
                host_config = info.get('HostConfig', {})
                cap_add = host_config.get('CapAdd') or []
                dangerous = [cap for cap in cap_add if cap in self.DANGEROUS_CAPABILITIES]
                if dangerous:
                    issues.append({
                        'name': c.get('name', c['id']),
                        'dangerous_caps': dangerous,
                    })
        return issues

    def check_volumes(self):
        """Check for sensitive host mounts."""
        sensitive_paths = ['/etc', '/var/run/docker.sock', '/proc', '/sys', '/root', '/']
        containers = self.list_containers()
        issues = []
        for c in containers:
            info = self.inspect_container(c['id'])
            if info:
                mounts = info.get('Mounts', [])
                for m in mounts:
                    source = m.get('Source', '')
                    for sp in sensitive_paths:
                        if source == sp or (sp != '/' and source.startswith(sp)):
                            issues.append({
                                'name': c.get('name', c['id']),
                                'mount': f"{source} -> {m.get('Destination', '?')}",
                                'mode': m.get('Mode', 'rw'),
                            })
        return issues

    def check_network_mode(self):
        """Check for containers using host network."""
        containers = self.list_containers()
        host_network = []
        for c in containers:
            info = self.inspect_container(c['id'])
            if info:
                net_mode = info.get('HostConfig', {}).get('NetworkMode', '')
                if net_mode == 'host':
                    host_network.append({
                        'name': c.get('name', c['id']),
                        'network_mode': 'host',
                    })
        return host_network

    def audit(self):
        """Run full container security audit."""
        issues = []
        for item in self.check_privileged():
            issues.append({'severity': 'critical', 'category': 'privileged', 'message': f"{item['name']}: {item['issue']}"})
        for item in self.check_root_containers():
            issues.append({'severity': 'warning', 'category': 'root_user', 'message': f"{item['name']}: Running as {item['user']}"})
        for item in self.check_capabilities():
            issues.append({'severity': 'high', 'category': 'capabilities', 'message': f"{item['name']}: Dangerous caps: {', '.join(item['dangerous_caps'])}"})
        for item in self.check_volumes():
            issues.append({'severity': 'high', 'category': 'volumes', 'message': f"{item['name']}: Sensitive mount {item['mount']} ({item['mode']})"})
        for item in self.check_network_mode():
            issues.append({'severity': 'warning', 'category': 'network', 'message': f"{item['name']}: Using host network mode"})
        return issues

    def print_report(self):
        """Print a formatted container audit report."""
        containers = self.list_containers()
        issues = self.audit()

        print(f"\n{'='*60}")
        print(f"  Container Security Audit Report")
        print(f"  Runtime: {self.runtime}")
        print(f"{'='*60}")
        print(f"\n  Containers: {len(containers)}")

        running = [c for c in containers if c.get('state') == 'running']
        stopped = [c for c in containers if c.get('state') != 'running']
        print(f"  Running: {len(running)}, Stopped: {len(stopped)}")

        if issues:
            print(f"\n  Security Issues ({len(issues)}):")
            for i in sorted(issues, key=lambda x: {'critical':0,'high':1,'warning':2}.get(x['severity'],3)):
                icon = {'critical':'!!','high':'!','warning':'~'}.get(i['severity'],'?')
                print(f"  [{icon}] [{i['severity'].upper():8s}] {i['message']}")
        else:
            print("\n  No security issues found.")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["ContainerAudit"]
