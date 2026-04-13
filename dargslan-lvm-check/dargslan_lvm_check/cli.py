"""CLI for dargslan-lvm-check — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan LVM Check — LVM volume health checker",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "pvs", "vgs", "lvs", "snapshots", "thin", "issues", "json"],
                       help="Command (default: report)")
    args = parser.parse_args()

    from dargslan_lvm_check import LVMCheck
    lc = LVMCheck()
    import json

    if args.command == 'report': lc.print_report()
    elif args.command == 'pvs':
        for pv in lc.get_pvs(): print(f"  {pv['name']} [{pv['vg']}]: {pv['size_human']} free={pv['free_human']}")
    elif args.command == 'vgs':
        for vg in lc.get_vgs(): print(f"  {vg['name']}: {vg['size_human']} ({vg['used_percent']}% used)")
    elif args.command == 'lvs':
        for lv in lc.get_lvs(): print(f"  {lv['vg']}/{lv['name']}: {lv['size_human']} [{lv.get('type','')}]")
    elif args.command == 'snapshots':
        snaps, _ = lc.check_snapshots()
        for s in snaps: print(f"  {s['name']} (origin: {s.get('origin','')}) data={s.get('data_percent',0)}%")
    elif args.command == 'thin':
        pools, _ = lc.check_thin_pools()
        for p in pools: print(f"  {p['name']}: data={p.get('data_percent',0)}%")
    elif args.command == 'issues':
        for i in lc.audit(): print(f"  [{i['severity'].upper()}] {i['message']}")
    elif args.command == 'json': print(json.dumps(lc.audit(), indent=2))

if __name__ == "__main__": main()
