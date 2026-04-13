import sys
from dargslan_crontab_backup import generate_report, export_all_crontabs, list_backups, get_user_crontab, get_system_cron_jobs
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report": print(generate_report())
    elif cmd == "export":
        exported = export_all_crontabs()
        for e in exported: print(f"  Exported {e['user']} ({e['lines']} lines) -> {e['file']}")
        if not exported: print("No crontabs to export.")
    elif cmd == "list":
        for b in list_backups(): print(f"  {b['modified']}  {b['file']}")
    elif cmd == "show":
        user = sys.argv[2] if len(sys.argv) > 2 else "root"
        ct = get_user_crontab(user)
        print(ct if ct else f"No crontab for {user}")
    elif cmd == "system":
        for j in get_system_cron_jobs(): print(f"  {j['directory']:25s} {j['file']}")
    elif cmd in ("help","--help","-h"): print("dargslan-cronbak -- Crontab backup manager\nUsage: dargslan-cronbak [report|export|list|show <user>|system]\nMore: https://dargslan.com")
    else: print(f"Unknown: {cmd}. Use --help"); sys.exit(1)
if __name__ == "__main__": main()
