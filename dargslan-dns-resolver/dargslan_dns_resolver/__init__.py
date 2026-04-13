"""
dargslan-dns-resolver — DNS Resolver Tester

Measure resolution time, test DNSSEC, compare resolvers, and detect DNS issues.
Zero external dependencies — uses socket and subprocess.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import socket
import subprocess
import time
import json
import re
import os


WELL_KNOWN_RESOLVERS = {
    '8.8.8.8': 'Google DNS',
    '8.8.4.4': 'Google DNS (secondary)',
    '1.1.1.1': 'Cloudflare DNS',
    '1.0.0.1': 'Cloudflare DNS (secondary)',
    '9.9.9.9': 'Quad9 DNS',
    '208.67.222.222': 'OpenDNS',
    '208.67.220.220': 'OpenDNS (secondary)',
}


class DNSResolver:
    """Test DNS resolver performance and configuration."""

    def __init__(self):
        pass

    def _run(self, args, timeout=10):
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
            return result.stdout.strip(), result.returncode
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return '', 1

    def get_system_resolvers(self):
        resolvers = []
        try:
            with open('/etc/resolv.conf', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('nameserver'):
                        parts = line.split()
                        if len(parts) >= 2:
                            ip = parts[1]
                            name = WELL_KNOWN_RESOLVERS.get(ip, '')
                            resolvers.append({'ip': ip, 'name': name})
        except (FileNotFoundError, PermissionError):
            pass
        return resolvers

    def resolve(self, hostname, record_type='A'):
        start = time.time()
        try:
            if record_type == 'A':
                results = socket.getaddrinfo(hostname, None, socket.AF_INET)
                ips = list(set(r[4][0] for r in results))
            elif record_type == 'AAAA':
                results = socket.getaddrinfo(hostname, None, socket.AF_INET6)
                ips = list(set(r[4][0] for r in results))
            else:
                ips = []

            elapsed = (time.time() - start) * 1000
            return {
                'hostname': hostname,
                'type': record_type,
                'results': ips,
                'time_ms': round(elapsed, 2),
                'success': True,
            }
        except socket.gaierror as e:
            elapsed = (time.time() - start) * 1000
            return {
                'hostname': hostname,
                'type': record_type,
                'error': str(e),
                'time_ms': round(elapsed, 2),
                'success': False,
            }

    def dig(self, hostname, record_type='A', server=None):
        args = ['dig', '+noall', '+answer', '+stats', hostname, record_type]
        if server:
            args.insert(1, f'@{server}')

        start = time.time()
        output, rc = self._run(args)
        elapsed = (time.time() - start) * 1000

        records = []
        query_time = None
        for line in output.split('\n'):
            if line.startswith(';; Query time:'):
                match = re.search(r'(\d+)\s+msec', line)
                if match:
                    query_time = int(match.group(1))
            elif line.strip() and not line.startswith(';'):
                records.append(line.strip())

        return {
            'hostname': hostname,
            'type': record_type,
            'server': server,
            'records': records,
            'query_time_ms': query_time,
            'total_time_ms': round(elapsed, 2),
            'success': rc == 0,
        }

    def benchmark_resolver(self, server, domains=None, rounds=3):
        if domains is None:
            domains = ['google.com', 'github.com', 'amazon.com', 'cloudflare.com', 'wikipedia.org']

        times = []
        for domain in domains:
            for _ in range(rounds):
                result = self.dig(domain, server=server)
                if result.get('query_time_ms') is not None:
                    times.append(result['query_time_ms'])
                elif result.get('total_time_ms'):
                    times.append(result['total_time_ms'])

        if not times:
            return {'server': server, 'error': 'No successful queries'}

        times.sort()
        return {
            'server': server,
            'name': WELL_KNOWN_RESOLVERS.get(server, ''),
            'queries': len(times),
            'avg_ms': round(sum(times) / len(times), 2),
            'min_ms': round(times[0], 2),
            'max_ms': round(times[-1], 2),
            'p50_ms': round(times[len(times) // 2], 2),
        }

    def compare_resolvers(self, servers=None):
        if servers is None:
            servers = ['8.8.8.8', '1.1.1.1', '9.9.9.9']
        results = []
        for server in servers:
            results.append(self.benchmark_resolver(server, rounds=2))
        results.sort(key=lambda x: x.get('avg_ms', 9999))
        return results

    def check_dnssec(self, hostname):
        output, rc = self._run(['dig', '+dnssec', '+short', hostname, 'A'])
        has_rrsig = 'RRSIG' in output or bool(re.search(r'\bRRSIG\b', output))

        output2, _ = self._run(['dig', '+noall', '+comments', hostname, 'A'])
        ad_flag = 'flags:' in output2 and ' ad' in output2

        return {
            'hostname': hostname,
            'dnssec_signed': has_rrsig,
            'ad_flag': ad_flag,
            'validated': ad_flag,
        }

    def reverse_lookup(self, ip):
        try:
            hostname = socket.gethostbyaddr(ip)
            return {'ip': ip, 'hostname': hostname[0], 'aliases': hostname[1]}
        except (socket.herror, socket.gaierror) as e:
            return {'ip': ip, 'error': str(e)}

    def check_resolv_conf(self):
        info = {'resolvers': self.get_system_resolvers()}
        content = ''
        try:
            with open('/etc/resolv.conf', 'r') as f:
                content = f.read()
        except (FileNotFoundError, PermissionError):
            pass

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('search ') or line.startswith('domain '):
                info['search_domains'] = line.split()[1:]
            if line.startswith('options '):
                info['options'] = line.split()[1:]

        is_symlink = os.path.islink('/etc/resolv.conf')
        info['is_symlink'] = is_symlink
        if is_symlink:
            info['symlink_target'] = os.readlink('/etc/resolv.conf')

        return info

    def audit(self):
        issues = []
        resolvers = self.get_system_resolvers()

        if not resolvers:
            issues.append({'severity': 'critical', 'message': 'No DNS resolvers configured'})
        elif len(resolvers) < 2:
            issues.append({'severity': 'warning', 'message': 'Only one DNS resolver configured — no redundancy'})

        for r in resolvers:
            result = self.resolve('google.com')
            if not result['success']:
                issues.append({'severity': 'critical', 'message': f"Resolver {r['ip']} failed to resolve google.com"})
            elif result['time_ms'] > 500:
                issues.append({'severity': 'warning', 'message': f"DNS resolution slow ({result['time_ms']}ms)"})

        return issues

    def print_report(self, domains=None):
        resolvers = self.get_system_resolvers()
        resolv_info = self.check_resolv_conf()
        issues = self.audit()

        print(f"\n{'='*60}")
        print(f"  DNS Resolver Report")
        print(f"{'='*60}")

        print(f"\n  System Resolvers ({len(resolvers)}):")
        for r in resolvers:
            name = f" ({r['name']})" if r['name'] else ''
            print(f"    {r['ip']}{name}")

        if resolv_info.get('search_domains'):
            print(f"  Search Domains: {' '.join(resolv_info['search_domains'])}")
        if resolv_info.get('is_symlink'):
            print(f"  resolv.conf -> {resolv_info.get('symlink_target', '?')}")

        test_domains = domains or ['google.com', 'github.com', 'dargslan.com']
        print(f"\n  Resolution Tests:")
        for d in test_domains:
            r = self.resolve(d)
            if r['success']:
                print(f"    {d}: {', '.join(r['results'][:3])} ({r['time_ms']}ms)")
            else:
                print(f"    {d}: FAILED — {r.get('error','')}")

        print(f"\n  Resolver Comparison:")
        comparison = self.compare_resolvers(rounds=1)
        for c in comparison:
            if c.get('error'):
                print(f"    {c['server']:>15s}: FAILED")
            else:
                name = f" ({c['name']})" if c.get('name') else ''
                print(f"    {c['server']:>15s}{name}: avg={c['avg_ms']}ms min={c['min_ms']}ms max={c['max_ms']}ms")

        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in issues:
                print(f"    [{i['severity'].upper():8s}] {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["DNSResolver"]
