"""CLI for dargslan-firewall-audit — https://dargslan.com"""
import argparse
import json
from dargslan_firewall_audit.audit import FirewallAudit

def main():
    parser = argparse.ArgumentParser(description="Firewall Audit — dargslan.com")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--fix", action="store_true", help="Show fix suggestions")
    args = parser.parse_args()

    audit = FirewallAudit()
    if args.json:
        print(json.dumps(audit.full_audit(), indent=2, default=str))
    else:
        audit.print_audit()

if __name__ == "__main__":
    main()
