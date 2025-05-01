"""
Report generation and management for Databricks security scans
"""

import json
import datetime
import os
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.markdown import Markdown

# Adicionar o diretório raiz ao path para permitir importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.resources import (
    enumerate_users, enumerate_groups, enumerate_clusters, enumerate_jobs,
    enumerate_secret_scopes, enumerate_secrets, enumerate_warehouses,
    enumerate_external_locations, format_resource_table
)
from core.auth import validate_credentials, get_workspace_url
from utils.discord import send_discord_notification, send_scan_notification, send_validation_notification
from utils.storage import export_file, save_scan_result
from utils.ui import print_success, print_error, print_warning, print_info, create_table

console = Console()

def generate_and_send_report(workspace, apikey, output=None, notify=None, scan_data=None):
    """
    Generate a comprehensive report for a Databricks workspace and optionally send notifications

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key
        output (str, optional): Output file path
        notify (str, optional): Notification method (discord)
        scan_data (dict, optional): Existing scan data to use instead of fetching new data

    Returns:
        dict: Report data
    """
    print_info(f"Generating report for workspace: {workspace}")

    # If no scan data provided, fetch it
    if not scan_data:
        # Validate credentials first
        user_info = validate_credentials(workspace, apikey)
        if not user_info:
            print_error("Failed to validate credentials. Report cannot be generated.")
            return None

        # Fetch basic information
        print_info("Fetching workspace information...")
        warehouses = enumerate_warehouses(workspace, apikey)

        # Fetch secret scopes and secrets
        print_info("Fetching secret scopes and secrets...")
        scopes = enumerate_secret_scopes(workspace, apikey)
        secrets_by_scope = {}

        if scopes:
            for scope in scopes:
                scope_name = scope.get("name")
                if scope_name:
                    secrets = enumerate_secrets(workspace, apikey, scope_name)
                    if secrets:
                        secrets_by_scope[scope_name] = secrets

        # Fetch clusters
        print_info("Fetching clusters...")
        clusters = enumerate_clusters(workspace, apikey)

        # Fetch users and groups
        print_info("Fetching users and groups...")
        users = enumerate_users(workspace, apikey)
        groups = enumerate_groups(workspace, apikey)

        # Build report data
        report_data = {
            "workspace": workspace,
            "timestamp": datetime.datetime.now().isoformat(),
            "user_info": user_info,
            "warehouse_info": warehouses or [],
            "scopes_and_secrets": secrets_by_scope,
            "clusters": clusters or [],
            "users": users or [],
            "groups": groups or []
        }
    else:
        # Use provided scan data
        report_data = {
            "workspace": workspace,
            "timestamp": datetime.datetime.now().isoformat(),
            "user_info": scan_data.get("user_info", {}),
            "warehouse_info": scan_data.get("resources", {}).get("warehouses", []),
            "scopes_and_secrets": scan_data.get("resources", {}).get("secrets", {}),
            "clusters": scan_data.get("resources", {}).get("clusters", []),
            "users": scan_data.get("resources", {}).get("users", []),
            "groups": scan_data.get("resources", {}).get("groups", []),
            "external_locations": scan_data.get("resources", {}).get("external_locations", []),
            "catalogs": scan_data.get("resources", {}).get("catalogs", [])
        }

    # Add security findings
    report_data["findings"] = generate_security_findings(report_data)

    # Save report to file if requested
    if output:
        if not output.endswith('.json'):
            output += '.json'

        export_path = export_file(report_data, "report", "json")
        if export_path:
            print_success(f"Report saved to: {export_path}")
        else:
            print_error("Failed to save report to file.")

    # Send notification if requested
    if notify:
        if notify.lower() == "discord":
            success = send_scan_notification(report_data)
            if success:
                print_success("Report notification sent to Discord.")
            else:
                print_error("Failed to send report notification to Discord.")

    # Save report to history
    save_scan_result(report_data, "report", workspace)

    return report_data

def generate_security_findings(report_data):
    """
    Generate security findings based on scan data

    Args:
        report_data (dict): Report data

    Returns:
        list: Security findings
    """
    findings = []

    # Check for public clusters
    clusters = report_data.get("clusters", [])
    for cluster in clusters:
        if cluster.get("enable_elastic_disk", False) and not cluster.get("single_user_name"):
            findings.append({
                "title": "Public cluster with elastic disk enabled",
                "description": f"Cluster '{cluster.get('cluster_name')}' has elastic disk enabled and is not assigned to a single user.",
                "severity": "medium",
                "resource_type": "cluster",
                "resource_id": cluster.get("cluster_id"),
                "recommendation": "Assign the cluster to a specific user or disable elastic disk."
            })

    # Check for exposed secrets
    scopes = report_data.get("scopes_and_secrets", {})
    for scope_name, secrets in scopes.items():
        if len(secrets) > 0:
            findings.append({
                "title": f"Secret scope '{scope_name}' contains {len(secrets)} secrets",
                "description": f"Secret scope '{scope_name}' contains {len(secrets)} secrets that could be exposed.",
                "severity": "info",
                "resource_type": "secret_scope",
                "resource_id": scope_name,
                "recommendation": "Review access permissions for this secret scope."
            })

    # Check for external locations
    external_locations = report_data.get("external_locations", [])
    for location in external_locations:
        findings.append({
            "title": f"External location '{location.get('name')}' configured",
            "description": f"External location points to {location.get('url')}",
            "severity": "info",
            "resource_type": "external_location",
            "resource_id": location.get("name"),
            "recommendation": "Verify that this external location is properly secured."
        })

    # Check for admin users
    users = report_data.get("users", [])
    admin_users = []
    for user in users:
        groups = user.get("groups", [])
        if "admins" in groups:
            admin_users.append(user.get("userName"))

    if len(admin_users) > 3:
        findings.append({
            "title": "High number of admin users",
            "description": f"There are {len(admin_users)} users with admin privileges.",
            "severity": "medium",
            "resource_type": "users",
            "resource_id": "admins",
            "recommendation": "Review admin access and reduce the number of admin users."
        })

    return findings

