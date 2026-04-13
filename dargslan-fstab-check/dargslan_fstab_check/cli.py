import sys
from dargslan_fstab_check import generate_report, parse_fstab, validate_fstab, check_mounted_vs_fstab
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report": print(generate_report())
    elif cmd == "list":
        for e in parse_fstab(): print(f"  {e['device']:40s} -> {e['mountpoint']:20s} ({e['fstype']})")
    elif cmd == "validate":
        r = validate_fstab()
        if r["issues"]:
            for i in r["issues"]: print(f"  [{i['severity'].upper()}] L{i['entry']['line_num']}: {i['issue']}")
        else: print("No issues found.")
    elif cmd == "unmounted":
        nm = check_mounted_vs_fstab()
        if nm:
            for m in nm: print(f"  [!] {m}")
        else: print("All fstab entries are mounted.")
    elif cmd in ("help","--help","-h"): print("dargslan-fstab -- Fstab validator\nUsage: dargslan-fstab [report|list|validate|unmounted]\nMore: https://dargslan.com")
    else: print(f"Unknown: {cmd}. Use --help"); sys.exit(1)
if __name__ == "__main__": main()
