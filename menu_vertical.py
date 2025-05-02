"""
Vertical bipartite menu system for BricksXploit
"""

import time
import sys
import os
from rich.text import Text

# Configurar o ambiente para importações
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Importações absolutas
from core.auth import validate_credentials
from core.profiles import list_profiles, switch_profile, add_new_profile
from core.report import validate_and_notify, generate_and_send_report
from core.scan import run_full_scan, run_targeted_scan
from core.export import export_scan_results, export_report
from utils.storage import save_config, get_webhook_url, set_webhook_url
from utils.storage import get_current_profile, save_scan_result
from utils.ui_vertical import VerticalUI

# Inicializar a interface vertical
ui = VerticalUI(title="BricksXploit", version="1.0.0")

def show_menu(config):
    """
    Display the main menu

    Args:
        config (dict): Application configuration
    """
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

    # Set active profile if exists
    org, profile_name, _ = get_current_profile()
    if profile_name:
        ui.set_active_profile(profile_name, org)

    # Add welcome notification
    ui.add_notification("Welcome to BricksXploit!", "INFO")
    ui.add_notification("Select an option from the menu", "INFO")

    # Display the UI
    ui.display(Text("Welcome to BricksXploit! Select an option from the menu.", style="cyan"))

    # Main menu loop
    while True:
        # Get user choice
        choice = ui.prompt("Select an option", choices=["1", "2", "3", "4", "5", "6", "7", "8"], default="1")

        if choice == "1":
            # Profile management
            profile_menu(config)
        elif choice == "2":
            # Scan workspace
            scan_menu(config)
        elif choice == "3":
            # Run SQL query
            ui.add_notification("SQL query functionality will be implemented in a future update.", "INFO")
            ui.display(Text("SQL query functionality will be implemented in a future update.", style="yellow"), selected_option="3")
        elif choice == "4":
            # Generate reports
            ui.add_notification("Report generation functionality will be implemented in a future update.", "INFO")
            ui.display(Text("Report generation functionality will be implemented in a future update.", style="yellow"), selected_option="4")
        elif choice == "5":
            # View results
            ui.add_notification("Results viewing functionality will be implemented in a future update.", "INFO")
            ui.display(Text("Results viewing functionality will be implemented in a future update.", style="yellow"), selected_option="5")
        elif choice == "6":
            # Configuration
            config_menu(config)
        elif choice == "7":
            # Validate credentials
            validate_menu(config)
        elif choice == "8":
            # Exit
            ui.add_notification("Exiting BricksXploit. Goodbye!", "INFO")
            ui.display(Text("Exiting BricksXploit. Goodbye!", style="cyan"), selected_option="8")
            time.sleep(1.0)
            sys.exit(0)

def profile_menu(_):
    """
    Display the profile management menu

    Args:
        _ (dict): Application configuration (not used)
    """
    # Define profile menu items
    menu_items = [
        "List Profiles",
        "Switch Profile",
        "Add Profile",
        "Remove Profile",
        "View Current Profile",
        "Back to Main Menu"
    ]

    ui.set_menu("Profile Management", menu_items)
    ui.display(Text("Profile Management: Manage Databricks workspace profiles.", style="cyan"))

    # Profile menu loop
    while True:
        # Get user choice
        choice = ui.prompt("Select an option", choices=["1", "2", "3", "4", "5", "6"], default="1")

        if choice == "1":
            # List profiles
            display_profiles()
        elif choice == "2":
            # Switch profile
            switch_profile_ui()
        elif choice == "3":
            # Add profile
            add_profile_ui()
        elif choice == "4":
            # Remove profile
            remove_profile_ui()
        elif choice == "5":
            # View current profile
            view_current_profile()
        elif choice == "6":
            # Back to main menu
            # Define main menu items again to ensure they're displayed correctly
            main_menu_items = [
                "Profile Management",
                "Scan Workspace",
                "Run SQL Query",
                "Generate Reports",
                "View Results",
                "Configuration",
                "Validate Credentials",
                "Exit"
            ]
            ui.set_menu("Main Menu", main_menu_items)
            # Display the main menu content before breaking out of the loop
            ui.add_notification("Returning to main menu...", "INFO")
            ui.display(Text("Welcome to BricksXploit! Select an option from the menu.", style="cyan"))
            break

