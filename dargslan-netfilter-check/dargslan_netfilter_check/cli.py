#!/usr/bin/env python3
"""Netfilter and Connection Tracking Analyzer."""

import subprocess
import argparse


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.returncode
    except:
        return "", 1


def check_conntrack():
    print("=== Connection Tracking ===")
    out, rc = run_cmd("conntrack -C 2>/dev/null")
    if rc == 0 and out:
        print(f"  Active connections: {out}")
    else:
        out2, _ = run_cmd("cat /proc/sys/net/netfilter/nf_conntrack_count 2>/dev/null")
        if out2:
            print(f"  Active connections: {out2}")

    max_out, _ = run_cmd("cat /proc/sys/net/netfilter/nf_conntrack_max 2>/dev/null")
    if max_out:
        print(f"  Max connections: {max_out}")
        count_out, _ = run_cmd("cat /proc/sys/net/netfilter/nf_conntrack_count 2>/dev/null")
        if count_out:
            usage = (int(count_out) / int(max_out)) * 100
            status = "WARNING" if usage > 80 else "OK"
            print(f"  Usage: {usage:.1f}% [{status}]")


def check_tables():
    print("\n=== Netfilter Tables ===")
    out, rc = run_cmd("nft list tables 2>/dev/null")
    if rc == 0 and out:
        print(f"  nftables tables:")
        for line in out.split("\n"):
            print(f"    {line}")
    else:
        out2, rc2 = run_cmd("iptables -L -n --line-numbers 2>/dev/null | head -30")
        if rc2 == 0 and out2:
            print(f"  iptables rules:")
            for line in out2.split("\n")[:20]:
                print(f"    {line}")
        else:
            print("  No netfilter tables accessible (may need sudo)")


def check_chains():
    print("\n=== Chain Statistics ===")
    for table in ["filter", "nat", "mangle"]:
        out, rc = run_cmd(f"iptables -t {table} -L -n -v 2>/dev/null | grep -E '^Chain'")
        if rc == 0 and out:
            for line in out.split("\n"):
                print(f"  [{table}] {line}")


def check_dropped():
    print("\n=== Dropped/Rejected Packets ===")
    out, rc = run_cmd("iptables -L -n -v 2>/dev/null | grep -E 'DROP|REJECT'")
    if rc == 0 and out:
        lines = out.strip().split("\n")
        print(f"  Rules with DROP/REJECT: {len(lines)}")
        for line in lines[:10]:
            parts = line.split()
            if len(parts) >= 3:
                print(f"    pkts={parts[0]} bytes={parts[1]} {' '.join(parts[2:8])}")
    else:
        print("  No DROP/REJECT rules found or not accessible")


def check_nat():
    print("\n=== NAT Rules ===")
    out, rc = run_cmd("iptables -t nat -L -n -v 2>/dev/null")
    if rc == 0 and out:
        for line in out.split("\n")[:15]:
            print(f"  {line}")
    else:
        print("  NAT table not accessible")


def main():
    parser = argparse.ArgumentParser(description="Netfilter and Connection Tracking Analyzer")
    parser.add_argument("--conntrack", action="store_true", help="Show connection tracking stats")
    parser.add_argument("--tables", action="store_true", help="Show netfilter tables")
    parser.add_argument("--chains", action="store_true", help="Show chain statistics")
    parser.add_argument("--dropped", action="store_true", help="Show dropped packets")
    parser.add_argument("--nat", action="store_true", help="Show NAT rules")
    args = parser.parse_args()

    print("Netfilter Connection Tracking Analyzer")
    print("=" * 40)

    if args.conntrack:
        check_conntrack()
    elif args.tables:
        check_tables()
    elif args.chains:
        check_chains()
    elif args.dropped:
        check_dropped()
    elif args.nat:
        check_nat()
    else:
        check_conntrack()
        check_tables()
        check_chains()
        check_dropped()

    print("\n" + "=" * 40)
    print("Powered by dargslan.com")


if __name__ == "__main__":
    main()
