"""
Scanning functionality for Databricks resources
"""

import requests
import json
import time
import datetime
import sys
import os
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, BarColumn
from rich.panel import Panel
from rich import box

# Adicionar o diretório raiz ao path para permitir importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.auth import validate_credentials
from core.resources import (
    enumerate_users, enumerate_groups, enumerate_clusters, enumerate_jobs,
    enumerate_secret_scopes, enumerate_secrets, enumerate_instance_pools,
    enumerate_warehouses, enumerate_external_locations, enumerate_metastores,
    enumerate_tokens, enumerate_acls, enumerate_all_resources, format_resource_table
)
from core.sql import execute_sql_statement, format_sql_results, get_catalogs, get_schemas, get_tables
from utils.storage import save_scan_result
from utils.ui import print_success, print_error, print_warning, print_info, progress_spinner, progress_bar

console = Console()

def run_full_scan(workspace, profile_data):
    """
    Run a comprehensive scan of the Databricks workspace

    Args:
        workspace (str): Databricks workspace
        profile_data (dict): Profile data with API key

    Returns:
        dict: Scan results
    """
    try:
        apikey = profile_data.get("apikey")

        if not apikey:
            print_error("API key not found in profile data")
            return None

        # Validate credentials
        print_info(f"Validating credentials for workspace: {workspace}")
        user_info = validate_credentials(workspace, apikey)

        if not user_info:
            print_error("Failed to validate credentials. Scan cannot proceed.")
            return None

        print_success(f"Credentials validated successfully! Starting full scan...")

        # Create progress bar for overall scan
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            scan_task = progress.add_task("Running full security scan...", total=100)

            # Initialize scan results
            scan_results = {
                "workspace": workspace,
                "scan_time": datetime.datetime.now().isoformat(),
                "user_info": user_info,
                "resources": {}
            }

            # Scan users and groups (10%)
            progress.update(scan_task, advance=5, description="Scanning users and groups...")
            users = enumerate_users(workspace, apikey)
            if users:
                scan_results["resources"]["users"] = users

            groups = enumerate_groups(workspace, apikey)
            if groups:
                scan_results["resources"]["groups"] = groups

            progress.update(scan_task, advance=5)

            # Scan clusters and jobs (10%)
            progress.update(scan_task, description="Scanning compute resources...")
            clusters = enumerate_clusters(workspace, apikey)
            if clusters:
                scan_results["resources"]["clusters"] = clusters

            jobs = enumerate_jobs(workspace, apikey)
            if jobs:
                scan_results["resources"]["jobs"] = jobs

            progress.update(scan_task, advance=10)

            # Scan secret scopes and secrets (15%)
            progress.update(scan_task, description="Scanning secrets...")
            scopes = enumerate_secret_scopes(workspace, apikey)
            if scopes:
                scan_results["resources"]["secret_scopes"] = scopes

                # Scan secrets in each scope
                secrets_by_scope = {}
                for scope in scopes:
                    scope_name = scope.get("name")
                    if scope_name:
                        secrets = enumerate_secrets(workspace, apikey, scope_name)
                        if secrets:
                            secrets_by_scope[scope_name] = secrets

                if secrets_by_scope:
                    scan_results["resources"]["secrets"] = secrets_by_scope

            progress.update(scan_task, advance=15)

            # Scan SQL warehouses (10%)
            progress.update(scan_task, description="Scanning SQL warehouses...")
            warehouses = enumerate_warehouses(workspace, apikey)
            if warehouses:
                scan_results["resources"]["warehouses"] = warehouses

            progress.update(scan_task, advance=10)

            # Scan Unity Catalog resources (15%)
            progress.update(scan_task, description="Scanning Unity Catalog resources...")

            # Scan catalogs
            catalogs = get_catalogs(workspace, apikey)
            if catalogs:
                scan_results["resources"]["catalogs"] = catalogs

                # Scan schemas in each catalog (sample only first catalog to avoid too many requests)
                if len(catalogs) > 0:
                    catalog_name = catalogs[0].get("name")
                    if catalog_name:
                        schemas = get_schemas(workspace, apikey, catalog_name)
                        if schemas:
                            scan_results["resources"]["schemas"] = schemas

                            # Scan tables in first schema (sample only)
                            if len(schemas) > 0:
                                schema_name = schemas[0].get("name")
                                if schema_name:
                                    tables = get_tables(workspace, apikey, catalog_name, schema_name)
                                    if tables:
                                        scan_results["resources"]["tables"] = tables

            # Scan external locations
            locations = enumerate_external_locations(workspace, apikey)
            if locations:
                scan_results["resources"]["external_locations"] = locations

            # Scan metastores
            metastores = enumerate_metastores(workspace, apikey)
            if metastores:
                scan_results["resources"]["metastores"] = metastores

            progress.update(scan_task, advance=15)

            # Scan instance pools and tokens (10%)
            progress.update(scan_task, description="Scanning instance pools and tokens...")
            pools = enumerate_instance_pools(workspace, apikey)
            if pools:
                scan_results["resources"]["instance_pools"] = pools

            tokens = enumerate_tokens(workspace, apikey)
            if tokens:
                scan_results["resources"]["tokens"] = tokens

            progress.update(scan_task, advance=10)

            # Scan ACLs for key resources (15%)
            progress.update(scan_task, description="Scanning access controls...")

            # Sample ACLs for clusters
            if clusters and len(clusters) > 0:
                cluster_acls = {}
                for cluster in clusters[:3]:  # Limit to first 3 clusters
                    cluster_id = cluster.get("cluster_id")
                    if cluster_id:
                        acls = enumerate_acls(workspace, apikey, "clusters", cluster_id)
                        if acls:
                            cluster_acls[cluster_id] = acls

                if cluster_acls:
                    if "acls" not in scan_results["resources"]:
                        scan_results["resources"]["acls"] = {}
                    scan_results["resources"]["acls"]["clusters"] = cluster_acls

            # Sample ACLs for jobs
            if jobs and len(jobs) > 0:
                job_acls = {}
                for job in jobs[:3]:  # Limit to first 3 jobs
                    job_id = job.get("job_id")
                    if job_id:
                        acls = enumerate_acls(workspace, apikey, "jobs", job_id)
                        if acls:
                            job_acls[job_id] = acls

                if job_acls:
                    if "acls" not in scan_results["resources"]:
                        scan_results["resources"]["acls"] = {}
                    scan_results["resources"]["acls"]["jobs"] = job_acls

            progress.update(scan_task, advance=15)

            # Scan complete
            progress.update(scan_task, advance=10, description="Scan complete!")

            # Get organization from profile data
            organization = profile_data.get("organization")

            # Save scan results
            result_path = save_scan_result(scan_results, "full_scan", workspace, organization)
            if result_path:
                print_success(f"Scan results saved to: {result_path}")

            return scan_results

    except Exception as e:
        print_error(f"Error during full scan: {e}")
        return None

