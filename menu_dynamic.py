"""
Dynamic menu system for BricksXploit
"""

import sys
import os
import time
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from datetime import datetime

# Adicionar o diretório raiz ao path para permitir importações absolutas
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.auth import validate_credentials, display_user_info, save_credentials, get_current_credentials
from core.scan import run_full_scan, run_targeted_scan, run_sql_query, display_scan_summary, validate_workspace_access
from core.report import generate_and_send_report, display_report, generate_markdown_report, validate_and_notify
from core.profiles import list_profiles, switch_profile, add_new_profile, remove_profile
from utils.storage import load_config, save_config, get_current_profile, list_scan_history, load_scan_result
from utils.discord import set_webhook_url, get_webhook_url
from utils.ui_dynamic import DynamicUI

# Inicializar a interface dinâmica
ui = DynamicUI(title="BricksXploit", version="1.0.0")
console = Console()

def show_menu(config):
    """
    Display the main menu and handle user choices using the dynamic UI

    Args:
        config (dict): Application configuration
    """
    # Get current profile info for display
    org, profile_name, profile_data = get_current_profile()
    if profile_name:
        ui.set_active_profile(profile_name, org)

    # Define main menu items
    menu_items = [
        "Profile Management",
        "Scan Workspace",
        "Run SQL Query",
        "Generate Reports",
        "View Results",
        "Configuration",
        "Validate Credentials",
        "Exit"
    ]

    ui.set_menu("Main Menu", menu_items)
    ui.set_content(Text("Welcome to BricksXploit! Select an option from the menu."))

    # Main menu loop
    while True:
        # Mostrar a interface e mantê-la visível
        with ui.display() as live:
            ui.update()
            time.sleep(1.0)  # Tempo maior para garantir que a interface seja visível

        # Obter a escolha do usuário fora do contexto Live
        choice = ui.prompt("Select an option", choices=["1", "2", "3", "4", "5", "6", "7", "8"], default="1")

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
            ui.add_notification("Exiting BricksXploit. Goodbye!", "SUCCESS")
            break

def profile_menu(config):
    """
    Display the profile management menu using the dynamic UI

    Args:
        config (dict): Application configuration
    """
    # Define profile menu items
    menu_items = [
        "List Profiles",
        "Switch Profile",
        "Add New Profile",
        "Remove Profile",
        "View Current Profile",
        "Back to Main Menu"
    ]

    ui.set_menu("Profile Management", menu_items)
    ui.set_content(Text("Profile Management: Manage your Databricks workspace profiles."))

    # Profile menu loop
    while True:
        # Mostrar a interface e mantê-la visível
        with ui.display() as live:
            ui.update()
            time.sleep(1.0)  # Tempo maior para garantir que a interface seja visível

        # Obter a escolha do usuário fora do contexto Live
        choice = ui.prompt("Select an option", choices=["1", "2", "3", "4", "5", "6"], default="1")

        if choice == "1":
            # List all profiles
            display_profiles()
        elif choice == "2":
            # Switch to a different profile
            switch_profile_ui()
        elif choice == "3":
            # Add a new profile
            add_profile_ui()
        elif choice == "4":
            # Remove a profile
            remove_profile_ui()
        elif choice == "5":
            # View current profile details
            view_current_profile()
        elif choice == "6":
            # Back to main menu
            break

def display_profiles():
    """
    Display all profiles in a table
    """
    # Create a table to display profiles
    table = ui.create_table(title="Available Profiles", box=box.SIMPLE)
    table.add_column("Profile", style="cyan")
    table.add_column("Workspace", style="green")
    table.add_column("Organization", style="yellow")
    table.add_column("Created", style="magenta")
    table.add_column("Status", style="blue")

    # Get profiles data
    profiles_data = list_profiles(return_data=True)

    if not profiles_data:
        ui.set_content(Text("No profiles found.", style="yellow"))
        ui.add_notification("No profiles found.", "WARNING")
        return

    # Add rows to the table
    for org_name, org_profiles in profiles_data.items():
        for profile_name, profile_data in org_profiles.items():
            # Use a friendly name for the profile instead of the workspace URL
            friendly_name = profile_name
            workspace = profile_data.get('workspace', 'Unknown')
            created = profile_data.get('created_at', 'Unknown')
            status = profile_data.get('status', '')

            table.add_row(
                friendly_name,
                workspace,
                org_name if org_name else "Default",
                created,
                status
            )

    # Update the UI with the table
    ui.set_content(table)
    ui.add_notification("Profiles listed successfully.", "INFO")

def switch_profile_ui():
    """
    Switch to a different profile
    """
    # Get profiles data
    profiles_data = list_profiles(return_data=True)

    if not profiles_data:
        ui.set_content(Text("No profiles found.", style="yellow"))
        ui.add_notification("No profiles found.", "WARNING")
        return

    # Create a list of profile choices
    profile_choices = []
    for org_name, org_profiles in profiles_data.items():
        for profile_name in org_profiles.keys():
            display_name = f"{profile_name} ({org_name})" if org_name else profile_name
            profile_choices.append((display_name, (org_name, profile_name)))

    # Display the choices
    table = ui.create_table(title="Available Profiles", box=box.SIMPLE)
    table.add_column("#", style="cyan")
    table.add_column("Profile", style="green")

    for i, (display_name, _) in enumerate(profile_choices, 1):
        table.add_row(str(i), display_name)

    ui.set_content(table)

    with ui.display() as live:
        ui.update()
        time.sleep(0.5)

    # Get user choice
    choice = ui.prompt("Select a profile (or 0 to cancel)",
                      choices=["0"] + [str(i) for i in range(1, len(profile_choices) + 1)],
                      default="1")

    if choice == "0":
        ui.add_notification("Profile switch cancelled.", "INFO")
        return

    # Switch to the selected profile
    selected_index = int(choice) - 1
    org_name, profile_name = profile_choices[selected_index][1]

    success = switch_profile(org_name, profile_name)

    if success:
        ui.set_active_profile(profile_name, org_name)
        ui.add_notification(f"Switched to profile: {profile_name}", "SUCCESS")
    else:
        ui.add_notification("Failed to switch profile.", "ERROR")

def add_profile_ui():
    """
    Add a new profile
    """
    # Get profile information
    with ui.display() as live:
        ui.update()
        time.sleep(0.5)

    workspace = ui.prompt("Enter workspace (e.g., dbc-xxxx.cloud.databricks.com)")

    with ui.display() as live:
        ui.update()
        time.sleep(0.5)

    apikey = ui.prompt("Enter API key", password=True)

    with ui.display() as live:
        ui.update()
        time.sleep(0.5)

    # Ask for a friendly profile name (different from workspace URL)
    profile_name = ui.prompt("Enter profile name (leave empty to use workspace URL)", default="")

    with ui.display() as live:
        ui.update()
        time.sleep(0.5)

    organization = ui.prompt("Enter organization name (optional)", default="")

    # Validate credentials
    ui.add_notification(f"Validating access to workspace: {workspace}", "INFO")

    with ui.display() as live:
        ui.set_content(Text(f"Validating credentials for: {workspace}...", style="cyan"))
        ui.update()

        # Validate the credentials
        valid, user_info = validate_credentials(workspace, apikey)

        if valid:
            ui.add_notification("Credentials validated successfully!", "SUCCESS")
            ui.add_notification(f"Valid access to workspace: {workspace}", "SUCCESS")

            if user_info:
                user_display = f"{user_info.get('displayName')} ({user_info.get('userName')})"
                ui.add_notification(f"Logged in as: {user_display}", "INFO")
        else:
            ui.add_notification("Invalid credentials or workspace not accessible.", "ERROR")
            ui.set_content(Text("Failed to validate credentials. Please try again.", style="red"))
            return

    # Save the profile if valid
    save_confirm = ui.confirm("Save these credentials?", default=True)

    if save_confirm:
        # Use the provided profile name or default to workspace
        final_profile_name = profile_name if profile_name else workspace

        # Save the profile
        success = add_new_profile(
            workspace,
            apikey,
            organization if organization else None,
            profile_name=final_profile_name
        )

        if success:
            ui.add_notification(f"Credentials saved for {final_profile_name}", "SUCCESS")
            ui.set_active_profile(final_profile_name, organization if organization else None)
        else:
            ui.add_notification("Failed to save credentials.", "ERROR")
    else:
        ui.add_notification("Credentials not saved.", "INFO")

