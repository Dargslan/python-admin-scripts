import sys
from dargslan_motd_manager import generate_report, get_current_motd, generate_banner, get_motd_scripts, generate_system_info
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report": print(generate_report())
    elif cmd == "show":
        motd = get_current_motd()
        print(motd["content"] if motd else "No MOTD configured.")
    elif cmd == "banner": print(generate_banner())
    elif cmd == "info":
        for info in generate_system_info(): print(f"  {info}")
    elif cmd == "scripts":
        for s in get_motd_scripts():
            print(f"  {'[X]' if s['executable'] else '[ ]'} {s['name']}")
    elif cmd in ("help","--help","-h"): print("dargslan-motd -- MOTD & banner manager\nUsage: dargslan-motd [report|show|banner|info|scripts]\nMore: https://dargslan.com")
    else: print(f"Unknown: {cmd}. Use --help"); sys.exit(1)
if __name__ == "__main__": main()
