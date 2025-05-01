"""
Authentication and credential validation for Databricks
"""

import requests
import json
import sys
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

# Adicionar o diretório raiz ao path para permitir importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.storage import load_config, add_profile, get_current_profile
from utils.ui import print_success, print_error, print_warning, print_info

console = Console()

def get_workspace_url(workspace):
    """
    Construct the full workspace URL

    Args:
        workspace (str): Workspace name or URL

    Returns:
        str: Full workspace URL
    """
    if not workspace:
        print_error("Workspace is missing! Please provide a valid workspace identifier.")
        return None

    # Check if it's already a full URL
    if workspace.startswith("http"):
        return workspace

    # Check for different Databricks domains
    if "databricks.com" in workspace:
        # Already has domain, just add https
        return f"https://{workspace}"
    else:
        # Add default domain
        return f"https://{workspace}.cloud.databricks.com"

def validate_credentials(workspace, apikey):
    """
    Validate credentials and return user profile information

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key

    Returns:
        dict: User profile data or None if invalid
    """
    workspace_url = get_workspace_url(workspace)
    if not workspace_url:
        return None

    url = f"{workspace_url}/api/2.0/preview/scim/v2/Me"
    headers = {"Authorization": f"Bearer {apikey}"}

    if not workspace or not apikey:
        print_error("Missing workspace or API key! Please provide valid credentials.")
        return None

    try:
        print_info(f"Validating credentials for: {workspace}")
        response = requests.get(url, headers=headers)

        # Check if response was successful
        response.raise_for_status()

        # If valid, return user data
        user_data = response.json()
        print_success(f"Credentials validated successfully!")
        return user_data

    except requests.exceptions.RequestException as e:
        print_error(f"Connection Error: {e}")
        return None

def display_user_info(profile, detailed=False):
    """
    Display user information in a formatted way

    Args:
        profile (dict): User profile data
        detailed (bool): Whether to show detailed information
    """
    if not profile:
        print_error("No profile data available!")
        return

    # Basic user info panel
    user_id = profile.get("id", "N/A")
    username = profile.get("userName", "N/A")
    display_name = profile.get("displayName", "N/A")
    email = profile.get("emails", [{}])[0].get("value", "N/A") if profile.get("emails") else "N/A"
    active = "✓" if profile.get("active", False) else "✗"

    # Get roles and groups
    roles = profile.get("roles", [])
    groups = profile.get("groups", [])

    # Create basic info panel
    basic_info = f"""
[bold cyan]User ID:[/bold cyan] {user_id}
[bold cyan]Username:[/bold cyan] {username}
[bold cyan]Display Name:[/bold cyan] {display_name}
[bold cyan]Email:[/bold cyan] {email}
[bold cyan]Active:[/bold cyan] {active}
"""

    # Add roles and groups summary
    if roles:
        role_text = ", ".join(roles[:5])
        if len(roles) > 5:
            role_text += f" and {len(roles) - 5} more"
        basic_info += f"\n[bold cyan]Roles:[/bold cyan] {role_text}"
    else:
        basic_info += "\n[bold cyan]Roles:[/bold cyan] No roles assigned"

    if groups:
        group_text = ", ".join(groups[:5])
        if len(groups) > 5:
            group_text += f" and {len(groups) - 5} more"
        basic_info += f"\n[bold cyan]Groups:[/bold cyan] {group_text}"
    else:
        basic_info += "\n[bold cyan]Groups:[/bold cyan] No groups assigned"

    # Create and display the panel
    panel = Panel(
        basic_info,
        title=f"[bold]User Information: {display_name}[/bold]",
        border_style="blue",
        box=box.ROUNDED
    )

    console.print(panel)

    # If detailed view is requested, show more information
    if detailed and profile.get("groups"):
        # Create a table for groups
        groups_table = Table(title="User Groups", box=box.SIMPLE)
        groups_table.add_column("Group Name", style="cyan")
        groups_table.add_column("Type", style="green")
        groups_table.add_column("Value", style="magenta")

        for group in profile.get("groups", []):
            groups_table.add_row(
                group,
                "Standard",
                ""
            )

        console.print(groups_table)

def display_user_info_table(profile):
    """
    Display user information in a table format

    Args:
        profile (dict): User profile data
    """
    if not profile:
        print_error("No profile data available!")
        return

    # Create a table for user information
    table = Table(title="User Information", style="bold cyan")

    table.add_column("Field", justify="right", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    # Add profile information
    table.add_row("User ID", profile.get("id", "N/A"))
    table.add_row("User Name", profile.get("userName", "N/A"))
    table.add_row("Full Name", profile.get("displayName", "N/A"))
    table.add_row("Email", profile.get("emails", [{}])[0].get("value", "N/A") if profile.get("emails") else "N/A")
    table.add_row("Active", "✓" if profile.get("active", False) else "✗")

    # Add roles and groups
    roles = ", ".join(profile.get("roles", [])) or "No roles assigned"
    groups = ", ".join(profile.get("groups", [])) or "No groups assigned"

    table.add_row("Roles", roles)
    table.add_row("Groups", groups)

    console.print(table)

def save_credentials(workspace, apikey, organization=None, profile_name=None):
    """
    Save credentials to profile storage

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key
        organization (str, optional): Organization name
        profile_name (str, optional): Custom profile name (defaults to workspace)

    Returns:
        bool: Success or failure
    """
    try:
        # Validate credentials first
        user_info = validate_credentials(workspace, apikey)

        if not user_info:
            print_error("Cannot save invalid credentials!")
            return False

        # Extract user information
        display_name = user_info.get("displayName")
        username = user_info.get("userName")

        # Use provided profile name or default to workspace
        final_profile_name = profile_name if profile_name else workspace

        # Create metadata
        metadata = {
            "user_id": user_info.get("id"),
            "username": username,
            "email": user_info.get("emails", [{}])[0].get("value") if user_info.get("emails") else None,
            "groups": user_info.get("groups", []),
            "roles": user_info.get("roles", [])
        }

        # Save profile
        success = add_profile(workspace, apikey, display_name, organization, metadata, profile_name=final_profile_name)

        if success:
            print_success(f"Credentials saved for {display_name} ({final_profile_name})")
            return True
        else:
            print_error("Failed to save credentials!")
            return False

    except Exception as e:
        print_error(f"Error saving credentials: {e}")
        return False

def get_current_credentials():
    """
    Get the currently active credentials

    Returns:
        tuple: (workspace, apikey, profile_data) or (None, None, None) if no active profile
    """
    org, profile_name, profile_data = get_current_profile()

    if not profile_data:
        print_warning("No active profile found! Please set an active profile first.")
        return None, None, None

    workspace = profile_data.get("workspace")
    apikey = profile_data.get("apikey")

    if not workspace or not apikey:
        print_error("Invalid profile data! Missing workspace or API key.")
        return None, None, None

    return workspace, apikey, profile_data
