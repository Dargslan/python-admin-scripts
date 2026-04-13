#!/usr/bin/env python3
"""Hostname and DNS Identity Verifier."""

import subprocess
import socket
import argparse


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.returncode
    except:
        return "", 1


def check_hostname():
    print("=== Hostname Information ===")
    hostname = socket.gethostname()
    print(f"  Hostname: {hostname}")

    try:
        fqdn = socket.getfqdn()
        print(f"  FQDN: {fqdn}")
    except:
        print("  FQDN: not available")

    out, rc = run_cmd("hostnamectl 2>/dev/null")
    if rc == 0 and out:
        for line in out.split("\n"):
            line = line.strip()
            if any(k in line.lower() for k in ["static", "transient", "pretty", "icon", "chassis", "operating", "kernel", "architecture"]):
                print(f"  {line}")


def check_hosts_file():
    print("\n=== /etc/hosts Entries ===")
    out, rc = run_cmd("grep -v '^#' /etc/hosts 2>/dev/null | grep -v '^$'")
    if rc == 0 and out:
        for line in out.split("\n"):
            print(f"  {line}")

        hostname = socket.gethostname()
        if hostname not in out:
            print(f"\n  WARNING: Hostname '{hostname}' not found in /etc/hosts")
    else:
        print("  Could not read /etc/hosts")


def check_dns_resolution():
    print("\n=== DNS Resolution ===")
    hostname = socket.gethostname()
    fqdn = socket.getfqdn()

    for name in [hostname, fqdn]:
        try:
            ip = socket.gethostbyname(name)
            print(f"  {name} -> {ip}")
        except socket.gaierror:
            print(f"  {name} -> FAILED to resolve")

    out, rc = run_cmd("dig +short $(hostname -f) 2>/dev/null")
    if rc == 0 and out:
        print(f"  DNS lookup: {out}")


def check_reverse_dns():
    print("\n=== Reverse DNS ===")
    out, rc = run_cmd("hostname -I 2>/dev/null")
    if rc == 0 and out:
        ips = out.strip().split()
        for ip in ips[:3]:
            try:
                rev = socket.gethostbyaddr(ip)
                print(f"  {ip} -> {rev[0]}")
            except:
                print(f"  {ip} -> No reverse DNS")


def check_domain_info():
    print("\n=== Domain Configuration ===")
    out, rc = run_cmd("dnsdomainname 2>/dev/null")
    if rc == 0 and out:
        print(f"  DNS Domain: {out}")
    else:
        print("  DNS Domain: not set")

    out2, rc2 = run_cmd("grep '^domain\\|^search' /etc/resolv.conf 2>/dev/null")
    if rc2 == 0 and out2:
        for line in out2.split("\n"):
            print(f"  resolv.conf: {line}")

    out3, _ = run_cmd("cat /etc/hostname 2>/dev/null")
    if out3:
        print(f"  /etc/hostname: {out3}")


def main():
    parser = argparse.ArgumentParser(description="Hostname and DNS Identity Verifier")
    parser.add_argument("--hostname", action="store_true", help="Show hostname details")
    parser.add_argument("--hosts", action="store_true", help="Show /etc/hosts")
    parser.add_argument("--dns", action="store_true", help="Check DNS resolution")
    parser.add_argument("--reverse", action="store_true", help="Check reverse DNS")
    parser.add_argument("--domain", action="store_true", help="Show domain config")
    args = parser.parse_args()

    print("Hostname & DNS Identity Verifier")
    print("=" * 40)

    if args.hostname:
        check_hostname()
    elif args.hosts:
        check_hosts_file()
    elif args.dns:
        check_dns_resolution()
    elif args.reverse:
        check_reverse_dns()
    elif args.domain:
        check_domain_info()
    else:
        check_hostname()
        check_hosts_file()
        check_dns_resolution()
        check_reverse_dns()
        check_domain_info()

    print("\n" + "=" * 40)
    print("Powered by dargslan.com")


if __name__ == "__main__":
    main()
