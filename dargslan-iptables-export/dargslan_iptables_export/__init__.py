"""
dargslan-iptables-export — Firewall Rule Exporter & Documenter

Export iptables/nftables rules to readable, shareable formats.
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
import re
import os
from datetime import datetime


class IptablesExport:
    """Export and document iptables/nftables firewall rules."""

    def __init__(self):
        self.backend = self._detect_backend()

    def _detect_backend(self):
        for cmd, name in [('nft', 'nftables'), ('iptables', 'iptables')]:
            try:
                subprocess.run([cmd, '--version'], capture_output=True, timeout=5)
                return name
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        return 'unknown'

    def _run(self, args):
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=15)
            return result.stdout.strip() if result.returncode == 0 else ''
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ''

    def get_iptables_rules(self):
        output = self._run(['iptables', '-L', '-n', '-v', '--line-numbers'])
        return output

    def get_iptables_save(self):
        output = self._run(['iptables-save'])
        return output

    def get_nftables_rules(self):
        output = self._run(['nft', 'list', 'ruleset'])
        return output

    def get_ip6tables_rules(self):
        output = self._run(['ip6tables', '-L', '-n', '-v', '--line-numbers'])
        return output

    def get_all_rules(self):
        rules = {'backend': self.backend, 'timestamp': datetime.now().isoformat()}

        if self.backend == 'nftables':
            rules['nftables'] = self.get_nftables_rules()
        rules['iptables'] = self.get_iptables_rules()
        rules['iptables_save'] = self.get_iptables_save()
        rules['ip6tables'] = self.get_ip6tables_rules()
        return rules

    def parse_iptables_rules(self):
        output = self.get_iptables_save()
        if not output: return []

        parsed = []
        current_table = ''
        for line in output.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'): continue
            if line.startswith('*'):
                current_table = line[1:]
                continue
            if line == 'COMMIT': continue
            if line.startswith(':'):
                parts = line.split()
                parsed.append({
                    'table': current_table,
                    'type': 'policy',
                    'chain': parts[0][1:],
                    'policy': parts[1],
                    'raw': line,
                })
            elif line.startswith('-A'):
                rule = {'table': current_table, 'type': 'rule', 'raw': line}
                parts = line.split()
                if len(parts) >= 2: rule['chain'] = parts[1]

                for i, p in enumerate(parts):
                    if p == '-s' and i + 1 < len(parts): rule['source'] = parts[i+1]
                    if p == '-d' and i + 1 < len(parts): rule['dest'] = parts[i+1]
                    if p == '-p' and i + 1 < len(parts): rule['protocol'] = parts[i+1]
                    if p == '--dport' and i + 1 < len(parts): rule['dport'] = parts[i+1]
                    if p == '--sport' and i + 1 < len(parts): rule['sport'] = parts[i+1]
                    if p == '-j' and i + 1 < len(parts): rule['target'] = parts[i+1]
                    if p == '-i' and i + 1 < len(parts): rule['in_iface'] = parts[i+1]
                    if p == '-o' and i + 1 < len(parts): rule['out_iface'] = parts[i+1]
                    if p == '-m' and i + 1 < len(parts): rule.setdefault('modules', []).append(parts[i+1])

                parsed.append(rule)
        return parsed

    def export_readable(self):
        rules = self.parse_iptables_rules()
        lines = []
        lines.append(f"# Firewall Rules Export")
        lines.append(f"# Generated: {datetime.now().isoformat()}")
        lines.append(f"# Backend: {self.backend}")
        lines.append(f"# Total rules: {len([r for r in rules if r['type'] == 'rule'])}")
        lines.append("")

        current_table = ''
        current_chain = ''
        for r in rules:
            if r['table'] != current_table:
                current_table = r['table']
                lines.append(f"\n## Table: {current_table}")
                lines.append("=" * 50)

            if r['type'] == 'policy':
                lines.append(f"\n### Chain: {r['chain']} (Policy: {r['policy']})")
                lines.append("-" * 40)
                current_chain = r['chain']
            elif r['type'] == 'rule':
                desc = []
                if r.get('protocol'): desc.append(f"proto={r['protocol']}")
                if r.get('source'): desc.append(f"src={r['source']}")
                if r.get('dest'): desc.append(f"dst={r['dest']}")
                if r.get('dport'): desc.append(f"dport={r['dport']}")
                if r.get('sport'): desc.append(f"sport={r['sport']}")
                if r.get('in_iface'): desc.append(f"in={r['in_iface']}")
                if r.get('out_iface'): desc.append(f"out={r['out_iface']}")
                target = r.get('target', 'N/A')
                desc_str = ', '.join(desc) if desc else 'match-all'
                lines.append(f"  [{target:8s}] {desc_str}")

        return '\n'.join(lines)

    def export_json(self):
        return json.dumps(self.parse_iptables_rules(), indent=2)

    def export_csv(self):
        rules = self.parse_iptables_rules()
        lines = ['table,chain,type,protocol,source,dest,dport,sport,target,raw']
        for r in rules:
            if r['type'] != 'rule': continue
            lines.append(','.join([
                r.get('table',''), r.get('chain',''), r['type'],
                r.get('protocol',''), r.get('source',''), r.get('dest',''),
                r.get('dport',''), r.get('sport',''), r.get('target',''),
                f'"{r.get("raw","")}"'
            ]))
        return '\n'.join(lines)

    def get_stats(self):
        rules = self.parse_iptables_rules()
        actual_rules = [r for r in rules if r['type'] == 'rule']
        tables = set(r['table'] for r in rules)
        chains = set(r['chain'] for r in rules)
        targets = {}
        for r in actual_rules:
            t = r.get('target', 'N/A')
            targets[t] = targets.get(t, 0) + 1
        return {
            'backend': self.backend,
            'total_rules': len(actual_rules),
            'tables': list(tables),
            'chains': list(chains),
            'targets': targets,
        }

    def audit(self):
        issues = []
        rules = self.parse_iptables_rules()
        actual_rules = [r for r in rules if r['type'] == 'rule']

        policies = {r['chain']: r['policy'] for r in rules if r['type'] == 'policy' and r['table'] == 'filter'}
        if policies.get('INPUT') == 'ACCEPT':
            issues.append({'severity': 'warning', 'message': 'INPUT chain default policy is ACCEPT (should be DROP)'})
        if policies.get('FORWARD') == 'ACCEPT':
            issues.append({'severity': 'info', 'message': 'FORWARD chain default policy is ACCEPT'})

        for r in actual_rules:
            if r.get('source') == '0.0.0.0/0' and r.get('dest') == '0.0.0.0/0' and r.get('target') == 'ACCEPT':
                if not r.get('protocol') and not r.get('dport'):
                    issues.append({'severity': 'warning', 'message': f"Overly permissive rule in {r.get('chain','')}"})

        if len(actual_rules) == 0:
            issues.append({'severity': 'info', 'message': 'No firewall rules configured'})

        return issues

    def print_report(self):
        stats = self.get_stats()
        issues = self.audit()

        print(f"\n{'='*60}")
        print(f"  Firewall Rules Export Report")
        print(f"  Backend: {stats['backend']}")
        print(f"{'='*60}")
        print(f"\n  Total Rules: {stats['total_rules']}")
        print(f"  Tables: {', '.join(stats['tables'])}")
        print(f"  Chains: {len(stats['chains'])}")
        print(f"\n  Targets:")
        for t, c in sorted(stats['targets'].items(), key=lambda x: -x[1]):
            print(f"    {t:15s} {c}")

        print(f"\n{self.export_readable()}")

        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in issues:
                print(f"    [{i['severity'].upper():8s}] {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["IptablesExport"]
