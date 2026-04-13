"""CLI for dargslan-ip-geo — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan IP Geo — IP geolocation and WHOIS lookup",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("ips", nargs="+", help="IP address(es) to look up")
    parser.add_argument("-w", "--whois", action="store_true", help="Include WHOIS data")
    parser.add_argument("-j", "--json", action="store_true", help="JSON output")
    parser.add_argument("-r", "--reverse", action="store_true", help="Reverse DNS only")
    args = parser.parse_args()

    from dargslan_ip_geo import IPGeo
    ig = IPGeo()
    import json as jsonlib

    if args.reverse:
        for ip in args.ips:
            r = ig.reverse_dns(ip.strip())
            print(f"  {r['ip']}: {r.get('hostname') or 'No PTR record'}")
    elif args.json:
        results = ig.bulk_lookup(args.ips)
        if args.whois:
            for r in results: r['whois'] = ig.whois(r.get('query', ''))
        print(jsonlib.dumps(results, indent=2))
    elif len(args.ips) == 1:
        ig.print_report(args.ips[0].strip())
        if args.whois:
            w = ig.whois(args.ips[0].strip())
            print("  WHOIS Data:")
            for k, v in (w.get('parsed', {}) or {}).items():
                print(f"    {k}: {v}")
    else:
        for ip in args.ips:
            ig.print_report(ip.strip())

if __name__ == "__main__": main()
