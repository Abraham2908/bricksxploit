"""
Main menu system for BricksXploit
"""

import sys
import os
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box

# Adicionar o diretório raiz ao path para permitir importações absolutas
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.auth import validate_credentials, display_user_info, save_credentials, get_current_credentials
from core.scan import run_full_scan, run_targeted_scan, run_sql_query, display_scan_summary, validate_workspace_access
from core.report import generate_and_send_report, display_report, generate_markdown_report, validate_and_notify
from core.profiles import list_profiles, switch_profile, add_new_profile, remove_profile
from utils.storage import load_config, save_config, get_current_profile, list_scan_history, load_scan_result
from utils.ui import create_menu, print_success, print_error, print_warning, print_info, confirm, ask_for_input
from utils.banner import print_banner, print_section_header
from utils.discord import set_webhook_url, get_webhook_url

console = Console()

def show_menu(config):
    """
    Display the main menu and handle user choices

    Args:
        config (dict): Application configuration
    """
    print_banner()

    # Get current profile info for display
    org, profile_name, profile_data = get_current_profile()
    active_profile = f"{profile_name} ({org})" if org else profile_name if profile_name else "None"

    while True:
        # Main menu options
        choice = create_menu(
            "Main Menu",
            [
                ("1", "Profile Management"),
                ("2", "Scan Workspace"),
                ("3", "Run SQL Query"),
                ("4", "Generate Reports"),
                ("5", "View Results"),
                ("6", "Configuration"),
                ("7", "Validate Credentials"),
                ("8", "Exit")
            ],
            active_profile
        )

        if choice == "1":
            # Profile management submenu
            profile_menu(config)
        elif choice == "2":
            # Scan workspace submenu
            scan_menu(config)
        elif choice == "3":
            # SQL query execution
            sql_menu(config)
        elif choice == "4":
            # Report generation submenu
            report_menu(config)
        elif choice == "5":
            # View results submenu
            results_menu(config)
        elif choice == "6":
            # Configuration submenu
            config_menu(config)
        elif choice == "7":
            # Validate credentials
            validate_menu(config)
        elif choice == "8":
            # Exit
            print_success("Exiting BricksXploit. Goodbye!")
            break

def profile_menu(config):
    """
    Display the profile management menu

    Args:
        config (dict): Application configuration
    """
    print_section_header("Profile Management")

    while True:
        # Get current profile info for display
        org, profile_name, profile_data = get_current_profile()
        active_profile = f"{profile_name} ({org})" if org else profile_name if profile_name else "None"

        choice = create_menu(
            "Profile Management",
            [
                ("1", "List Profiles"),
                ("2", "Switch Profile"),
                ("3", "Add New Profile"),
                ("4", "Remove Profile"),
                ("5", "View Current Profile"),
                ("6", "Back to Main Menu")
            ],
            active_profile
        )

        if choice == "1":
            # List all profiles
            list_profiles()
        elif choice == "2":
            # Switch to a different profile
            switch_profile()
        elif choice == "3":
            # Add a new profile
            workspace = ask_for_input("Enter workspace (e.g., dbc-xxxx.cloud.databricks.com): ")
            apikey = ask_for_input("Enter API key: ", password=True)
            organization = ask_for_input("Enter organization name (optional): ", default="")

            if not organization:
                organization = None

            add_new_profile(workspace, apikey, organization)
        elif choice == "4":
            # Remove a profile
            remove_profile()
        elif choice == "5":
            # View current profile details
            org, profile_name, profile_data = get_current_profile()

            if not profile_data:
                print_warning("No active profile selected.")
                continue

            print_info(f"Current Profile: {profile_name}")
            if org:
                print_info(f"Organization: {org}")

            print_info(f"Workspace: {profile_data.get('workspace')}")
            print_info(f"Created: {profile_data.get('created_at')}")

            # Display metadata if available
            metadata = profile_data.get("metadata", {})
            if metadata:
                print_info("Profile Metadata:")
                for key, value in metadata.items():
                    if key == "groups" or key == "roles":
                        if isinstance(value, list) and value:
                            print_info(f"  {key.title()}: {', '.join(value[:5])}" +
                                      (f" and {len(value) - 5} more" if len(value) > 5 else ""))
                    else:
                        print_info(f"  {key.title()}: {value}")
        elif choice == "6":
            # Back to main menu
            break

