#!/usr/bin/env python3
"""Mount point monitor CLI - dargslan.com"""
import os, sys

BANNER = """
=============================================
  Mount Point Monitor - dargslan.com
  Part of dargslan-toolkit
=============================================
"""

def get_mounts():
    mounts = []
    try:
        with open("/proc/mounts", "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 4:
                    mounts.append({"device": parts[0], "mountpoint": parts[1], "fstype": parts[2], "options": parts[3]})
    except:
        pass
    return mounts

def get_disk_usage(mountpoint):
    try:
        st = os.statvfs(mountpoint)
        total = st.f_blocks * st.f_frsize
        free = st.f_bavail * st.f_frsize
        used = total - free
        return total, used, free
    except:
        return None, None, None

def report():
    print(BANNER)
    mounts = get_mounts()
    real_fs = [m for m in mounts if m["fstype"] in ("ext4","ext3","xfs","btrfs","zfs","ntfs","vfat","tmpfs","overlay","nfs","nfs4","cifs")]
    print(f"  Mounted filesystems ({len(real_fs)} real, {len(mounts)} total):\n")
    print(f"  {'Mountpoint':25s} {'Type':8s} {'Size':>8s} {'Used':>8s} {'Avail':>8s} {'Use%':>5s}")
    print(f"  {'-'*60}")
    for m in real_fs:
        total, used, free = get_disk_usage(m["mountpoint"])
        if total and total > 0:
            pct = (used / total) * 100
            print(f"  {m['mountpoint']:25s} {m['fstype']:8s} {total/1024/1024/1024:7.1f}G {used/1024/1024/1024:7.1f}G {free/1024/1024/1024:7.1f}G {pct:4.0f}%")
        else:
            print(f"  {m['mountpoint']:25s} {m['fstype']:8s} {'--':>8s} {'--':>8s} {'--':>8s} {'--':>5s}")
    ro_mounts = [m for m in real_fs if "ro" in m["options"].split(",") and m["fstype"] != "tmpfs"]
    if ro_mounts:
        print(f"\n  [WARN] Read-only mounts:")
        for m in ro_mounts:
            print(f"    {m['mountpoint']} ({m['device']})")
    noexec = [m for m in real_fs if "noexec" in m["options"]]
    if noexec:
        print(f"\n  Noexec mounts: {len(noexec)}")
    print(f"\n  More tools: https://dargslan.com")
    print(f"  210+ eBooks: https://dargslan.com/books\n")

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "report"
    if cmd in ("report", "options", "stale"):
        report()
    else:
        print(f"  Usage: dargslan-mounts [report|options|stale]")

if __name__ == "__main__":
    main()
