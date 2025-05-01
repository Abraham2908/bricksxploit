"""
Resource enumeration and discovery for Databricks
"""

import requests
import json
import sys
import os
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

# Adicionar o diretório raiz ao path para permitir importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

console = Console()

def get_workspace_url(workspace):
    """
    Construct the full workspace URL

    Args:
        workspace (str): Workspace name or URL

    Returns:
        str: Full workspace URL
    """
    if workspace.startswith("http"):
        return workspace

    if "databricks.com" in workspace:
        return f"https://{workspace}"

    return f"https://{workspace}.cloud.databricks.com"

def enumerate_users(workspace, apikey):
    """
    Enumerate users in the Databricks workspace

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key

    Returns:
        list: List of users or None if failed
    """
    url = f"{get_workspace_url(workspace)}/api/2.0/preview/scim/v2/Users"
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }

    try:
        console.print("[blue]Enumerating users...[/blue]")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        users_data = response.json()
        users = users_data.get("Resources", [])

        console.print(f"[green]Found {len(users)} users[/green]")
        return users

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error enumerating users: {e}[/red]")
        return None

def enumerate_groups(workspace, apikey):
    """
    Enumerate groups in the Databricks workspace

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key

    Returns:
        list: List of groups or None if failed
    """
    url = f"{get_workspace_url(workspace)}/api/2.0/preview/scim/v2/Groups"
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }

    try:
        console.print("[blue]Enumerating groups...[/blue]")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        groups_data = response.json()
        groups = groups_data.get("Resources", [])

        console.print(f"[green]Found {len(groups)} groups[/green]")
        return groups

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error enumerating groups: {e}[/red]")
        return None

def enumerate_clusters(workspace, apikey):
    """
    Enumerate clusters in the Databricks workspace

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key

    Returns:
        list: List of clusters or None if failed
    """
    url = f"{get_workspace_url(workspace)}/api/2.0/clusters/list"
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }

    try:
        console.print("[blue]Enumerating clusters...[/blue]")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        clusters_data = response.json()
        clusters = clusters_data.get("clusters", [])

        console.print(f"[green]Found {len(clusters)} clusters[/green]")
        return clusters

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error enumerating clusters: {e}[/red]")
        return None

def enumerate_jobs(workspace, apikey):
    """
    Enumerate jobs in the Databricks workspace

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key

    Returns:
        list: List of jobs or None if failed
    """
    url = f"{get_workspace_url(workspace)}/api/2.1/jobs/list"
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }

    try:
        console.print("[blue]Enumerating jobs...[/blue]")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        jobs_data = response.json()
        jobs = jobs_data.get("jobs", [])

        console.print(f"[green]Found {len(jobs)} jobs[/green]")
        return jobs

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error enumerating jobs: {e}[/red]")
        return None

def enumerate_secret_scopes(workspace, apikey):
    """
    Enumerate secret scopes in the Databricks workspace

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key

    Returns:
        list: List of secret scopes or None if failed
    """
    url = f"{get_workspace_url(workspace)}/api/2.0/secrets/scopes/list"
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }

    try:
        console.print("[blue]Enumerating secret scopes...[/blue]")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        scopes_data = response.json()
        scopes = scopes_data.get("scopes", [])

        console.print(f"[green]Found {len(scopes)} secret scopes[/green]")
        return scopes

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error enumerating secret scopes: {e}[/red]")
        return None

def enumerate_secrets(workspace, apikey, scope_name):
    """
    Enumerate secrets in a scope

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key
        scope_name (str): Secret scope name

    Returns:
        list: List of secrets or None if failed
    """
    url = f"{get_workspace_url(workspace)}/api/2.0/secrets/list"
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }
    payload = {
        "scope": scope_name
    }

    try:
        console.print(f"[blue]Enumerating secrets in scope '{scope_name}'...[/blue]")
        response = requests.get(url, headers=headers, params=payload)
        response.raise_for_status()

        secrets_data = response.json()
        secrets = secrets_data.get("secrets", [])

        console.print(f"[green]Found {len(secrets)} secrets in scope '{scope_name}'[/green]")
        return secrets

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error enumerating secrets: {e}[/red]")
        return None

def enumerate_instance_pools(workspace, apikey):
    """
    Enumerate instance pools in the Databricks workspace

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key

    Returns:
        list: List of instance pools or None if failed
    """
    url = f"{get_workspace_url(workspace)}/api/2.0/instance-pools/list"
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }

    try:
        console.print("[blue]Enumerating instance pools...[/blue]")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        pools_data = response.json()
        pools = pools_data.get("instance_pools", [])

        console.print(f"[green]Found {len(pools)} instance pools[/green]")
        return pools

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error enumerating instance pools: {e}[/red]")
        return None