def display_report(report_data):
    """
    Display a formatted report in the console

    Args:
        report_data (dict): Report data
    """
    if not report_data:
        print_error("No report data to display.")
        return

    workspace = report_data.get("workspace", "Unknown")
    timestamp = report_data.get("timestamp", "Unknown")

    # Create header
    header_text = f"""
[bold cyan]Workspace:[/bold cyan] {workspace}
[bold cyan]Report Time:[/bold cyan] {timestamp}
"""

    header = Panel(
        header_text,
        title="[bold]Databricks Security Report[/bold]",
        border_style="blue",
        box=box.ROUNDED
    )

    console.print(header)

    # Display user info
    user_info = report_data.get("user_info")
    if user_info:
        user_table = Table(title="User Information")
        user_table.add_column("Field", style="cyan")
        user_table.add_column("Value", style="green")

        user_table.add_row("Username", user_info.get("userName", "N/A"))
        user_table.add_row("Display Name", user_info.get("displayName", "N/A"))
        user_table.add_row("Email", user_info.get("emails", [{}])[0].get("value", "N/A") if user_info.get("emails") else "N/A")

        console.print(user_table)

    # Display resource summaries
    print_info("Resource Summary:")

    # Users and groups
    users = report_data.get("users", [])
    groups = report_data.get("groups", [])
    console.print(f"• [bold cyan]Users:[/bold cyan] {len(users)}")
    console.print(f"• [bold cyan]Groups:[/bold cyan] {len(groups)}")

    # Clusters
    clusters = report_data.get("clusters", [])
    console.print(f"• [bold cyan]Clusters:[/bold cyan] {len(clusters)}")

    # Warehouses
    warehouses = report_data.get("warehouse_info", [])
    console.print(f"• [bold cyan]SQL Warehouses:[/bold cyan] {len(warehouses)}")

    # Secret scopes
    scopes = report_data.get("scopes_and_secrets", {})
    secret_count = sum(len(secrets) for secrets in scopes.values())
    console.print(f"• [bold cyan]Secret Scopes:[/bold cyan] {len(scopes)} scopes, {secret_count} secrets")

    # External locations
    locations = report_data.get("external_locations", [])
    if locations:
        console.print(f"• [bold cyan]External Locations:[/bold cyan] {len(locations)}")

    # Catalogs
    catalogs = report_data.get("catalogs", [])
    if catalogs:
        console.print(f"• [bold cyan]Catalogs:[/bold cyan] {len(catalogs)}")

    # Display findings
    findings = report_data.get("findings", [])
    if findings:
        findings_table = Table(title=f"Security Findings ({len(findings)})")
        findings_table.add_column("Title", style="cyan")
        findings_table.add_column("Severity", style="magenta")
        findings_table.add_column("Resource Type", style="blue")

        for finding in findings:
            severity_style = "green"
            if finding.get("severity") == "medium":
                severity_style = "yellow"
            elif finding.get("severity") == "high":
                severity_style = "red"

            findings_table.add_row(
                finding.get("title", "Unknown"),
                f"[{severity_style}]{finding.get('severity', 'Unknown')}[/{severity_style}]",
                finding.get("resource_type", "Unknown")
            )

        console.print(findings_table)

    # Offer to show detailed information
    print_info("Use 'show' command to view detailed information about specific resources.")

