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
from core.report import validate_and_notify
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
        "Profile",
        "Scan",
        "Run SQL Query",
        "Reports",
        "Results",
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
                "Profile",
                "Scan",
                "Run SQL Query",
                "Reports",
                "Results",
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
            "Profile",
            "Scan",
            "Run SQL Query",
            "Reports",
            "Results",
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
                "Profile",
                "Scan",
                "Run SQL Query",
                "Reports",
                "Results",
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
                "Profile",
                "Scan",
                "Run SQL Query",
                "Reports",
                "Results",
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
    Run a workspace scan with real-time updates in the UI

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

    # Create a progress table to show real-time scan status
    progress_table = ui.create_table(title=f"{display_name} Scan: {workspace}")
    progress_table.add_column("Resource", style="cyan")
    progress_table.add_column("Status", style="green")
    progress_table.add_column("Count", style="yellow")

    # Initialize the progress table with expected resources based on scan type
    if scan_type == "full":
        resources_to_scan = [
            "Users", "Groups", "Clusters", "Jobs", "Secret Scopes",
            "SQL Warehouses", "Catalogs", "Schemas", "Tables",
            "Instance Pools", "External Locations", "Tokens"
        ]
    elif scan_type == "users":
        resources_to_scan = ["Users", "Groups"]
    elif scan_type == "catalogs":
        resources_to_scan = ["Catalogs", "Schemas", "Tables"]
    elif scan_type == "secrets":
        resources_to_scan = ["Secret Scopes", "Secrets"]
    elif scan_type == "warehouses":
        resources_to_scan = ["SQL Warehouses"]
    else:
        resources_to_scan = [scan_type.replace("_", " ").title()]

    # Add rows for each resource to be scanned
    for resource in resources_to_scan:
        progress_table.add_row(resource, "Pending", "0")

    # Display initial progress
    ui.add_notification(f"Starting {display_name} scan on {workspace}...", "INFO")
    ui.display(progress_table, selected_option="2")

    # Create a callback function to update the UI during scan
    def update_scan_progress(resource_type, status, count=None):
        # Update the progress table
        try:
            # Find the row with the matching resource type
            for row_index, row in enumerate(progress_table.rows):
                # Check if the row is a tuple and has at least one element
                if isinstance(row, tuple) and len(row) > 0:
                    # Check if the first element has a 'plain' attribute
                    if hasattr(row[0], 'plain') and row[0].plain == resource_type:
                        progress_table.rows[row_index] = (
                            row[0],  # Keep the resource name
                            Text(status, style="green" if status == "Complete" else "yellow"),
                            Text(str(count) if count is not None else "0", style="yellow")
                        )
                        break
                # Alternative approach if rows are not tuples
                elif hasattr(row, 'cells') and len(row.cells) > 0:
                    cell_text = str(row.cells[0])
                    if resource_type in cell_text:
                        # Use the table's add_row method to update
                        # First, remove the old row
                        progress_table.rows.pop(row_index)
                        # Then add the new row at the same position
                        new_row = [
                            Text(resource_type, style="cyan"),
                            Text(status, style="green" if status == "Complete" else "yellow"),
                            Text(str(count) if count is not None else "0", style="yellow")
                        ]
                        progress_table.rows.insert(row_index, new_row)
                        break
        except Exception as e:
            # If there's an error updating the table, log it but don't crash
            ui.add_notification(f"Error updating progress table: {str(e)}", "WARNING")

        # Update the UI with notification regardless of table update success
        ui.add_notification(f"{resource_type}: {status} {f'({count} found)' if count else ''}", "INFO")
        ui.display(progress_table, selected_option="2")

    try:
        # Run the scan with progress updates
        if scan_type == "full":
            # For full scan, we'll use a custom wrapper to update progress
            def full_scan_with_updates():
                # Update initial status
                for resource in resources_to_scan:
                    update_scan_progress(resource, "Pending")

                # Run the actual scan
                scan_results = run_full_scan(workspace, profile_data)

                # Ensure scan_type is included in the results for Discord notifications
                if scan_results and isinstance(scan_results, dict):
                    scan_results["scan_type"] = "full"

                # Update final status for each resource
                if scan_results and "resources" in scan_results:
                    resources = scan_results["resources"]

                    # Update users
                    if "users" in resources:
                        update_scan_progress("Users", "Complete", len(resources["users"]))

                    # Update groups
                    if "groups" in resources:
                        update_scan_progress("Groups", "Complete", len(resources["groups"]))

                    # Update clusters
                    if "clusters" in resources:
                        update_scan_progress("Clusters", "Complete", len(resources["clusters"]))

                    # Update jobs
                    if "jobs" in resources:
                        update_scan_progress("Jobs", "Complete", len(resources["jobs"]))

                    # Update secret scopes
                    if "secret_scopes" in resources:
                        update_scan_progress("Secret Scopes", "Complete", len(resources["secret_scopes"]))

                    # Update SQL warehouses
                    if "warehouses" in resources:
                        update_scan_progress("SQL Warehouses", "Complete", len(resources["warehouses"]))

                    # Update catalogs
                    if "catalogs" in resources:
                        update_scan_progress("Catalogs", "Complete", len(resources["catalogs"]))

                    # Update schemas
                    if "schemas" in resources:
                        schema_count = 0
                        for catalog_schemas in resources["schemas"].values():
                            schema_count += len(catalog_schemas)
                        update_scan_progress("Schemas", "Complete", schema_count)

                    # Update tables
                    if "tables" in resources:
                        table_count = 0
                        for schema_tables in resources["tables"].values():
                            table_count += len(schema_tables)
                        update_scan_progress("Tables", "Complete", table_count)

                    # Update instance pools
                    if "instance_pools" in resources:
                        update_scan_progress("Instance Pools", "Complete", len(resources["instance_pools"]))

                    # Update external locations
                    if "external_locations" in resources:
                        update_scan_progress("External Locations", "Complete", len(resources["external_locations"]))

                    # Update tokens
                    if "tokens" in resources:
                        update_scan_progress("Tokens", "Complete", len(resources["tokens"]))

                return scan_results

            # Run the full scan with progress updates
            scan_results = ui.run_with_spinner(
                f"Running full workspace scan on {workspace}...",
                full_scan_with_updates
            )
        else:
            # For targeted scans, we'll use a custom wrapper to update progress
            def targeted_scan_with_updates():
                # Update initial status
                for resource in resources_to_scan:
                    update_scan_progress(resource, "Pending")

                # Run the actual scan
                scan_results = run_targeted_scan(workspace, profile_data, scan_type)

                # Ensure scan_type is included in the results for Discord notifications
                if scan_results and isinstance(scan_results, dict):
                    scan_results["scan_type"] = scan_type

                # Update final status for each resource
                if scan_results and "resources" in scan_results:
                    resources = scan_results["resources"]

                    if scan_type == "users":
                        # Update users
                        if "users" in resources:
                            update_scan_progress("Users", "Complete", len(resources["users"]))

                        # Update groups
                        if "groups" in resources:
                            update_scan_progress("Groups", "Complete", len(resources["groups"]))

                    elif scan_type == "catalogs":
                        # Update catalogs
                        if "catalogs" in resources:
                            update_scan_progress("Catalogs", "Complete", len(resources["catalogs"]))

                        # Update schemas
                        if "schemas" in resources:
                            schema_count = 0
                            for catalog_schemas in resources["schemas"].values():
                                schema_count += len(catalog_schemas)
                            update_scan_progress("Schemas", "Complete", schema_count)

                        # Update tables
                        if "tables" in resources:
                            table_count = 0
                            for schema_tables in resources["tables"].values():
                                table_count += len(schema_tables)
                            update_scan_progress("Tables", "Complete", table_count)

                    elif scan_type == "secrets":
                        # Update secret scopes
                        if "secret_scopes" in resources:
                            update_scan_progress("Secret Scopes", "Complete", len(resources["secret_scopes"]))

                        # Update secrets
                        if "secrets" in resources:
                            secret_count = 0
                            for scope_secrets in resources["secrets"].values():
                                secret_count += len(scope_secrets)
                            update_scan_progress("Secrets", "Complete", secret_count)

                    elif scan_type == "warehouses":
                        # Update SQL warehouses
                        if "warehouses" in resources:
                            update_scan_progress("SQL Warehouses", "Complete", len(resources["warehouses"]))

                    else:
                        # For other scan types, update the generic resource
                        resource_name = scan_type.replace("_", " ").title()
                        for resource_type, resource_data in resources.items():
                            if isinstance(resource_data, list):
                                update_scan_progress(resource_name, "Complete", len(resource_data))
                            elif isinstance(resource_data, dict):
                                update_scan_progress(resource_name, "Complete", len(resource_data))

                return scan_results

            # Run the targeted scan with progress updates
            scan_results = ui.run_with_spinner(
                f"Running {display_name} scan on {workspace}...",
                targeted_scan_with_updates
            )

        if not scan_results:
            ui.add_notification("Scan failed or returned no results.", "ERROR")
            ui.display(Text("Scan failed or returned no results.", style="red"), selected_option="2")
            return

        # Display scan summary with detailed information
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
                ui.add_notification(f"File saved at: {export_path}", "INFO")
            else:
                ui.add_notification("Failed to export scan results.", "ERROR")
                export_path = None  # Ensure it's None if export failed

        # Send to Discord if requested
        if send_to_discord:
            webhook_url = get_webhook_url()

            if not webhook_url:
                ui.add_notification("Discord webhook URL not configured.", "WARNING")
                ui.add_notification("Use Configuration > Discord Settings to set up webhook URL.", "INFO")
            else:
                # Import the send_scan_notification function directly
                from utils.discord import send_scan_notification

                success = ui.run_with_spinner(
                    "Sending scan results to Discord...",
                    send_scan_notification,
                    scan_results,
                    export_path  # Pass the file path to the notification
                )

                if success:
                    ui.add_notification("Scan results sent to Discord successfully.", "SUCCESS")
                    if export_path:
                        ui.add_notification("File path included in Discord notification.", "INFO")
                else:
                    ui.add_notification("Failed to send scan results to Discord.", "ERROR")

    except Exception as e:
        ui.add_notification(f"Error during scan: {str(e)}", "ERROR")
        ui.display(Text(f"Error during scan: {str(e)}", style="red"), selected_option="2")

