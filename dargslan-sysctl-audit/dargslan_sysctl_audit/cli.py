#!/usr/bin/env python3
"""Sysctl parameter auditor CLI - dargslan.com"""
import subprocess, sys

BANNER = """
=============================================
  Sysctl Parameter Auditor - dargslan.com
  Part of dargslan-toolkit
=============================================
"""

SECURITY_PARAMS = {
    "net.ipv4.ip_forward": ("0", "Disable IP forwarding unless router"),
    "net.ipv4.conf.all.rp_filter": ("1", "Enable reverse path filtering"),
    "net.ipv4.conf.all.accept_redirects": ("0", "Reject ICMP redirects"),
    "net.ipv4.conf.all.send_redirects": ("0", "Dont send ICMP redirects"),
    "net.ipv4.conf.all.accept_source_route": ("0", "Reject source-routed packets"),
    "net.ipv4.tcp_syncookies": ("1", "Enable SYN flood protection"),
    "net.ipv4.icmp_echo_ignore_broadcasts": ("1", "Ignore broadcast pings"),
    "kernel.randomize_va_space": ("2", "Full ASLR enabled"),
    "kernel.sysrq": ("0", "Disable magic SysRq key"),
    "fs.protected_hardlinks": ("1", "Protect hardlinks"),
    "fs.protected_symlinks": ("1", "Protect symlinks"),
}

PERFORMANCE_PARAMS = {
    "vm.swappiness": ("10", "Low swappiness for servers"),
    "net.core.somaxconn": ("65535", "Max socket connections"),
    "net.ipv4.tcp_max_syn_backlog": ("65535", "SYN backlog queue"),
    "net.core.netdev_max_backlog": ("65535", "Network device backlog"),
    "vm.dirty_ratio": ("10", "Dirty page ratio"),
    "vm.dirty_background_ratio": ("5", "Background dirty ratio"),
}

def get_sysctl(param):
    try:
        r = subprocess.run(["sysctl", "-n", param], capture_output=True, text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else None
    except:
        return None

def audit_params(params, title):
    print(f"\n  {title}:")
    passed = 0
    total = len(params)
    for param, (recommended, desc) in params.items():
        current = get_sysctl(param)
        if current is None:
            print(f"    [SKIP] {param} (not available)")
            total -= 1
            continue
        ok = current == recommended
        if ok: passed += 1
        status = "PASS" if ok else "WARN"
        print(f"    [{status}] {param} = {current} (rec: {recommended})")
        if not ok:
            print(f"           -> {desc}")
    return passed, total

def report():
    print(BANNER)
    sp, st = audit_params(SECURITY_PARAMS, "Security Parameters")
    pp, pt = audit_params(PERFORMANCE_PARAMS, "Performance Parameters")
    total_pass = sp + pp
    total_checks = st + pt
    print(f"\n  Score: {total_pass}/{total_checks} checks passed")
    print(f"  Security: {sp}/{st} | Performance: {pp}/{pt}")
    print(f"\n  More tools: https://dargslan.com")
    print(f"  210+ eBooks: https://dargslan.com/books\n")

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "report"
    if cmd in ("report", "security", "network", "all"):
        report()
    else:
        print(f"  Usage: dargslan-sysctl [report|security|network]")

if __name__ == "__main__":
    main()
