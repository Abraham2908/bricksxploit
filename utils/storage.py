"""
Storage utilities for BricksXploit configuration and profiles
"""

import json
import os
from pathlib import Path
from rich.console import Console
import datetime
import shutil

console = Console()

# Configuration files
CONFIG_DIR = Path.home() / ".bricksxploit"
CONFIG_FILE = CONFIG_DIR / "config.json"
PROFILES_FILE = CONFIG_DIR / "profiles.json"
HISTORY_DIR = CONFIG_DIR / "history"

# Default configuration
DEFAULT_CONFIG = {
    "version": "1.0.0",
    "current_profile": None,
    "current_organization": None,
    "discord_webhook": None,
    "export_dir": str(Path.home() / "bricksxploit_exports"),
    "theme": "default",
    "debug_mode": False,
    "auto_save_results": True,
    "max_history_items": 50
}

# Default profiles structure
DEFAULT_PROFILES = {
    "organizations": {},
    "default": {}
}

def ensure_config_dir():
    """
    Ensure the configuration directory exists
    """
    CONFIG_DIR.mkdir(exist_ok=True)
    HISTORY_DIR.mkdir(exist_ok=True)

    # Create export directory
    export_dir = Path(DEFAULT_CONFIG["export_dir"])
    export_dir.mkdir(exist_ok=True)

    return CONFIG_DIR

def load_config():
    """
    Load configuration, creating default if it doesn't exist
    """
    # Make sure directories exist first
    CONFIG_DIR.mkdir(exist_ok=True)
    HISTORY_DIR.mkdir(exist_ok=True)

    if not CONFIG_FILE.exists():
        # File doesn't exist, initialize with default config
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        console.print("[yellow]Configuration file not found, creating default.[/yellow]")
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)

        # Update with any missing default keys
        updated = False
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
                updated = True

        if updated:
            save_config(config)

        return config
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        console.print("[yellow]Using default configuration.[/yellow]")
        return DEFAULT_CONFIG

def save_config(config):
    """
    Save configuration to file
    """
    # Make sure directory exists
    CONFIG_DIR.mkdir(exist_ok=True)

    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        console.print(f"[red]Error saving configuration: {e}[/red]")
        return False

def update_config(key, value):
    """
    Update a specific configuration value
    """
    config = load_config()
    config[key] = value
    return save_config(config)

def load_profiles():
    """
    Load profiles, creating default if it doesn't exist
    """
    # Make sure directory exists
    CONFIG_DIR.mkdir(exist_ok=True)

    if not PROFILES_FILE.exists():
        # File doesn't exist, initialize with empty profiles
        with open(PROFILES_FILE, "w") as f:
            json.dump(DEFAULT_PROFILES, f, indent=4)
        console.print("[yellow]Profiles file not found, creating empty profiles.[/yellow]")
        return DEFAULT_PROFILES.copy()

    try:
        with open(PROFILES_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]Error loading profiles: {e}[/red]")
        console.print("[yellow]Using empty profiles.[/yellow]")
        return DEFAULT_PROFILES

def save_profiles(profiles):
    """
    Save profiles to file
    """
    # Make sure directory exists
    CONFIG_DIR.mkdir(exist_ok=True)

    try:
        with open(PROFILES_FILE, "w") as f:
            json.dump(profiles, f, indent=4)
        return True
    except Exception as e:
        console.print(f"[red]Error saving profiles: {e}[/red]")
        return False

def get_current_profile():
    """
    Get the currently active profile

    Returns:
        tuple: (organization, profile_name, profile_data) or (None, None, None) if no active profile
    """
    config = load_config()
    profiles = load_profiles()

    current_org = config.get("current_organization")
    current_profile = config.get("current_profile")

    if not current_profile:
        return None, None, None

    if current_org and current_org in profiles["organizations"]:
        if current_profile in profiles["organizations"][current_org]:
            return current_org, current_profile, profiles["organizations"][current_org][current_profile]

    # Try default profiles
    if current_profile in profiles["default"]:
        return None, current_profile, profiles["default"][current_profile]

    return None, None, None

def set_current_profile(organization, profile_name):
    """
    Set the current active profile

    Args:
        organization (str): Organization name or None for default
        profile_name (str): Profile name

    Returns:
        bool: Success or failure
    """
    config = load_config()
    profiles = load_profiles()

    # Verify profile exists
    if organization and organization in profiles["organizations"]:
        if profile_name in profiles["organizations"][organization]:
            config["current_organization"] = organization
            config["current_profile"] = profile_name
            return save_config(config)
    elif profile_name in profiles["default"]:
        config["current_organization"] = None
        config["current_profile"] = profile_name
        return save_config(config)

    return False