def display_profiles():
    """
    Display all profiles in a table
    """
    # Create a table to display profiles
    table = ui.create_table(title="Available Profiles")
    table.add_column("Profile", style="cyan")
    table.add_column("Workspace", style="green")
    table.add_column("Organization", style="yellow")
    table.add_column("Created", style="magenta")
    table.add_column("Status", style="blue")

    # Get profiles data
    ui.add_notification("Loading profiles...", "INFO")
    profiles_data = ui.run_with_spinner("Loading profiles...", list_profiles, return_data=True)

    if not profiles_data:
        ui.add_notification("No profiles found.", "WARNING")
        ui.display(Text("No profiles found.", style="yellow"), selected_option="1")
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
                org_name if org_name != "Default" else "Default",
                created,
                status
            )

    # Update the UI with the table
    ui.display(table, selected_option="1")
    ui.add_notification("Profiles listed successfully.", "SUCCESS")

def switch_profile_ui():
    """
    Switch to a different profile
    """
    # Get profiles data
    ui.add_notification("Loading profiles...", "INFO")
    profiles_data = ui.run_with_spinner("Loading profiles...", list_profiles, return_data=True)

    if not profiles_data:
        ui.add_notification("No profiles found.", "WARNING")
        ui.display(Text("No profiles found.", style="yellow"), selected_option="2")
        return

    # Create a list of profile choices
    profile_choices = []
    for org_name, org_profiles in profiles_data.items():
        for profile_name in org_profiles.keys():
            display_name = f"{profile_name} ({org_name})" if org_name != "Default" else profile_name
            profile_choices.append((display_name, (org_name if org_name != "Default" else None, profile_name)))

    # Display the choices
    table = ui.create_table(title="Available Profiles")
    table.add_column("#", style="cyan")
    table.add_column("Profile", style="green")

    for i, (display_name, _) in enumerate(profile_choices, 1):
        table.add_row(str(i), display_name)

    ui.display(table, selected_option="2")

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
    display_name = profile_choices[selected_index][0]

    ui.add_notification(f"Switching to profile: {display_name}...", "INFO")
    success = ui.run_with_spinner(f"Switching to profile {profile_name}...", switch_profile, org_name, profile_name)

    if success:
        ui.set_active_profile(profile_name, org_name)
        ui.add_notification(f"Switched to profile: {profile_name}", "SUCCESS")
        ui.display(Text(f"Successfully switched to profile: {display_name}", style="green"), selected_option="2")
    else:
        ui.add_notification("Failed to switch profile.", "ERROR")
        ui.display(Text("Failed to switch profile.", style="red"), selected_option="2")

def add_profile_ui():
    """
    Add a new profile
    """
    # Display form instructions
    ui.display(Text("Add Profile: Add a new Databricks workspace profile.\n\nPlease provide the following information:", style="cyan"), selected_option="3")

    # Get profile information
    workspace = ui.prompt("Enter workspace URL (e.g., https://dbc-xxxx.cloud.databricks.com, https://adb-xxxx.azuredatabricks.net, https://xxxx.gcp.databricks.com)")
    apikey = ui.prompt("Enter Databricks Personal Access Token (PAT)", password=True)

    # Ask for a friendly profile name (different from workspace URL)
    profile_name = ui.prompt("Enter profile name (leave empty to use workspace URL)", default="")
    organization = ui.prompt("Enter organization name (optional)", default="")

    # Validate credentials
    ui.add_notification(f"Validating access to workspace: {workspace}", "INFO")
    ui.display(Text(f"Validating credentials for: {workspace}...\nPlease wait...", style="cyan"), selected_option="3")

    # Validate the credentials
    user_info = ui.run_with_spinner(f"Validating credentials for {workspace}...", validate_credentials, workspace, apikey)

    if user_info:
        ui.add_notification("Credentials validated successfully!", "SUCCESS")
        ui.add_notification(f"Valid access to workspace: {workspace}", "SUCCESS")

        user_display = f"{user_info.get('displayName')} ({user_info.get('userName')})"
        ui.add_notification(f"Logged in as: {user_display}", "INFO")
        ui.display(Text(f"Successfully validated credentials for: {workspace}\nLogged in as: {user_display}", style="green"), selected_option="3")
    else:
        ui.add_notification("Invalid credentials or workspace not accessible.", "ERROR")
        ui.display(Text("Failed to validate credentials. Please try again.", style="red"), selected_option="3")
        return

    # Save the profile if valid
    save_confirm = ui.confirm("Save these credentials?", default=True)

    if save_confirm:
        # Use the provided profile name or default to workspace
        final_profile_name = profile_name if profile_name else workspace

        # Save the profile
        ui.add_notification(f"Saving profile: {final_profile_name}...", "INFO")

        try:
            # Pass the user_info to avoid re-validation
            success = ui.run_with_spinner(f"Saving profile {final_profile_name}...",
                                         add_new_profile,
                                         workspace,
                                         apikey,
                                         organization if organization else None,
                                         profile_name=final_profile_name,
                                         user_info=user_info)

            if success:
                ui.add_notification(f"Credentials saved for {final_profile_name}", "SUCCESS")
                ui.set_active_profile(final_profile_name, organization if organization else None)
                ui.display(Text(f"Profile saved successfully: {final_profile_name}", style="green"), selected_option="3")
            else:
                ui.add_notification("Failed to save credentials.", "ERROR")
                ui.display(Text("Failed to save credentials. Please try again.", style="red"), selected_option="3")
        except Exception as e:
            ui.add_notification(f"Error saving profile: {str(e)}", "ERROR")
            ui.display(Text(f"Error saving profile: {str(e)}", style="red"), selected_option="3")
    else:
        ui.add_notification("Credentials not saved.", "INFO")