def remove_profile_ui():
    """
    Remove a profile
    """
    # Get profiles data
    profiles_data = list_profiles(return_data=True)

    if not profiles_data:
        ui.set_content(Text("No profiles found.", style="yellow"))
        ui.add_notification("No profiles found.", "WARNING")
        return

    # Create a list of profile choices
    profile_choices = []
    for org_name, org_profiles in profiles_data.items():
        for profile_name in org_profiles.keys():
            display_name = f"{profile_name} ({org_name})" if org_name else profile_name
            profile_choices.append((display_name, (org_name, profile_name)))

    # Display the choices
    table = ui.create_table(title="Available Profiles", box=box.SIMPLE)
    table.add_column("#", style="cyan")
    table.add_column("Profile", style="green")

    for i, (display_name, _) in enumerate(profile_choices, 1):
        table.add_row(str(i), display_name)

    ui.set_content(table)

    with ui.display() as live:
        ui.update()
        time.sleep(0.5)

    # Get user choice
    choice = ui.prompt("Select a profile to remove (or 0 to cancel)",
                      choices=["0"] + [str(i) for i in range(1, len(profile_choices) + 1)],
                      default="0")

    if choice == "0":
        ui.add_notification("Profile removal cancelled.", "INFO")
        return

    # Confirm removal
    selected_index = int(choice) - 1
    org_name, profile_name = profile_choices[selected_index][1]
    display_name = profile_choices[selected_index][0]

    confirm = ui.confirm(f"Are you sure you want to remove profile: {display_name}?", default=False)

    if confirm:
        success = remove_profile(org_name, profile_name)

        if success:
            ui.add_notification(f"Profile removed: {display_name}", "SUCCESS")

            # Update active profile if it was removed
            current_org, current_profile, _ = get_current_profile()
            if current_profile == profile_name and current_org == org_name:
                ui.set_active_profile(None)
        else:
            ui.add_notification("Failed to remove profile.", "ERROR")
    else:
        ui.add_notification("Profile removal cancelled.", "INFO")

def view_current_profile():
    """
    View details of the current profile
    """
    # Get current profile info
    org, profile_name, profile_data = get_current_profile()

    if not profile_data:
        ui.set_content(Text("No active profile selected.", style="yellow"))
        ui.add_notification("No active profile selected.", "WARNING")
        return

    # Create a table to display profile details
    table = ui.create_table(title=f"Profile: {profile_name}", box=box.SIMPLE)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    # Add basic profile info
    table.add_row("Profile Name", profile_name)
    table.add_row("Organization", org if org else "Default")
    table.add_row("Workspace", profile_data.get('workspace', 'Unknown'))
    table.add_row("Created", profile_data.get('created_at', 'Unknown'))

    # Add metadata if available
    metadata = profile_data.get("metadata", {})
    if metadata:
        for key, value in metadata.items():
            if key == "groups" or key == "roles":
                if isinstance(value, list) and value:
                    display_value = ", ".join(value[:5])
                    if len(value) > 5:
                        display_value += f" and {len(value) - 5} more"
                    table.add_row(key.title(), display_value)
            else:
                table.add_row(key.title(), str(value))

    # Update the UI with the table
    ui.set_content(table)
    ui.add_notification(f"Viewing profile: {profile_name}", "INFO")

def validate_menu(config):
    """
    Validate credentials for a Databricks workspace

    Args:
        config (dict): Application configuration
    """
    ui.set_menu("Validate Credentials", ["Back to Main Menu"])
    ui.set_content(Text("Validate Credentials: Test access to a Databricks workspace."))

    with ui.display() as live:
        ui.update()
        time.sleep(0.5)

    # Get workspace and API key
    workspace = ui.prompt("Enter workspace (e.g., dbc-xxxx.cloud.databricks.com)")

    with ui.display() as live:
        ui.update()
        time.sleep(0.5)

    apikey = ui.prompt("Enter API key", password=True)

    # Ask if user wants to save credentials if valid
    save_if_valid = ui.confirm("Save these credentials if valid?", default=False)

    # Ask if user wants to send notification to Discord
    notify = ui.confirm("Send notification to Discord if valid?", default=False)

    # Validate credentials
    ui.add_notification(f"Validating access to workspace: {workspace}", "INFO")

    with ui.display() as live:
        ui.set_content(Text(f"Validating credentials for: {workspace}...", style="cyan"))
        ui.update()

        # Validate the credentials
        valid, user_info = validate_credentials(workspace, apikey)

        if valid:
            ui.add_notification("Credentials validated successfully!", "SUCCESS")
            ui.add_notification(f"Valid access to workspace: {workspace}", "SUCCESS")

            if user_info:
                user_display = f"{user_info.get('displayName')} ({user_info.get('userName')})"
                ui.add_notification(f"Logged in as: {user_display}", "INFO")

                # Display user info
                ui.set_content(Text(f"Successfully validated credentials for: {workspace}\nLogged in as: {user_display}", style="green"))
        else:
            ui.add_notification("Invalid credentials or workspace not accessible.", "ERROR")
            ui.set_content(Text("Failed to validate credentials. Please try again.", style="red"))
            return

    # Save credentials if requested and valid
    if save_if_valid and valid:
        # Ask for organization name
        with ui.display() as live:
            ui.update()
            time.sleep(0.5)

        organization = ui.prompt("Enter organization name (optional)", default="")

        # Ask for profile name
        with ui.display() as live:
            ui.update()
            time.sleep(0.5)

        profile_name = ui.prompt("Enter profile name (leave empty to use workspace URL)", default="")

        # Use the provided profile name or default to workspace
        final_profile_name = profile_name if profile_name else workspace

        # Save the profile
        ui.add_notification(f"Validating credentials for: {workspace}", "INFO")

        success = add_new_profile(
            workspace,
            apikey,
            organization if organization else None,
            profile_name=final_profile_name
        )

        if success:
            ui.add_notification(f"Credentials saved for {final_profile_name}", "SUCCESS")
            ui.set_active_profile(final_profile_name, organization if organization else None)
        else:
            ui.add_notification("Failed to save credentials.", "ERROR")

    # Send notification to Discord if requested and valid
    if notify and valid and user_info:
        webhook_url = get_webhook_url()

        if webhook_url:
            success = validate_and_notify(
                workspace,
                apikey,
                user_info,
                "discord"
            )

            if success:
                ui.add_notification("Notification sent to Discord successfully.", "SUCCESS")
            else:
                ui.add_notification("Failed to send notification to Discord.", "ERROR")
        else:
            ui.add_notification("Discord webhook URL not configured.", "WARNING")
            ui.add_notification("Use Configuration > Discord Settings to set up webhook URL.", "INFO")

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(2)