def scan_menu(config):
    """
    Display the scan menu

    Args:
        config (dict): Application configuration
    """
    print_section_header("Scan Workspace")

    while True:
        # Get current profile info for display
        org, profile_name, profile_data = get_current_profile()
        active_profile = f"{profile_name} ({org})" if org else profile_name if profile_name else "None"

        choice = create_menu(
            "Scan Options",
            [
                ("1", "Run Full Security Scan"),
                ("2", "Scan Users and Groups"),
                ("3", "Scan Clusters"),
                ("4", "Scan Secret Scopes"),
                ("5", "Scan SQL Warehouses"),
                ("6", "Scan Unity Catalog Resources"),
                ("7", "Back to Main Menu")
            ],
            active_profile
        )

        # Get current credentials
        workspace, apikey, profile_data = get_current_credentials()

        if not workspace or not apikey:
            print_error("No active profile selected. Please select a profile first.")
            break

        if choice == "1":
            # Run full security scan
            scan_results = run_full_scan(workspace, profile_data)
            if scan_results:
                display_scan_summary(scan_results)

                # Ask if user wants to generate a report
                if confirm("Would you like to generate a report from these results?", default=False):
                    output = ask_for_input("Enter output file name (leave empty to skip): ", default="")
                    notify = confirm("Send notification to Discord?", default=False)

                    generate_and_send_report(
                        workspace,
                        apikey,
                        output if output else None,
                        "discord" if notify else None,
                        scan_results
                    )
        elif choice == "2":
            # Scan users and groups
            scan_results = run_targeted_scan(workspace, profile_data, "users")
            if scan_results:
                print_success("Users and groups scan completed successfully.")
        elif choice == "3":
            # Scan clusters
            scan_results = run_targeted_scan(workspace, profile_data, "clusters")
            if scan_results:
                print_success("Clusters scan completed successfully.")
        elif choice == "4":
            # Scan secret scopes
            scan_results = run_targeted_scan(workspace, profile_data, "secrets")
            if scan_results:
                print_success("Secret scopes scan completed successfully.")
        elif choice == "5":
            # Scan SQL warehouses
            scan_results = run_targeted_scan(workspace, profile_data, "warehouses")
            if scan_results:
                print_success("SQL warehouses scan completed successfully.")
        elif choice == "6":
            # Scan Unity Catalog resources
            scan_results = run_targeted_scan(workspace, profile_data, "catalogs")
            if scan_results:
                print_success("Unity Catalog resources scan completed successfully.")
        elif choice == "7":
            # Back to main menu
            break

def sql_menu(config):
    """
    Display the SQL query menu

    Args:
        config (dict): Application configuration
    """
    print_section_header("SQL Query Execution")

    # Get current credentials
    workspace, apikey, profile_data = get_current_credentials()

    if not workspace or not apikey:
        print_error("No active profile selected. Please select a profile first.")
        return

    # Get query from user
    print_info("Enter SQL query to execute (press Enter twice to finish):")
    lines = []
    while True:
        line = input()
        if not line and lines and not lines[-1]:
            break
        lines.append(line)

    query = "\n".join(lines[:-1])  # Remove the last empty line

    if not query.strip():
        print_warning("Empty query. Operation cancelled.")
        return

    # Ask for additional parameters
    warehouse_id = ask_for_input("Enter warehouse ID (optional): ", default="")
    catalog = ask_for_input("Enter catalog name (optional): ", default="")
    schema = ask_for_input("Enter schema name (optional): ", default="")

    # Execute the query
    run_sql_query(
        workspace,
        profile_data,
        query,
        warehouse_id if warehouse_id else None,
        catalog if catalog else None,
        schema if schema else None
    )

