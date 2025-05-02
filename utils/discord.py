"""
Discord notification utilities for BricksXploit
"""

import requests
import datetime
import base64
import os
from rich.console import Console
from .storage import load_config, update_config

console = Console()

# Path to the banner image
BANNER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "banner.txt")

def get_banner_data():
    """
    Get the banner data as a base64 encoded string

    Returns:
        str: Base64 encoded banner data or None if not found
    """
    try:
        # Check if we have a banner.png file in the assets directory
        banner_png = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "banner.png")
        if os.path.exists(banner_png):
            with open(banner_png, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        return None
    except Exception:
        return None

def get_webhook_url():
    """
    Get the Discord webhook URL from configuration

    Returns:
        str: Webhook URL or None if not configured
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
    return update_config("discord_webhook", url)

def send_discord_notification(data, notification_type="report", title=None, message=None):
    """
    Send a notification to Discord

    Args:
        data (dict): Data to include in the notification
        notification_type (str): Type of notification (report, validation, alert)
        title (str, optional): Custom title
        message (str, optional): Custom message

    Returns:
        bool: Success or failure
    """
    webhook_url = get_webhook_url()

    if not webhook_url:
        console.print("[bold red]Discord webhook URL not configured.[/]")
        console.print("[yellow]Use 'config discord' to set up Discord notifications.[/yellow]")
        return False

    # Determine color based on notification type
    colors = {
        "report": 3447003,  # Blue
        "validation": 5763719,  # Green
        "alert": 15548997,  # Red
        "info": 10181046  # Purple
    }
    color = colors.get(notification_type, colors["info"])

    # Create timestamp
    timestamp = datetime.datetime.now().isoformat()

    # Create base payload
    payload = {
        "embeds": [
            {
                "title": title or f"BricksXploit {notification_type.capitalize()}",
                "color": color,
                "timestamp": timestamp,
                "footer": {
                    "text": "BricksXploit - Databricks Security Testing Tool"
                }
            }
        ]
    }

    # Try to add banner image if available
    banner_data = get_banner_data()
    if banner_data:
        # Add image to the first embed
        payload["embeds"][0]["image"] = {
            "url": f"data:image/png;base64,{banner_data}"
        }
    else:
        # If no banner image, try to add ASCII banner from text file
        try:
            if os.path.exists(BANNER_PATH):
                with open(BANNER_PATH, "r") as f:
                    banner_text = f.read()
                    # Add banner as a code block at the beginning of the message
                    if message:
                        message = f"```\n{banner_text}\n```\n\n{message}"
                    else:
                        message = f"```\n{banner_text}\n```"
        except Exception:
            # If banner can't be added, continue without it
            pass

    # Add custom message if provided
    if message:
        payload["content"] = message

    # Add fields based on notification type
    if notification_type == "validation":
        # Validation notification
        workspace = data.get("workspace", "Unknown")
        status = data.get("status", "Unknown")

        payload["embeds"][0]["description"] = f"Validation results for workspace: `{workspace}`"
        payload["embeds"][0]["fields"] = [
            {
                "name": "Status",
                "value": f"{'✅ Valid' if status == 'valid' else '❌ Invalid'}",
                "inline": True
            },
            {
                "name": "API Key",
                "value": f"`{data.get('apikey', 'Unknown')[:10]}...`",
                "inline": True
            }
        ]

        # Add user info if available
        if "user_info" in data and data["user_info"]:
            user_info = data["user_info"]
            payload["embeds"][0]["fields"].append({
                "name": "User",
                "value": f"{user_info.get('displayName', 'Unknown')} ({user_info.get('userName', 'Unknown')})",
                "inline": True
            })

            # Add groups if available
            if "groups" in user_info and user_info["groups"]:
                groups = ", ".join(user_info["groups"][:5])
                if len(user_info["groups"]) > 5:
                    groups += f" and {len(user_info['groups']) - 5} more"

                payload["embeds"][0]["fields"].append({
                    "name": "Groups",
                    "value": groups,
                    "inline": False
                })

    elif notification_type == "report":
        # Full report notification
        workspace = data.get("workspace", "Unknown")

        payload["embeds"][0]["description"] = f"Security scan report for workspace: `{workspace}`"

        # Add summary fields
        fields = []

        # Add user info
        if "user_info" in data:
            user_info = data["user_info"]
            fields.append({
                "name": "User",
                "value": f"{user_info.get('displayName', 'Unknown')} ({user_info.get('userName', 'Unknown')})",
                "inline": True
            })

        # Add warehouses
        if "warehouse_info" in data and data["warehouse_info"]:
            warehouses = data["warehouse_info"]
            warehouse_text = "\n".join([f"• {wh.get('name', 'Unknown')} (ID: {wh.get('id', 'Unknown')})" for wh in warehouses[:5]])

            if len(warehouses) > 5:
                warehouse_text += f"\n• ... and {len(warehouses) - 5} more"

            fields.append({
                "name": f"SQL Warehouses ({len(warehouses)})",
                "value": warehouse_text or "None found",
                "inline": False
            })

        # Add scopes and secrets
        if "scopes_and_secrets" in data and data["scopes_and_secrets"]:
            scopes = data["scopes_and_secrets"]
            scope_text = "\n".join([f"• {scope}: {len(secrets)} secrets" for scope, secrets in list(scopes.items())[:5]])

            if len(scopes) > 5:
                scope_text += f"\n• ... and {len(scopes) - 5} more scopes"

            fields.append({
                "name": f"Secret Scopes ({len(scopes)})",
                "value": scope_text or "None found",
                "inline": False
            })

        # Add clusters
        if "clusters" in data and data["clusters"]:
            clusters = data["clusters"]
            cluster_text = "\n".join([f"• {cluster.get('cluster_name', 'Unknown')} ({cluster.get('state', 'Unknown')})" for cluster in clusters[:5]])

            if len(clusters) > 5:
                cluster_text += f"\n• ... and {len(clusters) - 5} more"

            fields.append({
                "name": f"Clusters ({len(clusters)})",
                "value": cluster_text or "None found",
                "inline": False
            })

        # Add catalogs
        if "catalogs" in data and data["catalogs"]:
            catalogs = data["catalogs"]
            catalog_text = "\n".join([f"• {catalog.get('name', 'Unknown')}" for catalog in catalogs[:5]])

            if len(catalogs) > 5:
                catalog_text += f"\n• ... and {len(catalogs) - 5} more"

            fields.append({
                "name": f"Catalogs ({len(catalogs)})",
                "value": catalog_text or "None found",
                "inline": False
            })

        # Add external locations
        if "external_locations" in data and data["external_locations"]:
            locations = data["external_locations"]
            location_text = "\n".join([f"• {loc.get('name', 'Unknown')}: {loc.get('url', 'Unknown')}" for loc in locations[:5]])

            if len(locations) > 5:
                location_text += f"\n• ... and {len(locations) - 5} more"

            fields.append({
                "name": f"External Locations ({len(locations)})",
                "value": location_text or "None found",
                "inline": False
            })

        # Add findings or issues if available
        if "findings" in data and data["findings"]:
            findings = data["findings"]
            finding_text = "\n".join([f"• {finding.get('title', 'Unknown')}: {finding.get('severity', 'Unknown')}" for finding in findings[:5]])

            if len(findings) > 5:
                finding_text += f"\n• ... and {len(findings) - 5} more"

            fields.append({
                "name": f"Security Findings ({len(findings)})",
                "value": finding_text or "None found",
                "inline": False
            })

        payload["embeds"][0]["fields"] = fields

    elif notification_type == "alert":
        # Alert notification
        workspace = data.get("workspace", "Unknown")
        alert_type = data.get("alert_type", "Unknown")

        payload["embeds"][0]["description"] = f"⚠️ Security alert for workspace: `{workspace}`"
        payload["embeds"][0]["fields"] = [
            {
                "name": "Alert Type",
                "value": alert_type,
                "inline": True
            },
            {
                "name": "Severity",
                "value": data.get("severity", "Unknown"),
                "inline": True
            },
            {
                "name": "Details",
                "value": data.get("details", "No details provided"),
                "inline": False
            }
        ]

    # Send the notification
    try:
        response = requests.post(webhook_url, json=payload)

        if response.status_code == 204:
            console.print(f"[bold green]Notification sent to Discord successfully![/]")
            return True
        else:
            console.print(f"[bold red]Failed to send notification to Discord. Status code: {response.status_code}[/]")
            return False

    except Exception as e:
        console.print(f"[bold red]Error sending Discord notification: {e}[/]")
        return False

def send_validation_notification(workspace, apikey, status, user_info=None):
    """
    Send a validation notification to Discord

    Args:
        workspace (str): Workspace name
        apikey (str): API key
        status (str): Validation status (valid, invalid)
        user_info (dict, optional): User information

    Returns:
        bool: Success or failure
    """
    data = {
        "workspace": workspace,
        "apikey": apikey,
        "status": status,
        "user_info": user_info
    }

    return send_discord_notification(
        data,
        notification_type="validation",
        title="Databricks Credentials Validation",
        message=f"BricksXploit validation result for `{workspace}`: **{'Valid' if status == 'valid' else 'Invalid'}**"
    )

def send_scan_notification(report_data, file_path=None):
    """
    Send a scan report notification to Discord with file information

    Args:
        report_data (dict): Report data
        file_path (str, optional): Path to the exported file

    Returns:
        bool: Success or failure
    """
    workspace = report_data.get("workspace", "Unknown")
    scan_time = report_data.get("timestamp", "Unknown")

    # Create a more detailed message with better formatting
    message = f"# BricksXploit Security Scan Report\n\n"
    message += f"## Workspace: `{workspace}`\n\n"

    # Add scan type if available
    scan_type = "Unknown"
    if "scan_type" in report_data:
        scan_type = report_data.get("scan_type", "").replace("_", " ").title()
    else:
        # Try to determine scan type from resources
        resources = report_data.get("resources", {})
        if "users" in resources and "groups" in resources and not "catalogs" in resources:
            scan_type = "Users & Permissions"
        elif "catalogs" in resources and "schemas" in resources:
            scan_type = "Catalogs & Schemas"
        elif "secret_scopes" in resources:
            scan_type = "Secret Scopes"
        elif "warehouses" in resources:
            scan_type = "SQL Warehouses"
        elif len(resources.keys()) > 3:
            scan_type = "Full Workspace"

    message += f"**Scan Type:** {scan_type}\n"
    message += f"**Scan Time:** {scan_time}\n"

    # Add file information if available
    if file_path:
        message += f"**Report File:** `{file_path}`\n\n"
    else:
        message += "\n"

    # Add summary counts in a more organized format
    resources = report_data.get("resources", {})
    if resources:
        message += "## Resource Summary\n\n"

        # Create a table-like format for resource counts
        message += "| Resource Type | Count |\n"
        message += "|---------------|-------|\n"

        # Add users and groups
        if "users" in resources:
            message += f"| Users | {len(resources['users'])} |\n"
        if "groups" in resources:
            message += f"| Groups | {len(resources['groups'])} |\n"

        # Add catalogs and schemas
        if "catalogs" in resources:
            message += f"| Catalogs | {len(resources['catalogs'])} |\n"
        if "schemas" in resources:
            message += f"| Schemas | {len(resources['schemas'])} |\n"

        # Add secret scopes
        if "secret_scopes" in resources:
            message += f"| Secret Scopes | {len(resources['secret_scopes'])} |\n"

        # Add SQL warehouses
        if "warehouses" in resources:
            message += f"| SQL Warehouses | {len(resources['warehouses'])} |\n"

        message += "\n"

        # Add sample data for each resource type
        if "users" in resources and resources["users"]:
            message += "## Sample Users\n\n"
            sample_users = resources["users"][:5]
            for user in sample_users:
                if isinstance(user, dict):
                    message += f"- {user.get('display_name', 'Unknown')} ({user.get('user_name', 'Unknown')})\n"
                else:
                    # Handle different user object formats
                    try:
                        message += f"- {getattr(user, 'display_name', 'Unknown')} ({getattr(user, 'user_name', 'Unknown')})\n"
                    except:
                        message += f"- {str(user)}\n"

            if len(resources["users"]) > 5:
                message += f"... and {len(resources['users']) - 5} more users\n"
            message += "\n"

        # Add sample catalogs if available
        if "catalogs" in resources and resources["catalogs"]:
            message += "## Sample Catalogs\n\n"
            sample_catalogs = resources["catalogs"][:5]
            for catalog in sample_catalogs:
                if isinstance(catalog, dict):
                    message += f"- {catalog.get('name', 'Unknown')}\n"
                else:
                    # Handle different catalog object formats
                    try:
                        message += f"- {getattr(catalog, 'name', 'Unknown')}\n"
                    except:
                        message += f"- {str(catalog)}\n"

            if len(resources["catalogs"]) > 5:
                message += f"... and {len(resources['catalogs']) - 5} more catalogs\n"
            message += "\n"

    # Add a footer with tool information
    message += "---\n"
    message += "*Generated by BricksXploit - Databricks Security Testing Tool*"

    return send_discord_notification(
        report_data,
        notification_type="report",
        title=f"Databricks Security Scan Report - {scan_type}",
        message=message
    )

def send_alert_notification(workspace, alert_type, severity, details):
    """
    Send an alert notification to Discord

    Args:
        workspace (str): Workspace name
        alert_type (str): Type of alert
        severity (str): Alert severity (low, medium, high, critical)
        details (str): Alert details

    Returns:
        bool: Success or failure
    """
    data = {
        "workspace": workspace,
        "alert_type": alert_type,
        "severity": severity,
        "details": details
    }

    return send_discord_notification(
        data,
        notification_type="alert",
        title=f"Databricks Security Alert - {severity.upper()}",
        message=f"⚠️ BricksXploit detected a {severity} security issue in `{workspace}`"
    )