def config_menu(config):
    """
    Display the configuration menu

    Args:
        config (dict): Application configuration
    """
    # Define configuration menu items
    menu_items = [
        "Discord Settings",
        "Display Settings",
        "Scan Settings",
        "Back to Main Menu"
    ]

    ui.set_menu("Configuration", menu_items)
    ui.set_content(Text("Configuration: Manage application settings."))

    # Configuration menu loop
    while True:
        # Mostrar a interface e mantê-la visível
        with ui.display() as live:
            ui.update()
            time.sleep(1.0)  # Tempo maior para garantir que a interface seja visível

        # Obter a escolha do usuário fora do contexto Live
        choice = ui.prompt("Select an option", choices=["1", "2", "3", "4"], default="1")

        if choice == "1":
            # Discord settings
            discord_settings(config)
        elif choice == "2":
            # Display settings
            display_settings(config)
        elif choice == "3":
            # Scan settings
            scan_settings(config)
        elif choice == "4":
            # Back to main menu
            break

def discord_settings(config):
    """
    Configure Discord webhook settings

    Args:
        config (dict): Application configuration
    """
    ui.set_content(Text("Discord Settings: Configure Discord webhook for notifications."))

    # Get current webhook URL
    current_webhook = get_webhook_url()

    if current_webhook:
        ui.add_notification(f"Current Discord webhook URL: {current_webhook[:20]}...", "INFO")
    else:
        ui.add_notification("No Discord webhook URL configured.", "INFO")

    # Ask if user wants to update webhook URL
    update = ui.confirm("Update Discord webhook URL?", default=False)

    if update:
        with ui.display() as live:
            ui.update()
            time.sleep(0.5)

        webhook_url = ui.prompt("Enter Discord webhook URL", default=current_webhook if current_webhook else "")

        if webhook_url:
            success = set_webhook_url(webhook_url)

            if success:
                ui.add_notification("Discord webhook URL updated successfully.", "SUCCESS")
            else:
                ui.add_notification("Failed to update Discord webhook URL.", "ERROR")
        else:
            ui.add_notification("Discord webhook URL not updated.", "INFO")

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(1)

def display_settings(config):
    """
    Configure display settings

    Args:
        config (dict): Application configuration
    """
    ui.set_content(Text("Display Settings: Configure application display settings."))

    # Get current display settings
    current_settings = config.get("display", {})

    # Create a table to display current settings
    table = ui.create_table(title="Current Display Settings", box=box.SIMPLE)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    for key, value in current_settings.items():
        table.add_row(key, str(value))

    ui.set_content(table)

    # Ask if user wants to update display settings
    update = ui.confirm("Update display settings?", default=False)

    if update:
        # Get new settings
        with ui.display() as live:
            ui.update()
            time.sleep(0.5)

        show_banner = ui.confirm("Show banner on startup?",
                               default=current_settings.get("show_banner", True))

        with ui.display() as live:
            ui.update()
            time.sleep(0.5)

        compact_tables = ui.confirm("Use compact tables?",
                                  default=current_settings.get("compact_tables", False))

        # Update settings
        config["display"] = {
            "show_banner": show_banner,
            "compact_tables": compact_tables
        }

        # Save config
        save_config(config)

        ui.add_notification("Display settings updated successfully.", "SUCCESS")

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(1)

def scan_settings(config):
    """
    Configure scan settings

    Args:
        config (dict): Application configuration
    """
    ui.set_content(Text("Scan Settings: Configure workspace scanning settings."))

    # Get current scan settings
    current_settings = config.get("scan", {})

    # Create a table to display current settings
    table = ui.create_table(title="Current Scan Settings", box=box.SIMPLE)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    for key, value in current_settings.items():
        table.add_row(key, str(value))

    ui.set_content(table)

    # Ask if user wants to update scan settings
    update = ui.confirm("Update scan settings?", default=False)

    if update:
        # Get new settings
        with ui.display() as live:
            ui.update()
            time.sleep(0.5)

        scan_timeout = ui.prompt("Scan timeout (seconds)",
                               default=str(current_settings.get("timeout", 60)))

        with ui.display() as live:
            ui.update()
            time.sleep(0.5)

        max_results = ui.prompt("Maximum results per API call",
                              default=str(current_settings.get("max_results", 100)))

        # Update settings
        try:
            config["scan"] = {
                "timeout": int(scan_timeout),
                "max_results": int(max_results)
            }

            # Save config
            save_config(config)

            ui.add_notification("Scan settings updated successfully.", "SUCCESS")
        except ValueError:
            ui.add_notification("Invalid settings. Please enter numeric values.", "ERROR")

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(1)

def scan_menu(config):
    """
    Display the scan menu

    Args:
        config (dict): Application configuration
    """
    # Define scan menu items
    menu_items = [
        "Run Full Security Scan",
        "Scan Users and Groups",
        "Scan Clusters",
        "Scan Secret Scopes",
        "Scan SQL Warehouses",
        "Scan Unity Catalog Resources",
        "Back to Main Menu"
    ]

    ui.set_menu("Scan Workspace", menu_items)
    ui.set_content(Text("Scan Workspace: Scan Databricks workspace for security information."))

    # Scan menu loop
    while True:
        # Mostrar a interface e mantê-la visível
        with ui.display() as live:
            ui.update()
            time.sleep(1.0)  # Tempo maior para garantir que a interface seja visível

        # Obter a escolha do usuário fora do contexto Live
        choice = ui.prompt("Select an option", choices=["1", "2", "3", "4", "5", "6", "7"], default="1")

        # Get current credentials
        workspace, apikey, profile_data = get_current_credentials()

        if not workspace or not apikey:
            ui.add_notification("No active profile selected. Please select a profile first.", "ERROR")
            ui.set_content(Text("No active profile selected. Please select a profile first.", style="red"))
            time.sleep(2)
            break

        if choice == "1":
            # Run full security scan
            run_full_scan_ui(workspace, profile_data)
        elif choice == "2":
            # Scan users and groups
            run_targeted_scan_ui(workspace, profile_data, "users")
        elif choice == "3":
            # Scan clusters
            run_targeted_scan_ui(workspace, profile_data, "clusters")
        elif choice == "4":
            # Scan secret scopes
            run_targeted_scan_ui(workspace, profile_data, "secrets")
        elif choice == "5":
            # Scan SQL warehouses
            run_targeted_scan_ui(workspace, profile_data, "warehouses")
        elif choice == "6":
            # Scan Unity Catalog resources
            run_targeted_scan_ui(workspace, profile_data, "catalogs")
        elif choice == "7":
            # Back to main menu
            break

