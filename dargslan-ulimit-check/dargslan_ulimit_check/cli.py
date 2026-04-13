import sys
from dargslan_ulimit_check import generate_report, get_current_limits, get_system_limits, get_open_files_count, check_limits_conf
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report": print(generate_report())
    elif cmd == "current":
        for k, v in get_current_limits().items(): print(f"  {k:45s} {v}")
    elif cmd == "system":
        for k, v in get_system_limits().items(): print(f"  {k:25s} = {v}")
    elif cmd == "files":
        of = get_open_files_count()
        if of: print(f"Open: {of['allocated']} / Max: {of['max']}")
        else: print("Cannot read file-nr")
    elif cmd == "conf":
        for e in check_limits_conf(): print(f"  [{e['source']}] {e['rule']}")
    elif cmd in ("help","--help","-h"): print("dargslan-ulimit -- Resource limits checker\nUsage: dargslan-ulimit [report|current|system|files|conf]\nMore: https://dargslan.com")
    else: print(f"Unknown: {cmd}. Use --help"); sys.exit(1)
if __name__ == "__main__": main()
