import sys
from dargslan_sudoers_audit import generate_report, parse_sudoers, check_syntax, find_security_issues, get_sudo_users
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report": print(generate_report())
    elif cmd == "rules":
        for e in parse_sudoers(): print(f"  {e['rule']}")
    elif cmd == "syntax":
        s = check_syntax(); print(s["output"])
    elif cmd == "issues":
        issues = find_security_issues()
        if issues:
            for i in issues: print(f"  [{i['severity'].upper()}] {i['issue']}")
        else: print("No security issues found.")
    elif cmd == "users":
        users = get_sudo_users(); print(f"Sudo users: {', '.join(users)}" if users else "No sudo users found.")
    elif cmd in ("help","--help","-h"): print("dargslan-sudoers -- Sudoers auditor\nUsage: dargslan-sudoers [report|rules|syntax|issues|users]\nMore: https://dargslan.com")
    else: print(f"Unknown: {cmd}. Use --help"); sys.exit(1)
if __name__ == "__main__": main()
