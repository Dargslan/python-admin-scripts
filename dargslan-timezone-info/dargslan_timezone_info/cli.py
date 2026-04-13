import sys
from dargslan_timezone_info import generate_report, get_timezone, check_ntp_status, get_hardware_clock
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report": print(generate_report())
    elif cmd == "timezone":
        tz = get_timezone(); print(f"Timezone: {tz['timezone']} (UTC{tz['utc_offset']})")
    elif cmd == "ntp":
        n = check_ntp_status()
        print(f"Synced: {'Yes' if n['synced'] else 'No'}"); print(f"Service: {n['service']}")
        if n['server']: print(f"Server: {n['server']}")
    elif cmd == "hwclock":
        hw = get_hardware_clock(); print(hw if hw else "Cannot read hardware clock.")
    elif cmd in ("help","--help","-h"): print("dargslan-tz -- Timezone & NTP checker\nUsage: dargslan-tz [report|timezone|ntp|hwclock]\nMore: https://dargslan.com")
    else: print(f"Unknown: {cmd}. Use --help"); sys.exit(1)
if __name__ == "__main__": main()
