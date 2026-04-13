"""CLI for dargslan-package-audit — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Package Audit — Linux package auditor",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "upgradable", "security", "orphans", "count", "issues", "json"],
                       help="Command (default: report)")
    args = parser.parse_args()

    from dargslan_package_audit import PackageAudit
    pa = PackageAudit()
    import json

    if args.command == 'report': pa.print_report()
    elif args.command == 'upgradable':
        for p in pa.check_upgradable(): print(f"  {p['name']}")
    elif args.command == 'security':
        for s in pa.check_security_updates(): print(f"  [!!] {s['name']}")
    elif args.command == 'orphans':
        for o in pa.check_auto_removable(): print(f"  {o['name']}")
    elif args.command == 'count': print(f"  Installed: {pa.count_installed()}")
    elif args.command == 'issues':
        for i in pa.audit(): print(f"  [{i['severity'].upper()}] {i['message']}")
    elif args.command == 'json': print(json.dumps(pa.audit(), indent=2))

if __name__ == "__main__": main()
