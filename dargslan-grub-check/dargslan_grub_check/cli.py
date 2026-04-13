#!/usr/bin/env python3
"""GRUB bootloader checker CLI - dargslan.com"""
import os, sys, glob

BANNER = """
=============================================
  GRUB Bootloader Checker - dargslan.com
  Part of dargslan-toolkit
=============================================
"""

def find_grub_config():
    paths = ["/boot/grub/grub.cfg", "/boot/grub2/grub.cfg", "/etc/default/grub"]
    found = {}
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, 'r') as f:
                    found[p] = f.read()
            except PermissionError:
                found[p] = None
    return found

def get_kernel_params():
    try:
        with open("/proc/cmdline", "r") as f:
            return f.read().strip()
    except:
        return None

def get_installed_kernels():
    kernels = sorted(glob.glob("/boot/vmlinuz-*"))
    return kernels

def report():
    print(BANNER)
    cmdline = get_kernel_params()
    if cmdline:
        print(f"  Current kernel cmdline:")
        print(f"    {cmdline}")
    kernels = get_installed_kernels()
    if kernels:
        print(f"\n  Installed kernels ({len(kernels)}):")
        for k in kernels:
            size = os.path.getsize(k) / 1024 / 1024
            current = " (current)" if os.uname().release in k else ""
            print(f"    {os.path.basename(k):40s} {size:.1f} MB{current}")
    configs = find_grub_config()
    if "/etc/default/grub" in configs and configs["/etc/default/grub"]:
        print(f"\n  GRUB defaults (/etc/default/grub):")
        for line in configs["/etc/default/grub"].splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                print(f"    {line}")
    if not configs:
        print("  No GRUB configuration found (may need root access)")
    print(f"\n  More tools: https://dargslan.com")
    print(f"  210+ eBooks: https://dargslan.com/books\n")

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "report"
    if cmd in ("report", "kernels", "params", "config"):
        report()
    else:
        print(f"  Usage: dargslan-grub [report|kernels|params|config]")

if __name__ == "__main__":
    main()
