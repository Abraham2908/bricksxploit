"""
Export functionality for BricksXploit
"""

import json
import csv
import os
import sys
import datetime
from rich.console import Console

# Adicionar o diretório raiz ao path para permitir importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.storage import export_file
from utils.ui import print_success, print_error, print_info

console = Console()

def export_scan_results(scan_results, format="json", output_file=None):
    """
    Export scan results to a file

    Args:
        scan_results (dict): Scan results to export
        format (str): Export format (json, csv)
        output_file (str, optional): Output file path

    Returns:
        str: Path to exported file or None if failed
    """
    if not scan_results:
        print_error("No scan results to export.")
        return None

    # Generate default filename if not provided
    if not output_file:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        workspace = scan_results.get("workspace", "unknown")
        output_file = f"bricksxploit_scan_{workspace}_{timestamp}"

    # Export based on format
    if format.lower() == "json":
        return export_json(scan_results, output_file)
    elif format.lower() == "csv":
        return export_csv(scan_results, output_file)
    else:
        print_error(f"Unsupported export format: {format}")
        return None

def export_json(data, output_file):
    """
    Export data to JSON file

    Args:
        data (dict): Data to export
        output_file (str): Output file path

    Returns:
        str: Path to exported file or None if failed
    """
    # Ensure file has .json extension
    if not output_file.lower().endswith(".json"):
        output_file += ".json"

    try:
        export_path = export_file(data, output_file, "json")
        if export_path:
            print_success(f"Data exported to JSON: {export_path}")
            return export_path
        else:
            print_error("Failed to export data to JSON.")
            return None
    except Exception as e:
        print_error(f"Error exporting to JSON: {e}")
        return None

def export_csv(data, output_file):
    """
    Export data to CSV file

    Args:
        data (dict): Data to export
        output_file (str): Output file path

    Returns:
        str: Path to exported file or None if failed
    """
    # Ensure file has .csv extension
    if not output_file.lower().endswith(".csv"):
        output_file += ".csv"

    try:
        # Flatten the data structure for CSV export
        flattened_data = flatten_data(data)

        # Write to CSV file
        with open(output_file, "w", newline="") as csvfile:
            if not flattened_data:
                print_error("No data to export to CSV.")
                return None

            # Get field names from first item
            fieldnames = flattened_data[0].keys()

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in flattened_data:
                writer.writerow(row)

        print_success(f"Data exported to CSV: {output_file}")
        return output_file
    except Exception as e:
        print_error(f"Error exporting to CSV: {e}")
        return None

def flatten_data(data):
    """
    Flatten nested data structure for CSV export

    Args:
        data (dict): Data to flatten

    Returns:
        list: List of flattened dictionaries
    """
    flattened = []

    # Handle different resource types
    if "resources" in data:
        resources = data["resources"]

        # Process users
        if "users" in resources:
            for user in resources["users"]:
                flat_user = {
                    "resource_type": "user",
                    "id": user.get("id"),
                    "username": user.get("userName"),
                    "display_name": user.get("displayName"),
                    "active": user.get("active"),
                    "email": user.get("emails", [{}])[0].get("value") if user.get("emails") else None
                }
                flattened.append(flat_user)

        # Process groups
        if "groups" in resources:
            for group in resources["groups"]:
                flat_group = {
                    "resource_type": "group",
                    "id": group.get("id"),
                    "display_name": group.get("displayName"),
                    "member_count": len(group.get("members", []))
                }
                flattened.append(flat_group)

        # Process clusters
        if "clusters" in resources:
            for cluster in resources["clusters"]:
                flat_cluster = {
                    "resource_type": "cluster",
                    "id": cluster.get("cluster_id"),
                    "name": cluster.get("cluster_name"),
                    "state": cluster.get("state"),
                    "creator": cluster.get("creator_user_name")
                }
                flattened.append(flat_cluster)

        # Process warehouses
        if "warehouses" in resources:
            for warehouse in resources["warehouses"]:
                flat_warehouse = {
                    "resource_type": "warehouse",
                    "id": warehouse.get("id"),
                    "name": warehouse.get("name"),
                    "size": warehouse.get("size"),
                    "state": warehouse.get("state")
                }
                flattened.append(flat_warehouse)

        # Process secret scopes
        if "secret_scopes" in resources:
            for scope in resources["secret_scopes"]:
                flat_scope = {
                    "resource_type": "secret_scope",
                    "name": scope.get("name"),
                    "backend_type": scope.get("backend_type")
                }
                flattened.append(flat_scope)

        # Process external locations
        if "external_locations" in resources:
            for location in resources["external_locations"]:
                flat_location = {
                    "resource_type": "external_location",
                    "name": location.get("name"),
                    "url": location.get("url"),
                    "owner": location.get("owner")
                }
                flattened.append(flat_location)

    # If no resources found, try to flatten the top-level data
    if not flattened and isinstance(data, dict):
        # Try to extract basic information
        flat_data = {
            "workspace": data.get("workspace"),
            "timestamp": data.get("timestamp")
        }

        # Add other top-level fields
        for key, value in data.items():
            if key not in ["resources", "workspace", "timestamp"] and not isinstance(value, (dict, list)):
                flat_data[key] = value

        flattened.append(flat_data)

    return flattened

def export_user_info(user_info, output_file=None):
    """
    Export user information to a file

    Args:
        user_info (dict): User information to export
        output_file (str, optional): Output file path

    Returns:
        str: Path to exported file or None if failed
    """
    if not user_info:
        print_error("No user information to export.")
        return None

    # Generate default filename if not provided
    if not output_file:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        username = user_info.get("userName", "unknown")
        output_file = f"bricksxploit_user_{username}_{timestamp}.json"

    # Export to JSON
    try:
        with open(output_file, "w") as f:
            json.dump(user_info, f, indent=4)

        print_success(f"User information exported to: {output_file}")
        return output_file
    except Exception as e:
        print_error(f"Error exporting user information: {e}")
        return None

def export_report(report_data, format="json", output_file=None):
    """
    Export report to a file

    Args:
        report_data (dict): Report data to export
        format (str): Export format (json, csv, markdown)
        output_file (str, optional): Output file path

    Returns:
        str: Path to exported file or None if failed
    """
    if not report_data:
        print_error("No report data to export.")
        return None

    # Generate default filename if not provided
    if not output_file:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        workspace = report_data.get("workspace", "unknown")
        output_file = f"bricksxploit_report_{workspace}_{timestamp}"

    # Export based on format
    if format.lower() == "json":
        return export_json(report_data, output_file)
    elif format.lower() == "csv":
        return export_csv(report_data, output_file)
    elif format.lower() == "markdown" or format.lower() == "md":
        # Markdown export is handled by the report module
        from .report import generate_markdown_report
        return generate_markdown_report(report_data, output_file)
    else:
        print_error(f"Unsupported export format: {format}")
        return None