def remove_profile_ui():
    """
    Remove a profile
    """
    # Get profiles data
    ui.add_notification("Loading profiles...", "INFO")
    profiles_data = ui.run_with_spinner("Loading profiles...", list_profiles, return_data=True)

    if not profiles_data:
        ui.add_notification("No profiles found.", "WARNING")
        ui.display(Text("No profiles found.", style="yellow"), selected_option="4")
        return

    # Create a list of profile choices
    profile_choices = []
    for org_name, org_profiles in profiles_data.items():
        for profile_name in org_profiles.keys():
            display_name = f"{profile_name} ({org_name})" if org_name != "Default" else profile_name
            profile_choices.append((display_name, (org_name if org_name != "Default" else None, profile_name)))

    # Display the choices
    table = ui.create_table(title="Available Profiles")
    table.add_column("#", style="cyan")
    table.add_column("Profile", style="green")

    for i, (display_name, _) in enumerate(profile_choices, 1):
        table.add_row(str(i), display_name)

    ui.display(table, selected_option="4")

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
        ui.add_notification(f"Removing profile: {display_name}...", "INFO")

        # Import the storage function directly to avoid confusion with the profiles module function
        from utils.storage import remove_profile as remove_profile_storage

        success = ui.run_with_spinner(
            f"Removing profile {display_name}...",
            remove_profile_storage,
            profile_name,
            org_name
        )

        if success:
            ui.add_notification(f"Profile removed: {display_name}", "SUCCESS")
            ui.display(Text(f"Profile removed successfully: {display_name}", style="green"), selected_option="4")

            # Update active profile if it was removed
            current_org, current_profile, _ = get_current_profile()
            if current_profile == profile_name and current_org == org_name:
                ui.set_active_profile(None)
        else:
            ui.add_notification("Failed to remove profile.", "ERROR")
            ui.display(Text("Failed to remove profile. Please try again.", style="red"), selected_option="4")
    else:
        ui.add_notification("Profile removal cancelled.", "INFO")

def view_current_profile():
    """
    View details of the current profile
    """
    # Get current profile info
    org, profile_name, profile_data = get_current_profile()

    if not profile_data:
        ui.add_notification("No active profile selected.", "WARNING")
        ui.display(Text("No active profile selected.", style="yellow"), selected_option="5")
        return

    # Create a table to display profile details
    table = ui.create_table(title=f"Profile: {profile_name}")
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
    ui.display(table, selected_option="5")
    ui.add_notification(f"Viewing profile: {profile_name}", "INFO")

