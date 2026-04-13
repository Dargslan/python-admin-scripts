"""dargslan-tmpfile-cleaner -- Temp file cleaner.
Find and clean temporary files, orphaned tmp dirs, and old cache files.
Part of the Dargslan Linux Sysadmin Toolkit: https://dargslan.com
"""
__version__ = "1.0.0"
import os, subprocess, time
from datetime import datetime

TMP_DIRS = ["/tmp", "/var/tmp", "/var/cache"]

def _human_size(s):
    for u in ("B","KB","MB","GB","TB"):
        if s < 1024: return f"{s:.1f}{u}"
        s /= 1024
    return f"{s:.1f}PB"

def scan_tmp_files(directory="/tmp", max_age_days=7):
    old_files = []
    cutoff = time.time() - (max_age_days * 86400)
    try:
        for root, dirs, files in os.walk(directory):
            for f in files:
                path = os.path.join(root, f)
                try:
                    st = os.stat(path)
                    if st.st_mtime < cutoff:
                        old_files.append({"path": path, "size": st.st_size, "size_human": _human_size(st.st_size), "age_days": int((time.time()-st.st_mtime)/86400), "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")})
                except OSError: pass
    except OSError: pass
    return sorted(old_files, key=lambda x: x["size"], reverse=True)

def get_tmp_usage():
    results = []
    for d in TMP_DIRS:
        total = 0; count = 0
        try:
            for root, dirs, files in os.walk(d):
                for f in files:
                    try: total += os.path.getsize(os.path.join(root, f)); count += 1
                    except OSError: pass
        except OSError: pass
        if count > 0: results.append({"directory": d, "total": total, "total_human": _human_size(total), "files": count})
    return results

def find_orphaned_dirs(directory="/tmp", max_age_days=30):
    orphaned = []
    cutoff = time.time() - (max_age_days * 86400)
    try:
        for entry in os.scandir(directory):
            if entry.is_dir():
                try:
                    st = entry.stat()
                    if st.st_mtime < cutoff:
                        size = sum(os.path.getsize(os.path.join(r,f)) for r,d,fs in os.walk(entry.path) for f in fs)
                        orphaned.append({"path": entry.path, "size": size, "size_human": _human_size(size), "age_days": int((time.time()-st.st_mtime)/86400)})
                except OSError: pass
    except OSError: pass
    return orphaned

def generate_report():
    usage = get_tmp_usage()
    old_files = scan_tmp_files("/tmp", 7)
    orphaned = find_orphaned_dirs("/tmp", 30)
    lines = ["="*60, "TEMP FILE CLEANER REPORT", "="*60]
    if usage:
        lines.append("\n--- Temp Directory Usage ---")
        for u in usage: lines.append(f"  {u['directory']:20s} {u['total_human']:>10s} ({u['files']} files)")
    lines.append(f"\n--- Old Files in /tmp (>7 days): {len(old_files)} ---")
    for f in old_files[:15]: lines.append(f"  {f['size_human']:>10s}  {f['age_days']}d old  {f['path']}")
    if orphaned:
        lines.append(f"\n--- Orphaned Dirs in /tmp (>30 days): {len(orphaned)} ---")
        for d in orphaned[:10]: lines.append(f"  {d['size_human']:>10s}  {d['age_days']}d old  {d['path']}")
    lines += ["\n"+"="*60, "More tools: https://dargslan.com | pip install dargslan-toolkit", "="*60]
    return "\n".join(lines)