def enumerate_warehouses(workspace, apikey):
    """
    Enumerate SQL warehouses in the Databricks workspace

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key

    Returns:
        list: List of warehouses or None if failed
    """
    url = f"{get_workspace_url(workspace)}/api/2.0/sql/warehouses"
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }

    try:
        console.print("[blue]Enumerating SQL warehouses...[/blue]")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        warehouses_data = response.json()
        warehouses = warehouses_data.get("warehouses", [])

        console.print(f"[green]Found {len(warehouses)} SQL warehouses[/green]")
        return warehouses

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error enumerating SQL warehouses: {e}[/red]")
        return None

def enumerate_external_locations(workspace, apikey):
    """
    Enumerate external locations in the Databricks workspace

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key

    Returns:
        list: List of external locations or None if failed
    """
    url = f"{get_workspace_url(workspace)}/api/2.0/unity-catalog/external-locations"
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }

    try:
        console.print("[blue]Enumerating external locations...[/blue]")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        locations_data = response.json()
        locations = locations_data.get("external_locations", [])

        console.print(f"[green]Found {len(locations)} external locations[/green]")
        return locations

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error enumerating external locations: {e}[/red]")
        return None

def enumerate_metastores(workspace, apikey):
    """
    Enumerate metastores in the Databricks workspace

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key

    Returns:
        list: List of metastores or None if failed
    """
    url = f"{get_workspace_url(workspace)}/api/2.0/unity-catalog/metastores"
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }

    try:
        console.print("[blue]Enumerating metastores...[/blue]")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        metastores_data = response.json()
        metastores = metastores_data.get("metastores", [])

        console.print(f"[green]Found {len(metastores)} metastores[/green]")
        return metastores

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error enumerating metastores: {e}[/red]")
        return None

def enumerate_tokens(workspace, apikey):
    """
    Enumerate tokens in the Databricks workspace

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key

    Returns:
        list: List of tokens or None if failed
    """
    url = f"{get_workspace_url(workspace)}/api/2.0/token/list"
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }

    try:
        console.print("[blue]Enumerating tokens...[/blue]")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        tokens_data = response.json()
        tokens = tokens_data.get("token_infos", [])

        console.print(f"[green]Found {len(tokens)} tokens[/green]")
        return tokens

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error enumerating tokens: {e}[/red]")
        return None

def enumerate_acls(workspace, apikey, object_type, object_id):
    """
    Enumerate ACLs for an object

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key
        object_type (str): Object type (cluster, job, notebook, etc.)
        object_id (str): Object ID

    Returns:
        list: List of ACLs or None if failed
    """
    url = f"{get_workspace_url(workspace)}/api/2.0/preview/permissions/{object_type}/{object_id}"
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }

    try:
        console.print(f"[blue]Enumerating ACLs for {object_type} {object_id}...[/blue]")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        acls_data = response.json()
        acls = acls_data.get("access_control_list", [])

        console.print(f"[green]Found {len(acls)} ACL entries for {object_type} {object_id}[/green]")
        return acls

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error enumerating ACLs: {e}[/red]")
        return None

