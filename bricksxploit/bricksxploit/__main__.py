from bricksxploit.core import auth
from bricksxploit.menu import show_menu
from bricksxploit.utils.storage import load_config, save_config
from bricksxploit.core.report import generate_and_send_report

import argparse
from rich.console import Console

console = Console()

def main():
    parser = argparse.ArgumentParser(description="bricksxploit - Databricks API Exploitation Toolkit")
    parser.add_argument("--workspace", help="Databricks workspace ID (e.g., dbc-xxxx)")
    parser.add_argument("--apikey", help="Personal access token")
    parser.add_argument("--notify", choices=["discord"], help="Send report to Discord")
    parser.add_argument("--output", help="Save report to .json file")

    args = parser.parse_args()
    config = load_config()

    if args.workspace and args.apikey:
        try:
            profile = auth.validate_credentials(args.workspace, args.apikey)
            config['profiles'][args.workspace] = {
                "apikey": args.apikey,
                "user": profile.get("userName"),
                "displayName": profile.get("displayName"),
                "groups": profile.get("groups", [])
            }
            config["current"] = args.workspace
            save_config(config)

            console.print(f"\n[bold green]✔️ Credentials validated successfully![/bold green]")
            console.print(f"[cyan]Successfully logged in as [bold]{profile.get('displayName')}[/bold] ({profile.get('userName')})[/cyan]")

            auth.display_user_info_table(profile)

            if args.output or args.notify:
                generate_and_send_report(args.workspace, args.apikey, args.output, args.notify)
                return

        except Exception as e:
            console.print(f"[red]Failed to authenticate: {e}[/red]")
            return

    show_menu(config)

if __name__ == "__main__":
    main()
