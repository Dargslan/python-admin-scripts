"""dargslan-fstab-check -- Fstab validator.
Check /etc/fstab syntax, detect missing devices, verify mount options and UUID references.
Part of the Dargslan Linux Sysadmin Toolkit: https://dargslan.com
"""
__version__ = "1.0.0"
import os, subprocess

def parse_fstab(path="/etc/fstab"):
    entries = []
    try:
        with open(path) as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"): continue
                parts = line.split()
                if len(parts) >= 4:
                    entries.append({"line_num": i, "device": parts[0], "mountpoint": parts[1], "fstype": parts[2], "options": parts[3], "dump": parts[4] if len(parts)>4 else "0", "pass": parts[5] if len(parts)>5 else "0", "raw": line})
    except (IOError, OSError): pass
    return entries

def validate_fstab():
    entries = parse_fstab()
    issues = []
    for e in entries:
        if e["device"].startswith("UUID="):
            uuid = e["device"].split("=")[1]
            blk_path = f"/dev/disk/by-uuid/{uuid}"
            if not os.path.exists(blk_path): issues.append({"entry": e, "issue": f"UUID {uuid} not found on system", "severity": "error"})
        if not os.path.isdir(e["mountpoint"]) and e["mountpoint"] != "none" and e["mountpoint"] != "swap":
            issues.append({"entry": e, "issue": f"Mount point {e['mountpoint']} does not exist", "severity": "warning"})
        if e["fstype"] == "swap" and e["mountpoint"] != "none":
            issues.append({"entry": e, "issue": "Swap entry should have 'none' as mountpoint", "severity": "info"})
        if "noauto" not in e["options"] and e["device"].startswith("/dev/sd"):
            issues.append({"entry": e, "issue": f"Using device name {e['device']} instead of UUID (fragile)", "severity": "warning"})
    return {"entries": entries, "issues": issues}

def check_mounted_vs_fstab():
    fstab = parse_fstab()
    fstab_mounts = {e["mountpoint"] for e in fstab if e["mountpoint"] not in ("none","swap")}
    mounted = set()
    try:
        with open("/proc/mounts") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2: mounted.add(parts[1])
    except OSError: pass
    not_mounted = fstab_mounts - mounted
    return list(not_mounted)

def generate_report():
    result = validate_fstab()
    not_mounted = check_mounted_vs_fstab()
    lines = ["="*60, "FSTAB VALIDATION REPORT", "="*60]
    lines.append(f"\nTotal entries: {len(result['entries'])}")
    lines.append(f"Issues found: {len(result['issues'])}")
    lines.append("\n--- Fstab Entries ---")
    for e in result["entries"]:
        lines.append(f"  L{e['line_num']:3d}: {e['device']:40s} -> {e['mountpoint']:20s} ({e['fstype']})")
    if result["issues"]:
        lines.append("\n--- Issues ---")
        for i in result["issues"]:
            icon = "[ERR]" if i["severity"]=="error" else "[WRN]" if i["severity"]=="warning" else "[INF]"
            lines.append(f"  {icon} Line {i['entry']['line_num']}: {i['issue']}")
    if not_mounted:
        lines.append("\n--- Not Currently Mounted ---")
        for m in not_mounted: lines.append(f"  [!] {m}")
    lines += ["\n"+"="*60, "More tools: https://dargslan.com | pip install dargslan-toolkit", "="*60]
    return "\n".join(lines)
