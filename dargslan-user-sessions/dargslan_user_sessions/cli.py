"""CLI interface for dargslan-user-sessions."""

import sys
from dargslan_user_sessions import generate_report, get_active_sessions, get_idle_sessions, get_session_types, get_last_logins


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "report"

    if cmd == "report":
        print(generate_report())
    elif cmd == "active":
        for s in get_active_sessions():
            print(f"{s['user']:15s} {s['tty']:10s} {s.get('date','')} {s.get('time','')}")
    elif cmd == "idle":
        minutes = int(args[1]) if len(args) > 1 else 30
        idle = get_idle_sessions(minutes)
        if idle:
            for s in idle:
                print(f"[IDLE] {s['user']:15s} {s['tty']:10s} {s.get('idle_minutes', '?')}min")
        else:
            print(f"No sessions idle for more than {minutes} minutes.")
    elif cmd == "types":
        types = get_session_types()
        for t, sessions in types.items():
            if sessions:
                print(f"\n{t.upper()} ({len(sessions)}):")
                for s in sessions:
                    print(f"  {s['user']:15s} {s['tty']}")
    elif cmd == "last":
        count = int(args[1]) if len(args) > 1 else 10
        for entry in get_last_logins(count):
            print(f"  {entry}")
    elif cmd in ("help", "--help", "-h"):
        print("dargslan-sessions — Linux user session manager")
        print("Usage: dargslan-sessions [command]")
        print("Commands: report, active, idle [min], types, last [n]")
        print("More: https://dargslan.com")
    else:
        print(f"Unknown command: {cmd}. Use --help for usage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