def display_scan_summary(scan_results, scan_type):
    """
    Display a summary of scan results with detailed navigation information

    Args:
        scan_results (dict): Scan results
        scan_type (str): Type of scan
    """
    if not scan_results:
        ui.add_notification("No scan results to display.", "WARNING")
        ui.display(Text("No scan results to display.", style="yellow"), selected_option="2")
        return

    workspace = scan_results.get("workspace", "Unknown")
    resources = scan_results.get("resources", {})
    # Include scan time in notification
    scan_time = scan_results.get("scan_time", "Unknown")
    ui.add_notification(f"Scan completed at: {scan_time}", "INFO")

    # Create a main table for the scan summary
    summary_table = ui.create_table(title=f"Workspace Scan: {workspace}")
    summary_table.add_column("Resource Type", style="cyan")
    summary_table.add_column("Count", style="green")
    summary_table.add_column("Status", style="yellow")

    # Add scan metadata
    scan_type_display = scan_type.replace("_", " ").title()

    # Create a more detailed view based on scan type
    if scan_type == "full":
        # Show all resource types in the summary table
        resource_types = [
            ("Users", "users"),
            ("Groups", "groups"),
            ("Catalogs", "catalogs"),
            ("Secret Scopes", "secret_scopes"),
            ("SQL Warehouses", "warehouses"),
            ("Clusters", "clusters"),
            ("Jobs", "jobs"),
            ("Instance Pools", "instance_pools"),
            ("External Locations", "external_locations"),
            ("Tokens", "tokens")
        ]

        for display_name, key in resource_types:
            if key in resources:
                count = len(resources[key])
                summary_table.add_row(
                    display_name,
                    str(count),
                    "✓ Complete" if count > 0 else "No items found"
                )

        # Display the summary table
        ui.display(summary_table, selected_option="2")

    elif scan_type == "users":
        # Show users and groups
        if "users" in resources:
            users = resources["users"]
            summary_table.add_row("Users", str(len(users)), "✓ Complete")

        if "groups" in resources:
            groups = resources["groups"]
            summary_table.add_row("Groups", str(len(groups)), "✓ Complete")

        # Display the summary table
        ui.display(summary_table, selected_option="2")

        # Show detailed users table if available
        if "users" in resources and len(resources["users"]) > 0:
            # Create a table for users
            users_table = ui.create_table(title="Users")
            users_table.add_column("Username", style="cyan")
            users_table.add_column("Display Name", style="green")
            users_table.add_column("Groups", style="yellow")

            # Add sample of users (up to 10)
            sample_users = resources["users"][:10]
            for user in sample_users:
                username = user.get("userName", "N/A")
                display_name = user.get("displayName", "N/A")

                # Get groups for this user
                user_groups = []
                if "groups" in user:
                    user_groups = [g.get("display", g.get("value", "")) for g in user.get("groups", [])]

                # Format groups display
                groups_display = ", ".join(user_groups[:3])
                if len(user_groups) > 3:
                    groups_display += f" +{len(user_groups) - 3} more"

                users_table.add_row(username, display_name, groups_display)

            # Add note if showing a sample
            if len(resources["users"]) > 10:
                ui.add_notification(f"Showing sample of {len(sample_users)} users out of {len(resources['users'])} total", "INFO")

            # Display the users table
            ui.display(users_table, selected_option="2")

    elif scan_type == "catalogs":
        # Show catalogs, schemas, and tables
        if "catalogs" in resources:
            catalogs = resources["catalogs"]
            summary_table.add_row("Catalogs", str(len(catalogs)), "✓ Complete")

        if "schemas" in resources:
            # Count total schemas across all catalogs
            schema_count = 0
            for catalog_schemas in resources["schemas"].values():
                schema_count += len(catalog_schemas)
            summary_table.add_row("Schemas", str(schema_count), "✓ Sample")

        if "tables" in resources:
            # Count total tables across all schemas
            table_count = 0
            for schema_tables in resources["tables"].values():
                table_count += len(schema_tables)
            summary_table.add_row("Tables", str(table_count), "✓ Sample")

        # Display the summary table
        ui.display(summary_table, selected_option="2")

        # Show detailed catalogs and schemas if available
        if "catalogs" in resources and len(resources["catalogs"]) > 0:
            # Create a table for catalogs and schemas
            catalogs_table = ui.create_table(title="Catalogs and Schemas")
            catalogs_table.add_column("Catalog", style="cyan")
            catalogs_table.add_column("Schemas", style="green")
            catalogs_table.add_column("Sample Tables", style="yellow")

            # Add catalogs and their schemas
            for catalog in resources["catalogs"]:
                catalog_name = catalog.get("name", "N/A")

                # Get schemas for this catalog
                catalog_schemas = []
                if "schemas" in resources and catalog_name in resources["schemas"]:
                    catalog_schemas = resources["schemas"][catalog_name]

                # Format schemas display
                schemas_display = ", ".join([s.get("name", "N/A") for s in catalog_schemas[:3]])
                if len(catalog_schemas) > 3:
                    schemas_display += f" +{len(catalog_schemas) - 3} more"
                elif not catalog_schemas:
                    schemas_display = "No schemas found"

                # Get sample tables
                sample_tables = "No tables sampled"
                for schema_key, tables in resources.get("tables", {}).items():
                    if schema_key.startswith(f"{catalog_name}."):
                        table_names = [t.get("name", "N/A") for t in tables[:3]]
                        sample_tables = ", ".join(table_names)
                        if len(tables) > 3:
                            sample_tables += f" +{len(tables) - 3} more"
                        break

                catalogs_table.add_row(catalog_name, schemas_display, sample_tables)

            # Display the catalogs table
            ui.display(catalogs_table, selected_option="2")

    elif scan_type == "secrets":
        # Show secret scopes and secrets
        if "secret_scopes" in resources:
            scopes = resources["secret_scopes"]
            summary_table.add_row("Secret Scopes", str(len(scopes)), "✓ Complete")

        if "secrets" in resources:
            # Count total secrets across all scopes
            secret_count = 0
            for scope_secrets in resources["secrets"].values():
                secret_count += len(scope_secrets)
            summary_table.add_row("Secrets", str(secret_count), "✓ Complete")

        # Display the summary table
        ui.display(summary_table, selected_option="2")

        # Show detailed secret scopes if available
        if "secret_scopes" in resources and len(resources["secret_scopes"]) > 0:
            # Create a table for secret scopes
            scopes_table = ui.create_table(title="Secret Scopes")
            scopes_table.add_column("Scope Name", style="cyan")
            scopes_table.add_column("Backend Type", style="green")
            scopes_table.add_column("Secrets", style="yellow")

            # Add secret scopes and their secrets
            for scope in resources["secret_scopes"]:
                scope_name = scope.get("name", "N/A")
                backend_type = scope.get("backend_type", "N/A")

                # Get secrets for this scope
                scope_secrets = []
                if "secrets" in resources and scope_name in resources["secrets"]:
                    scope_secrets = resources["secrets"][scope_name]

                # Format secrets display
                secrets_display = ", ".join([s.get("key", "N/A") for s in scope_secrets[:3]])
                if len(scope_secrets) > 3:
                    secrets_display += f" +{len(scope_secrets) - 3} more"
                elif not scope_secrets:
                    secrets_display = "No secrets found"

                scopes_table.add_row(scope_name, backend_type, secrets_display)

            # Display the scopes table
            ui.display(scopes_table, selected_option="2")

    elif scan_type == "warehouses":
        # Show SQL warehouses
        if "warehouses" in resources:
            warehouses = resources["warehouses"]
            summary_table.add_row("SQL Warehouses", str(len(warehouses)), "✓ Complete")

        # Display the summary table
        ui.display(summary_table, selected_option="2")

        # Show detailed warehouses if available
        if "warehouses" in resources and len(resources["warehouses"]) > 0:
            # Create a table for warehouses
            warehouses_table = ui.create_table(title="SQL Warehouses")
            warehouses_table.add_column("Name", style="cyan")
            warehouses_table.add_column("Size", style="green")
            warehouses_table.add_column("State", style="yellow")

            # Add warehouses
            for warehouse in resources["warehouses"]:
                name = warehouse.get("name", "N/A")
                size = warehouse.get("size", "N/A")
                state = warehouse.get("state", "N/A")

                warehouses_table.add_row(name, size, state)

            # Display the warehouses table
            ui.display(warehouses_table, selected_option="2")

    else:
        # For other scan types, just show the summary table
        for resource_type, resource_data in resources.items():
            if isinstance(resource_data, list):
                summary_table.add_row(
                    resource_type.replace("_", " ").title(),
                    str(len(resource_data)),
                    "✓ Complete"
                )
            elif isinstance(resource_data, dict):
                summary_table.add_row(
                    resource_type.replace("_", " ").title(),
                    str(len(resource_data)),
                    "✓ Complete"
                )

        # Display the summary table
        ui.display(summary_table, selected_option="2")

    # Add notification about scan completion
    ui.add_notification(f"Scan of {workspace} completed successfully", "SUCCESS")
    ui.add_notification(f"Scan type: {scan_type_display}", "INFO")

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
