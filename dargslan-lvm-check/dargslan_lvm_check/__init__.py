"""
dargslan-lvm-check — LVM Volume Health Checker

Audit PV, VG, LV status, thin pool usage, and snapshot health.
Zero external dependencies — uses LVM CLI tools.

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


class LVMCheck:
    """Check LVM volume health and status."""

    def __init__(self):
        pass

    def _run(self, args):
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=15)
            return result.stdout.strip() if result.returncode == 0 else ''
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ''

    @staticmethod
    def _parse_size(size_str):
        if not size_str: return 0
        size_str = size_str.strip()
        multipliers = {'b': 1, 'k': 1024, 'm': 1024**2, 'g': 1024**3, 't': 1024**4}
        match = re.match(r'([\d.]+)\s*([bBkKmMgGtT])?', size_str)
        if match:
            val = float(match.group(1))
            unit = (match.group(2) or 'b').lower()
            return int(val * multipliers.get(unit, 1))
        return 0

    @staticmethod
    def _format_bytes(b):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if b < 1024: return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} PB"

    def get_pvs(self):
        output = self._run(['pvs', '--noheadings', '--nosuffix', '--units', 'b',
                            '-o', 'pv_name,vg_name,pv_size,pv_free,pv_attr', '--separator', '|'])
        pvs = []
        for line in output.split('\n'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 5:
                size = int(float(parts[2])) if parts[2] else 0
                free = int(float(parts[3])) if parts[3] else 0
                pvs.append({
                    'name': parts[0], 'vg': parts[1],
                    'size': size, 'free': free,
                    'size_human': self._format_bytes(size),
                    'free_human': self._format_bytes(free),
                    'attr': parts[4],
                    'used_percent': round((size - free) / size * 100, 1) if size else 0,
                })
        return pvs

    def get_vgs(self):
        output = self._run(['vgs', '--noheadings', '--nosuffix', '--units', 'b',
                            '-o', 'vg_name,pv_count,lv_count,vg_size,vg_free,vg_attr', '--separator', '|'])
        vgs = []
        for line in output.split('\n'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 6:
                size = int(float(parts[3])) if parts[3] else 0
                free = int(float(parts[4])) if parts[4] else 0
                vgs.append({
                    'name': parts[0],
                    'pv_count': int(parts[1]) if parts[1] else 0,
                    'lv_count': int(parts[2]) if parts[2] else 0,
                    'size': size, 'free': free,
                    'size_human': self._format_bytes(size),
                    'free_human': self._format_bytes(free),
                    'attr': parts[5],
                    'used_percent': round((size - free) / size * 100, 1) if size else 0,
                })
        return vgs

    def get_lvs(self):
        output = self._run(['lvs', '--noheadings', '--nosuffix', '--units', 'b',
                            '-o', 'lv_name,vg_name,lv_size,lv_attr,data_percent,pool_lv,origin', '--separator', '|'])
        lvs = []
        for line in output.split('\n'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 7:
                size = int(float(parts[2])) if parts[2] else 0
                lv = {
                    'name': parts[0], 'vg': parts[1],
                    'size': size, 'size_human': self._format_bytes(size),
                    'attr': parts[3],
                }
                if parts[4]: lv['data_percent'] = float(parts[4])
                if parts[5]: lv['pool'] = parts[5]
                if parts[6]: lv['origin'] = parts[6]

                attr = parts[3]
                if attr and len(attr) >= 1:
                    if attr[0] == 't': lv['type'] = 'thin-pool'
                    elif attr[0] == 'V': lv['type'] = 'thin'
                    elif attr[0] == 's': lv['type'] = 'snapshot'
                    elif attr[0] == '-': lv['type'] = 'linear'
                    else: lv['type'] = 'other'

                lvs.append(lv)
        return lvs

    def check_snapshots(self):
        lvs = self.get_lvs()
        snapshots = [lv for lv in lvs if lv.get('type') == 'snapshot' or lv.get('origin')]
        issues = []
        for snap in snapshots:
            if snap.get('data_percent', 0) > 80:
                issues.append({'severity': 'critical', 'lv': snap['name'],
                    'message': f"Snapshot {snap.get('data_percent')}% full — will become invalid at 100%"})
        return snapshots, issues

    def check_thin_pools(self):
        lvs = self.get_lvs()
        pools = [lv for lv in lvs if lv.get('type') == 'thin-pool']
        issues = []
        for pool in pools:
            if pool.get('data_percent', 0) > 85:
                issues.append({'severity': 'critical', 'pool': pool['name'],
                    'message': f"Thin pool {pool.get('data_percent')}% full"})
            elif pool.get('data_percent', 0) > 70:
                issues.append({'severity': 'warning', 'pool': pool['name'],
                    'message': f"Thin pool {pool.get('data_percent')}% full"})
        return pools, issues

    def audit(self):
        issues = []
        for vg in self.get_vgs():
            if vg['used_percent'] > 95:
                issues.append({'severity': 'critical', 'message': f"VG {vg['name']}: {vg['used_percent']}% used"})
            elif vg['used_percent'] > 85:
                issues.append({'severity': 'warning', 'message': f"VG {vg['name']}: {vg['used_percent']}% used"})

        _, snap_issues = self.check_snapshots()
        issues.extend(snap_issues)

        _, pool_issues = self.check_thin_pools()
        issues.extend(pool_issues)

        for pv in self.get_pvs():
            if 'm' in pv.get('attr', '').lower():
                issues.append({'severity': 'warning', 'message': f"PV {pv['name']}: missing flag set"})

        return issues

    def print_report(self):
        pvs = self.get_pvs()
        vgs = self.get_vgs()
        lvs = self.get_lvs()
        issues = self.audit()

        print(f"\n{'='*60}")
        print(f"  LVM Volume Health Report")
        print(f"{'='*60}")

        if pvs:
            print(f"\n  Physical Volumes ({len(pvs)}):")
            for pv in pvs:
                print(f"    {pv['name']} [{pv['vg']}]: {pv['size_human']} (free: {pv['free_human']})")

        if vgs:
            print(f"\n  Volume Groups ({len(vgs)}):")
            for vg in vgs:
                print(f"    {vg['name']}: {vg['size_human']} ({vg['used_percent']}% used, {vg['lv_count']} LVs)")

        if lvs:
            print(f"\n  Logical Volumes ({len(lvs)}):")
            for lv in lvs:
                extra = f" [{lv.get('type','')}]" if lv.get('type') else ''
                pct = f" data={lv['data_percent']}%" if 'data_percent' in lv else ''
                print(f"    {lv['vg']}/{lv['name']}: {lv['size_human']}{extra}{pct}")
        else:
            print("\n  No LVM volumes found.")

        if issues:
            print(f"\n  Issues ({len(issues)}):")
            for i in issues:
                print(f"    [{i['severity'].upper():8s}] {i['message']}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")


__all__ = ["LVMCheck"]
