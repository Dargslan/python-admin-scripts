"""CLI for dargslan-container-audit — https://dargslan.com"""

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Container Audit — Security audit for Docker/Podman containers",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "list", "privileged", "root", "caps", "volumes", "network", "issues", "json"],
                       help="Command (default: report)")
    parser.add_argument("-r", "--runtime", choices=["docker", "podman"], help="Container runtime")
    args = parser.parse_args()

    from dargslan_container_audit import ContainerAudit
    ca = ContainerAudit(runtime=args.runtime)

    import json as jsonlib

    if args.command == 'report':
        ca.print_report()
    elif args.command == 'list':
        for c in ca.list_containers():
            print(f"  [{c.get('state','?'):10s}] {c.get('name','?'):30s} {c.get('image','?')}")
    elif args.command == 'privileged':
        for c in ca.check_privileged():
            print(f"  PRIVILEGED: {c['name']} ({c['image']})")
    elif args.command == 'root':
        for c in ca.check_root_containers():
            print(f"  ROOT: {c['name']} as {c['user']}")
    elif args.command == 'caps':
        for c in ca.check_capabilities():
            print(f"  {c['name']}: {', '.join(c['dangerous_caps'])}")
    elif args.command == 'volumes':
        for v in ca.check_volumes():
            print(f"  {v['name']}: {v['mount']} ({v['mode']})")
    elif args.command == 'network':
        for n in ca.check_network_mode():
            print(f"  {n['name']}: {n['network_mode']}")
    elif args.command == 'issues':
        for i in ca.audit():
            print(f"  [{i['severity'].upper():8s}] {i['message']}")
    elif args.command == 'json':
        print(jsonlib.dumps(ca.audit(), indent=2))


if __name__ == "__main__":
    main()
