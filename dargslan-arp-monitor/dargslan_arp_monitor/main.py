import subprocess, sys, os, re

  def get_arp_table():
      entries = []
      try:
          if os.path.isfile('/proc/net/arp'):
              with open('/proc/net/arp') as f:
                  lines = f.readlines()[1:]
                  for line in lines:
                      parts = line.split()
                      if len(parts) >= 6:
                          entries.append({'ip': parts[0], 'type': parts[1], 'flags': parts[2], 'mac': parts[3], 'mask': parts[4], 'device': parts[5]})
      except Exception as e:
          print(f"Error reading ARP table: {e}")
      return entries

  def detect_duplicates(entries):
      mac_map = {}
      for e in entries:
          if e['mac'] != '00:00:00:00:00:00':
              mac_map.setdefault(e['mac'], []).append(e['ip'])
      return {mac: ips for mac, ips in mac_map.items() if len(ips) > 1}

  def main():
      print("=== ARP Table Monitor ===")
      print()
      entries = get_arp_table()
      if not entries:
          print("ARP table is empty")
          return
      print(f"{'IP Address':<18} {'MAC Address':<20} {'Device':<10} {'Flags'}")
      print("-" * 60)
      for e in entries:
          print(f"{e['ip']:<18} {e['mac']:<20} {e['device']:<10} {e['flags']}")
      dupes = detect_duplicates(entries)
      if dupes:
          print(f"\nWARNING: Duplicate MACs detected:")
          for mac, ips in dupes.items():
              print(f"  {mac} -> {', '.join(ips)}")
      stale = [e for e in entries if e['mac'] == '00:00:00:00:00:00']
      if stale:
          print(f"\nIncomplete entries: {len(stale)}")
          for s in stale:
              print(f"  {s['ip']} on {s['device']}")
      print(f"\nTotal: {len(entries)} entries, {len(dupes)} duplicate MACs, {len(stale)} incomplete")

  if __name__ == "__main__":
      main()
  