def report_menu(config):
    """
    Display the report generation menu

    Args:
        config (dict): Application configuration
    """
    print_section_header("Report Generation")

    while True:
        # Get current profile info for display
        org, profile_name, profile_data = get_current_profile()
        active_profile = f"{profile_name} ({org})" if org else profile_name if profile_name else "None"

        choice = create_menu(
            "Report Options",
            [
                ("1", "Generate Full Security Report"),
                ("2", "Generate Markdown Report"),
                ("3", "View Latest Report"),
                ("4", "Send Report to Discord"),
                ("5", "Back to Main Menu")
            ],
            active_profile
        )

        # Get current credentials
        workspace, apikey, profile_data = get_current_credentials()

        if not workspace or not apikey:
            print_error("No active profile selected. Please select a profile first.")
            break

        if choice == "1":
            # Generate full security report
            output = ask_for_input("Enter output file name (leave empty to skip): ", default="")
            notify = confirm("Send notification to Discord?", default=False)

            report_data = generate_and_send_report(
                workspace,
                apikey,
                output if output else None,
                "discord" if notify else None
            )

            if report_data:
                display_report(report_data)
        elif choice == "2":
            # Generate Markdown report
            # First, get the latest scan results
            history = list_scan_history(limit=5)

            if not history:
                print_warning("No scan history found. Run a scan first.")
                continue

            print_info("Select a scan result to use:")
            for i, item in enumerate(history):
                print_info(f"{i+1}. {item.get('scan_type')} - {item.get('workspace')} - {item.get('timestamp')}")

            selection = ask_for_input("Enter selection (or 0 to cancel): ", default="1")

            try:
                selection = int(selection)
                if selection == 0:
                    continue

                if selection < 1 or selection > len(history):
                    print_error("Invalid selection.")
                    continue

                # Load the selected scan result
                scan_result = load_scan_result(history[selection-1].get("filename"))

                if not scan_result:
                    print_error("Failed to load scan result.")
                    continue

                # Generate Markdown report
                output = ask_for_input("Enter output file name (leave empty to skip): ", default="")

                markdown = generate_markdown_report(
                    scan_result.get("data", scan_result),
                    output if output else None
                )

                if markdown:
                    print_success("Markdown report generated successfully.")
            except ValueError:
                print_error("Invalid selection. Please enter a number.")
        elif choice == "3":
            # View latest report
            history = list_scan_history(limit=5)

            if not history:
                print_warning("No scan history found. Run a scan first.")
                continue

            # Find the latest report
            report_items = [item for item in history if item.get("scan_type") == "report"]

            if not report_items:
                print_warning("No report found in history. Generate a report first.")
                continue

            # Load and display the latest report
            report_data = load_scan_result(report_items[0].get("filename"))

            if report_data:
                display_report(report_data.get("data", report_data))
            else:
                print_error("Failed to load report.")
        elif choice == "4":
            # Send report to Discord
            webhook_url = get_webhook_url()

            if not webhook_url:
                print_error("Discord webhook URL not configured.")
                print_info("Use Configuration > Discord Settings to set up webhook URL.")
                continue

            # Get the latest scan results
            history = list_scan_history(limit=5)

            if not history:
                print_warning("No scan history found. Run a scan first.")
                continue

            print_info("Select a scan result to send:")
            for i, item in enumerate(history):
                print_info(f"{i+1}. {item.get('scan_type')} - {item.get('workspace')} - {item.get('timestamp')}")

            selection = ask_for_input("Enter selection (or 0 to cancel): ", default="1")

            try:
                selection = int(selection)
                if selection == 0:
                    continue

                if selection < 1 or selection > len(history):
                    print_error("Invalid selection.")
                    continue

                # Load the selected scan result
                scan_result = load_scan_result(history[selection-1].get("filename"))

                if not scan_result:
                    print_error("Failed to load scan result.")
                    continue

                # Generate and send report
                report_data = generate_and_send_report(
                    scan_result.get("workspace", workspace),
                    apikey,
                    None,
                    "discord",
                    scan_result.get("data", scan_result)
                )

                if report_data:
                    print_success("Report sent to Discord successfully.")
            except ValueError:
                print_error("Invalid selection. Please enter a number.")
        elif choice == "5":
            # Back to main menu
            break