def run_targeted_scan(workspace, profile_data, scan_type):
    """
    Run a targeted scan of specific resources

    Args:
        workspace (str): Databricks workspace
        profile_data (dict): Profile data with API key
        scan_type (str): Type of scan to run (users, groups, clusters, etc.)

    Returns:
        dict: Scan results
    """
    try:
        apikey = profile_data.get("apikey")
        organization = profile_data.get("organization")

        if not apikey:
            print_error("API key not found in profile data")
            return None

        # Validate credentials
        print_info(f"Validating credentials for workspace: {workspace}")
        user_info = validate_credentials(workspace, apikey)

        if not user_info:
            print_error("Failed to validate credentials. Scan cannot proceed.")
            return None

        print_success(f"Credentials validated successfully! Starting {scan_type} scan...")

        # Initialize scan results
        scan_results = {
            "workspace": workspace,
            "scan_time": datetime.datetime.now().isoformat(),
            "scan_type": scan_type,
            "user_info": user_info,
            "resources": {}  # Use a consistent resources dictionary
        }

        # Run the appropriate scan based on type
        with progress_spinner(f"Scanning {scan_type}...") as progress:
            task = progress.add_task("Scanning", total=None)

            if scan_type == "users":
                users = enumerate_users(workspace, apikey)
                if users:
                    # Store users in a resources dictionary to maintain consistent structure
                    scan_results["resources"]["users"] = users
                    # Also store count for summary display
                    scan_results["users_count"] = len(users)

            elif scan_type == "groups":
                groups = enumerate_groups(workspace, apikey)
                if groups:
                    scan_results["resources"]["groups"] = groups
                    scan_results["groups_count"] = len(groups)

            elif scan_type == "clusters":
                clusters = enumerate_clusters(workspace, apikey)
                if clusters:
                    scan_results["resources"]["clusters"] = clusters
                    scan_results["clusters_count"] = len(clusters)

            elif scan_type == "jobs":
                jobs = enumerate_jobs(workspace, apikey)
                if jobs:
                    scan_results["resources"]["jobs"] = jobs
                    scan_results["jobs_count"] = len(jobs)

            elif scan_type == "secrets":
                scopes = enumerate_secret_scopes(workspace, apikey)
                if scopes:
                    scan_results["resources"]["secret_scopes"] = scopes
                    scan_results["secret_scopes_count"] = len(scopes)

                    # Scan secrets in each scope
                    secrets_by_scope = {}
                    total_secrets = 0
                    for scope in scopes:
                        scope_name = scope.get("name")
                        if scope_name:
                            secrets = enumerate_secrets(workspace, apikey, scope_name)
                            if secrets:
                                secrets_by_scope[scope_name] = secrets
                                total_secrets += len(secrets)

                    if secrets_by_scope:
                        scan_results["resources"]["secrets"] = secrets_by_scope
                        scan_results["secrets_count"] = total_secrets

            elif scan_type == "warehouses":
                warehouses = enumerate_warehouses(workspace, apikey)
                if warehouses:
                    scan_results["resources"]["warehouses"] = warehouses
                    scan_results["warehouses_count"] = len(warehouses)

            elif scan_type == "catalogs":
                catalogs = get_catalogs(workspace, apikey)
                if catalogs:
                    scan_results["resources"]["catalogs"] = catalogs
                    scan_results["catalogs_count"] = len(catalogs)

                    # For catalogs, only sample a limited number to avoid excessive API calls
                    sample_catalogs = catalogs[:2] if len(catalogs) > 2 else catalogs

                    # Store the full list but mark that we're only sampling for schemas/tables
                    scan_results["sample_note"] = "Only a sample of schemas and tables are shown for demonstration. Use the 'exploit' feature for complete data extraction."

                    # Sample schemas from selected catalogs
                    schemas_by_catalog = {}
                    total_schemas = 0

                    for catalog in sample_catalogs:
                        catalog_name = catalog.get("name")
                        if catalog_name:
                            schemas = get_schemas(workspace, apikey, catalog_name)
                            if schemas:
                                # Only keep a sample of schemas
                                sample_schemas = schemas[:3] if len(schemas) > 3 else schemas
                                schemas_by_catalog[catalog_name] = sample_schemas
                                total_schemas += len(schemas)  # Store total count, not just sample

                                # Sample tables from selected schemas
                                tables_by_schema = {}
                                total_tables = 0

                                for schema in sample_schemas[:1]:  # Only sample first schema
                                    schema_name = schema.get("name")
                                    if schema_name:
                                        tables = get_tables(workspace, apikey, catalog_name, schema_name)
                                        if tables:
                                            # Only keep a sample of tables
                                            sample_tables = tables[:5] if len(tables) > 5 else tables
                                            tables_by_schema[f"{catalog_name}.{schema_name}"] = sample_tables
                                            total_tables += len(tables)  # Store total count, not just sample

                    if schemas_by_catalog:
                        scan_results["resources"]["schemas"] = schemas_by_catalog
                        scan_results["schemas_count"] = total_schemas

                    if tables_by_schema:
                        scan_results["resources"]["tables"] = tables_by_schema
                        scan_results["tables_count"] = total_tables

            elif scan_type == "external_locations":
                locations = enumerate_external_locations(workspace, apikey)
                if locations:
                    scan_results["resources"]["external_locations"] = locations
                    scan_results["external_locations_count"] = len(locations)

            elif scan_type == "tokens":
                tokens = enumerate_tokens(workspace, apikey)
                if tokens:
                    scan_results["resources"]["tokens"] = tokens
                    scan_results["tokens_count"] = len(tokens)

            elif scan_type == "instance_pools":
                pools = enumerate_instance_pools(workspace, apikey)
                if pools:
                    scan_results["resources"]["instance_pools"] = pools
                    scan_results["instance_pools_count"] = len(pools)

            else:
                print_error(f"Unknown scan type: {scan_type}")
                return None

            progress.update(task, completed=True)

        # Save scan results
        result_path = save_scan_result(scan_results, scan_type, workspace, organization)
        if result_path:
            print_success(f"Scan results saved to: {result_path}")

        return scan_results

    except Exception as e:
        print_error(f"Error during {scan_type} scan: {e}")
        return None

