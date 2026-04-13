"""CLI for dargslan-iptables-export — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan iptables Export — Firewall rule exporter & documenter",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "readable", "json", "csv", "raw", "stats", "issues"],
                       help="Command (default: report)")
    parser.add_argument("-o", "--output", help="Output file path")
    args = parser.parse_args()

    from dargslan_iptables_export import IptablesExport
    ie = IptablesExport()

    if args.command == 'report': ie.print_report()
    elif args.command == 'readable':
        output = ie.export_readable()
        if args.output:
            with open(args.output, 'w') as f: f.write(output)
            print(f"  Exported to {args.output}")
        else:
            print(output)
    elif args.command == 'json':
        output = ie.export_json()
        if args.output:
            with open(args.output, 'w') as f: f.write(output)
            print(f"  Exported to {args.output}")
        else:
            print(output)
    elif args.command == 'csv':
        output = ie.export_csv()
        if args.output:
            with open(args.output, 'w') as f: f.write(output)
            print(f"  Exported to {args.output}")
        else:
            print(output)
    elif args.command == 'raw': print(ie.get_iptables_rules() or ie.get_nftables_rules())
    elif args.command == 'stats':
        import json as jsonlib
        print(jsonlib.dumps(ie.get_stats(), indent=2))
    elif args.command == 'issues':
        for i in ie.audit(): print(f"  [{i['severity'].upper()}] {i['message']}")

if __name__ == "__main__": main()