def run_full_scan_ui(workspace, profile_data):
    """
    Run a full security scan with UI feedback

    Args:
        workspace (str): Databricks workspace URL
        profile_data (dict): Profile data
    """
    ui.set_content(Text(f"Running full security scan on {workspace}...", style="cyan"))
    ui.add_notification(f"Starting full security scan on {workspace}", "INFO")

    # Create a spinner
    with ui.create_spinner("Running full security scan...") as progress:
        task = progress.add_task("Scanning...", total=None)

        # Run the scan
        with ui.display() as live:
            ui.update()

            # Run the scan
            scan_results = run_full_scan(workspace, profile_data)

    if scan_results:
        ui.add_notification("Full security scan completed successfully.", "SUCCESS")

        # Display scan summary
        summary_text = display_scan_summary(scan_results, return_text=True)

        # Create a table to display scan results
        table = ui.create_table(title=f"Scan Results: {workspace}", box=box.SIMPLE)
        table.add_column("Category", style="cyan")
        table.add_column("Count", style="green")

        # Add rows from summary
        for category, count in scan_results.get("summary", {}).items():
            table.add_row(category, str(count))

        ui.set_content(table)

        # Ask if user wants to generate a report
        generate_report = ui.confirm("Would you like to generate a report from these results?", default=False)

        if generate_report:
            with ui.display() as live:
                ui.update()
                time.sleep(0.5)

            output = ui.prompt("Enter output file name (leave empty to skip)", default="")
            notify = ui.confirm("Send notification to Discord?", default=False)

            if output or notify:
                ui.add_notification("Generating report...", "INFO")

                with ui.display() as live:
                    ui.set_content(Text("Generating report...", style="cyan"))
                    ui.update()

                    # Generate the report
                    report_data = generate_and_send_report(
                        workspace,
                        profile_data.get("apikey"),
                        output if output else None,
                        "discord" if notify else None,
                        scan_results
                    )

                if report_data:
                    ui.add_notification("Report generated successfully.", "SUCCESS")

                    if notify:
                        ui.add_notification("Report sent to Discord.", "SUCCESS")

                    if output:
                        ui.add_notification(f"Report saved to {output}", "SUCCESS")
                else:
                    ui.add_notification("Failed to generate report.", "ERROR")
    else:
        ui.add_notification("Failed to run security scan.", "ERROR")
        ui.set_content(Text("Failed to run security scan. Please try again.", style="red"))

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(2)

def run_targeted_scan_ui(workspace, profile_data, scan_type):
    """
    Run a targeted scan with UI feedback

    Args:
        workspace (str): Databricks workspace URL
        profile_data (dict): Profile data
        scan_type (str): Type of scan to run
    """
    scan_type_display = {
        "users": "Users and Groups",
        "clusters": "Clusters",
        "secrets": "Secret Scopes",
        "warehouses": "SQL Warehouses",
        "catalogs": "Unity Catalog Resources"
    }.get(scan_type, scan_type.title())

    ui.set_content(Text(f"Running {scan_type_display} scan on {workspace}...", style="cyan"))
    ui.add_notification(f"Starting {scan_type_display} scan on {workspace}", "INFO")

    # Create a spinner
    with ui.create_spinner(f"Running {scan_type_display} scan...") as progress:
        task = progress.add_task("Scanning...", total=None)

        # Run the scan
        with ui.display() as live:
            ui.update()

            # Run the scan
            scan_results = run_targeted_scan(workspace, profile_data, scan_type)

    if scan_results:
        ui.add_notification(f"{scan_type_display} scan completed successfully.", "SUCCESS")

        # Create a table to display scan results
        table = ui.create_table(title=f"{scan_type_display} Scan Results: {workspace}", box=box.SIMPLE)

        # Add columns based on scan type
        if scan_type == "users":
            table.add_column("Users", style="cyan")
            table.add_column("Groups", style="green")

            # Add summary data
            table.add_row(
                str(len(scan_results.get("users", []))),
                str(len(scan_results.get("groups", [])))
            )
        elif scan_type == "clusters":
            table.add_column("Clusters", style="cyan")
            table.add_column("Running", style="green")

            # Count running clusters
            running = sum(1 for c in scan_results.get("clusters", []) if c.get("state") == "RUNNING")

            # Add summary data
            table.add_row(
                str(len(scan_results.get("clusters", []))),
                str(running)
            )
        elif scan_type == "secrets":
            table.add_column("Secret Scopes", style="cyan")
            table.add_column("Secrets", style="green")

            # Count secrets
            secrets_count = sum(len(scope.get("secrets", [])) for scope in scan_results.get("scopes", []))

            # Add summary data
            table.add_row(
                str(len(scan_results.get("scopes", []))),
                str(secrets_count)
            )
        elif scan_type == "warehouses":
            table.add_column("SQL Warehouses", style="cyan")
            table.add_column("Running", style="green")

            # Count running warehouses
            running = sum(1 for w in scan_results.get("warehouses", []) if w.get("state") == "RUNNING")

            # Add summary data
            table.add_row(
                str(len(scan_results.get("warehouses", []))),
                str(running)
            )
        elif scan_type == "catalogs":
            table.add_column("Catalogs", style="cyan")
            table.add_column("Schemas", style="green")

            # Count schemas
            schemas_count = sum(len(cat.get("schemas", [])) for cat in scan_results.get("catalogs", []))

            # Add summary data
            table.add_row(
                str(len(scan_results.get("catalogs", []))),
                str(schemas_count)
            )

        ui.set_content(table)

        # Ask if user wants to see details
        show_details = ui.confirm("Would you like to see detailed results?", default=False)

        if show_details:
            # Display detailed results based on scan type
            if scan_type == "users":
                display_users_details(scan_results)
            elif scan_type == "clusters":
                display_clusters_details(scan_results)
            elif scan_type == "secrets":
                display_secrets_details(scan_results)
            elif scan_type == "warehouses":
                display_warehouses_details(scan_results)
            elif scan_type == "catalogs":
                display_catalogs_details(scan_results)
    else:
        ui.add_notification(f"Failed to run {scan_type_display} scan.", "ERROR")
        ui.set_content(Text(f"Failed to run {scan_type_display} scan. Please try again.", style="red"))

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(2)

def display_users_details(scan_results):
    """
    Display detailed users and groups information

    Args:
        scan_results (dict): Scan results
    """
    # Create a table for users
    users_table = ui.create_table(title="Users", box=box.SIMPLE)
    users_table.add_column("Username", style="cyan")
    users_table.add_column("Display Name", style="green")
    users_table.add_column("Groups", style="yellow")

    # Add user rows
    for user in scan_results.get("users", [])[:10]:  # Limit to 10 users for display
        username = user.get("userName", "")
        display_name = user.get("displayName", "")
        groups = ", ".join(user.get("groups", [])[:3])
        if len(user.get("groups", [])) > 3:
            groups += f" and {len(user.get('groups', [])) - 3} more"

        users_table.add_row(username, display_name, groups)

    if len(scan_results.get("users", [])) > 10:
        users_table.add_row("...", f"and {len(scan_results.get('users', [])) - 10} more users", "")

    ui.set_content(users_table)

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(2)

    # Create a table for groups
    groups_table = ui.create_table(title="Groups", box=box.SIMPLE)
    groups_table.add_column("Group Name", style="cyan")
    groups_table.add_column("Members", style="green")

    # Add group rows
    for group in scan_results.get("groups", [])[:10]:  # Limit to 10 groups for display
        group_name = group.get("displayName", "")
        members_count = len(group.get("members", []))

        groups_table.add_row(group_name, str(members_count))

    if len(scan_results.get("groups", [])) > 10:
        groups_table.add_row("...", f"and {len(scan_results.get('groups', [])) - 10} more groups")

    ui.set_content(groups_table)

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(2)

