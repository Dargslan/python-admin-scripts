"""CLI for dargslan-dns-resolver — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan DNS Resolver — DNS resolver tester",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "resolve", "dig", "compare", "dnssec", "reverse", "config", "issues", "json"],
                       help="Command (default: report)")
    parser.add_argument("targets", nargs="*", help="Hostnames or IPs")
    parser.add_argument("-s", "--server", help="DNS server to use")
    parser.add_argument("-t", "--type", default="A", help="Record type (A, AAAA, MX, etc.)")
    args = parser.parse_args()

    from dargslan_dns_resolver import DNSResolver
    dr = DNSResolver()
    import json

    targets = [t for t in args.targets if t not in ('report','resolve','dig','compare','dnssec','reverse','config','issues','json')]

    if args.command == 'report': dr.print_report(targets or None)
    elif args.command == 'resolve':
        for t in targets or ['google.com']:
            r = dr.resolve(t, args.type)
            if r['success']:
                print(f"  {t}: {', '.join(r['results'])} ({r['time_ms']}ms)")
            else:
                print(f"  {t}: FAILED — {r.get('error','')}")
    elif args.command == 'dig':
        for t in targets or ['google.com']:
            r = dr.dig(t, args.type, server=args.server)
            for rec in r['records']: print(f"  {rec}")
            if r.get('query_time_ms'): print(f"  Query time: {r['query_time_ms']}ms")
    elif args.command == 'compare':
        for c in dr.compare_resolvers(targets or None):
            if c.get('error'): print(f"  {c['server']}: FAILED")
            else: print(f"  {c['server']:>15s}: avg={c['avg_ms']}ms")
    elif args.command == 'dnssec':
        for t in targets or ['google.com']:
            r = dr.check_dnssec(t)
            print(f"  {t}: signed={r['dnssec_signed']} validated={r['validated']}")
    elif args.command == 'reverse':
        for t in targets:
            r = dr.reverse_lookup(t)
            print(f"  {t}: {r.get('hostname', r.get('error',''))}")
    elif args.command == 'config':
        c = dr.check_resolv_conf()
        for r in c['resolvers']: print(f"  Resolver: {r['ip']} {r.get('name','')}")
    elif args.command == 'issues':
        for i in dr.audit(): print(f"  [{i['severity'].upper()}] {i['message']}")
    elif args.command == 'json': print(json.dumps(dr.audit(), indent=2))

if __name__ == "__main__": main()
