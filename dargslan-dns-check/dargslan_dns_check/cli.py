"""CLI for dargslan-dns-check — https://dargslan.com"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Dargslan DNS Checker — Query and analyze DNS records",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("domain", help="Domain to query")
    parser.add_argument("-t", "--type", default="all", help="Record type: A, AAAA, MX, NS, TXT, CNAME, SOA, all (default: all)")
    parser.add_argument("-j", "--json", action="store_true", help="JSON output")
    parser.add_argument("-n", "--nameserver", default="8.8.8.8", help="DNS nameserver (default: 8.8.8.8)")
    parser.add_argument("-p", "--propagation", action="store_true", help="Check DNS propagation")
    parser.add_argument("-r", "--reverse", action="store_true", help="Reverse DNS lookup (domain = IP)")
    args = parser.parse_args()

    from dargslan_dns_check import DNSChecker
    checker = DNSChecker(nameserver=args.nameserver)

    if args.reverse:
        import json
        result = checker.reverse_lookup(args.domain)
        print(json.dumps(result, indent=2))
    elif args.propagation:
        import json
        results = checker.check_propagation(args.domain, args.type if args.type != 'all' else 'A')
        print(json.dumps(results, indent=2, default=str))
    elif args.json:
        print(checker.to_json(args.domain))
    elif args.type.upper() == 'ALL':
        checker.print_report(args.domain)
    else:
        import json
        records = checker.query(args.domain, args.type)
        print(json.dumps(records, indent=2, default=str))


if __name__ == "__main__":
    main()