def enumerate_all_resources(workspace, apikey):
    """
    Enumerate all resources in the Databricks workspace

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key

    Returns:
        dict: Dictionary of all resources or None if failed
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Enumerating all resources..."),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Scanning", total=None)

        # Initialize results dictionary
        results = {
            "workspace": workspace,
            "timestamp": None,
            "resources": {}
        }

        # Enumerate users
        users = enumerate_users(workspace, apikey)
        if users:
            results["resources"]["users"] = users

        # Enumerate groups
        groups = enumerate_groups(workspace, apikey)
        if groups:
            results["resources"]["groups"] = groups

        # Enumerate clusters
        clusters = enumerate_clusters(workspace, apikey)
        if clusters:
            results["resources"]["clusters"] = clusters

        # Enumerate jobs
        jobs = enumerate_jobs(workspace, apikey)
        if jobs:
            results["resources"]["jobs"] = jobs

        # Enumerate secret scopes
        scopes = enumerate_secret_scopes(workspace, apikey)
        if scopes:
            results["resources"]["secret_scopes"] = scopes

            # Enumerate secrets in each scope
            secrets_by_scope = {}
            for scope in scopes:
                scope_name = scope.get("name")
                if scope_name:
                    secrets = enumerate_secrets(workspace, apikey, scope_name)
                    if secrets:
                        secrets_by_scope[scope_name] = secrets

            if secrets_by_scope:
                results["resources"]["secrets"] = secrets_by_scope

        # Enumerate instance pools
        pools = enumerate_instance_pools(workspace, apikey)
        if pools:
            results["resources"]["instance_pools"] = pools

        # Enumerate SQL warehouses
        warehouses = enumerate_warehouses(workspace, apikey)
        if warehouses:
            results["resources"]["warehouses"] = warehouses

        # Enumerate external locations
        locations = enumerate_external_locations(workspace, apikey)
        if locations:
            results["resources"]["external_locations"] = locations

        # Enumerate metastores
        metastores = enumerate_metastores(workspace, apikey)
        if metastores:
            results["resources"]["metastores"] = metastores

        # Enumerate tokens
        tokens = enumerate_tokens(workspace, apikey)
        if tokens:
            results["resources"]["tokens"] = tokens

        progress.update(task, completed=True)

        return results

def format_resource_table(resource_type, resources):
    """
    Format resources as a table

    Args:
        resource_type (str): Resource type
        resources (list): List of resources

    Returns:
        Table: Rich Table object with formatted resources
    """
    if not resources:
        return None

    # Define table columns based on resource type
    columns = []
    if resource_type == "users":
        columns = [
            ("ID", "id", "cyan"),
            ("Username", "userName", "green"),
            ("Display Name", "displayName", "blue"),
            ("Active", "active", "magenta")
        ]
    elif resource_type == "groups":
        columns = [
            ("ID", "id", "cyan"),
            ("Display Name", "displayName", "green"),
            ("Members", "members", "blue")
        ]
    elif resource_type == "clusters":
        columns = [
            ("ID", "cluster_id", "cyan"),
            ("Name", "cluster_name", "green"),
            ("State", "state", "blue"),
            ("Creator", "creator_user_name", "magenta")
        ]
    elif resource_type == "jobs":
        columns = [
            ("ID", "job_id", "cyan"),
            ("Name", "settings.name", "green"),
            ("Creator", "creator_user_name", "blue"),
            ("Schedule", "settings.schedule", "magenta")
        ]
    elif resource_type == "secret_scopes":
        columns = [
            ("Name", "name", "cyan"),
            ("Backend Type", "backend_type", "green")
        ]
    elif resource_type == "instance_pools":
        columns = [
            ("ID", "instance_pool_id", "cyan"),
            ("Name", "instance_pool_name", "green"),
            ("State", "state", "blue"),
            ("Node Type", "node_type_id", "magenta")
        ]
    elif resource_type == "warehouses":
        columns = [
            ("ID", "id", "cyan"),
            ("Name", "name", "green"),
            ("Size", "size", "blue"),
            ("State", "state", "magenta")
        ]
    elif resource_type == "external_locations":
        columns = [
            ("Name", "name", "cyan"),
            ("URL", "url", "green"),
            ("Owner", "owner", "blue")
        ]
    elif resource_type == "metastores":
        columns = [
            ("ID", "metastore_id", "cyan"),
            ("Name", "name", "green"),
            ("Owner", "owner", "blue")
        ]
    elif resource_type == "tokens":
        columns = [
            ("ID", "token_id", "cyan"),
            ("Comment", "comment", "green"),
            ("Created", "creation_time", "blue"),
            ("Expiry", "expiry_time", "magenta")
        ]
    else:
        # Generic columns for unknown resource types
        columns = [
            ("ID", "id", "cyan"),
            ("Name", "name", "green")
        ]

    # Create table
    table = Table(title=f"{resource_type.replace('_', ' ').title()}")

    # Add columns
    for header, _, style in columns:
        table.add_column(header, style=style)

    # Add rows
    for resource in resources:
        row = []
        for _, key, _ in columns:
            # Handle nested keys (e.g., "settings.name")
            if "." in key:
                parts = key.split(".")
                value = resource
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        value = "N/A"
                        break
            else:
                value = resource.get(key, "N/A")

            # Handle special cases
            if key == "members" and isinstance(value, list):
                value = f"{len(value)} members"
            elif key == "active":
                value = "✓" if value else "✗"
            elif key == "settings.schedule" and value != "N/A":
                value = "Scheduled"

            row.append(str(value))

        table.add_row(*row)

    return table
