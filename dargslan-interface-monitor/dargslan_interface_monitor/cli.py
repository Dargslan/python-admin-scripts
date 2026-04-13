import sys
from dargslan_interface_monitor import generate_report, get_interfaces, get_traffic_stats, check_errors
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report": print(generate_report())
    elif cmd == "list":
        for i in get_interfaces():
            state = "UP" if i["state"]=="up" else "DOWN"
            print(f"  {i['name']:15s} [{state}] {', '.join(i['ips']) if i['ips'] else 'no IP'}")
    elif cmd == "traffic":
        for s in get_traffic_stats():
            if s["rx_bytes"] > 0 or s["tx_bytes"] > 0:
                print(f"  {s['name']:15s} RX: {s['rx_human']:>10s}  TX: {s['tx_human']:>10s}")
    elif cmd == "errors":
        errs = check_errors()
        if errs:
            for e in errs: print(f"  [!] {e['name']}: {e['rx_errors']} rx errors, {e['tx_errors']} tx errors")
        else: print("No interface errors found.")
    elif cmd in ("help","--help","-h"): print("dargslan-iface -- Network interface monitor\nUsage: dargslan-iface [report|list|traffic|errors]\nMore: https://dargslan.com")
    else: print(f"Unknown: {cmd}. Use --help"); sys.exit(1)
if __name__ == "__main__": main()
