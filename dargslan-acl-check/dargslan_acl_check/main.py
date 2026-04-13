import os, subprocess, sys, stat

  SENSITIVE_PATHS = ['/etc/shadow', '/etc/passwd', '/etc/sudoers', '/etc/ssh/sshd_config', '/root/.ssh', '/etc/crontab']

  def check_permissions(path):
      issues = []
      try:
          st = os.stat(path)
          mode = st.st_mode
          if mode & stat.S_IWOTH:
              issues.append(f"WARN: {path} is world-writable ({oct(mode)[-3:]})")
          if mode & stat.S_IROTH and path in ['/etc/shadow']:
              issues.append(f"CRIT: {path} is world-readable ({oct(mode)[-3:]})")
          if st.st_uid != 0 and path.startswith('/etc/'):
              issues.append(f"INFO: {path} not owned by root (uid={st.st_uid})")
      except (FileNotFoundError, PermissionError):
          pass
      return issues

  def check_suid():
      suids = []
      for d in ['/usr/bin', '/usr/sbin', '/bin', '/sbin']:
          if not os.path.isdir(d):
              continue
          try:
              for f in os.listdir(d):
                  fp = os.path.join(d, f)
                  try:
                      st = os.stat(fp)
                      if st.st_mode & stat.S_ISUID:
                          suids.append(fp)
                  except:
                      pass
          except:
              pass
      return suids

  def main():
      print("=== File ACL & Permission Checker ===")
      print()
      all_issues = []
      for p in SENSITIVE_PATHS:
          issues = check_permissions(p)
          all_issues.extend(issues)
      if all_issues:
          print("Permission Issues:")
          for i in all_issues:
              print(f"  {i}")
      else:
          print("No permission issues found on sensitive files")
      print()
      suids = check_suid()
      print(f"SUID binaries found: {len(suids)}")
      for s in suids[:15]:
          print(f"  {s}")
      if len(suids) > 15:
          print(f"  ... and {len(suids)-15} more")

  if __name__ == "__main__":
      main()
  