def add_profile(workspace, apikey, display_name=None, organization=None, metadata=None, profile_name=None):
    """
    Add a new profile

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key
        display_name (str, optional): Display name for the profile
        organization (str, optional): Organization name
        metadata (dict, optional): Additional metadata
        profile_name (str, optional): Custom profile name (defaults to workspace)

    Returns:
        bool: Success or failure
    """
    profiles = load_profiles()

    # Use provided profile name or default to workspace
    final_profile_name = profile_name if profile_name else workspace

    # Create profile data
    profile_data = {
        "workspace": workspace,
        "apikey": apikey,
        "display_name": display_name or workspace,
        "created_at": datetime.datetime.now().isoformat(),
        "last_used": None,
        "metadata": metadata or {}
    }

    # Add to appropriate section
    if organization:
        if organization not in profiles["organizations"]:
            profiles["organizations"][organization] = {}

        profiles["organizations"][organization][final_profile_name] = profile_data
    else:
        profiles["default"][final_profile_name] = profile_data

    return save_profiles(profiles)

def remove_profile(profile_name, organization=None):
    """
    Remove a profile

    Args:
        profile_name (str): Profile name
        organization (str, optional): Organization name

    Returns:
        bool: Success or failure
    """
    profiles = load_profiles()
    config = load_config()

    # Remove from appropriate section
    if organization and organization in profiles["organizations"]:
        if profile_name in profiles["organizations"][organization]:
            del profiles["organizations"][organization][profile_name]

            # If this was the current profile, reset current profile
            if (config.get("current_organization") == organization and
                config.get("current_profile") == profile_name):
                config["current_organization"] = None
                config["current_profile"] = None
                save_config(config)

            return save_profiles(profiles)
    elif profile_name in profiles["default"]:
        del profiles["default"][profile_name]

        # If this was the current profile, reset current profile
        if (config.get("current_organization") is None and
            config.get("current_profile") == profile_name):
            config["current_profile"] = None
            save_config(config)

        return save_profiles(profiles)

    return False

def update_profile_metadata(profile_name, metadata, organization=None):
    """
    Update profile metadata

    Args:
        profile_name (str): Profile name
        metadata (dict): Metadata to update
        organization (str, optional): Organization name

    Returns:
        bool: Success or failure
    """
    profiles = load_profiles()

    # Update appropriate profile
    if organization and organization in profiles["organizations"]:
        if profile_name in profiles["organizations"][organization]:
            profiles["organizations"][organization][profile_name]["metadata"].update(metadata)
            return save_profiles(profiles)
    elif profile_name in profiles["default"]:
        profiles["default"][profile_name]["metadata"].update(metadata)
        return save_profiles(profiles)

    return False

def save_scan_result(result, scan_type, workspace):
    """
    Save scan result to history

    Args:
        result (dict): Scan result data
        scan_type (str): Type of scan
        workspace (str): Workspace name

    Returns:
        str: Path to saved file
    """
    # Make sure directories exist
    CONFIG_DIR.mkdir(exist_ok=True)
    HISTORY_DIR.mkdir(exist_ok=True)

    # Create timestamp and filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{scan_type}_{workspace}_{timestamp}.json"
    filepath = HISTORY_DIR / filename

    # Add metadata
    result_with_meta = {
        "timestamp": timestamp,
        "scan_type": scan_type,
        "workspace": workspace,
        "data": result
    }

    # Save to file
    try:
        with open(filepath, "w") as f:
            json.dump(result_with_meta, f, indent=4)

        # Cleanup old history if needed
        cleanup_history()

        return str(filepath)
    except Exception as e:
        console.print(f"[red]Error saving scan result: {e}[/red]")
        return None

def list_scan_history(limit=10):
    """
    List scan history

    Args:
        limit (int): Maximum number of items to return

    Returns:
        list: List of history items
    """
    # Make sure directories exist
    CONFIG_DIR.mkdir(exist_ok=True)
    HISTORY_DIR.mkdir(exist_ok=True)

    history_files = list(HISTORY_DIR.glob("*.json"))
    history_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    history = []
    for file in history_files[:limit]:
        try:
            with open(file, "r") as f:
                data = json.load(f)
                history.append({
                    "filename": file.name,
                    "timestamp": data.get("timestamp"),
                    "scan_type": data.get("scan_type"),
                    "workspace": data.get("workspace")
                })
        except Exception:
            # Skip files that can't be loaded
            pass

    return history

