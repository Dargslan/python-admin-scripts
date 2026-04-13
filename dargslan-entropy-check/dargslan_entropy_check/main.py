import os, sys, time

  def get_entropy():
      try:
          with open('/proc/sys/kernel/random/entropy_avail') as f:
              return int(f.read().strip())
      except:
          return -1

  def get_pool_size():
      try:
          with open('/proc/sys/kernel/random/poolsize') as f:
              return int(f.read().strip())
      except:
          return -1

  def get_urandom_min():
      try:
          with open('/proc/sys/kernel/random/urandom_min_reseed_secs') as f:
              return int(f.read().strip())
      except:
          return -1

  def check_rng_devices():
      devices = []
      for dev in ['/dev/random', '/dev/urandom', '/dev/hwrng']:
          if os.path.exists(dev):
              devices.append(dev)
      return devices

  def main():
      print("=== System Entropy Monitor ===")
      print()
      entropy = get_entropy()
      pool = get_pool_size()
      print(f"Available entropy:  {entropy} bits")
      print(f"Pool size:          {pool} bits")
      if entropy >= 0 and pool > 0:
          pct = (entropy / pool) * 100
          print(f"Pool fill:          {pct:.1f}%")
          bar_len = 40
          filled = int(bar_len * pct / 100)
          bar = '█' * filled + '░' * (bar_len - filled)
          print(f"  [{bar}]")
      print()
      if entropy < 100:
          print("WARNING: Low entropy! Crypto operations may block.")
          print("  Consider: apt install haveged / rng-tools")
      elif entropy < 500:
          print("INFO: Moderate entropy level")
      else:
          print("OK: Sufficient entropy for crypto operations")
      print()
      devs = check_rng_devices()
      print(f"RNG devices: {', '.join(devs)}")
      reseed = get_urandom_min()
      if reseed >= 0:
          print(f"Urandom reseed interval: {reseed}s")

  if __name__ == "__main__":
      main()
  