#!/usr/bin/env python3
"""SSH hardening checker CLI - dargslan.com"""
import subprocess, os, sys

BANNER = """
=============================================
  SSH Hardening Checker - dargslan.com
  Part of dargslan-toolkit
=============================================
"""

def get_sshd_config():
    config_path = "/etc/ssh/sshd_config"
    if not os.path.exists(config_path):
        return None, config_path
    try:
        with open(config_path, 'r') as f:
            return f.read(), config_path
    except PermissionError:
        return None, config_path

def parse_config(content):
    settings = {}
    if not content:
        return settings
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            settings[parts[0].lower()] = parts[1]
    return settings

def check_hardening(settings):
    checks = []
    checks.append(("PermitRootLogin", settings.get("permitrootlogin", "yes"), "no", "Disable root SSH login"))
    checks.append(("PasswordAuthentication", settings.get("passwordauthentication", "yes"), "no", "Use key-based auth only"))
    checks.append(("Port", settings.get("port", "22"), "non-22", "Change default SSH port"))
    checks.append(("PermitEmptyPasswords", settings.get("permitemptypasswords", "no"), "no", "Never allow empty passwords"))
    checks.append(("X11Forwarding", settings.get("x11forwarding", "yes"), "no", "Disable X11 forwarding"))
    checks.append(("MaxAuthTries", settings.get("maxauthtries", "6"), "3", "Limit auth attempts"))
    checks.append(("Protocol", settings.get("protocol", "2"), "2", "Use SSH protocol 2 only"))
    checks.append(("UsePAM", settings.get("usepam", "yes"), "yes", "Enable PAM authentication"))
    return checks

def report():
    print(BANNER)
    content, path = get_sshd_config()
    if content is None:
        print(f"  Cannot read {path} (run as root or check permissions)")
        print("\n  Recommended SSH hardening settings:")
        print("  - PermitRootLogin no")
        print("  - PasswordAuthentication no")
        print("  - Port <non-standard>")
        print("  - MaxAuthTries 3")
        print("  - X11Forwarding no")
    else:
        settings = parse_config(content)
        checks = check_hardening(settings)
        passed = 0
        for name, current, recommended, desc in checks:
            if name == "Port":
                ok = current != "22"
            else:
                ok = current.lower() == recommended.lower()
            status = "PASS" if ok else "WARN"
            if ok:
                passed += 1
            print(f"  [{status}] {name}: {current} (recommended: {recommended})")
            if not ok:
                print(f"         -> {desc}")
        print(f"\n  Score: {passed}/{len(checks)} checks passed")
    print(f"\n  More security tools: https://dargslan.com")
    print(f"  210+ eBooks: https://dargslan.com/books\n")

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "report"
    if cmd in ("report", "check", "audit"):
        report()
    elif cmd == "config":
        content, path = get_sshd_config()
        print(f"\n  SSH config: {path}")
        if content:
            settings = parse_config(content)
            for k, v in settings.items():
                print(f"  {k} = {v}")
        else:
            print("  Cannot read config")
    elif cmd == "keys":
        ssh_dir = os.path.expanduser("~/.ssh")
        print(f"\n  SSH keys in {ssh_dir}:")
        if os.path.isdir(ssh_dir):
            for f in os.listdir(ssh_dir):
                fp = os.path.join(ssh_dir, f)
                size = os.path.getsize(fp) if os.path.isfile(fp) else 0
                print(f"  {f:30s} {size:>8d} bytes")
        else:
            print("  No .ssh directory found")
    else:
        print(f"  Usage: dargslan-sshd [report|config|keys]")

if __name__ == "__main__":
    main()
