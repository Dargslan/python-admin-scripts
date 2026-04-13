import sys
from dargslan_apt_history import generate_report, parse_apt_history, get_dpkg_recent, get_installed_count, check_security_updates
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report": print(generate_report())
    elif cmd == "history":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        for h in parse_apt_history(n): print(f"  {h.get('date',''):20s} [{h.get('type','?'):7s}] {h.get('packages','')[:80]}")
    elif cmd == "count": print(f"Installed packages: {get_installed_count()}")
    elif cmd == "security":
        sec = check_security_updates()
        if sec:
            for s in sec: print(f"  [SEC] {s}")
        else: print("No pending security updates.")
    elif cmd == "dpkg":
        for d in get_dpkg_recent(): print(f"  {d}")
    elif cmd in ("help","--help","-h"): print("dargslan-apthist -- Package install history\nUsage: dargslan-apthist [report|history|count|security|dpkg]\nMore: https://dargslan.com")
    else: print(f"Unknown: {cmd}. Use --help"); sys.exit(1)
if __name__ == "__main__": main()
