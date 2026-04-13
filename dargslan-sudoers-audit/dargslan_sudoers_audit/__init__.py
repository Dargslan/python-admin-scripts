"""dargslan-sudoers-audit -- Sudoers configuration auditor.
Check sudo rules, NOPASSWD entries, user privileges, and syntax validation.
Part of the Dargslan Linux Sysadmin Toolkit: https://dargslan.com
"""
__version__ = "1.0.0"
import subprocess, os

def parse_sudoers():
    entries = []
    for path in ["/etc/sudoers"]:
        try:
            with open(path) as f:
                for i, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#") or line.startswith("Defaults"): continue
                    entries.append({"line_num": i, "source": path, "rule": line, "has_nopasswd": "NOPASSWD" in line})
        except (IOError, PermissionError): pass
    sudoers_d = "/etc/sudoers.d"
    if os.path.isdir(sudoers_d):
        for fname in sorted(os.listdir(sudoers_d)):
            fpath = os.path.join(sudoers_d, fname)
            if os.path.isfile(fpath):
                try:
                    with open(fpath) as f:
                        for i, line in enumerate(f, 1):
                            line = line.strip()
                            if not line or line.startswith("#") or line.startswith("Defaults"): continue
                            entries.append({"line_num": i, "source": fpath, "rule": line, "has_nopasswd": "NOPASSWD" in line})
                except (IOError, PermissionError): pass
    return entries

def check_syntax():
    try:
        r = subprocess.run(["visudo", "-c"], capture_output=True, text=True, timeout=10)
        return {"valid": r.returncode == 0, "output": r.stdout.strip() + r.stderr.strip()}
    except (subprocess.SubprocessError, FileNotFoundError):
        return {"valid": None, "output": "visudo not available"}

def find_security_issues():
    issues = []
    entries = parse_sudoers()
    for e in entries:
        if e["has_nopasswd"]:
            if "ALL" in e["rule"].split("NOPASSWD")[-1]:
                issues.append({"rule": e["rule"], "source": e["source"], "issue": "NOPASSWD with ALL commands -- high risk", "severity": "high"})
            else:
                issues.append({"rule": e["rule"], "source": e["source"], "issue": "NOPASSWD entry found", "severity": "medium"})
        if "ALL=(ALL:ALL) ALL" in e["rule"] or "ALL=(ALL) ALL" in e["rule"]:
            if "root" not in e["rule"].split()[0] and "%" not in e["rule"].split()[0]:
                issues.append({"rule": e["rule"], "source": e["source"], "issue": "Full sudo access for non-root user", "severity": "medium"})
    return issues

def get_sudo_users():
    users = []
    try:
        r = subprocess.run(["getent", "group", "sudo"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            parts = r.stdout.strip().split(":")
            if len(parts) >= 4 and parts[3]: users.extend(parts[3].split(","))
    except (subprocess.SubprocessError, FileNotFoundError): pass
    try:
        r = subprocess.run(["getent", "group", "wheel"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            parts = r.stdout.strip().split(":")
            if len(parts) >= 4 and parts[3]: users.extend(parts[3].split(","))
    except (subprocess.SubprocessError, FileNotFoundError): pass
    return list(set(users))

def generate_report():
    entries = parse_sudoers()
    syntax = check_syntax()
    issues = find_security_issues()
    sudo_users = get_sudo_users()
    lines = ["="*60, "SUDOERS AUDIT REPORT", "="*60]
    lines.append(f"\nSyntax valid: {'Yes' if syntax['valid'] else 'No' if syntax['valid'] is not None else 'Unknown'}")
    lines.append(f"Total rules: {len(entries)}")
    lines.append(f"NOPASSWD rules: {sum(1 for e in entries if e['has_nopasswd'])}")
    lines.append(f"Security issues: {len(issues)}")
    if sudo_users: lines.append(f"Sudo/wheel users: {', '.join(sudo_users)}")
    if entries:
        lines.append("\n--- Sudoers Rules ---")
        for e in entries[:20]: lines.append(f"  [{os.path.basename(e['source'])}] {e['rule'][:80]}")
    if issues:
        lines.append("\n--- Security Issues ---")
        for i in issues:
            icon = "[HIGH]" if i["severity"]=="high" else "[MED]"
            lines.append(f"  {icon} {i['issue']}")
            lines.append(f"       Rule: {i['rule'][:70]}")
    lines += ["\n"+"="*60, "More tools: https://dargslan.com | pip install dargslan-toolkit", "="*60]
    return "\n".join(lines)
