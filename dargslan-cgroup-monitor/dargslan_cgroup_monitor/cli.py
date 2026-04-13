"""CLI for dargslan-cgroup-monitor — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Cgroup Monitor — Linux cgroup resource monitor",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "list", "slices", "containers", "issues", "json"],
                       help="Command (default: report)")
    args = parser.parse_args()

    from dargslan_cgroup_monitor import CgroupMonitor
    cm = CgroupMonitor()
    import json

    if args.command == 'report': cm.print_report()
    elif args.command == 'list':
        for cg in cm.list_cgroups(): print(f"  {cg['path']} ({cg['procs']} procs) mem={cg.get('memory_human','N/A')}")
    elif args.command == 'slices':
        for s in cm.get_system_slices(): print(f"  {s['path']} ({s['procs']} procs)")
    elif args.command == 'containers':
        for c in cm.get_container_cgroups(): print(f"  {c['path']} mem={c.get('memory_human','N/A')}")
    elif args.command == 'issues':
        for i in cm.audit(): print(f"  [{i['severity'].upper()}] {i['cgroup']}: {i['message']}")
    elif args.command == 'json': print(json.dumps(cm.list_cgroups(), indent=2, default=str))

if __name__ == "__main__": main()
