"""
Profile management for BricksXploit
"""

import sys
import os
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

# Adicionar o diretório raiz ao path para permitir importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.auth import validate_credentials, display_user_info
from utils.storage import (
    load_profiles, save_profiles, get_current_profile,
    set_current_profile, add_profile, remove_profile as remove_profile_storage
)
from utils.ui import print_success, print_error, print_warning, print_info, ask_for_input, confirm

console = Console()

def list_profiles(return_data=False):
    """
    List all available profiles

    Args:
        return_data (bool, optional): If True, return profiles data instead of printing

    Returns:
        dict: Profiles data if return_data is True, None otherwise
    """
    profiles = load_profiles()

    # If return_data is True, prepare and return the data
    if return_data:
        result = {}

        # Add default profiles
        if profiles["default"]:
            result["Default"] = {}
            for name, data in profiles["default"].items():
                # Get current profile to mark active status
                org, profile_name, _ = get_current_profile()
                status = "Active" if name == profile_name and org is None else ""

                # Copy data and add status
                profile_data = data.copy()
                profile_data["status"] = status
                result["Default"][name] = profile_data

        # Add organization profiles
        if profiles["organizations"]:
            for org_name, org_profiles in profiles["organizations"].items():
                if not org_profiles:
                    continue

                result[org_name] = {}
                for name, data in org_profiles.items():
                    # Get current profile to mark active status
                    org, profile_name, _ = get_current_profile()
                    status = "Active" if name == profile_name and org == org_name else ""

                    # Copy data and add status
                    profile_data = data.copy()
                    profile_data["status"] = status
                    result[org_name][name] = profile_data

        return result

    # Otherwise, display profiles in tables
    # Check if there are any profiles
    if not profiles["organizations"] and not profiles["default"]:
        print_warning("No profiles found.")
        return

    # Get current profile
    org, profile_name, _ = get_current_profile()

    # Create table for default profiles
    if profiles["default"]:
        table = Table(title="Default Profiles")
        table.add_column("Profile", style="cyan")
        table.add_column("Workspace", style="green")
        table.add_column("Created", style="blue")
        table.add_column("Status", style="magenta")

        for name, data in profiles["default"].items():
            status = "[green]Active[/green]" if name == profile_name and org is None else ""
            table.add_row(
                name,
                data.get("workspace", "N/A"),
                data.get("created_at", "N/A"),
                status
            )

        console.print(table)

    # Create tables for organization profiles
    if profiles["organizations"]:
        for org_name, org_profiles in profiles["organizations"].items():
            if not org_profiles:
                continue

            org_table = Table(title=f"Organization: {org_name}")
            org_table.add_column("Profile", style="cyan")
            org_table.add_column("Workspace", style="green")
            org_table.add_column("Created", style="blue")
            org_table.add_column("Status", style="magenta")

            for name, data in org_profiles.items():
                status = "[green]Active[/green]" if name == profile_name and org == org_name else ""
                org_table.add_row(
                    name,
                    data.get("workspace", "N/A"),
                    data.get("created_at", "N/A"),
                    status
                )

            console.print(org_table)

def switch_profile(org_name=None, profile_name=None):
    """
    Switch to a different profile

    Args:
        org_name (str, optional): Organization name
        profile_name (str, optional): Profile name

    Returns:
        bool: Success or failure
    """
    # If org_name and profile_name are provided, switch directly
    if profile_name is not None:
        if set_current_profile(org_name, profile_name):
            print_success(f"Switched to profile: {profile_name}" + (f" ({org_name})" if org_name else ""))
            return True
        else:
            print_error(f"Failed to switch to profile: {profile_name}")
            return False

    # Otherwise, show interactive menu
    profiles = load_profiles()

    # Check if there are any profiles
    if not profiles["organizations"] and not profiles["default"]:
        print_warning("No profiles found. Please add a profile first.")
        return False

    # Get current profile
    current_org, current_profile, _ = get_current_profile()

    # Create a list of all profiles
    all_profiles = []

    # Add default profiles
    for name in profiles["default"].keys():
        all_profiles.append((None, name))

    # Add organization profiles
    for org_name, org_profiles in profiles["organizations"].items():
        for name in org_profiles.keys():
            all_profiles.append((org_name, name))

    # Display profiles for selection
    print_info("Available profiles:")
    for i, (org, name) in enumerate(all_profiles):
        status = " [green](Active)[/green]" if org == current_org and name == current_profile else ""
        if org:
            print_info(f"{i+1}. {name} ({org}){status}")
        else:
            print_info(f"{i+1}. {name}{status}")

    # Get user selection
    selection = ask_for_input("Enter profile number (or 0 to cancel): ", default="0")

    try:
        selection = int(selection)
        if selection == 0:
            return False

        if selection < 1 or selection > len(all_profiles):
            print_error("Invalid selection.")
            return False

        # Get selected profile
        org, name = all_profiles[selection-1]

        # Set as current profile
        if set_current_profile(org, name):
            print_success(f"Switched to profile: {name}" + (f" ({org})" if org else ""))
            return True
        else:
            print_error("Failed to switch profile.")
            return False

    except ValueError:
        print_error("Invalid selection. Please enter a number.")
        return False

