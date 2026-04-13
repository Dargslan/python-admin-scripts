"""dargslan-file-integrity — File integrity checker with hash-based change detection."""

__version__ = "1.0.0"

import os
import hashlib
import json
import stat
from datetime import datetime
from pathlib import Path

DEFAULT_PATHS = [
    "/etc/passwd", "/etc/shadow", "/etc/group", "/etc/sudoers",
    "/etc/ssh/sshd_config", "/etc/hosts", "/etc/fstab",
    "/etc/crontab", "/etc/resolv.conf", "/etc/hostname",
    "/boot/grub/grub.cfg", "/etc/pam.d",
]

BASELINE_FILE = os.path.expanduser("~/.dargslan-fim-baseline.json")


def hash_file(filepath, algorithm="sha256"):
    try:
        h = hashlib.new(algorithm)
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except (PermissionError, FileNotFoundError, OSError):
        return None


def get_file_metadata(filepath):
    try:
        st = os.stat(filepath)
        return {
            "path": filepath,
            "size": st.st_size,
            "mode": oct(st.st_mode),
            "uid": st.st_uid,
            "gid": st.st_gid,
            "mtime": datetime.fromtimestamp(st.st_mtime).isoformat(),
            "hash": hash_file(filepath),
        }
    except (FileNotFoundError, PermissionError, OSError):
        return {"path": filepath, "error": "cannot access"}


def scan_directory(dirpath, extensions=None):
    results = []
    try:
        for root, dirs, files in os.walk(dirpath):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for f in files:
                if extensions and not any(f.endswith(e) for e in extensions):
                    continue
                full = os.path.join(root, f)
                results.append(get_file_metadata(full))
    except PermissionError:
        pass
    return results


def scan_paths(paths=None):
    if paths is None:
        paths = DEFAULT_PATHS
    results = []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                for f in files:
                    results.append(get_file_metadata(os.path.join(root, f)))
        elif os.path.isfile(p):
            results.append(get_file_metadata(p))
        else:
            results.append({"path": p, "error": "not found"})
    return results


def create_baseline(paths=None):
    scanned = scan_paths(paths)
    baseline = {
        "created": datetime.now().isoformat(),
        "files": {f["path"]: f for f in scanned if "error" not in f},
    }
    with open(BASELINE_FILE, "w") as fh:
        json.dump(baseline, fh, indent=2)
    return baseline


def load_baseline():
    try:
        with open(BASELINE_FILE, "r") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def compare_with_baseline(paths=None):
    baseline = load_baseline()
    if not baseline:
        return {"error": "No baseline found. Run 'baseline' first."}

    current = scan_paths(paths)
    changes = {"modified": [], "added": [], "removed": [], "permission_changed": []}
    current_map = {f["path"]: f for f in current if "error" not in f}
    baseline_files = baseline.get("files", {})

    for path, cur in current_map.items():
        if path in baseline_files:
            base = baseline_files[path]
            if cur.get("hash") != base.get("hash"):
                changes["modified"].append({
                    "path": path,
                    "old_hash": base.get("hash", "")[:16],
                    "new_hash": cur.get("hash", "")[:16],
                })
            if cur.get("mode") != base.get("mode"):
                changes["permission_changed"].append({
                    "path": path,
                    "old_mode": base.get("mode"),
                    "new_mode": cur.get("mode"),
                })
        else:
            changes["added"].append({"path": path})

    for path in baseline_files:
        if path not in current_map:
            changes["removed"].append({"path": path})

    return {
        "baseline_date": baseline.get("created"),
        "check_date": datetime.now().isoformat(),
        "baseline_files": len(baseline_files),
        "current_files": len(current_map),
        "changes": changes,
        "total_changes": sum(len(v) for v in changes.values()),
    }


def generate_report(paths=None):
    scanned = scan_paths(paths)
    comparison = compare_with_baseline(paths)
    issues = []

    for f in scanned:
        if "error" not in f:
            mode = int(f.get("mode", "0o0"), 8) if isinstance(f.get("mode"), str) else 0
            if mode & stat.S_IWOTH and f["path"] not in ("/tmp",):
                issues.append({
                    "severity": "critical",
                    "message": f"World-writable critical file: {f['path']}"
                })

    if isinstance(comparison, dict) and "changes" in comparison:
        if comparison["changes"]["modified"]:
            for mod in comparison["changes"]["modified"]:
                issues.append({
                    "severity": "warning",
                    "message": f"File modified since baseline: {mod['path']}"
                })
        if comparison["changes"]["removed"]:
            for rem in comparison["changes"]["removed"]:
                issues.append({
                    "severity": "critical",
                    "message": f"File removed since baseline: {rem['path']}"
                })

    return {
        "timestamp": datetime.now().isoformat(),
        "files_scanned": len(scanned),
        "files_accessible": len([f for f in scanned if "error" not in f]),
        "comparison": comparison if isinstance(comparison, dict) and "error" not in comparison else None,
        "issues": issues,
        "issues_count": len(issues),
    }


def audit():
    report = generate_report()
    return report["issues"]
