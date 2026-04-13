import os, sys, multiprocessing

  def get_load():
      try:
          return os.getloadavg()
      except:
          return (0, 0, 0)

  def get_cpu_count():
      try:
          return multiprocessing.cpu_count()
      except:
          return 1

  def get_processes():
      try:
          with open('/proc/loadavg') as f:
              parts = f.read().strip().split()
              if len(parts) >= 4:
                  running, total = parts[3].split('/')
                  return int(running), int(total)
      except:
          pass
      return 0, 0

  def load_bar(load_val, cpus):
      pct = min((load_val / cpus) * 100, 200)
      bar_len = 40
      filled = int(bar_len * min(pct, 100) / 100)
      over = int(bar_len * max(pct - 100, 0) / 100)
      bar = '█' * filled + '▓' * over + '░' * max(bar_len - filled - over, 0)
      return f"[{bar}] {pct:.0f}%"

  def main():
      print("=== Load Average Analyzer ===")
      print()
      load1, load5, load15 = get_load()
      cpus = get_cpu_count()
      running, total = get_processes()
      print(f"CPU cores:    {cpus}")
      print(f"Processes:    {running} running / {total} total")
      print()
      print(f"  1 min:  {load1:.2f}  {load_bar(load1, cpus)}")
      print(f"  5 min:  {load5:.2f}  {load_bar(load5, cpus)}")
      print(f" 15 min:  {load15:.2f}  {load_bar(load15, cpus)}")
      print()
      if load1 > cpus * 2:
          print("CRITICAL: Load significantly exceeds CPU count")
      elif load1 > cpus:
          print("WARNING: Load exceeds CPU count — possible bottleneck")
      elif load1 > cpus * 0.7:
          print("INFO: Moderate load")
      else:
          print("OK: Load is within normal range")

  if __name__ == "__main__":
      main()
  