def display_clusters_details(scan_results):
    """
    Display detailed clusters information

    Args:
        scan_results (dict): Scan results
    """
    # Create a table for clusters
    clusters_table = ui.create_table(title="Clusters", box=box.SIMPLE)
    clusters_table.add_column("Cluster Name", style="cyan")
    clusters_table.add_column("ID", style="green")
    clusters_table.add_column("State", style="yellow")
    clusters_table.add_column("Creator", style="magenta")

    # Add cluster rows
    for cluster in scan_results.get("clusters", [])[:10]:  # Limit to 10 clusters for display
        cluster_name = cluster.get("cluster_name", "")
        cluster_id = cluster.get("cluster_id", "")
        state = cluster.get("state", "")
        creator = cluster.get("creator_user_name", "")

        clusters_table.add_row(cluster_name, cluster_id, state, creator)

    if len(scan_results.get("clusters", [])) > 10:
        clusters_table.add_row("...", f"and {len(scan_results.get('clusters', [])) - 10} more clusters", "", "")

    ui.set_content(clusters_table)

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(2)

def display_secrets_details(scan_results):
    """
    Display detailed secrets information

    Args:
        scan_results (dict): Scan results
    """
    # Create a table for secret scopes
    scopes_table = ui.create_table(title="Secret Scopes", box=box.SIMPLE)
    scopes_table.add_column("Scope Name", style="cyan")
    scopes_table.add_column("Backend Type", style="green")
    scopes_table.add_column("Secrets", style="yellow")

    # Add scope rows
    for scope in scan_results.get("scopes", []):
        scope_name = scope.get("name", "")
        backend_type = scope.get("backend_type", "")
        secrets_count = len(scope.get("secrets", []))

        scopes_table.add_row(scope_name, backend_type, str(secrets_count))

    ui.set_content(scopes_table)

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(2)

def display_warehouses_details(scan_results):
    """
    Display detailed SQL warehouses information

    Args:
        scan_results (dict): Scan results
    """
    # Create a table for warehouses
    warehouses_table = ui.create_table(title="SQL Warehouses", box=box.SIMPLE)
    warehouses_table.add_column("Warehouse Name", style="cyan")
    warehouses_table.add_column("ID", style="green")
    warehouses_table.add_column("State", style="yellow")
    warehouses_table.add_column("Size", style="magenta")

    # Add warehouse rows
    for warehouse in scan_results.get("warehouses", []):
        warehouse_name = warehouse.get("name", "")
        warehouse_id = warehouse.get("id", "")
        state = warehouse.get("state", "")
        size = warehouse.get("warehouse_type", "")

        warehouses_table.add_row(warehouse_name, warehouse_id, state, size)

    ui.set_content(warehouses_table)

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(2)

def display_catalogs_details(scan_results):
    """
    Display detailed Unity Catalog resources information

    Args:
        scan_results (dict): Scan results
    """
    # Create a table for catalogs
    catalogs_table = ui.create_table(title="Unity Catalogs", box=box.SIMPLE)
    catalogs_table.add_column("Catalog Name", style="cyan")
    catalogs_table.add_column("Owner", style="green")
    catalogs_table.add_column("Schemas", style="yellow")

    # Add catalog rows
    for catalog in scan_results.get("catalogs", []):
        catalog_name = catalog.get("name", "")
        owner = catalog.get("owner", "")
        schemas_count = len(catalog.get("schemas", []))

        catalogs_table.add_row(catalog_name, owner, str(schemas_count))

    ui.set_content(catalogs_table)

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(2)

def generate_full_report(workspace, apikey, profile_data):
    """
    Generate a full security report

    Args:
        workspace (str): Databricks workspace URL
        apikey (str): API key
        profile_data (dict): Profile data
    """
    ui.set_content(Text(f"Generating full security report for {workspace}...", style="cyan"))
    ui.add_notification(f"Generating full security report for {workspace}", "INFO")

    # Ask for output file
    with ui.display() as live:
        ui.update()
        time.sleep(0.5)

    output = ui.prompt("Enter output file name (leave empty to skip)", default="")

    # Ask for Discord notification
    with ui.display() as live:
        ui.update()
        time.sleep(0.5)

    notify = ui.confirm("Send notification to Discord?", default=False)

    # Generate the report
    ui.add_notification("Generating report...", "INFO")

    with ui.display() as live:
        ui.set_content(Text("Generating report...", style="cyan"))
        ui.update()

        # Generate the report
        report_data = generate_and_send_report(
            workspace,
            apikey,
            output if output else None,
            "discord" if notify else None
        )

    if report_data:
        ui.add_notification("Report generated successfully.", "SUCCESS")

        if notify:
            ui.add_notification("Report sent to Discord.", "SUCCESS")

        if output:
            ui.add_notification(f"Report saved to {output}", "SUCCESS")

        # Display report summary
        table = ui.create_table(title=f"Report Summary: {workspace}", box=box.SIMPLE)
        table.add_column("Category", style="cyan")
        table.add_column("Count", style="green")

        # Add rows from summary
        for category, count in report_data.get("summary", {}).items():
            table.add_row(category, str(count))

        ui.set_content(table)
    else:
        ui.add_notification("Failed to generate report.", "ERROR")
        ui.set_content(Text("Failed to generate report. Please try again.", style="red"))

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(2)

def generate_markdown_report_ui(workspace, apikey, profile_data):
    """
    Generate a Markdown report

    Args:
        workspace (str): Databricks workspace URL
        apikey (str): API key
        profile_data (dict): Profile data
    """
    ui.set_content(Text(f"Generating Markdown report for {workspace}...", style="cyan"))
    ui.add_notification(f"Generating Markdown report for {workspace}", "INFO")

    # First, get the latest scan results
    history = list_scan_history(limit=5)

    if not history:
        ui.add_notification("No scan history found. Run a scan first.", "WARNING")
        ui.set_content(Text("No scan history found. Run a scan first.", style="yellow"))
        time.sleep(2)
        return

    # Create a table to display scan history
    table = ui.create_table(title="Scan History", box=box.SIMPLE)
    table.add_column("#", style="cyan")
    table.add_column("Scan Type", style="green")
    table.add_column("Workspace", style="yellow")
    table.add_column("Timestamp", style="magenta")

    for i, item in enumerate(history, 1):
        table.add_row(
            str(i),
            item.get("scan_type", ""),
            item.get("workspace", ""),
            item.get("timestamp", "")
        )

    ui.set_content(table)

    with ui.display() as live:
        ui.update()
        time.sleep(0.5)

    # Get user selection
    selection = ui.prompt("Enter selection (or 0 to cancel)",
                        choices=["0"] + [str(i) for i in range(1, len(history) + 1)],
                        default="1")

    if selection == "0":
        ui.add_notification("Report generation cancelled.", "INFO")
        return

    # Load the selected scan result
    selected_index = int(selection) - 1
    scan_result = load_scan_result(history[selected_index].get("filename"))

    if not scan_result:
        ui.add_notification("Failed to load scan result.", "ERROR")
        ui.set_content(Text("Failed to load scan result. Please try again.", style="red"))
        time.sleep(2)
        return

    # Ask for output file
    with ui.display() as live:
        ui.update()
        time.sleep(0.5)

    output = ui.prompt("Enter output file name (leave empty to skip)", default="")

    # Generate the report
    ui.add_notification("Generating Markdown report...", "INFO")

    with ui.display() as live:
        ui.set_content(Text("Generating Markdown report...", style="cyan"))
        ui.update()

        # Generate the report
        markdown = generate_markdown_report(
            scan_result.get("data", scan_result),
            output if output else None
        )

    if markdown:
        ui.add_notification("Markdown report generated successfully.", "SUCCESS")

        if output:
            ui.add_notification(f"Report saved to {output}", "SUCCESS")

        # Display report preview
        ui.set_content(Text(f"Markdown report generated successfully.\nSaved to: {output}", style="green"))
    else:
        ui.add_notification("Failed to generate Markdown report.", "ERROR")
        ui.set_content(Text("Failed to generate Markdown report. Please try again.", style="red"))

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(2)

