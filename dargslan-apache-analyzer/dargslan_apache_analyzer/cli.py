"""CLI for dargslan-apache-analyzer — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Apache Analyzer — Apache HTTP Server config analyzer",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "vhosts", "modules", "issues", "test", "json"],
                       help="Command (default: report)")
    parser.add_argument("-c", "--config", help="Apache config path")
    args = parser.parse_args()

    from dargslan_apache_analyzer import ApacheAnalyzer
    aa = ApacheAnalyzer(config_path=args.config)
    import json

    if args.command == 'report': aa.print_report()
    elif args.command == 'vhosts':
        for v in aa.get_vhosts():
            ssl = " [SSL]" if v['ssl'] else ""
            print(f"  {v['server_name']}{ssl} ({v['file']})")
    elif args.command == 'modules':
        for m in aa.get_loaded_modules(): print(f"  {m}")
    elif args.command == 'issues':
        for i in aa.check_security(): print(f"  [{i['severity'].upper()}] {i['message']}")
    elif args.command == 'test':
        r = aa.test_config()
        print(f"  Valid: {r['valid']}\n  {r['output']}")
    elif args.command == 'json': print(json.dumps(aa.check_security(), indent=2))

if __name__ == "__main__": main()