def generate_markdown_report(report_data, output_file=None):
    """
    Generate a Markdown report from scan data

    Args:
        report_data (dict): Report data
        output_file (str, optional): Output file path

    Returns:
        str: Markdown report content
    """
    if not report_data:
        print_error("No report data to generate Markdown.")
        return None

    workspace = report_data.get("workspace", "Unknown")
    timestamp = report_data.get("timestamp", "Unknown")

    # Create markdown content
    markdown = f"""# Databricks Security Report

## Overview

- **Workspace:** {workspace}
- **Report Time:** {timestamp}

## User Information

"""

    # Add user info
    user_info = report_data.get("user_info")
    if user_info:
        markdown += f"""- **Username:** {user_info.get('userName', 'N/A')}
- **Display Name:** {user_info.get('displayName', 'N/A')}
- **Email:** {user_info.get('emails', [{}])[0].get('value', 'N/A') if user_info.get('emails') else 'N/A'}

"""

    # Add resource summaries
    markdown += "## Resource Summary\n\n"

    # Users and groups
    users = report_data.get("users", [])
    groups = report_data.get("groups", [])
    markdown += f"- **Users:** {len(users)}\n"
    markdown += f"- **Groups:** {len(groups)}\n"

    # Clusters
    clusters = report_data.get("clusters", [])
    markdown += f"- **Clusters:** {len(clusters)}\n"

    # Warehouses
    warehouses = report_data.get("warehouse_info", [])
    markdown += f"- **SQL Warehouses:** {len(warehouses)}\n"

    # Secret scopes
    scopes = report_data.get("scopes_and_secrets", {})
    secret_count = sum(len(secrets) for secrets in scopes.values())
    markdown += f"- **Secret Scopes:** {len(scopes)} scopes, {secret_count} secrets\n"

    # External locations
    locations = report_data.get("external_locations", [])
    if locations:
        markdown += f"- **External Locations:** {len(locations)}\n"

    # Catalogs
    catalogs = report_data.get("catalogs", [])
    if catalogs:
        markdown += f"- **Catalogs:** {len(catalogs)}\n"

    markdown += "\n"

    # Add findings
    findings = report_data.get("findings", [])
    if findings:
        markdown += f"## Security Findings ({len(findings)})\n\n"

        for i, finding in enumerate(findings):
            severity = finding.get("severity", "Unknown")
            markdown += f"### {i+1}. {finding.get('title', 'Unknown')}\n\n"
            markdown += f"- **Severity:** {severity}\n"
            markdown += f"- **Resource Type:** {finding.get('resource_type', 'Unknown')}\n"
            markdown += f"- **Description:** {finding.get('description', 'No description')}\n"
            markdown += f"- **Recommendation:** {finding.get('recommendation', 'No recommendation')}\n\n"

    # Add detailed resource sections
    markdown += "## Detailed Resources\n\n"

    # Add clusters
    if clusters:
        markdown += "### Clusters\n\n"
        markdown += "| Name | ID | State | Creator |\n"
        markdown += "|------|----|---------|---------|\n"

        for cluster in clusters[:10]:  # Limit to 10 for readability
            markdown += f"| {cluster.get('cluster_name', 'N/A')} | {cluster.get('cluster_id', 'N/A')} | {cluster.get('state', 'N/A')} | {cluster.get('creator_user_name', 'N/A')} |\n"

        if len(clusters) > 10:
            markdown += f"\n*...and {len(clusters) - 10} more clusters*\n"

        markdown += "\n"

    # Add warehouses
    if warehouses:
        markdown += "### SQL Warehouses\n\n"
        markdown += "| Name | ID | Size | State |\n"
        markdown += "|------|----|---------|---------|\n"

        for warehouse in warehouses[:10]:  # Limit to 10 for readability
            markdown += f"| {warehouse.get('name', 'N/A')} | {warehouse.get('id', 'N/A')} | {warehouse.get('size', 'N/A')} | {warehouse.get('state', 'N/A')} |\n"

        if len(warehouses) > 10:
            markdown += f"\n*...and {len(warehouses) - 10} more warehouses*\n"

        markdown += "\n"

    # Add secret scopes
    if scopes:
        markdown += "### Secret Scopes\n\n"

        for scope_name, secrets in scopes.items():
            markdown += f"- **{scope_name}**: {len(secrets)} secrets\n"

        markdown += "\n"

    # Save to file if requested
    if output_file:
        if not output_file.endswith('.md'):
            output_file += '.md'

        try:
            with open(output_file, 'w') as f:
                f.write(markdown)
            print_success(f"Markdown report saved to: {output_file}")
        except Exception as e:
            print_error(f"Failed to save Markdown report: {e}")

    return markdown

def validate_and_notify(workspace, apikey, notify=None):
    """
    Validate workspace access and send notification

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key
        notify (str, optional): Notification method (discord)

    Returns:
        dict: Validation results
    """
    print_info(f"Validating access to workspace: {workspace}")

    # Validate credentials
    user_info = validate_credentials(workspace, apikey)

    if not user_info:
        print_error("Invalid credentials or workspace not accessible.")
        result = {
            "workspace": workspace,
            "apikey": apikey,
            "status": "invalid",
            "timestamp": datetime.datetime.now().isoformat()
        }
    else:
        print_success(f"Valid access to workspace: {workspace}")
        print_info(f"Logged in as: {user_info.get('displayName')} ({user_info.get('userName')})")

        result = {
            "workspace": workspace,
            "apikey": apikey,
            "status": "valid",
            "timestamp": datetime.datetime.now().isoformat(),
            "user_info": user_info
        }

    # Send notification if requested
    if notify and notify.lower() == "discord":
        success = send_validation_notification(
            workspace,
            apikey,
            result.get("status"),
            user_info if result.get("status") == "valid" else None
        )

        if success:
            print_success("Validation notification sent to Discord.")
        else:
            print_error("Failed to send validation notification to Discord.")

    # Save validation result
    save_scan_result(result, "validation", workspace)

    return result
