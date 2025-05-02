"""
BricksXploit - Databricks API Security Testing Tool
"""

import argparse
import sys
import os
from rich.console import Console
from rich.text import Text

# Configurar o ambiente para importações
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Importações absolutas
from core.auth import save_credentials
from core.report import validate_and_notify, generate_and_send_report
from menu_vertical import show_menu
from utils.storage import load_config
from utils.ui_vertical import VerticalUI

# Inicializar a interface vertical
ui = VerticalUI(title="BricksXploit", version="1.0.0")
console = Console()

def main():
    """
    Main entry point for BricksXploit
    """
    parser = argparse.ArgumentParser(description="BricksXploit - Databricks API Security Testing Tool")
    parser.add_argument("--workspace", help="Databricks workspace (e.g., dbc-xxxx.cloud.databricks.com)")
    parser.add_argument("--apikey", help="Databricks API key")
    parser.add_argument("--validate", action="store_true", help="Validate credentials only")
    parser.add_argument("--notify", choices=["discord"], help="Send notification to Discord")
    parser.add_argument("--output", help="Save report to file")
    parser.add_argument("--save", action="store_true", help="Save credentials if valid")
    parser.add_argument("--organization", help="Organization name for saved credentials")
    parser.add_argument("--profile", help="Profile name for saved credentials")

    args = parser.parse_args()
    config = load_config()

    # Handle command-line arguments
    if args.workspace and args.apikey:
        if args.validate:
            # Validate credentials only
            ui.add_notification(f"Validating credentials for workspace: {args.workspace}", "INFO")
            ui.display(Text(f"Validating credentials for workspace: {args.workspace}", style="cyan"))

            result = ui.run_with_spinner(
                f"Validating credentials for {args.workspace}...",
                validate_and_notify,
                args.workspace,
                args.apikey,
                args.notify
            )

            # Save credentials if requested and valid
            if args.save and result.get("status") == "valid":
                organization = args.organization
                profile_name = args.profile if args.profile else args.workspace

                ui.add_notification(f"Saving credentials for: {args.workspace}", "INFO")

                success = ui.run_with_spinner(
                    f"Saving credentials for {args.workspace}...",
                    save_credentials,
                    args.workspace,
                    args.apikey,
                    organization,
                    profile_name=profile_name
                )

                if success:
                    ui.add_notification(f"Credentials saved for: {profile_name}", "SUCCESS")
                    ui.display(Text(f"Credentials saved for: {profile_name}", style="green"))
                else:
                    ui.add_notification("Failed to save credentials.", "ERROR")
                    ui.display(Text("Failed to save credentials.", style="red"))

            return

        elif args.output or args.notify:
            # Generate report
            ui.add_notification(f"Generating report for workspace: {args.workspace}", "INFO")
            ui.display(Text(f"Generating report for workspace: {args.workspace}", style="cyan"))

            report_data = ui.run_with_spinner(
                f"Generating report for {args.workspace}...",
                generate_and_send_report,
                args.workspace,
                args.apikey,
                args.output,
                args.notify
            )

            if report_data:
                ui.add_notification("Report generated successfully.", "SUCCESS")

                result_text = Text("Report generated successfully.\n", style="green")

                if args.output:
                    ui.add_notification(f"Report saved to {args.output}", "SUCCESS")
                    result_text.append(f"Report saved to {args.output}\n", style="green")

                if args.notify:
                    ui.add_notification(f"Report sent to {args.notify}", "SUCCESS")
                    result_text.append(f"Report sent to {args.notify}", style="green")

                ui.display(result_text)

            # Save credentials if requested
            if args.save:
                organization = args.organization
                profile_name = args.profile if args.profile else args.workspace

                ui.add_notification(f"Saving credentials for: {args.workspace}", "INFO")

                success = ui.run_with_spinner(
                    f"Saving credentials for {args.workspace}...",
                    save_credentials,
                    args.workspace,
                    args.apikey,
                    organization,
                    profile_name=profile_name
                )

                if success:
                    ui.add_notification(f"Credentials saved for: {profile_name}", "SUCCESS")
                    ui.display(Text(f"Credentials saved for: {profile_name}", style="green"))
                else:
                    ui.add_notification("Failed to save credentials.", "ERROR")
                    ui.display(Text("Failed to save credentials.", style="red"))

            return

    # Show interactive menu
    show_menu(config)

if __name__ == "__main__":
    main()
