"""CLI interface for dargslan-hostname-info."""

import sys
from dargslan_hostname_info import generate_report, get_hostname, get_fqdn, get_all_ips, reverse_dns, resolve_hostname, get_hosts_file


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "report"

    if cmd == "report":
        print(generate_report())
    elif cmd == "hostname":
        print(get_hostname())
    elif cmd == "fqdn":
        print(get_fqdn())
    elif cmd == "ips":
        for ip in get_all_ips():
            print(f"  {ip['family']:4s} {ip['ip']}")
    elif cmd == "reverse":
        if len(args) < 2:
            print("Usage: dargslan-hostname reverse <ip>")
            sys.exit(1)
        result = reverse_dns(args[1])
        if result:
            print(f"Hostname: {result['hostname']}")
            if result['aliases']:
                print(f"Aliases: {', '.join(result['aliases'])}")
        else:
            print(f"No reverse DNS found for {args[1]}")
    elif cmd == "resolve":
        if len(args) < 2:
            print("Usage: dargslan-hostname resolve <hostname>")
            sys.exit(1)
        results = resolve_hostname(args[1])
        if results:
            for r in results:
                print(f"  {r['family']:4s} {r['ip']}")
        else:
            print(f"Cannot resolve {args[1]}")
    elif cmd == "hosts":
        for h in get_hosts_file():
            print(f"  {h['ip']:20s} {' '.join(h['hostnames'])}")
    elif cmd in ("help", "--help", "-h"):
        print("dargslan-hostname — Hostname & domain resolver")
        print("Usage: dargslan-hostname [command]")
        print("Commands: report, hostname, fqdn, ips, reverse <ip>, resolve <host>, hosts")
        print("More: https://dargslan.com")
    else:
        print(f"Unknown command: {cmd}. Use --help for usage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
