"""CLI for dargslan-socket-stats."""

import sys
import json
from . import generate_report, get_tcp_sockets, get_udp_sockets, get_listening_sockets, get_connection_states, audit, __version__


def print_report(data):
    print(f"Socket Statistics Report")
    print(f"{'=' * 60}")
    print(f"Timestamp: {data['timestamp']}")
    print(f"TCP Connections: {data['tcp_connections']}")
    print(f"UDP Sockets: {data['udp_sockets']}")
    print(f"Listening: {data['listening']}")
    print()

    if data["connection_states"]:
        print("TCP Connection States:")
        print(f"{'-' * 40}")
        for state, count in sorted(data["connection_states"].items(), key=lambda x: x[1], reverse=True):
            bar = "#" * min(count, 40)
            print(f"  {state:<15} {count:>6}  {bar}")
        print()

    if data["listening_sockets"]:
        print("Listening Sockets:")
        print(f"{'-' * 40}")
        for s in data["listening_sockets"][:20]:
            proc = s.get("process", "unknown")
            print(f"  {s['protocol']:<5} {s['local']:<25} {proc}")
        print()

    if data["issues"]:
        print(f"Issues Found: {data['issues_count']}")
        for issue in data["issues"]:
            print(f"  [{issue['severity'].upper()}] {issue['message']}")
    else:
        print("No issues found.")

    print(f"\nMore Linux tools: https://dargslan.com/cheat-sheets")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(f"dargslan-socket-stats v{__version__}")
        print(f"Linux socket statistics analyzer")
        print(f"\nUsage: dargslan-socket <command>")
        print(f"\nCommands:")
        print(f"  report     Full socket statistics report")
        print(f"  tcp        TCP connections only")
        print(f"  udp        UDP sockets only")
        print(f"  listen     Listening sockets")
        print(f"  states     TCP connection state breakdown")
        print(f"  audit      Security audit (issues only)")
        print(f"  json       Full report as JSON")
        print(f"  version    Show version")
        print(f"\nhttps://dargslan.com — Linux & DevOps Books")
        return

    cmd = args[0]
    if cmd == "version":
        print(f"dargslan-socket-stats v{__version__}")
    elif cmd == "report":
        print_report(generate_report())
    elif cmd == "tcp":
        socks = get_tcp_sockets()
        print(f"TCP Connections: {len(socks)}")
        for s in socks[:30]:
            proc = s.get("process", "?")
            print(f"  {s['state']:<13} {s['local']:<25} → {s['remote']:<25} {proc}")
    elif cmd == "udp":
        socks = get_udp_sockets()
        print(f"UDP Sockets: {len(socks)}")
        for s in socks[:30]:
            proc = s.get("process", "?")
            print(f"  {s['local']:<25} → {s['remote']:<25} {proc}")
    elif cmd == "listen":
        socks = get_listening_sockets()
        print(f"Listening Sockets: {len(socks)}")
        for s in socks:
            proc = s.get("process", "?")
            print(f"  {s['protocol']:<5} {s['local']:<30} {proc}")
    elif cmd == "states":
        states = get_connection_states()
        total = sum(states.values())
        print(f"TCP Connection States (total: {total}):")
        for state, count in sorted(states.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total * 100) if total > 0 else 0
            print(f"  {state:<15} {count:>6} ({pct:.1f}%)")
    elif cmd == "audit":
        issues = audit()
        if not issues:
            print("No issues found.")
        for i in issues:
            print(f"[{i['severity'].upper()}] {i['message']}")
    elif cmd == "json":
        print(json.dumps(generate_report(), indent=2))
    else:
        print(f"Unknown command: {cmd}. Use --help for usage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
