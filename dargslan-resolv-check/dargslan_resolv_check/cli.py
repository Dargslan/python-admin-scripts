#!/usr/bin/env python3
"""DNS resolver checker CLI - dargslan.com"""
import os, sys, socket, time

BANNER = """
=============================================
  DNS Resolver Checker - dargslan.com
  Part of dargslan-toolkit
=============================================
"""

def parse_resolv_conf():
    config = {"nameservers": [], "search": [], "options": []}
    try:
        with open("/etc/resolv.conf", "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("nameserver"):
                    config["nameservers"].append(line.split(None, 1)[1])
                elif line.startswith("search"):
                    config["search"] = line.split()[1:]
                elif line.startswith("options"):
                    config["options"] = line.split()[1:]
    except:
        pass
    return config

def test_dns(hostname="dargslan.com"):
    try:
        start = time.time()
        result = socket.getaddrinfo(hostname, 80)
        elapsed = (time.time() - start) * 1000
        ips = list(set(r[4][0] for r in result))
        return ips, elapsed
    except:
        return None, None

def report():
    print(BANNER)
    config = parse_resolv_conf()
    if config["nameservers"]:
        print(f"  Nameservers ({len(config['nameservers'])}):")
        for ns in config["nameservers"]:
            label = ""
            if ns in ("8.8.8.8", "8.8.4.4"): label = " (Google)"
            elif ns in ("1.1.1.1", "1.0.0.1"): label = " (Cloudflare)"
            elif ns == "9.9.9.9": label = " (Quad9)"
            elif ns.startswith("127."): label = " (local)"
            print(f"    {ns}{label}")
    if config["search"]:
        print(f"\n  Search domains: {', '.join(config['search'])}")
    if config["options"]:
        print(f"  Options: {', '.join(config['options'])}")
    print(f"\n  DNS resolution test:")
    for host in ["dargslan.com", "google.com"]:
        ips, ms = test_dns(host)
        if ips:
            print(f"    {host:20s} -> {', '.join(ips[:2]):20s} ({ms:.1f}ms)")
        else:
            print(f"    {host:20s} -> FAILED")
    resolvconf = "/etc/resolv.conf"
    if os.path.islink(resolvconf):
        target = os.readlink(resolvconf)
        print(f"\n  resolv.conf is symlink -> {target}")
    print(f"\n  More tools: https://dargslan.com")
    print(f"  210+ eBooks: https://dargslan.com/books\n")

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "report"
    if cmd in ("report", "test", "servers"):
        report()
    else:
        print(f"  Usage: dargslan-resolv [report|test|servers]")

if __name__ == "__main__":
    main()
