"""CLI for dargslan-ssl-checker — https://dargslan.com"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Dargslan SSL Checker — Check SSL/TLS certificates",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("domains", nargs="+", help="Domain(s) to check")
    parser.add_argument("-p", "--port", type=int, default=443, help="Port (default: 443)")
    parser.add_argument("-j", "--json", action="store_true", help="JSON output")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Timeout in seconds")
    args = parser.parse_args()

    from dargslan_ssl_checker import SSLChecker
    checker = SSLChecker(timeout=args.timeout)

    if args.json:
        import json
        results = checker.check_multiple(args.domains, args.port)
        print(json.dumps(results, indent=2))
    else:
        for domain in args.domains:
            checker.print_report(domain.strip(), args.port)


if __name__ == "__main__":
    main()