def validate_menu(_):
    """
    Validate credentials for a Databricks workspace

    Args:
        _ (dict): Application configuration (not used)
    """
    ui.set_menu("Validate Credentials", ["Back to Main Menu"])
    ui.display(Text("Validate Credentials: Test access to a Databricks workspace.\n\nPlease provide the following information:", style="cyan"), selected_option="7")

    # Add option to return to main menu
    if ui.confirm("Return to main menu?", default=False):
        # Define main menu items again to ensure they're displayed correctly
        main_menu_items = [
            "Profile Management",
            "Scan Workspace",
            "Run SQL Query",
            "Generate Reports",
            "View Results",
            "Configuration",
            "Validate Credentials",
            "Exit"
        ]
        ui.set_menu("Main Menu", main_menu_items)
        # Display the main menu content
        ui.add_notification("Returning to main menu...", "INFO")
        ui.display(Text("Welcome to BricksXploit! Select an option from the menu.", style="cyan"))
        return

    # Get workspace and API key
    workspace = ui.prompt("Enter workspace URL (e.g., https://dbc-xxxx.cloud.databricks.com, https://adb-xxxx.azuredatabricks.net, https://xxxx.gcp.databricks.com)")
    apikey = ui.prompt("Enter Databricks Personal Access Token (PAT)", password=True)

    # Ask if user wants to save credentials if valid
    save_if_valid = ui.confirm("Save these credentials if valid?", default=False)

    # Ask if user wants to send notification to Discord
    notify = ui.confirm("Send notification to Discord if valid?", default=False)

    # Validate credentials
    ui.add_notification(f"Validating access to workspace: {workspace}", "INFO")
    ui.display(Text(f"Validating credentials for: {workspace}...\nPlease wait...", style="cyan"), selected_option="7")

    # Validate the credentials
    user_info = ui.run_with_spinner(f"Validating credentials for {workspace}...", validate_credentials, workspace, apikey)

    if user_info:
        ui.add_notification("Credentials validated successfully!", "SUCCESS")
        ui.add_notification(f"Valid access to workspace: {workspace}", "SUCCESS")

        user_display = f"{user_info.get('displayName')} ({user_info.get('userName')})"
        ui.add_notification(f"Logged in as: {user_display}", "INFO")
        ui.display(Text(f"Successfully validated credentials for: {workspace}\nLogged in as: {user_display}", style="green"), selected_option="7")

        # Save credentials if requested and valid
        if save_if_valid:
            # Ask for organization name
            organization = ui.prompt("Enter organization name (optional)", default="")

            # Ask for profile name
            profile_name = ui.prompt("Enter profile name (leave empty to use workspace URL)", default="")

            # Use the provided profile name or default to workspace
            final_profile_name = profile_name if profile_name else workspace

            # Save the profile
            ui.add_notification(f"Saving credentials for: {workspace}", "INFO")

            try:
                # Pass the user_info to avoid re-validation
                success = ui.run_with_spinner(f"Saving profile {final_profile_name}...",
                                             add_new_profile,
                                             workspace,
                                             apikey,
                                             organization if organization else None,
                                             profile_name=final_profile_name,
                                             user_info=user_info)

                if success:
                    ui.add_notification(f"Credentials saved for {final_profile_name}", "SUCCESS")
                    ui.set_active_profile(final_profile_name, organization if organization else None)
                    ui.display(Text(f"Profile saved successfully: {final_profile_name}", style="green"), selected_option="7")
                else:
                    ui.add_notification("Failed to save credentials.", "ERROR")
                    ui.display(Text("Failed to save credentials. Please try again.", style="red"), selected_option="7")
            except Exception as e:
                ui.add_notification(f"Error saving profile: {str(e)}", "ERROR")
                ui.display(Text(f"Error saving profile: {str(e)}", style="red"), selected_option="7")

        # Send notification to Discord if requested and valid
        if notify and user_info:
            webhook_url = get_webhook_url()

            if webhook_url:
                ui.add_notification("Sending notification to Discord...", "INFO")
                success = ui.run_with_spinner("Sending notification to Discord...",
                                             validate_and_notify,
                                             workspace,
                                             apikey,
                                             "discord")

                if success:
                    ui.add_notification("Notification sent to Discord successfully.", "SUCCESS")
                    ui.display(Text("Notification sent to Discord successfully.", style="green"), selected_option="7")
                else:
                    ui.add_notification("Failed to send notification to Discord.", "ERROR")
                    ui.display(Text("Failed to send notification to Discord.", style="red"), selected_option="7")
            else:
                ui.add_notification("Discord webhook URL not configured.", "WARNING")
                ui.add_notification("Use Configuration > Discord Settings to set up webhook URL.", "INFO")
                ui.display(Text("Discord webhook URL not configured.\nUse Configuration > Discord Settings to set up webhook URL.", style="yellow"), selected_option="7")
    else:
        ui.add_notification("Invalid credentials or workspace not accessible.", "ERROR")
        ui.display(Text("Failed to validate credentials. Please try again.", style="red"), selected_option="7")

