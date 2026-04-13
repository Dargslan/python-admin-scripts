"""CLI for dargslan-nginx-analyzer — https://dargslan.com"""

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Nginx Analyzer — Analyze Nginx configuration",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "servers", "ssl", "headers", "issues", "test", "json"],
                       help="Command (default: report)")
    parser.add_argument("-c", "--config", help="Nginx config path")
    args = parser.parse_args()

    from dargslan_nginx_analyzer import NginxAnalyzer
    na = NginxAnalyzer(config_path=args.config)

    import json

    if args.command == 'report':
        na.print_report()
    elif args.command == 'servers':
        for s in na.get_server_blocks():
            ssl = " [SSL]" if s['ssl'] else ""
            print(f"  {s['server_name']}{ssl} ({s['file']})")
    elif args.command == 'ssl':
        for i in na.check_ssl_config():
            print(f"  [{i['severity'].upper()}] {i['server']}: {i['message']}")
    elif args.command == 'headers':
        for i in na.check_security_headers():
            print(f"  [{i['severity'].upper()}] {i['server']}: {i['message']}")
    elif args.command == 'issues':
        for i in na.audit():
            print(f"  [{i['severity'].upper()}] {i['server']}: {i['message']}")
    elif args.command == 'test':
        result = na.test_config()
        print(f"  Valid: {result['valid']}")
        print(f"  Output: {result['output']}")
    elif args.command == 'json':
        print(json.dumps(na.audit(), indent=2))


if __name__ == "__main__":
    main()
