"""CLI for dargslan-network-latency."""

import sys
import json
from . import generate_report, ping_host, tcp_latency, traceroute, compare_hosts, audit, __version__


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(f"dargslan-network-latency v{__version__}")
        print(f"Network latency tester")
        print(f"\nUsage: dargslan-latency <command> [hosts...]")
        print(f"\nCommands:")
        print(f"  report [hosts]     Full latency report (default: 8.8.8.8 1.1.1.1 9.9.9.9)")
        print(f"  ping <host>        Ping a host with detailed stats")
        print(f"  tcp <host> [port]  TCP connection latency")
        print(f"  trace <host>       Traceroute to host")
        print(f"  compare h1 h2 ... Compare latency across hosts")
        print(f"  audit              Issues only")
        print(f"  json [hosts]       Full report as JSON")
        print(f"  version            Show version")
        print(f"\nhttps://dargslan.com — Linux & DevOps Books")
        return
    cmd = args[0]
    if cmd == "version":
        print(f"dargslan-network-latency v{__version__}")
    elif cmd == "report":
        hosts = args[1:] if len(args) > 1 else None
        data = generate_report(hosts)
        print(f"Network Latency Report")
        print(f"{'=' * 60}")
        for r in data["results"]:
            if r.get("reachable"):
                print(f"  {r['host']:<20} avg={r['avg_ms']}ms  min={r['min_ms']}ms  max={r['max_ms']}ms  jitter={r['jitter_ms']}ms  loss={r.get('packet_loss',0)}%")
            else:
                print(f"  {r['host']:<20} UNREACHABLE")
        if data["issues"]:
            print(f"\nIssues ({data['issues_count']}):")
            for i in data["issues"]:
                print(f"  [{i['severity'].upper()}] {i['message']}")
        print(f"\nMore tools: https://dargslan.com/cheat-sheets")
    elif cmd == "ping":
        if len(args) < 2: print("Usage: dargslan-latency ping <host>"); sys.exit(1)
        r = ping_host(args[1], 10)
        if r.get("reachable"):
            print(f"Host: {r['host']}")
            print(f"  Avg: {r['avg_ms']}ms  Min: {r['min_ms']}ms  Max: {r['max_ms']}ms")
            print(f"  Jitter: {r['jitter_ms']}ms  Loss: {r.get('packet_loss',0)}%")
        else:
            print(f"Host unreachable: {r['host']}")
    elif cmd == "tcp":
        if len(args) < 2: print("Usage: dargslan-latency tcp <host> [port]"); sys.exit(1)
        port = int(args[2]) if len(args) > 2 else 443
        r = tcp_latency(args[1], port)
        if r.get("reachable"):
            print(f"TCP {r['host']}:{r['port']}")
            print(f"  Avg: {r['avg_ms']}ms  Min: {r['min_ms']}ms  Max: {r['max_ms']}ms  Jitter: {r['jitter_ms']}ms")
        else:
            print(f"Cannot connect to {args[1]}:{port}")
    elif cmd == "trace":
        if len(args) < 2: print("Usage: dargslan-latency trace <host>"); sys.exit(1)
        hops = traceroute(args[1])
        print(f"Traceroute to {args[1]}:")
        for h in hops:
            ip = h["ip"] or "*"
            avg = f"{h['avg_ms']}ms" if h["avg_ms"] else "*"
            print(f"  {h['hop']:>3}  {ip:<18} {avg}")
    elif cmd == "compare":
        if len(args) < 2: print("Usage: dargslan-latency compare host1 host2 ..."); sys.exit(1)
        results = compare_hosts(args[1:])
        print(f"Latency Comparison (sorted by avg):")
        for r in results:
            if r.get("reachable"):
                print(f"  {r['host']:<20} {r['avg_ms']}ms")
            else:
                print(f"  {r['host']:<20} UNREACHABLE")
    elif cmd == "audit":
        issues = audit()
        if not issues: print("No issues found.")
        for i in issues: print(f"[{i['severity'].upper()}] {i['message']}")
    elif cmd == "json":
        hosts = args[1:] if len(args) > 1 else None
        print(json.dumps(generate_report(hosts), indent=2))
    else:
        print(f"Unknown command: {cmd}. Use --help."); sys.exit(1)

if __name__ == "__main__":
    main()