def config_menu(_):
    """
    Display the configuration menu

    Args:
        _ (dict): Application configuration (not used)
    """
    # Define configuration menu items
    menu_items = [
        "Discord Settings",
        "Display Settings",
        "Scan Settings",
        "Back to Main Menu"
    ]

    ui.set_menu("Configuration", menu_items)
    ui.display(Text("Configuration: Manage application settings.", style="cyan"), selected_option="6")

    # Configuration menu loop
    while True:
        # Get user choice
        choice = ui.prompt("Select an option", choices=["1", "2", "3", "4"], default="1")

        if choice == "1":
            # Discord settings
            discord_settings(_)
        elif choice == "2":
            # Display settings
            display_settings(_)
        elif choice == "3":
            # Scan settings
            scan_settings(_)
        elif choice == "4":
            # Back to main menu
            # Define main menu items again to ensure they're displayed correctly
            main_menu_items = [
                "Profile Management",
                "Scan Workspace",
                "Run SQL Query",
                "Generate Reports",
                "View Results",
                "Configuration",
                "Validate Credentials",
                "Exit"
            ]
            ui.set_menu("Main Menu", main_menu_items)
            # Display the main menu content before breaking out of the loop
            ui.add_notification("Returning to main menu...", "INFO")
            ui.display(Text("Welcome to BricksXploit! Select an option from the menu.", style="cyan"))
            break

def discord_settings(_):
    """
    Configure Discord webhook settings

    Args:
        _ (dict): Application configuration (not used)
    """
    # Get current webhook URL
    current_webhook = get_webhook_url()

    if current_webhook:
        ui.add_notification(f"Current Discord webhook URL: {current_webhook[:20]}...", "INFO")
        ui.display(Text(f"Current Discord webhook URL: {current_webhook[:20]}...", style="cyan"), selected_option="1")
    else:
        ui.add_notification("No Discord webhook URL configured.", "INFO")
        ui.display(Text("No Discord webhook URL configured.", style="yellow"), selected_option="1")

    # Ask if user wants to update webhook URL
    update = ui.confirm("Update Discord webhook URL?", default=False)

    if update:
        webhook_url = ui.prompt("Enter Discord webhook URL", default=current_webhook if current_webhook else "")

        if webhook_url:
            ui.add_notification("Updating Discord webhook URL...", "INFO")
            success = ui.run_with_spinner("Updating Discord webhook URL...", set_webhook_url, webhook_url)

            if success:
                ui.add_notification("Discord webhook URL updated successfully.", "SUCCESS")
                ui.display(Text("Discord webhook URL updated successfully.", style="green"), selected_option="1")
            else:
                ui.add_notification("Failed to update Discord webhook URL.", "ERROR")
                ui.display(Text("Failed to update Discord webhook URL.", style="red"), selected_option="1")
        else:
            ui.add_notification("Discord webhook URL not updated.", "INFO")

def display_settings(_):
    """
    Configure display settings

    Args:
        _ (dict): Application configuration (not used)
    """
    # Load config
    from utils.storage import load_config
    config = load_config()

    # Get current display settings
    current_settings = config.get("display", {})

    # Create a table to display current settings
    table = ui.create_table(title="Current Display Settings")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    for key, value in current_settings.items():
        table.add_row(key, str(value))

    ui.display(table, selected_option="2")

    # Ask if user wants to update display settings
    update = ui.confirm("Update display settings?", default=False)

    if update:
        # Get new settings
        # Example setting: show_banner
        show_banner = ui.confirm("Show banner on startup?", default=current_settings.get("show_banner", True))

        # Update settings
        config["display"] = config.get("display", {})
        config["display"]["show_banner"] = show_banner

        # Save config
        ui.add_notification("Saving display settings...", "INFO")
        success = ui.run_with_spinner("Saving display settings...", save_config, config)

        if success:
            ui.add_notification("Display settings updated successfully.", "SUCCESS")
            ui.display(Text("Display settings updated successfully.", style="green"), selected_option="2")
        else:
            ui.add_notification("Failed to update display settings.", "ERROR")
            ui.display(Text("Failed to update display settings.", style="red"), selected_option="2")

