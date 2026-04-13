"""CLI for dargslan-docker-health — https://dargslan.com"""
import argparse
import json
from dargslan_docker_health.health import DockerHealth

def main():
    parser = argparse.ArgumentParser(description="Docker Health Check — dargslan.com")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--unhealthy", action="store_true", help="Show only unhealthy")
    parser.add_argument("--all", action="store_true", help="Include stopped containers")
    args = parser.parse_args()

    dh = DockerHealth()
    if args.json:
        data = dh.get_unhealthy() if args.unhealthy else dh.check_all()
        print(json.dumps(data, indent=2, default=str))
    else:
        dh.print_status(unhealthy_only=args.unhealthy)

if __name__ == "__main__":
    main()
