import os, sys, time

  def get_diskstats():
      stats = {}
      try:
          with open('/proc/diskstats') as f:
              for line in f:
                  parts = line.split()
                  if len(parts) >= 14:
                      name = parts[2]
                      if not any(name.startswith(p) for p in ['loop', 'ram', 'dm-']):
                          stats[name] = {
                              'reads': int(parts[3]), 'read_sectors': int(parts[5]),
                              'read_ms': int(parts[6]), 'writes': int(parts[7]),
                              'write_sectors': int(parts[9]), 'write_ms': int(parts[10]),
                              'io_ms': int(parts[12])
                          }
      except Exception as e:
          print(f"Error: {e}")
      return stats

  def format_bytes(sectors, sector_size=512):
      b = sectors * sector_size
      for u in ['B', 'KB', 'MB', 'GB', 'TB']:
          if b < 1024:
              return f"{b:.1f} {u}"
          b /= 1024
      return f"{b:.1f} PB"

  def main():
      print("=== Disk I/O Monitor ===")
      print()
      stats = get_diskstats()
      if not stats:
          print("No disk statistics available")
          return
      print(f"{'Device':<12} {'Reads':<10} {'Read Data':<12} {'Writes':<10} {'Write Data':<12} {'IO ms'}")
      print("-" * 70)
      for name, s in sorted(stats.items()):
          if any(c.isdigit() for c in name) and not name[-1].isdigit():
              continue
          print(f"{name:<12} {s['reads']:<10} {format_bytes(s['read_sectors']):<12} {s['writes']:<10} {format_bytes(s['write_sectors']):<12} {s['io_ms']}")

  if __name__ == "__main__":
      main()
  