def add_new_profile(workspace, apikey, organization=None, profile_name=None, user_info=None):
    """
    Add a new profile

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key
        organization (str, optional): Organization name
        profile_name (str, optional): Custom profile name (defaults to workspace)
        user_info (dict, optional): User info from validate_credentials (to avoid re-validation)

    Returns:
        bool: Success or failure
    """
    # Validate credentials if user_info not provided
    if not user_info:
        print_info(f"Validating credentials for workspace: {workspace}")
        user_info = validate_credentials(workspace, apikey)

        if not user_info:
            print_error("Invalid credentials. Profile not added.")
            return False

    # Get display name from user info
    display_name = user_info.get("displayName") or workspace

    # Use provided profile name or default to workspace
    final_profile_name = profile_name if profile_name else workspace

    # Create metadata (limit the amount of data stored to improve performance)
    metadata = {
        "user_id": user_info.get("id"),
        "username": user_info.get("userName"),
        "email": user_info.get("emails", [{}])[0].get("value") if user_info.get("emails") else None
    }

    # Only include groups and roles if they're not too large
    groups = user_info.get("groups", [])
    if groups and len(groups) <= 20:  # Limit to 20 groups
        metadata["groups"] = groups

    roles = user_info.get("roles", [])
    if roles and len(roles) <= 10:  # Limit to 10 roles
        metadata["roles"] = roles

    # Add profile
    success = add_profile(workspace, apikey, display_name, organization, metadata, profile_name=final_profile_name)

    if success:
        print_success(f"Profile added: {final_profile_name}" + (f" ({organization})" if organization else ""))

        # Set as current profile automatically
        if set_current_profile(organization, final_profile_name):
            print_success(f"Current profile set to: {final_profile_name}" + (f" ({organization})" if organization else ""))
        else:
            print_error("Failed to set current profile.")

        return True
    else:
        print_error("Failed to add profile.")
        return False

def remove_profile(org_name=None, profile_name=None):
    """
    Remove a profile

    Args:
        org_name (str, optional): Organization name
        profile_name (str, optional): Profile name

    Returns:
        bool: Success or failure
    """
    # If org_name and profile_name are provided, remove directly
    if profile_name is not None:
        # Confirm removal
        if not confirm(f"Are you sure you want to remove profile: {profile_name}" + (f" ({org_name})" if org_name else "") + "?", default=False):
            print_info("Operation cancelled.")
            return False

        # Remove profile
        if remove_profile_storage(profile_name, org_name):
            print_success(f"Profile removed: {profile_name}" + (f" ({org_name})" if org_name else ""))
            return True
        else:
            print_error(f"Failed to remove profile: {profile_name}")
            return False

    # Otherwise, show interactive menu
    profiles = load_profiles()

    # Check if there are any profiles
    if not profiles["organizations"] and not profiles["default"]:
        print_warning("No profiles found.")
        return False

    # Get current profile
    current_org, current_profile, _ = get_current_profile()

    # Create a list of all profiles
    all_profiles = []

    # Add default profiles
    for name in profiles["default"].keys():
        all_profiles.append((None, name))

    # Add organization profiles
    for org_name, org_profiles in profiles["organizations"].items():
        for name in org_profiles.keys():
            all_profiles.append((org_name, name))

    # Display profiles for selection
    print_info("Select profile to remove:")
    for i, (org, name) in enumerate(all_profiles):
        status = " [green](Active)[/green]" if org == current_org and name == current_profile else ""
        if org:
            print_info(f"{i+1}. {name} ({org}){status}")
        else:
            print_info(f"{i+1}. {name}{status}")

    # Get user selection
    selection = ask_for_input("Enter profile number (or 0 to cancel): ", default="0")

    try:
        selection = int(selection)
        if selection == 0:
            return False

        if selection < 1 or selection > len(all_profiles):
            print_error("Invalid selection.")
            return False

        # Get selected profile
        org, name = all_profiles[selection-1]

        # Confirm removal
        if not confirm(f"Are you sure you want to remove profile: {name}" + (f" ({org})" if org else "") + "?", default=False):
            print_info("Operation cancelled.")
            return False

        # Remove profile
        if remove_profile_storage(name, org):
            print_success(f"Profile removed: {name}" + (f" ({org})" if org else ""))
            return True
        else:
            print_error("Failed to remove profile.")
            return False

    except ValueError:
        print_error("Invalid selection. Please enter a number.")
        return False