def run_sql_query(workspace, profile_data, query, warehouse_id=None, catalog=None, schema=None):
    """
    Run a SQL query on the Databricks workspace

    Args:
        workspace (str): Databricks workspace
        profile_data (dict): Profile data with API key
        query (str): SQL query to run
        warehouse_id (str, optional): Warehouse ID to use
        catalog (str, optional): Catalog to use
        schema (str, optional): Schema to use

    Returns:
        dict: Query results
    """
    try:
        apikey = profile_data.get("apikey")

        if not apikey:
            print_error("API key not found in profile data")
            return None

        # Validate credentials
        print_info(f"Validating credentials for workspace: {workspace}")
        user_info = validate_credentials(workspace, apikey)

        if not user_info:
            print_error("Failed to validate credentials. Query cannot proceed.")
            return None

        print_success(f"Credentials validated successfully! Executing SQL query...")

        # Execute the query
        result = execute_sql_statement(workspace, apikey, query, warehouse_id, catalog, schema)

        if not result:
            print_error("Failed to execute SQL query.")
            return None

        # Format and display the results
        table = format_sql_results(result)
        if table:
            console.print(table)

        # Save the results
        query_results = {
            "workspace": workspace,
            "query_time": datetime.datetime.now().isoformat(),
            "query": query,
            "warehouse_id": warehouse_id,
            "catalog": catalog,
            "schema": schema,
            "result": result
        }

        # Get organization from profile data
        organization = profile_data.get("organization")

        result_path = save_scan_result(query_results, "sql_query", workspace, organization)
        if result_path:
            print_success(f"Query results saved to: {result_path}")

        return query_results

    except Exception as e:
        print_error(f"Error executing SQL query: {e}")
        return None

