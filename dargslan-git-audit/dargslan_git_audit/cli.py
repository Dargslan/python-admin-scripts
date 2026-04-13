"""CLI for dargslan-git-audit — https://dargslan.com"""
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Dargslan Git Audit — Git repository security auditor",
        epilog="More tools at https://dargslan.com | eBooks: https://dargslan.com/books",
    )
    parser.add_argument("command", nargs="?", default="report",
                       choices=["report", "secrets", "sensitive", "gitignore", "large", "stats", "issues", "json"],
                       help="Command (default: report)")
    parser.add_argument("-p", "--path", help="Repository path")
    parser.add_argument("-s", "--size", type=int, default=10, help="Large file threshold (MB)")
    args = parser.parse_args()

    from dargslan_git_audit import GitAudit
    ga = GitAudit(repo_path=args.path)
    import json

    if args.command == 'report': ga.print_report()
    elif args.command == 'secrets':
        for s in ga.scan_working_secrets(): print(f"  [{s['severity'].upper()}] {s['file']}: {s['type']}")
    elif args.command == 'sensitive':
        for f in ga.check_sensitive_files(): print(f"  [{f['severity'].upper()}] {f['file']}")
    elif args.command == 'gitignore':
        for g in ga.check_gitignore():
            tracked = " [TRACKED!]" if g['tracked'] else ""
            print(f"  Missing: {g['pattern']}{tracked}")
    elif args.command == 'large':
        for f in ga.find_large_files(args.size): print(f"  {f['size_mb']:.1f} MB: {f['path']}")
    elif args.command == 'stats': print(json.dumps(ga.repo_stats(), indent=2))
    elif args.command == 'issues':
        for i in ga.audit(): print(f"  [{i['severity'].upper()}] {i['message']}")
    elif args.command == 'json': print(json.dumps(ga.audit(), indent=2))

if __name__ == "__main__": main()
