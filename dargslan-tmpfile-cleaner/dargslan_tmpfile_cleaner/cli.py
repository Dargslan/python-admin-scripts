import sys
from dargslan_tmpfile_cleaner import generate_report, scan_tmp_files, get_tmp_usage, find_orphaned_dirs
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report": print(generate_report())
    elif cmd == "scan":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        for f in scan_tmp_files("/tmp", days): print(f"  {f['size_human']:>10s}  {f['age_days']}d  {f['path']}")
    elif cmd == "usage":
        for u in get_tmp_usage(): print(f"  {u['directory']:20s} {u['total_human']:>10s} ({u['files']} files)")
    elif cmd == "orphaned":
        for d in find_orphaned_dirs(): print(f"  {d['size_human']:>10s}  {d['age_days']}d  {d['path']}")
    elif cmd in ("help","--help","-h"): print("dargslan-tmpclean -- Temp file cleaner\nUsage: dargslan-tmpclean [report|scan|usage|orphaned]\nMore: https://dargslan.com")
    else: print(f"Unknown: {cmd}. Use --help"); sys.exit(1)
if __name__ == "__main__": main()
