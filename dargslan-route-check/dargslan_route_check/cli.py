#!/usr/bin/env python3
"""Network Routing Table Analyzer - Check and analyze routing tables."""

import subprocess
import argparse
import re


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.returncode
    except:
        return "", 1


def show_routes():
    print("=== Routing Table ===")
    out, rc = run_cmd("ip route show 2>/dev/null")
    if rc == 0 and out:
        for line in out.split("\n"):
            if "default" in line:
                print(f"  DEFAULT: {line}")
            else:
                print(f"  {line}")
    else:
        out2, _ = run_cmd("route -n 2>/dev/null")
        if out2:
            print(f"  {out2}")
        else:
            out3, _ = run_cmd("netstat -rn 2>/dev/null")
            print(f"  {out3}")


def check_gateway():
    print("\n=== Default Gateway ===")
    out, rc = run_cmd("ip route show default 2>/dev/null")
    if rc == 0 and out:
        match = re.search(r'default via (\S+) dev (\S+)', out)
        if match:
            gw = match.group(1)
            dev = match.group(2)
            print(f"  Gateway:   {gw}")
            print(f"  Interface: {dev}")

            ping_out, ping_rc = run_cmd(f"ping -c 1 -W 2 {gw} 2>/dev/null")
            if ping_rc == 0:
                rtt = re.search(r'time=(\S+)', ping_out)
                print(f"  Reachable: Yes ({rtt.group(1)}ms)" if rtt else "  Reachable: Yes")
            else:
                print(f"  Reachable: NO - Gateway unreachable!")
        else:
            print(f"  {out}")
    else:
        print("  No default gateway configured")


def check_dns_routes():
    print("\n=== DNS Server Routes ===")
    out, rc = run_cmd("grep nameserver /etc/resolv.conf 2>/dev/null")
    if rc == 0 and out:
        for line in out.split("\n"):
            if "nameserver" in line:
                dns = line.split()[-1]
                route_out, _ = run_cmd(f"ip route get {dns} 2>/dev/null")
                if route_out:
                    match = re.search(r'via (\S+) dev (\S+)', route_out)
                    if match:
                        print(f"  {dns} via {match.group(1)} dev {match.group(2)}")
                    else:
                        print(f"  {dns}: {route_out.split(chr(10))[0]}")


def check_interfaces():
    print("\n=== Interface Routes ===")
    out, rc = run_cmd("ip -brief addr show 2>/dev/null")
    if rc == 0 and out:
        for line in out.split("\n"):
            parts = line.split()
            if len(parts) >= 3 and parts[1] == "UP":
                iface = parts[0]
                addrs = parts[2:]
                print(f"  {iface}: {', '.join(addrs)}")
                route_out, _ = run_cmd(f"ip route show dev {iface} 2>/dev/null")
                if route_out:
                    for r in route_out.split("\n"):
                        print(f"    -> {r}")


def trace_route(host):
    print(f"\n=== Route to {host} ===")
    out, rc = run_cmd(f"ip route get {host} 2>/dev/null")
    if rc == 0 and out:
        print(f"  {out.split(chr(10))[0]}")

    print(f"\n  Traceroute (max 10 hops):")
    out2, rc2 = run_cmd(f"traceroute -m 10 -w 2 {host} 2>/dev/null")
    if rc2 == 0 and out2:
        for line in out2.split("\n"):
            print(f"  {line}")
    else:
        out3, _ = run_cmd(f"tracepath -m 10 {host} 2>/dev/null")
        if out3:
            for line in out3.split("\n")[:12]:
                print(f"  {line}")
        else:
            print("  traceroute/tracepath not available")


def main():
    parser = argparse.ArgumentParser(description="Network Routing Table Analyzer")
    parser.add_argument("--routes", action="store_true", help="Show routing table")
    parser.add_argument("--gateway", action="store_true", help="Check default gateway")
    parser.add_argument("--dns", action="store_true", help="Check DNS routes")
    parser.add_argument("--interfaces", action="store_true", help="Show interface routes")
    parser.add_argument("--trace", type=str, metavar="HOST", help="Trace route to host")
    args = parser.parse_args()

    print("Network Routing Table Analyzer")
    print("=" * 40)

    if args.routes:
        show_routes()
    elif args.gateway:
        check_gateway()
    elif args.dns:
        check_dns_routes()
    elif args.interfaces:
        check_interfaces()
    elif args.trace:
        trace_route(args.trace)
    else:
        show_routes()
        check_gateway()
        check_dns_routes()
        check_interfaces()

    print("\n" + "=" * 40)
    print("Powered by dargslan.com")


if __name__ == "__main__":
    main()