def view_latest_report():
    """
    View the latest report
    """
    ui.set_content(Text("Loading latest report...", style="cyan"))
    ui.add_notification("Loading latest report...", "INFO")

    # Get scan history
    history = list_scan_history(limit=5)

    if not history:
        ui.add_notification("No scan history found.", "WARNING")
        ui.set_content(Text("No scan history found. Run a scan first.", style="yellow"))
        time.sleep(2)
        return

    # Find the latest report
    report_items = [item for item in history if item.get("scan_type") == "report"]

    if not report_items:
        ui.add_notification("No report found in history. Generate a report first.", "WARNING")
        ui.set_content(Text("No report found in history. Generate a report first.", style="yellow"))
        time.sleep(2)
        return

    # Load the latest report
    report_data = load_scan_result(report_items[0].get("filename"))

    if not report_data:
        ui.add_notification("Failed to load report.", "ERROR")
        ui.set_content(Text("Failed to load report. Please try again.", style="red"))
        time.sleep(2)
        return

    # Display report summary
    table = ui.create_table(title=f"Report: {report_items[0].get('workspace')}", box=box.SIMPLE)
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="green")

    # Add rows from summary
    for category, count in report_data.get("summary", {}).items():
        table.add_row(category, str(count))

    ui.set_content(table)
    ui.add_notification("Report loaded successfully.", "SUCCESS")

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(2)

def send_report_to_discord(workspace, apikey, profile_data):
    """
    Send a report to Discord

    Args:
        workspace (str): Databricks workspace URL
        apikey (str): API key
        profile_data (dict): Profile data
    """
    ui.set_content(Text("Sending report to Discord...", style="cyan"))

    # Check if Discord webhook is configured
    webhook_url = get_webhook_url()

    if not webhook_url:
        ui.add_notification("Discord webhook URL not configured.", "ERROR")
        ui.add_notification("Use Configuration > Discord Settings to set up webhook URL.", "INFO")
        ui.set_content(Text("Discord webhook URL not configured.\nUse Configuration > Discord Settings to set up webhook URL.", style="red"))
        time.sleep(2)
        return

    # Get scan history
    history = list_scan_history(limit=5)

    if not history:
        ui.add_notification("No scan history found. Run a scan first.", "WARNING")
        ui.set_content(Text("No scan history found. Run a scan first.", style="yellow"))
        time.sleep(2)
        return

    # Create a table to display scan history
    table = ui.create_table(title="Scan History", box=box.SIMPLE)
    table.add_column("#", style="cyan")
    table.add_column("Scan Type", style="green")
    table.add_column("Workspace", style="yellow")
    table.add_column("Timestamp", style="magenta")

    for i, item in enumerate(history, 1):
        table.add_row(
            str(i),
            item.get("scan_type", ""),
            item.get("workspace", ""),
            item.get("timestamp", "")
        )

    ui.set_content(table)

    with ui.display() as live:
        ui.update()
        time.sleep(0.5)

    # Get user selection
    selection = ui.prompt("Enter selection (or 0 to cancel)",
                        choices=["0"] + [str(i) for i in range(1, len(history) + 1)],
                        default="1")

    if selection == "0":
        ui.add_notification("Report sending cancelled.", "INFO")
        return

    # Load the selected scan result
    selected_index = int(selection) - 1
    scan_result = load_scan_result(history[selected_index].get("filename"))

    if not scan_result:
        ui.add_notification("Failed to load scan result.", "ERROR")
        ui.set_content(Text("Failed to load scan result. Please try again.", style="red"))
        time.sleep(2)
        return

    # Send the report to Discord
    ui.add_notification("Sending report to Discord...", "INFO")

    with ui.display() as live:
        ui.set_content(Text("Sending report to Discord...", style="cyan"))
        ui.update()

        # Generate and send report
        report_data = generate_and_send_report(
            scan_result.get("workspace", workspace),
            apikey,
            None,
            "discord",
            scan_result.get("data", scan_result)
        )

    if report_data:
        ui.add_notification("Report sent to Discord successfully.", "SUCCESS")
        ui.set_content(Text("Report sent to Discord successfully.", style="green"))
    else:
        ui.add_notification("Failed to send report to Discord.", "ERROR")
        ui.set_content(Text("Failed to send report to Discord. Please try again.", style="red"))

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(2)

def report_menu(config):
    """
    Display the report generation menu

    Args:
        config (dict): Application configuration
    """
    # Define report menu items
    menu_items = [
        "Generate Full Security Report",
        "Generate Markdown Report",
        "View Latest Report",
        "Send Report to Discord",
        "Back to Main Menu"
    ]

    ui.set_menu("Report Generation", menu_items)
    ui.set_content(Text("Report Generation: Generate and view security reports."))

    # Report menu loop
    while True:
        # Mostrar a interface e mantê-la visível
        with ui.display() as live:
            ui.update()
            time.sleep(1.0)  # Tempo maior para garantir que a interface seja visível

        # Obter a escolha do usuário fora do contexto Live
        choice = ui.prompt("Select an option", choices=["1", "2", "3", "4", "5"], default="1")

        # Get current credentials
        workspace, apikey, profile_data = get_current_credentials()

        if not workspace or not apikey:
            ui.add_notification("No active profile selected. Please select a profile first.", "ERROR")
            ui.set_content(Text("No active profile selected. Please select a profile first.", style="red"))
            time.sleep(2)
            break

        if choice == "1":
            # Generate full security report
            generate_full_report(workspace, apikey, profile_data)
        elif choice == "2":
            # Generate Markdown report
            generate_markdown_report_ui(workspace, apikey, profile_data)
        elif choice == "3":
            # View latest report
            view_latest_report()
        elif choice == "4":
            # Send report to Discord
            send_report_to_discord(workspace, apikey, profile_data)
        elif choice == "5":
            # Back to main menu
            break

