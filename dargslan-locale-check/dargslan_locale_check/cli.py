#!/usr/bin/env python3
"""Locale checker CLI - dargslan.com"""
import os, sys, subprocess, locale

BANNER = """
=============================================
  Locale & Language Checker - dargslan.com
  Part of dargslan-toolkit
=============================================
"""

def report():
    print(BANNER)
    current = locale.getlocale()
    print(f"  Current locale:    {current[0]}.{current[1]}" if current[0] else "  Current locale:    (not set)")
    env_vars = ["LANG", "LC_ALL", "LC_CTYPE", "LC_MESSAGES", "LC_COLLATE", "LC_TIME", "LC_NUMERIC", "LC_MONETARY", "LANGUAGE"]
    print(f"\n  Locale environment variables:")
    for v in env_vars:
        val = os.environ.get(v, "(not set)")
        print(f"    {v:15s} = {val}")
    try:
        result = subprocess.run(["locale", "-a"], capture_output=True, text=True, timeout=5)
        locales = result.stdout.strip().split('\n') if result.stdout.strip() else []
        utf8 = [l for l in locales if 'utf' in l.lower() or 'UTF' in l]
        print(f"\n  Available locales: {len(locales)} total, {len(utf8)} UTF-8")
        if utf8[:5]:
            for l in utf8[:5]:
                print(f"    {l}")
            if len(utf8) > 5:
                print(f"    ... and {len(utf8)-5} more")
    except:
        print("\n  Could not list available locales")
    print(f"\n  Python encoding:   {sys.getdefaultencoding()}")
    print(f"  Filesystem enc:    {sys.getfilesystemencoding()}")
    print(f"  Preferred enc:     {locale.getpreferredencoding()}")
    print(f"\n  More tools: https://dargslan.com")
    print(f"  210+ eBooks: https://dargslan.com/books\n")

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "report"
    if cmd in ("report", "list", "encoding"):
        report()
    else:
        print(f"  Usage: dargslan-locale [report|list|encoding]")

if __name__ == "__main__":
    main()