def results_menu(config):
    """
    Display the results viewing menu

    Args:
        config (dict): Application configuration
    """
    print_section_header("View Results")

    while True:
        choice = create_menu(
            "Results Options",
            [
                ("1", "View Scan History"),
                ("2", "View Specific Scan Result"),
                ("3", "Back to Main Menu")
            ]
        )

        if choice == "1":
            # View scan history
            history = list_scan_history(limit=10)

            if not history:
                print_warning("No scan history found.")
                continue

            print_info("Scan History:")
            for i, item in enumerate(history):
                print_info(f"{i+1}. {item.get('scan_type')} - {item.get('workspace')} - {item.get('timestamp')}")
        elif choice == "2":
            # View specific scan result
            history = list_scan_history(limit=10)

            if not history:
                print_warning("No scan history found.")
                continue

            print_info("Select a scan result to view:")
            for i, item in enumerate(history):
                print_info(f"{i+1}. {item.get('scan_type')} - {item.get('workspace')} - {item.get('timestamp')}")

            selection = ask_for_input("Enter selection (or 0 to cancel): ", default="1")

            try:
                selection = int(selection)
                if selection == 0:
                    continue

                if selection < 1 or selection > len(history):
                    print_error("Invalid selection.")
                    continue

                # Load the selected scan result
                scan_result = load_scan_result(history[selection-1].get("filename"))

                if not scan_result:
                    print_error("Failed to load scan result.")
                    continue

                # Display the scan result based on type
                scan_type = history[selection-1].get("scan_type")

                if scan_type == "full_scan":
                    display_scan_summary(scan_result.get("data", scan_result))
                elif scan_type == "report":
                    display_report(scan_result.get("data", scan_result))
                else:
                    # Generic display for other types
                    print_info(f"Scan Type: {scan_type}")
                    print_info(f"Workspace: {scan_result.get('workspace')}")
                    print_info(f"Timestamp: {scan_result.get('timestamp')}")

                    # Display a summary of the data
                    data = scan_result.get("data", scan_result)
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if key not in ["workspace", "timestamp", "scan_type"]:
                                if isinstance(value, list):
                                    print_info(f"{key}: {len(value)} items")
                                elif isinstance(value, dict):
                                    print_info(f"{key}: {len(value)} items")
                                else:
                                    print_info(f"{key}: {value}")
            except ValueError:
                print_error("Invalid selection. Please enter a number.")
        elif choice == "3":
            # Back to main menu
            break

def config_menu(config):
    """
    Display the configuration menu

    Args:
        config (dict): Application configuration
    """
    print_section_header("Configuration")

    while True:
        choice = create_menu(
            "Configuration Options",
            [
                ("1", "Discord Settings"),
                ("2", "Export Settings"),
                ("3", "Back to Main Menu")
            ]
        )

        if choice == "1":
            # Discord settings
            webhook_url = get_webhook_url()

            print_info(f"Current Discord webhook URL: {webhook_url or 'Not configured'}")

            new_url = ask_for_input("Enter new Discord webhook URL (leave empty to keep current): ", default="")

            if new_url:
                if set_webhook_url(new_url):
                    print_success("Discord webhook URL updated successfully.")
                else:
                    print_error("Failed to update Discord webhook URL.")
        elif choice == "2":
            # Export settings
            config = load_config()
            export_dir = config.get("export_dir")

            print_info(f"Current export directory: {export_dir}")

            new_dir = ask_for_input("Enter new export directory (leave empty to keep current): ", default="")

            if new_dir:
                config["export_dir"] = new_dir
                if save_config(config):
                    print_success("Export directory updated successfully.")
                else:
                    print_error("Failed to update export directory.")
        elif choice == "3":
            # Back to main menu
            break

def validate_menu(config):
    """
    Display the validation menu

    Args:
        config (dict): Application configuration
    """
    print_section_header("Validate Credentials")

    # Ask for credentials
    workspace = ask_for_input("Enter workspace (e.g., dbc-xxxx.cloud.databricks.com): ")
    apikey = ask_for_input("Enter API key: ", password=True)

    # Ask if user wants to save these credentials
    save_creds = confirm("Save these credentials if valid?", default=False)

    # Ask if user wants to send notification
    notify = confirm("Send notification to Discord if valid?", default=False)

    # Validate credentials
    result = validate_and_notify(
        workspace,
        apikey,
        "discord" if notify else None
    )

    # If credentials are valid and user wants to save them
    if result.get("status") == "valid" and save_creds:
        organization = ask_for_input("Enter organization name (optional): ", default="")

        if not organization:
            organization = None

        save_credentials(workspace, apikey, organization)
