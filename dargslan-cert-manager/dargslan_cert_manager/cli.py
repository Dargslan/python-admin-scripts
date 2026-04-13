"""CLI for dargslan-cert-manager — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Cert Manager — SSL/TLS certificate inventory manager",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "check", "file", "local", "issues", "json"],
                       help="Command (default: report)")
    parser.add_argument("hosts", nargs="*", help="Hostnames to check (host:port)")
    parser.add_argument("-f", "--cert-file", help="Certificate file path")
    args = parser.parse_args()

    from dargslan_cert_manager import CertManager
    cm = CertManager()
    import json

    hosts = [h for h in args.hosts if h not in ('report','check','file','local','issues','json')]

    if args.command == 'report': cm.print_report(hosts or None)
    elif args.command == 'check':
        for r in cm.bulk_check(hosts or []):
            days = r.get('days_until_expiry','?')
            print(f"  {r.get('hostname','')}: {days} days {'[EXPIRED]' if r.get('expired') else ''}")
    elif args.command == 'file':
        if args.cert_file:
            r = cm.check_file(args.cert_file)
            print(json.dumps(r, indent=2))
    elif args.command == 'local':
        for c in cm.find_local_certs(): print(f"  {c}")
    elif args.command == 'issues':
        for i in cm.audit(hosts or None): print(f"  [{i['severity'].upper()}] {i['message']}")
    elif args.command == 'json': print(json.dumps(cm.audit(hosts or None), indent=2))

if __name__ == "__main__": main()
