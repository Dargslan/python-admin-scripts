import os, subprocess, sys, glob

  def check_core_pattern():
      try:
          with open('/proc/sys/kernel/core_pattern') as f:
              return f.read().strip()
      except:
          return 'unknown'

  def check_core_limits():
      try:
          import resource
          soft, hard = resource.getrlimit(resource.RLIMIT_CORE)
          return soft, hard
      except:
          return -1, -1

  def find_core_dumps():
      cores = []
      for pattern in ['/var/lib/systemd/coredump/core.*', '/tmp/core.*', '/var/crash/*', './core', './core.*']:
          cores.extend(glob.glob(pattern))
      return cores

  def check_coredumpctl():
      try:
          result = subprocess.run(['coredumpctl', 'list', '--no-pager', '-n', '10'], capture_output=True, text=True, timeout=5)
          if result.returncode == 0:
              return result.stdout.strip()
      except:
          pass
      return None

  def main():
      print("=== Core Dump Checker ===")
      print()
      pattern = check_core_pattern()
      print(f"Core pattern: {pattern}")
      soft, hard = check_core_limits()
      print(f"Core limits:  soft={soft if soft >= 0 else 'unknown'}, hard={hard if hard >= 0 else 'unknown'}")
      if soft == 0:
          print("  INFO: Core dumps are disabled (soft limit = 0)")
      print()
      cores = find_core_dumps()
      if cores:
          print(f"Core dump files found: {len(cores)}")
          total = 0
          for c in cores[:10]:
              try:
                  sz = os.path.getsize(c)
                  total += sz
                  print(f"  {c} ({sz // 1024 // 1024}MB)")
              except:
                  print(f"  {c} (size unknown)")
          if total > 0:
              print(f"\nTotal core dump size: {total // 1024 // 1024}MB")
      else:
          print("No core dump files found")
      print()
      journal = check_coredumpctl()
      if journal:
          print("Recent coredumpctl entries:")
          print(journal)

  if __name__ == "__main__":
      main()
  