def results_menu(config):
    """
    Display the results viewing menu

    Args:
        config (dict): Application configuration
    """
    # Define results menu items
    menu_items = [
        "View Scan History",
        "View Specific Scan Result",
        "Back to Main Menu"
    ]

    ui.set_menu("View Results", menu_items)
    ui.set_content(Text("View Results: Browse and view scan results."))

    # Results menu loop
    while True:
        # Mostrar a interface e mantê-la visível
        with ui.display() as live:
            ui.update()
            time.sleep(1.0)  # Tempo maior para garantir que a interface seja visível

        # Obter a escolha do usuário fora do contexto Live
        choice = ui.prompt("Select an option", choices=["1", "2", "3"], default="1")

        if choice == "1":
            # View scan history
            view_scan_history()
        elif choice == "2":
            # View specific scan result
            view_specific_scan()
        elif choice == "3":
            # Back to main menu
            break

def view_scan_history():
    """
    View scan history
    """
    ui.set_content(Text("Loading scan history...", style="cyan"))
    ui.add_notification("Loading scan history...", "INFO")

    # Get scan history
    history = list_scan_history(limit=10)

    if not history:
        ui.add_notification("No scan history found.", "WARNING")
        ui.set_content(Text("No scan history found. Run a scan first.", style="yellow"))
        time.sleep(2)
        return

    # Create a table to display scan history
    table = ui.create_table(title="Scan History", box=box.SIMPLE)
    table.add_column("#", style="cyan")
    table.add_column("Scan Type", style="green")
    table.add_column("Workspace", style="yellow")
    table.add_column("Timestamp", style="magenta")

    for i, item in enumerate(history, 1):
        table.add_row(
            str(i),
            item.get("scan_type", ""),
            item.get("workspace", ""),
            item.get("timestamp", "")
        )

    ui.set_content(table)
    ui.add_notification("Scan history loaded successfully.", "SUCCESS")

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(2)

def view_specific_scan():
    """
    View a specific scan result
    """
    ui.set_content(Text("Loading scan history...", style="cyan"))
    ui.add_notification("Loading scan history...", "INFO")

    # Get scan history
    history = list_scan_history(limit=10)

    if not history:
        ui.add_notification("No scan history found.", "WARNING")
        ui.set_content(Text("No scan history found. Run a scan first.", style="yellow"))
        time.sleep(2)
        return

    # Create a table to display scan history
    table = ui.create_table(title="Scan History", box=box.SIMPLE)
    table.add_column("#", style="cyan")
    table.add_column("Scan Type", style="green")
    table.add_column("Workspace", style="yellow")
    table.add_column("Timestamp", style="magenta")

    for i, item in enumerate(history, 1):
        table.add_row(
            str(i),
            item.get("scan_type", ""),
            item.get("workspace", ""),
            item.get("timestamp", "")
        )

    ui.set_content(table)

    with ui.display() as live:
        ui.update()
        time.sleep(0.5)

    # Get user selection
    selection = ui.prompt("Enter selection (or 0 to cancel)",
                        choices=["0"] + [str(i) for i in range(1, len(history) + 1)],
                        default="1")

    if selection == "0":
        ui.add_notification("View cancelled.", "INFO")
        return

    # Load the selected scan result
    selected_index = int(selection) - 1
    scan_result = load_scan_result(history[selected_index].get("filename"))

    if not scan_result:
        ui.add_notification("Failed to load scan result.", "ERROR")
        ui.set_content(Text("Failed to load scan result. Please try again.", style="red"))
        time.sleep(2)
        return

    # Display scan result based on type
    scan_type = history[selected_index].get("scan_type", "")

    if scan_type == "full_scan":
        display_full_scan_result(scan_result)
    elif scan_type == "users":
        display_users_scan_result(scan_result)
    elif scan_type == "clusters":
        display_clusters_scan_result(scan_result)
    elif scan_type == "secrets":
        display_secrets_scan_result(scan_result)
    elif scan_type == "warehouses":
        display_warehouses_scan_result(scan_result)
    elif scan_type == "catalogs":
        display_catalogs_scan_result(scan_result)
    elif scan_type == "report":
        display_report_result(scan_result)
    else:
        # Generic display for unknown scan types
        ui.add_notification(f"Viewing scan result: {scan_type}", "INFO")

        # Create a table to display summary
        table = ui.create_table(title=f"Scan Result: {history[selected_index].get('workspace')}", box=box.SIMPLE)
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")

        # Add rows from top-level keys
        for key, value in scan_result.items():
            if key != "data" and not isinstance(value, (dict, list)):
                table.add_row(key, str(value))

        ui.set_content(table)

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(2)

def display_full_scan_result(scan_result):
    """
    Display a full scan result

    Args:
        scan_result (dict): Scan result data
    """
    ui.add_notification("Viewing full scan result", "INFO")

    # Create a table to display summary
    table = ui.create_table(title=f"Full Scan Summary: {scan_result.get('workspace')}", box=box.SIMPLE)
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="green")

    # Add rows from summary
    for category, count in scan_result.get("summary", {}).items():
        table.add_row(category, str(count))

    ui.set_content(table)

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(2)

def display_users_scan_result(scan_result):
    """
    Display a users scan result

    Args:
        scan_result (dict): Scan result data
    """
    ui.add_notification("Viewing users scan result", "INFO")

    # Get the actual data
    data = scan_result.get("data", scan_result)

    # Create a table for users
    users_table = ui.create_table(title="Users", box=box.SIMPLE)
    users_table.add_column("Username", style="cyan")
    users_table.add_column("Display Name", style="green")
    users_table.add_column("Groups", style="yellow")

    # Add user rows
    for user in data.get("users", [])[:10]:  # Limit to 10 users for display
        username = user.get("userName", "")
        display_name = user.get("displayName", "")
        groups = ", ".join(user.get("groups", [])[:3])
        if len(user.get("groups", [])) > 3:
            groups += f" and {len(user.get('groups', [])) - 3} more"

        users_table.add_row(username, display_name, groups)

    if len(data.get("users", [])) > 10:
        users_table.add_row("...", f"and {len(data.get('users', [])) - 10} more users", "")

    ui.set_content(users_table)

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(2)

    # Create a table for groups
    groups_table = ui.create_table(title="Groups", box=box.SIMPLE)
    groups_table.add_column("Group Name", style="cyan")
    groups_table.add_column("Members", style="green")

    # Add group rows
    for group in data.get("groups", [])[:10]:  # Limit to 10 groups for display
        group_name = group.get("displayName", "")
        members_count = len(group.get("members", []))

        groups_table.add_row(group_name, str(members_count))

    if len(data.get("groups", [])) > 10:
        groups_table.add_row("...", f"and {len(data.get('groups', [])) - 10} more groups")

    ui.set_content(groups_table)

def display_clusters_scan_result(scan_result):
    """
    Display a clusters scan result

    Args:
        scan_result (dict): Scan result data
    """
    ui.add_notification("Viewing clusters scan result", "INFO")

    # Get the actual data
    data = scan_result.get("data", scan_result)

    # Create a table for clusters
    clusters_table = ui.create_table(title="Clusters", box=box.SIMPLE)
    clusters_table.add_column("Cluster Name", style="cyan")
    clusters_table.add_column("ID", style="green")
    clusters_table.add_column("State", style="yellow")
    clusters_table.add_column("Creator", style="magenta")

    # Add cluster rows
    for cluster in data.get("clusters", [])[:10]:  # Limit to 10 clusters for display
        cluster_name = cluster.get("cluster_name", "")
        cluster_id = cluster.get("cluster_id", "")
        state = cluster.get("state", "")
        creator = cluster.get("creator_user_name", "")

        clusters_table.add_row(cluster_name, cluster_id, state, creator)

    if len(data.get("clusters", [])) > 10:
        clusters_table.add_row("...", f"and {len(data.get('clusters', [])) - 10} more clusters", "", "")

    ui.set_content(clusters_table)