def display_scan_summary(scan_results, scan_type=None):
    """
    Display a summary of scan results

    Args:
        scan_results (dict): Scan results
        scan_type (str, optional): Type of scan
    """
    if not scan_results:
        print_error("No scan results to display.")
        return

    workspace = scan_results.get("workspace", "Unknown")
    scan_time = scan_results.get("scan_time", "Unknown")
    scan_type_display = scan_type or scan_results.get("scan_type", "Unknown")

    # Create a summary panel
    summary_text = f"""
Workspace: [bold cyan]{workspace}[/bold cyan]
Scan Time: [bold cyan]{scan_time}[/bold cyan]
Scan Type: [bold cyan]{scan_type_display}[/bold cyan]

[bold green]Resources Found:[/bold green]
"""

    # Check for sample note
    if "sample_note" in scan_results:
        summary_text += f"\n[italic yellow]{scan_results['sample_note']}[/italic yellow]\n\n"

    # First check for direct count fields
    for key in scan_results:
        if key.endswith("_count"):
            resource_type = key.replace("_count", "")
            summary_text += f"• [bold blue]{resource_type.replace('_', ' ').title()}:[/bold blue] {scan_results[key]}\n"

    # If no direct counts, use resources dictionary
    if not any(key.endswith("_count") for key in scan_results):
        resources = scan_results.get("resources", {})
        for resource_type, resource_data in resources.items():
            if resource_type == "secrets":
                # Special handling for secrets
                scope_count = len(resource_data)
                secret_count = sum(len(secrets) for secrets in resource_data.values())
                summary_text += f"• [bold blue]{resource_type.replace('_', ' ').title()}:[/bold blue] {scope_count} scopes, {secret_count} secrets\n"
            elif resource_type == "acls":
                # Special handling for ACLs
                acl_count = sum(len(acls) for acl_type in resource_data.values() for acls in acl_type.values())
                summary_text += f"• [bold blue]{resource_type.upper()}:[/bold blue] {acl_count} entries\n"
            elif resource_type == "schemas":
                # Special handling for schemas which might be nested by catalog
                if isinstance(resource_data, dict):
                    schema_count = sum(len(schemas) for schemas in resource_data.values())
                    summary_text += f"• [bold blue]{resource_type.replace('_', ' ').title()}:[/bold blue] {schema_count}\n"
                else:
                    summary_text += f"• [bold blue]{resource_type.replace('_', ' ').title()}:[/bold blue] {len(resource_data)}\n"
            elif resource_type == "tables":
                # Special handling for tables which might be nested by schema
                if isinstance(resource_data, dict):
                    table_count = sum(len(tables) for tables in resource_data.values())
                    summary_text += f"• [bold blue]{resource_type.replace('_', ' ').title()}:[/bold blue] {table_count}\n"
                else:
                    summary_text += f"• [bold blue]{resource_type.replace('_', ' ').title()}:[/bold blue] {len(resource_data)}\n"
            elif isinstance(resource_data, list):
                summary_text += f"• [bold blue]{resource_type.replace('_', ' ').title()}:[/bold blue] {len(resource_data)}\n"
            elif isinstance(resource_data, dict):
                summary_text += f"• [bold blue]{resource_type.replace('_', ' ').title()}:[/bold blue] {len(resource_data)}\n"

    # Create and display the panel
    panel = Panel(
        summary_text,
        title="[bold]Scan Summary[/bold]",
        border_style="green",
        box=box.ROUNDED
    )

    console.print(panel)

    # Display user info if available
    user_info = scan_results.get("user_info")
    if user_info:
        user_table = Table(title="User Information")
        user_table.add_column("Field", style="cyan")
        user_table.add_column("Value", style="green")

        user_table.add_row("Username", user_info.get("userName", "N/A"))
        user_table.add_row("Display Name", user_info.get("displayName", "N/A"))
        user_table.add_row("Email", user_info.get("emails", [{}])[0].get("value", "N/A") if user_info.get("emails") else "N/A")
        user_table.add_row("Active", "✓" if user_info.get("active", False) else "✗")

        # Add groups if available
        groups = user_info.get("groups", [])
        if groups:
            group_names = ", ".join([g for g in groups[:5]])
            if len(groups) > 5:
                group_names += f" and {len(groups) - 5} more"
            user_table.add_row("Groups", group_names)

        console.print(user_table)

    # Offer to display detailed results
    print_info("Use 'show' command to view detailed results for specific resource types.")

def validate_workspace_access(workspace, apikey):
    """
    Validate access to a Databricks workspace

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key

    Returns:
        dict: Validation results
    """
    try:
        print_info(f"Validating access to workspace: {workspace}")

        # Validate credentials
        user_info = validate_credentials(workspace, apikey)

        if not user_info:
            print_error("Invalid credentials or workspace not accessible.")
            return {
                "workspace": workspace,
                "status": "invalid",
                "timestamp": datetime.datetime.now().isoformat()
            }

        # Access is valid
        print_success(f"Valid access to workspace: {workspace}")
        print_info(f"Logged in as: {user_info.get('displayName')} ({user_info.get('userName')})")

        # Return validation results
        return {
            "workspace": workspace,
            "status": "valid",
            "timestamp": datetime.datetime.now().isoformat(),
            "user_info": user_info
        }

    except Exception as e:
        print_error(f"Error validating workspace access: {e}")
        return {
            "workspace": workspace,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }
