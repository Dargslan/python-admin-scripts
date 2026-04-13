#!/usr/bin/env python3
"""Environment variable auditor CLI - dargslan.com"""
import os, sys

BANNER = """
=============================================
  Environment Variable Auditor - dargslan.com
  Part of dargslan-toolkit
=============================================
"""

SENSITIVE_PATTERNS = ["PASSWORD", "SECRET", "TOKEN", "API_KEY", "PRIVATE_KEY", "CREDENTIAL", "AWS_ACCESS", "AWS_SECRET", "DB_PASS", "DATABASE_URL"]

def check_path():
    issues = []
    path = os.environ.get("PATH", "")
    dirs = path.split(":")
    seen = set()
    for d in dirs:
        if not d:
            issues.append("Empty entry in PATH")
        elif d in seen:
            issues.append(f"Duplicate PATH entry: {d}")
        elif not os.path.isdir(d):
            issues.append(f"Non-existent PATH dir: {d}")
        elif d == ".":
            issues.append("Current dir (.) in PATH - security risk")
        seen.add(d)
    return dirs, issues

def check_sensitive():
    findings = []
    for key in sorted(os.environ.keys()):
        for pattern in SENSITIVE_PATTERNS:
            if pattern in key.upper():
                val = os.environ[key]
                masked = val[:3] + "***" + val[-2:] if len(val) > 8 else "***"
                findings.append((key, masked))
                break
    return findings

def report():
    print(BANNER)
    env_count = len(os.environ)
    print(f"  Total environment variables: {env_count}")
    sensitive = check_sensitive()
    if sensitive:
        print(f"\n  Sensitive variables found ({len(sensitive)}):")
        for key, masked in sensitive:
            print(f"    [WARN] {key} = {masked}")
    else:
        print(f"\n  No sensitive variable patterns detected")
    path_dirs, path_issues = check_path()
    print(f"\n  PATH entries: {len(path_dirs)}")
    for d in path_dirs[:10]:
        exists = "OK" if os.path.isdir(d) else "MISSING"
        print(f"    [{exists:7s}] {d}")
    if len(path_dirs) > 10:
        print(f"    ... and {len(path_dirs)-10} more")
    if path_issues:
        print(f"\n  PATH issues ({len(path_issues)}):")
        for issue in path_issues:
            print(f"    [WARN] {issue}")
    shell = os.environ.get("SHELL", "unknown")
    user = os.environ.get("USER", "unknown")
    home = os.environ.get("HOME", "unknown")
    print(f"\n  Shell: {shell} | User: {user} | Home: {home}")
    print(f"\n  More tools: https://dargslan.com")
    print(f"  210+ eBooks: https://dargslan.com/books\n")

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "report"
    if cmd in ("report", "secrets", "path", "all"):
        report()
    else:
        print(f"  Usage: dargslan-envaudit [report|secrets|path]")

if __name__ == "__main__":
    main()
