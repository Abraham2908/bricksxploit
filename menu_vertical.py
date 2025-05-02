"""
Vertical bipartite menu system for BricksXploit
"""

import time
import sys
import os
from rich.text import Text
from rich.panel import Panel
from rich.align import Align

# Configurar o ambiente para importações
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Importações absolutas
from core.auth import validate_credentials
from core.profiles import list_profiles, switch_profile, add_new_profile, remove_profile
from core.report import validate_and_notify
from utils.storage import load_config, save_config, get_webhook_url, set_webhook_url
from utils.storage import get_current_profile
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
            ui.add_notification("Scan functionality will be implemented in a future update.", "INFO")
            ui.display(Text("Scan functionality will be implemented in a future update.", style="yellow"), selected_option="2")
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
            
def profile_menu(config):
    """
    Display the profile management menu
    
    Args:
        config (dict): Application configuration
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
    workspace = ui.prompt("Enter workspace (e.g., dbc-xxxx.cloud.databricks.com)")
    apikey = ui.prompt("Enter API key", password=True)
    
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
        success = ui.run_with_spinner(f"Removing profile {display_name}...", remove_profile, org_name, profile_name)

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
    
def validate_menu(config):
    """
    Validate credentials for a Databricks workspace

    Args:
        config (dict): Application configuration
    """
    ui.set_menu("Validate Credentials", ["Back to Main Menu"])
    ui.display(Text("Validate Credentials: Test access to a Databricks workspace.\n\nPlease provide the following information:", style="cyan"), selected_option="7")

    # Get workspace and API key
    workspace = ui.prompt("Enter workspace (e.g., dbc-xxxx.cloud.databricks.com)")
    apikey = ui.prompt("Enter API key", password=True)

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
    ui.display(Text("Configuration: Manage application settings.", style="cyan"), selected_option="6")

    # Configuration menu loop
    while True:
        # Get user choice
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
        
def display_settings(config):
    """
    Configure display settings

    Args:
        config (dict): Application configuration
    """
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
        
def scan_settings(config):
    """
    Configure scan settings

    Args:
        config (dict): Application configuration
    """
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