def scan_menu(_):
    """
    Display the scan menu

    Args:
        _ (dict): Application configuration (not used)
    """
    # Define scan menu items
    menu_items = [
        "Full Workspace Scan",
        "Scan Users & Permissions",
        "Scan Catalogs & Schemas",
        "Scan Secret Scopes",
        "Scan SQL Warehouses",
        "Export Scan Results",
        "Back to Main Menu"
    ]

    ui.set_menu("Scan Workspace", menu_items)
    ui.display(Text("Scan Workspace: Enumerate and analyze Databricks workspace resources.", style="cyan"), selected_option="2")

    # Scan menu loop
    while True:
        # Get user choice
        choice = ui.prompt("Select an option", choices=["1", "2", "3", "4", "5", "6", "7"], default="1")

        if choice == "1":
            # Full workspace scan
            run_workspace_scan("full")
        elif choice == "2":
            # Scan users and permissions
            run_workspace_scan("users")
        elif choice == "3":
            # Scan catalogs and schemas
            run_workspace_scan("catalogs")
        elif choice == "4":
            # Scan secret scopes
            run_workspace_scan("secrets")
        elif choice == "5":
            # Scan SQL warehouses
            run_workspace_scan("warehouses")
        elif choice == "6":
            # Export scan results
            export_scan_results_ui()
        elif choice == "7":
            # Back to main menu
            # Define main menu items again to ensure they're displayed correctly
            main_menu_items = [
                "Profile Management",
                "Scan Workspace",
                "Run SQL Query",
                "Generate Reports",
                "View Results",
                "Configuration",
                "Validate Credentials",
                "Exit"
            ]
            ui.set_menu("Main Menu", main_menu_items)
            # Display the main menu content before breaking out of the loop
            ui.add_notification("Returning to main menu...", "INFO")
            ui.display(Text("Welcome to BricksXploit! Select an option from the menu.", style="cyan"))
            break

def run_workspace_scan(scan_type):
    """
    Run a workspace scan

    Args:
        scan_type (str): Type of scan to run (full, users, catalogs, secrets, warehouses)
    """
    # Get current profile info
    org, profile_name, profile_data = get_current_profile()

    if not profile_data:
        ui.add_notification("No active profile selected.", "WARNING")
        ui.display(Text("No active profile selected. Please select a profile first.", style="yellow"), selected_option="2")
        return

    workspace = profile_data.get("workspace")
    if not workspace:
        ui.add_notification("Invalid profile data. Missing workspace.", "ERROR")
        ui.display(Text("Invalid profile data. Missing workspace.", style="red"), selected_option="2")
        return

    # Confirm scan
    scan_type_display = {
        "full": "Full Workspace",
        "users": "Users & Permissions",
        "catalogs": "Catalogs & Schemas",
        "secrets": "Secret Scopes",
        "warehouses": "SQL Warehouses"
    }

    display_name = scan_type_display.get(scan_type, scan_type.title())

    confirm = ui.confirm(f"Run {display_name} scan on {workspace}?", default=True)
    if not confirm:
        ui.add_notification("Scan cancelled.", "INFO")
        return

    # Ask if user wants to save results
    save_results = ui.confirm("Save scan results to file?", default=True)

    # Ask if user wants to send results to Discord
    send_to_discord = ui.confirm("Send scan results to Discord?", default=False)

    # Run the scan
    ui.add_notification(f"Starting {display_name} scan on {workspace}...", "INFO")
    ui.display(Text(f"Starting {display_name} scan on {workspace}...\nThis may take a while depending on the size of your workspace.", style="cyan"), selected_option="2")

    try:
        if scan_type == "full":
            # Run full scan
            scan_results = ui.run_with_spinner(
                f"Running full workspace scan on {workspace}...",
                run_full_scan,
                workspace,
                profile_data
            )
        else:
            # Run targeted scan
            scan_results = ui.run_with_spinner(
                f"Running {display_name} scan on {workspace}...",
                run_targeted_scan,
                workspace,
                profile_data,
                scan_type
            )

        if not scan_results:
            ui.add_notification("Scan failed or returned no results.", "ERROR")
            ui.display(Text("Scan failed or returned no results.", style="red"), selected_option="2")
            return

        # Display scan summary
        display_scan_summary(scan_results, scan_type)

        # Save results if requested
        if save_results:
            # Ask for export format
            export_format = ui.prompt(
                "Export format",
                choices=["json", "csv"],
                default="json"
            )

            # Export the results
            export_path = ui.run_with_spinner(
                f"Exporting scan results to {export_format.upper()}...",
                export_scan_results,
                scan_results,
                export_format
            )

            if export_path:
                ui.add_notification(f"Scan results exported to: {export_path}", "SUCCESS")
            else:
                ui.add_notification("Failed to export scan results.", "ERROR")

        # Send to Discord if requested
        if send_to_discord:
            webhook_url = get_webhook_url()

            if not webhook_url:
                ui.add_notification("Discord webhook URL not configured.", "WARNING")
                ui.add_notification("Use Configuration > Discord Settings to set up webhook URL.", "INFO")
            else:
                success = ui.run_with_spinner(
                    "Sending scan results to Discord...",
                    generate_and_send_report,
                    workspace,
                    profile_data.get("apikey"),
                    notify="discord",
                    scan_data=scan_results
                )

                if success:
                    ui.add_notification("Scan results sent to Discord successfully.", "SUCCESS")
                else:
                    ui.add_notification("Failed to send scan results to Discord.", "ERROR")

    except Exception as e:
        ui.add_notification(f"Error during scan: {str(e)}", "ERROR")
        ui.display(Text(f"Error during scan: {str(e)}", style="red"), selected_option="2")

