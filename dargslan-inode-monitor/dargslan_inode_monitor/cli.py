import sys
from dargslan_inode_monitor import generate_report, get_inode_usage, find_inode_heavy_dirs, check_inode_alerts
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report": print(generate_report())
    elif cmd == "usage":
        for u in get_inode_usage(): print(f"  {u['mountpoint']:25s} {u['use_percent']:>5s} ({u['inodes_used']}/{u['inodes_total']})")
    elif cmd == "heavy":
        d = sys.argv[2] if len(sys.argv) > 2 else "/var"
        for h in find_inode_heavy_dirs(d): print(f"  {h['entries']:>8d} entries  {h['path']}")
    elif cmd == "alerts":
        alerts = check_inode_alerts()
        if alerts:
            for a in alerts: print(f"  [!] {a['mountpoint']} at {a['use_percent']}")
        else: print("No inode alerts.")
    elif cmd in ("help","--help","-h"): print("dargslan-inodes -- Inode usage monitor\nUsage: dargslan-inodes [report|usage|heavy|alerts]\nMore: https://dargslan.com")
    else: print(f"Unknown: {cmd}. Use --help"); sys.exit(1)
if __name__ == "__main__": main()
