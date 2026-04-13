import sys
from dargslan_pam_audit import generate_report, get_pam_files, parse_pam_file, audit_security
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report": print(generate_report())
    elif cmd == "files":
        for f in get_pam_files():
            flag = " [CRITICAL]" if f["critical"] else ""
            print(f"  {f['name']:25s} {f['size']:>6d}B{flag}")
    elif cmd == "audit":
        issues = audit_security()
        if issues:
            for i in issues: print(f"  [{i['severity'].upper()}] {i['file']}: {i['issue']}")
        else: print("No security issues found.")
    elif cmd == "show":
        if len(sys.argv) < 3: print("Usage: dargslan-pam show <file>"); sys.exit(1)
        import os; path = os.path.join("/etc/pam.d", sys.argv[2])
        for e in parse_pam_file(path): print(f"  {e['raw']}")
    elif cmd in ("help","--help","-h"): print("dargslan-pam -- PAM config auditor\nUsage: dargslan-pam [report|files|audit|show <file>]\nMore: https://dargslan.com")
    else: print(f"Unknown: {cmd}. Use --help"); sys.exit(1)
if __name__ == "__main__": main()
