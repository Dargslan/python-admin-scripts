"""dargslan-systemd-unit — Systemd unit file analyzer."""

__version__ = "1.0.0"

import os
import re
import json
import subprocess
from datetime import datetime
from collections import defaultdict

UNIT_DIRS = ["/etc/systemd/system", "/lib/systemd/system", "/usr/lib/systemd/system"]

SECURITY_DIRECTIVES = [
    "ProtectSystem", "ProtectHome", "PrivateTmp", "NoNewPrivileges",
    "ProtectKernelModules", "ProtectKernelTunables", "RestrictSUIDSGID",
    "PrivateDevices", "ProtectClock", "ProtectHostname",
    "RestrictNamespaces", "RestrictRealtime", "MemoryDenyWriteExecute",
    "SystemCallFilter", "ReadOnlyPaths", "ReadWritePaths",
]


def _run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception:
        return ""


def parse_unit_file(filepath):
    sections = defaultdict(dict)
    current_section = None
    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or line.startswith(";"):
                    continue
                m = re.match(r'^\[(\w+)\]$', line)
                if m:
                    current_section = m.group(1)
                    continue
                if current_section and "=" in line:
                    key, _, value = line.partition("=")
                    sections[current_section][key.strip()] = value.strip()
    except (FileNotFoundError, PermissionError):
        pass
    return dict(sections)


def find_unit_files(unit_type=None):
    files = []
    for d in UNIT_DIRS:
        if os.path.isdir(d):
            try:
                for f in os.listdir(d):
                    if unit_type and not f.endswith(f".{unit_type}"):
                        continue
                    full = os.path.join(d, f)
                    if os.path.isfile(full):
                        files.append(full)
            except PermissionError:
                pass
    return sorted(set(files))


def analyze_security(parsed):
    score = 0
    max_score = len(SECURITY_DIRECTIVES)
    found = []
    missing = []
    service = parsed.get("Service", {})
    for directive in SECURITY_DIRECTIVES:
        if directive in service:
            val = service[directive].lower()
            if val in ("true", "yes", "full", "strict"):
                score += 1
                found.append(directive)
            else:
                found.append(f"{directive}={service[directive]}")
                score += 0.5
        else:
            missing.append(directive)
    return {
        "score": round(score / max_score * 100, 1) if max_score > 0 else 0,
        "found": found,
        "missing": missing,
    }


def lint_unit(filepath):
    parsed = parse_unit_file(filepath)
    issues = []
    if not parsed:
        issues.append({"severity": "critical", "message": f"Cannot parse: {filepath}"})
        return issues
    if "Unit" not in parsed:
        issues.append({"severity": "warning", "message": "Missing [Unit] section"})
    if "Service" not in parsed and filepath.endswith(".service"):
        issues.append({"severity": "critical", "message": "Service file missing [Service] section"})
    if "Install" not in parsed:
        issues.append({"severity": "info", "message": "Missing [Install] section (cannot be enabled)"})
    service = parsed.get("Service", {})
    if filepath.endswith(".service"):
        if "ExecStart" not in service:
            issues.append({"severity": "critical", "message": "Missing ExecStart directive"})
        if "Type" not in service:
            issues.append({"severity": "info", "message": "No Type specified (defaults to simple)"})
        if service.get("Type") == "forking" and "PIDFile" not in service:
            issues.append({"severity": "warning", "message": "Type=forking without PIDFile"})
        if "Restart" not in service:
            issues.append({"severity": "warning", "message": "No Restart policy defined"})
        if service.get("User", "root") == "root":
            issues.append({"severity": "warning", "message": "Running as root (consider User= directive)"})
    security = analyze_security(parsed)
    if security["score"] < 30:
        issues.append({"severity": "warning", "message": f"Low security score: {security['score']}% — consider hardening"})
    return issues


def get_unit_status(name):
    status = _run(f"systemctl is-active {name} 2>/dev/null")
    enabled = _run(f"systemctl is-enabled {name} 2>/dev/null")
    return {"active": status, "enabled": enabled}


def generate_report(filepath=None):
    if filepath:
        parsed = parse_unit_file(filepath)
        security = analyze_security(parsed)
        issues = lint_unit(filepath)
        name = os.path.basename(filepath)
        status = get_unit_status(name)
        return {
            "timestamp": datetime.now().isoformat(),
            "file": filepath,
            "name": name,
            "sections": parsed,
            "status": status,
            "security": security,
            "issues": issues,
            "issues_count": len(issues),
        }
    else:
        units = find_unit_files("service")
        all_issues = []
        summaries = []
        for u in units[:50]:
            name = os.path.basename(u)
            issues = lint_unit(u)
            sec = analyze_security(parse_unit_file(u))
            summaries.append({"file": name, "security_score": sec["score"], "issues": len(issues)})
            all_issues.extend(issues)
        return {
            "timestamp": datetime.now().isoformat(),
            "units_scanned": len(summaries),
            "summaries": summaries,
            "total_issues": len(all_issues),
            "issues": all_issues[:20],
        }


def audit(filepath=None):
    report = generate_report(filepath)
    return report.get("issues", [])
