import sys
from dargslan_kernel_module import generate_report, get_loaded_modules, get_module_info, find_unused_modules, get_blacklisted, _human_size
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report": print(generate_report())
    elif cmd == "list":
        for m in get_loaded_modules(): print(f"  {m['name']:30s} {_human_size(m['size']):>8s}  used: {m['used_by']}")
    elif cmd == "info":
        if len(sys.argv)<3: print("Usage: dargslan-kmod info <module>"); sys.exit(1)
        info = get_module_info(sys.argv[2])
        if info:
            for k, v in info.items(): print(f"  {k}: {v}")
        else: print(f"Module not found: {sys.argv[2]}")
    elif cmd == "unused":
        for m in find_unused_modules(): print(f"  {m['name']:30s} {_human_size(m['size'])}")
    elif cmd == "blacklist":
        for b in get_blacklisted(): print(f"  {b['module']:30s} ({b['source']})")
    elif cmd in ("help","--help","-h"): print("dargslan-kmod -- Kernel module manager\nUsage: dargslan-kmod [report|list|info <mod>|unused|blacklist]\nMore: https://dargslan.com")
    else: print(f"Unknown: {cmd}. Use --help"); sys.exit(1)
if __name__ == "__main__": main()
