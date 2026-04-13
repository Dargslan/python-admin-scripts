import os, subprocess, sys, datetime

  def get_ssh_keys():
      keys = []
      for user_dir in ['/root'] + [f'/home/{u}' for u in os.listdir('/home')] if os.path.isdir('/home') else ['/root']:
          ak = os.path.join(user_dir, '.ssh', 'authorized_keys')
          if os.path.isfile(ak):
              try:
                  with open(ak) as f:
                      for line in f:
                          line = line.strip()
                          if line and not line.startswith('#'):
                              keys.append({'user': os.path.basename(user_dir) if user_dir != '/root' else 'root', 'key': line, 'file': ak})
              except PermissionError:
                  keys.append({'user': os.path.basename(user_dir), 'key': '[permission denied]', 'file': ak})
      return keys

  def check_key_types(keys):
      weak = []
      for k in keys:
          parts = k['key'].split()
          if len(parts) >= 2:
              ktype = parts[0]
              if ktype in ('ssh-dss', 'ssh-dsa'):
                  weak.append(f"  WEAK: {k['user']} uses DSA key (deprecated)")
              elif ktype == 'ssh-rsa':
                  weak.append(f"  INFO: {k['user']} uses RSA key (consider ed25519)")
      return weak

  def main():
      print("=== SSH Key Audit ===")
      print()
      keys = get_ssh_keys()
      if not keys:
          print("No authorized_keys found")
          return
      print(f"Found {len(keys)} authorized key(s):")
      for k in keys:
          parts = k['key'].split()
          ktype = parts[0] if parts else 'unknown'
          comment = parts[-1] if len(parts) >= 3 else 'no-comment'
          print(f"  User: {k['user']}  Type: {ktype}  Comment: {comment}")
      print()
      weak = check_key_types(keys)
      if weak:
          print("Key Analysis:")
          for w in weak:
              print(w)
      else:
          print("All keys use strong algorithms")
      host_keys = [f for f in os.listdir('/etc/ssh') if f.startswith('ssh_host_') and f.endswith('.pub')] if os.path.isdir('/etc/ssh') else []
      if host_keys:
          print(f"\nHost keys: {len(host_keys)}")
          for hk in host_keys:
              print(f"  {hk}")

  if __name__ == "__main__":
      main()
  