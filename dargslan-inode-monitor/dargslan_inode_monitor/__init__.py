"""dargslan-inode-monitor -- Inode usage monitor.
Track inode consumption, find dirs with excessive files, prevent inode exhaustion.
Part of the Dargslan Linux Sysadmin Toolkit: https://dargslan.com
"""
__version__ = "1.0.0"
import subprocess, os

def get_inode_usage():
    results = []
    try:
        r = subprocess.run(["df", "-i"], capture_output=True, text=True, timeout=10)
        for line in r.stdout.strip().split("\n")[1:]:
            parts = line.split()
            if len(parts) >= 6 and parts[4] != "-":
                results.append({"filesystem": parts[0], "inodes_total": parts[1], "inodes_used": parts[2], "inodes_free": parts[3], "use_percent": parts[4], "mountpoint": parts[5]})
    except (subprocess.SubprocessError, OSError): pass
    return results

def find_inode_heavy_dirs(directory="/", max_depth=3, top_n=10):
    dirs = []
    try:
        for root, subdirs, files in os.walk(directory):
            depth = root.replace(directory, "").count(os.sep)
            if depth >= max_depth: subdirs.clear(); continue
            count = len(files) + len(subdirs)
            if count > 100: dirs.append({"path": root, "entries": count})
    except (OSError, PermissionError): pass
    return sorted(dirs, key=lambda x: x["entries"], reverse=True)[:top_n]

def check_inode_alerts(threshold=80):
    alerts = []
    for u in get_inode_usage():
        try:
            pct = int(u["use_percent"].replace("%", ""))
            if pct >= threshold: alerts.append({**u, "percent_int": pct})
        except ValueError: pass
    return alerts

def generate_report():
    usage = get_inode_usage()
    alerts = check_inode_alerts()
    heavy = find_inode_heavy_dirs("/var", 3, 10)
    lines = ["="*60, "INODE USAGE MONITOR REPORT", "="*60]
    if usage:
        lines.append("\n--- Filesystem Inode Usage ---")
        for u in usage:
            flag = " [WARNING]" if any(a["mountpoint"]==u["mountpoint"] for a in alerts) else ""
            lines.append(f"  {u['mountpoint']:25s} {u['use_percent']:>5s} used ({u['inodes_used']}/{u['inodes_total']}){flag}")
    if alerts:
        lines.append(f"\n--- Inode Alerts (>={80}%) ---")
        for a in alerts: lines.append(f"  [!] {a['mountpoint']} at {a['use_percent']} inode usage")
    if heavy:
        lines.append("\n--- Directories with Most Entries (/var) ---")
        for d in heavy: lines.append(f"  {d['entries']:>8d} entries  {d['path']}")
    lines += ["\n"+"="*60, "More tools: https://dargslan.com | pip install dargslan-toolkit", "="*60]
    return "\n".join(lines)