def load_scan_result(filename):
    """
    Load a scan result from history

    Args:
        filename (str): Filename of the scan result

    Returns:
        dict: Scan result data
    """
    filepath = HISTORY_DIR / filename

    if not filepath.exists():
        console.print(f"[red]Scan result file not found: {filename}[/red]")
        return None

    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]Error loading scan result: {e}[/red]")
        return None

def cleanup_history():
    """
    Clean up old history files
    """
    config = load_config()
    max_items = config.get("max_history_items", DEFAULT_CONFIG["max_history_items"])

    history_files = list(HISTORY_DIR.glob("*.json"))
    history_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    # Remove old files
    for file in history_files[max_items:]:
        try:
            file.unlink()
        except Exception:
            # Ignore errors
            pass

def save_scan_result(data, scan_type, workspace):
    """
    Save scan result to history

    Args:
        data (dict): Scan data
        scan_type (str): Type of scan
        workspace (str): Workspace name

    Returns:
        str: Path to saved file
    """
    # Make sure directory exists
    HISTORY_DIR.mkdir(exist_ok=True)

    # Generate filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{scan_type}_{workspace}_{timestamp}.json"
    filepath = HISTORY_DIR / filename

    try:
        # Add metadata
        data["scan_type"] = scan_type
        data["workspace"] = workspace
        data["timestamp"] = timestamp

        # Save to file
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)

        return str(filepath)
    except Exception as e:
        console.print(f"[red]Error saving scan result: {e}[/red]")
        return None

def list_scan_results():
    """
    List all scan results in history

    Returns:
        list: List of scan result metadata
    """
    # Make sure directory exists
    HISTORY_DIR.mkdir(exist_ok=True)

    # Get all scan result files
    history_files = list(HISTORY_DIR.glob("*.json"))
    history_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    # Load metadata from each file
    results = []
    for file in history_files:
        try:
            with open(file, "r") as f:
                data = json.load(f)
                results.append(data)
        except Exception as e:
            console.print(f"[red]Error loading scan result {file}: {e}[/red]")

    return results

def export_file(data, filename, format="json"):
    """
    Export data to a file

    Args:
        data: Data to export
        filename (str): Filename
        format (str): Export format (json, csv)

    Returns:
        str: Path to exported file
    """
    config = load_config()
    export_dir = Path(config.get("export_dir", DEFAULT_CONFIG["export_dir"]))
    export_dir.mkdir(exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename}_{timestamp}.{format}"
    filepath = export_dir / filename

    try:
        if format == "json":
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)
        elif format == "csv":
            # CSV export handled by specific export functions
            pass
        else:
            console.print(f"[red]Unsupported export format: {format}[/red]")
            return None

        return str(filepath)
    except Exception as e:
        console.print(f"[red]Error exporting data: {e}[/red]")
        return None

def get_webhook_url():
    """
    Get the Discord webhook URL from configuration

    Returns:
        str: Webhook URL or None if not set
    """
    config = load_config()
    return config.get("discord_webhook")

def set_webhook_url(url):
    """
    Set the Discord webhook URL in configuration

    Args:
        url (str): Webhook URL

    Returns:
        bool: Success or failure
    """
    config = load_config()
    config["discord_webhook"] = url
    return save_config(config)

def backup_config():
    """
    Create a backup of configuration files

    Returns:
        str: Path to backup directory
    """
    # Make sure directories exist
    CONFIG_DIR.mkdir(exist_ok=True)
    HISTORY_DIR.mkdir(exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = CONFIG_DIR / f"backup_{timestamp}"
    backup_dir.mkdir(exist_ok=True)

    try:
        if CONFIG_FILE.exists():
            shutil.copy2(CONFIG_FILE, backup_dir / CONFIG_FILE.name)

        if PROFILES_FILE.exists():
            shutil.copy2(PROFILES_FILE, backup_dir / PROFILES_FILE.name)

        return str(backup_dir)
    except Exception as e:
        console.print(f"[red]Error creating backup: {e}[/red]")
        return None