def display_secrets_scan_result(scan_result):
    """
    Display a secrets scan result

    Args:
        scan_result (dict): Scan result data
    """
    ui.add_notification("Viewing secrets scan result", "INFO")

    # Get the actual data
    data = scan_result.get("data", scan_result)

    # Create a table for secret scopes
    scopes_table = ui.create_table(title="Secret Scopes", box=box.SIMPLE)
    scopes_table.add_column("Scope Name", style="cyan")
    scopes_table.add_column("Backend Type", style="green")
    scopes_table.add_column("Secrets", style="yellow")

    # Add scope rows
    for scope in data.get("scopes", []):
        scope_name = scope.get("name", "")
        backend_type = scope.get("backend_type", "")
        secrets_count = len(scope.get("secrets", []))

        scopes_table.add_row(scope_name, backend_type, str(secrets_count))

    ui.set_content(scopes_table)

def display_warehouses_scan_result(scan_result):
    """
    Display a warehouses scan result

    Args:
        scan_result (dict): Scan result data
    """
    ui.add_notification("Viewing warehouses scan result", "INFO")

    # Get the actual data
    data = scan_result.get("data", scan_result)

    # Create a table for warehouses
    warehouses_table = ui.create_table(title="SQL Warehouses", box=box.SIMPLE)
    warehouses_table.add_column("Warehouse Name", style="cyan")
    warehouses_table.add_column("ID", style="green")
    warehouses_table.add_column("State", style="yellow")
    warehouses_table.add_column("Size", style="magenta")

    # Add warehouse rows
    for warehouse in data.get("warehouses", []):
        warehouse_name = warehouse.get("name", "")
        warehouse_id = warehouse.get("id", "")
        state = warehouse.get("state", "")
        size = warehouse.get("warehouse_type", "")

        warehouses_table.add_row(warehouse_name, warehouse_id, state, size)

    ui.set_content(warehouses_table)

def display_catalogs_scan_result(scan_result):
    """
    Display a catalogs scan result

    Args:
        scan_result (dict): Scan result data
    """
    ui.add_notification("Viewing catalogs scan result", "INFO")

    # Get the actual data
    data = scan_result.get("data", scan_result)

    # Create a table for catalogs
    catalogs_table = ui.create_table(title="Unity Catalogs", box=box.SIMPLE)
    catalogs_table.add_column("Catalog Name", style="cyan")
    catalogs_table.add_column("Owner", style="green")
    catalogs_table.add_column("Schemas", style="yellow")

    # Add catalog rows
    for catalog in data.get("catalogs", []):
        catalog_name = catalog.get("name", "")
        owner = catalog.get("owner", "")
        schemas_count = len(catalog.get("schemas", []))

        catalogs_table.add_row(catalog_name, owner, str(schemas_count))

    ui.set_content(catalogs_table)

def display_report_result(scan_result):
    """
    Display a report result

    Args:
        scan_result (dict): Scan result data
    """
    ui.add_notification("Viewing report result", "INFO")

    # Get the actual data
    data = scan_result.get("data", scan_result)

    # Create a table to display summary
    table = ui.create_table(title=f"Report: {scan_result.get('workspace')}", box=box.SIMPLE)
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="green")

    # Add rows from summary
    for category, count in data.get("summary", {}).items():
        table.add_row(category, str(count))

    ui.set_content(table)

def sql_menu(config):
    """
    Display the SQL query menu

    Args:
        config (dict): Application configuration
    """
    ui.set_menu("SQL Query", ["Back to Main Menu"])
    ui.set_content(Text("SQL Query: Execute SQL queries against Databricks SQL warehouses."))

    # Get current credentials
    workspace, apikey, profile_data = get_current_credentials()

    if not workspace or not apikey:
        ui.add_notification("No active profile selected. Please select a profile first.", "ERROR")
        ui.set_content(Text("No active profile selected. Please select a profile first.", style="red"))
        time.sleep(2)
        return

    # Get query from user
    with ui.display() as live:
        ui.update()
        time.sleep(1.0)  # Tempo maior para garantir que a interface seja visível

        ui.add_notification("Enter SQL query to execute (press Enter twice to finish)", "INFO")

    # Collect query lines
    query_lines = []
    line = ui.prompt("SQL Query (line 1)", default="")
    query_lines.append(line)

    line_num = 2
    while line:
        line = ui.prompt(f"SQL Query (line {line_num}, press Enter to finish)", default="")
        if line:
            query_lines.append(line)
        line_num += 1

    query = "\n".join(query_lines)

    if not query.strip():
        ui.add_notification("Empty query. Operation cancelled.", "WARNING")
        return

    # Ask for additional parameters
    with ui.display() as live:
        ui.update()
        time.sleep(1.0)  # Tempo maior para garantir que a interface seja visível

        warehouse_id = ui.prompt("Enter warehouse ID (optional)", default="")

    with ui.display() as live:
        ui.update()
        time.sleep(1.0)  # Tempo maior para garantir que a interface seja visível

        catalog = ui.prompt("Enter catalog name (optional)", default="")

    with ui.display() as live:
        ui.update()
        time.sleep(1.0)  # Tempo maior para garantir que a interface seja visível

        schema = ui.prompt("Enter schema name (optional)", default="")

    # Execute the query
    ui.add_notification("Executing SQL query...", "INFO")

    with ui.display() as live:
        ui.set_content(Text("Executing SQL query...", style="cyan"))
        ui.update()
        time.sleep(1.0)  # Tempo maior para garantir que a interface seja visível

        # Execute the query
        result = run_sql_query(
            workspace,
            profile_data,
            query,
            warehouse_id if warehouse_id else None,
            catalog if catalog else None,
            schema if schema else None,
            return_result=True
        )

    if result and "error" not in result:
        ui.add_notification("SQL query executed successfully.", "SUCCESS")

        # Display the results
        if "results" in result and result["results"]:
            # Create a table for results
            results_table = ui.create_table(title="Query Results", box=box.SIMPLE)

            # Add columns
            columns = result["results"]["schema"]
            for column in columns:
                results_table.add_column(column["name"], style="cyan")

            # Add rows
            for row in result["results"]["data"][:20]:  # Limit to 20 rows for display
                results_table.add_row(*[str(value) for value in row])

            if len(result["results"]["data"]) > 20:
                results_table.add_row(*["..." for _ in columns])
                results_table.add_caption(f"Showing 20 of {len(result['results']['data'])} rows")

            ui.set_content(results_table)
        else:
            ui.set_content(Text("Query executed successfully, but no results returned.", style="yellow"))
    else:
        error_message = result.get("error", "Unknown error") if result else "Failed to execute query"
        ui.add_notification(f"Failed to execute SQL query: {error_message}", "ERROR")
        ui.set_content(Text(f"Failed to execute SQL query: {error_message}", style="red"))

    # Wait for user to continue
    with ui.display() as live:
        ui.update()
        time.sleep(3.0)  # Tempo maior para garantir que o usuário veja os resultados