def display_scan_summary(scan_results, scan_type):
    """
    Display a summary of scan results

    Args:
        scan_results (dict): Scan results
        scan_type (str): Type of scan
    """
    # Create a table to display scan summary
    table = ui.create_table(title=f"Scan Summary: {scan_type.title()}")
    table.add_column("Resource Type", style="cyan")
    table.add_column("Count", style="green")
    table.add_column("Details", style="yellow")

    # Extract resource counts based on scan type
    if scan_type == "full":
        resources = scan_results.get("resources", {})

        # Add rows for each resource type
        if "users" in resources:
            table.add_row("Users", str(len(resources["users"])), f"Found {len(resources['users'])} users")

        if "groups" in resources:
            table.add_row("Groups", str(len(resources["groups"])), f"Found {len(resources['groups'])} groups")

        if "clusters" in resources:
            table.add_row("Clusters", str(len(resources["clusters"])), f"Found {len(resources['clusters'])} clusters")

        if "jobs" in resources:
            table.add_row("Jobs", str(len(resources["jobs"])), f"Found {len(resources['jobs'])} jobs")

        if "secret_scopes" in resources:
            table.add_row("Secret Scopes", str(len(resources["secret_scopes"])), f"Found {len(resources['secret_scopes'])} secret scopes")

        if "warehouses" in resources:
            table.add_row("SQL Warehouses", str(len(resources["warehouses"])), f"Found {len(resources['warehouses'])} SQL warehouses")

        if "catalogs" in resources:
            table.add_row("Catalogs", str(len(resources["catalogs"])), f"Found {len(resources['catalogs'])} catalogs")

        if "external_locations" in resources:
            table.add_row("External Locations", str(len(resources["external_locations"])), f"Found {len(resources['external_locations'])} external locations")

        if "instance_pools" in resources:
            table.add_row("Instance Pools", str(len(resources["instance_pools"])), f"Found {len(resources['instance_pools'])} instance pools")

        if "tokens" in resources:
            table.add_row("Tokens", str(len(resources["tokens"])), f"Found {len(resources['tokens'])} tokens")
    else:
        # For targeted scans, show specific resource counts
        if scan_type == "users" and "users" in scan_results:
            table.add_row("Users", str(len(scan_results["users"])), f"Found {len(scan_results['users'])} users")

        if scan_type == "users" and "groups" in scan_results:
            table.add_row("Groups", str(len(scan_results["groups"])), f"Found {len(scan_results['groups'])} groups")

        if scan_type == "catalogs" and "catalogs" in scan_results:
            table.add_row("Catalogs", str(len(scan_results["catalogs"])), f"Found {len(scan_results['catalogs'])} catalogs")

        if scan_type == "secrets" and "secret_scopes" in scan_results:
            table.add_row("Secret Scopes", str(len(scan_results["secret_scopes"])), f"Found {len(scan_results['secret_scopes'])} secret scopes")

        if scan_type == "warehouses" and "warehouses" in scan_results:
            table.add_row("SQL Warehouses", str(len(scan_results["warehouses"])), f"Found {len(scan_results['warehouses'])} SQL warehouses")

    # Display the table
    ui.display(table, selected_option="2")
    ui.add_notification("Scan completed successfully.", "SUCCESS")

