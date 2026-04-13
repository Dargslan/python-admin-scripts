"""CLI for dargslan-ssh-audit — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan SSH Audit — Audit SSH server configuration",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "issues", "keys", "auth-keys", "json"],
                       help="Command (default: report)")
    parser.add_argument("-c", "--config", help="sshd_config path")
    args = parser.parse_args()

    from dargslan_ssh_audit import SSHAudit
    sa = SSHAudit(config_path=args.config)
    import json

    if args.command == 'report': sa.print_report()
    elif args.command == 'issues':
        for i in sa.audit(): print(f"  [{i['severity'].upper()}] {i.get('setting','')}: {i['message']}")
    elif args.command == 'keys':
        for k in sa.check_host_keys(): print(f"  {k['type']}: {k['path']} {'[WEAK]' if k['weak'] else '[OK]'}")
    elif args.command == 'auth-keys':
        for a in sa.check_authorized_keys(): print(f"  [{a['severity'].upper()}] {a['file']}: {a['issue']}")
    elif args.command == 'json': print(json.dumps(sa.audit(), indent=2))

if __name__ == "__main__": main()
