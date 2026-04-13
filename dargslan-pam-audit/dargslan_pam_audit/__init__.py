"""dargslan-pam-audit -- PAM configuration auditor.
Audit PAM stack, check module security, password policy, and auth settings.
Part of the Dargslan Linux Sysadmin Toolkit: https://dargslan.com
"""
__version__ = "1.0.0"
import os, glob

PAM_DIR = "/etc/pam.d"
CRITICAL_FILES = ["sshd", "login", "su", "sudo", "common-auth", "common-password", "system-auth", "password-auth"]

def get_pam_files():
    files = []
    if os.path.isdir(PAM_DIR):
        for f in sorted(os.listdir(PAM_DIR)):
            path = os.path.join(PAM_DIR, f)
            if os.path.isfile(path):
                try:
                    size = os.path.getsize(path)
                    files.append({"name": f, "path": path, "size": size, "critical": f in CRITICAL_FILES})
                except OSError: pass
    return files

def parse_pam_file(path):
    entries = []
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue
                if line.startswith("@include"):
                    entries.append({"type": "include", "module": line.split()[1] if len(line.split())>1 else "", "raw": line})
                else:
                    parts = line.split()
                    if len(parts) >= 3:
                        entries.append({"type": parts[0], "control": parts[1], "module": parts[2], "args": parts[3:] if len(parts)>3 else [], "raw": line})
    except (IOError, OSError): pass
    return entries

def audit_security():
    issues = []
    sshd = os.path.join(PAM_DIR, "sshd")
    if os.path.exists(sshd):
        entries = parse_pam_file(sshd)
        has_deny = any("pam_faildelay" in e.get("module","") or "pam_tally2" in e.get("module","") or "pam_faillock" in e.get("module","") for e in entries)
        if not has_deny: issues.append({"file": "sshd", "issue": "No brute-force protection module (pam_faillock/pam_tally2)", "severity": "warning"})
    for name in ["common-password", "password-auth", "system-auth"]:
        path = os.path.join(PAM_DIR, name)
        if os.path.exists(path):
            entries = parse_pam_file(path)
            has_quality = any("pam_pwquality" in e.get("module","") or "pam_cracklib" in e.get("module","") for e in entries)
            if not has_quality: issues.append({"file": name, "issue": "No password quality module (pam_pwquality/pam_cracklib)", "severity": "warning"})
            has_unix = any("pam_unix" in e.get("module","") for e in entries)
            if has_unix:
                sha512 = any("sha512" in " ".join(e.get("args",[])) for e in entries if "pam_unix" in e.get("module",""))
                if not sha512: issues.append({"file": name, "issue": "pam_unix not using sha512 hashing", "severity": "info"})
    return issues

def generate_report():
    files = get_pam_files()
    issues = audit_security()
    lines = ["="*60, "PAM CONFIGURATION AUDIT REPORT", "="*60]
    lines.append(f"\nPAM files found: {len(files)}")
    critical = [f for f in files if f["critical"]]
    lines.append(f"Critical files present: {len(critical)}/{len(CRITICAL_FILES)}")
    lines.append(f"Security issues: {len(issues)}")
    if critical:
        lines.append("\n--- Critical PAM Files ---")
        for f in critical:
            entries = parse_pam_file(f["path"])
            modules = set(e.get("module","").split("/")[-1] for e in entries if e.get("module"))
            lines.append(f"  {f['name']:20s} {len(entries)} rules  modules: {', '.join(sorted(modules)[:5])}")
    if issues:
        lines.append("\n--- Security Issues ---")
        for i in issues:
            icon = "[WRN]" if i["severity"]=="warning" else "[INF]"
            lines.append(f"  {icon} {i['file']}: {i['issue']}")
    missing = [f for f in CRITICAL_FILES if not os.path.exists(os.path.join(PAM_DIR, f))]
    if missing:
        lines.append("\n--- Missing Critical Files ---")
        for m in missing: lines.append(f"  [!] {m}")
    lines += ["\n"+"="*60, "More tools: https://dargslan.com | pip install dargslan-toolkit", "="*60]
    return "\n".join(lines)