def export_scan_results_ui():
    """
    Export scan results to a file
    """
    # Load available scan results
    from utils.storage import list_scan_results
    scan_results = list_scan_results()

    if not scan_results:
        ui.add_notification("No scan results found.", "WARNING")
        ui.display(Text("No scan results found. Run a scan first.", style="yellow"), selected_option="6")
        return

    # Create a table to display available scan results
    table = ui.create_table(title="Available Scan Results")
    table.add_column("#", style="cyan")
    table.add_column("Scan Type", style="green")
    table.add_column("Workspace", style="yellow")
    table.add_column("Timestamp", style="magenta")

    # Add rows for each scan result
    for i, result in enumerate(scan_results, 1):
        table.add_row(
            str(i),
            result.get("scan_type", "Unknown"),
            result.get("workspace", "Unknown"),
            result.get("timestamp", "Unknown")
        )

    ui.display(table, selected_option="6")

    # Get user choice
    choice = ui.prompt(
        "Select a scan result to export (or 0 to cancel)",
        choices=["0"] + [str(i) for i in range(1, len(scan_results) + 1)],
        default="0"
    )

    if choice == "0":
        ui.add_notification("Export cancelled.", "INFO")
        return

    # Get selected scan result
    selected_index = int(choice) - 1
    selected_result = scan_results[selected_index]

    # Ask for export format
    export_format = ui.prompt(
        "Export format",
        choices=["json", "csv", "markdown"],
        default="json"
    )

    # Export the results
    export_path = ui.run_with_spinner(
        f"Exporting scan results to {export_format.upper()}...",
        export_report,
        selected_result.get("data", {}),
        export_format
    )

    if export_path:
        ui.add_notification(f"Scan results exported to: {export_path}", "SUCCESS")
        ui.display(Text(f"Scan results exported to: {export_path}", style="green"), selected_option="6")
    else:
        ui.add_notification("Failed to export scan results.", "ERROR")
        ui.display(Text("Failed to export scan results.", style="red"), selected_option="6")

def scan_settings(_):
    """
    Configure scan settings

    Args:
        _ (dict): Application configuration (not used)
    """
    # Load config
    from utils.storage import load_config
    config = load_config()

    # Get current scan settings
    current_settings = config.get("scan", {})

    # Create a table to display current settings
    table = ui.create_table(title="Current Scan Settings")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    for key, value in current_settings.items():
        table.add_row(key, str(value))

    ui.display(table, selected_option="3")

    # Ask if user wants to update scan settings
    update = ui.confirm("Update scan settings?", default=False)

    if update:
        # Get new settings
        # Example setting: scan_timeout
        scan_timeout = ui.prompt(
            "Enter scan timeout in seconds",
            default=str(current_settings.get("scan_timeout", 30))
        )

        try:
            scan_timeout = int(scan_timeout)
        except ValueError:
            ui.add_notification("Invalid timeout value. Using default.", "WARNING")
            scan_timeout = 30

        # Update settings
        config["scan"] = config.get("scan", {})
        config["scan"]["scan_timeout"] = scan_timeout

        # Save config
        ui.add_notification("Saving scan settings...", "INFO")
        success = ui.run_with_spinner("Saving scan settings...", save_config, config)

        if success:
            ui.add_notification("Scan settings updated successfully.", "SUCCESS")
            ui.display(Text("Scan settings updated successfully.", style="green"), selected_option="3")
        else:
            ui.add_notification("Failed to update scan settings.", "ERROR")
            ui.display(Text("Failed to update scan settings.", style="red"), selected_option="3")
