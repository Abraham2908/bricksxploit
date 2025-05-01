"""
SQL statement execution and management for Databricks
"""

import requests
import time
import json
import sys
import os
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

# Adicionar o diretório raiz ao path para permitir importações absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

console = Console()

def execute_sql_statement(workspace, apikey, statement, warehouse_id=None, catalog=None, schema=None):
    """
    Execute a SQL statement on Databricks

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key
        statement (str): SQL statement to execute
        warehouse_id (str, optional): Warehouse ID to use
        catalog (str, optional): Catalog to use
        schema (str, optional): Schema to use

    Returns:
        dict: Statement execution result or None if failed
    """
    url = f"https://{workspace}/api/2.0/sql/statements/"
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }

    # Prepare request payload
    payload = {
        "statement": statement,
    }

    # Add optional parameters if provided
    if warehouse_id:
        payload["warehouse_id"] = warehouse_id
    if catalog:
        payload["catalog"] = catalog
    if schema:
        payload["schema"] = schema

    try:
        # Submit the SQL statement
        console.print(f"[blue]Executing SQL statement: {statement[:50]}{'...' if len(statement) > 50 else ''}[/blue]")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        # Get the statement ID
        statement_data = response.json()
        statement_id = statement_data.get("statement_id")

        if not statement_id:
            console.print("[red]Failed to get statement ID from response.[/red]")
            return None

        # Wait for the statement to complete
        return wait_for_statement_completion(workspace, apikey, statement_id)

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error executing SQL statement: {e}[/red]")
        return None

def wait_for_statement_completion(workspace, apikey, statement_id, timeout=300, poll_interval=2):
    """
    Wait for a SQL statement to complete

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key
        statement_id (str): Statement ID to check
        timeout (int): Maximum time to wait in seconds
        poll_interval (int): Time between status checks in seconds

    Returns:
        dict: Statement result or None if failed or timed out
    """
    url = f"https://{workspace}/api/2.0/sql/statements/{statement_id}"
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }

    # Create a progress spinner
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Waiting for SQL statement to complete..."),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Executing", total=None)

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()

                statement_status = response.json()
                status = statement_status.get("status", {}).get("state")

                # Check if the statement has completed
                if status == "SUCCEEDED":
                    progress.update(task, completed=True)
                    return statement_status
                elif status in ["FAILED", "CANCELED"]:
                    progress.update(task, completed=True)
                    error_message = statement_status.get("status", {}).get("error", {}).get("message", "Unknown error")
                    console.print(f"[red]SQL statement failed: {error_message}[/red]")
                    return statement_status

                # Wait before checking again
                time.sleep(poll_interval)

            except requests.exceptions.RequestException as e:
                console.print(f"[red]Error checking statement status: {e}[/red]")
                return None

        # Timeout reached
        console.print(f"[yellow]Timeout reached while waiting for SQL statement to complete.[/yellow]")
        return None

def format_sql_results(statement_result):
    """
    Format SQL statement results for display

    Args:
        statement_result (dict): Statement result from API

    Returns:
        Table: Rich Table object with formatted results
    """
    if not statement_result:
        return None

    # Check if the statement succeeded
    status = statement_result.get("status", {}).get("state")
    if status != "SUCCEEDED":
        error_message = statement_result.get("status", {}).get("error", {}).get("message", "Unknown error")
        console.print(f"[red]Cannot format results. SQL statement failed: {error_message}[/red]")
        return None

    # Get the result data
    manifest = statement_result.get("manifest", {})
    schema = manifest.get("schema", [])
    result_data = statement_result.get("result", {}).get("data_array", [])

    if not schema or not result_data:
        console.print("[yellow]No results returned from SQL statement.[/yellow]")
        return None

    # Create a table for the results
    table = Table(title="SQL Query Results", box=None)

    # Add columns from schema
    for column in schema:
        name = column.get("name", "Unknown")
        table.add_column(name, style="cyan")

    # Add rows from result data
    for row in result_data:
        # Convert all values to strings
        str_row = [str(value) if value is not None else "NULL" for value in row]
        table.add_row(*str_row)

    return table

def get_warehouses(workspace, apikey):
    """
    Get list of SQL warehouses

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key

    Returns:
        list: List of warehouses or None if failed
    """
    url = f"https://{workspace}/api/2.0/sql/warehouses"
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        warehouses = response.json().get("warehouses", [])
        return warehouses

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error getting warehouses: {e}[/red]")
        return None

def get_catalogs(workspace, apikey):
    """
    Get list of catalogs

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key

    Returns:
        list: List of catalogs or None if failed
    """
    # Use SQL statement to get catalogs
    statement = "SHOW CATALOGS"
    result = execute_sql_statement(workspace, apikey, statement)

    if not result:
        return None

    # Extract catalog names from result
    catalogs = []
    result_data = result.get("result", {}).get("data_array", [])

    for row in result_data:
        if row and len(row) > 0:
            catalogs.append({"name": row[0]})

    return catalogs

def get_schemas(workspace, apikey, catalog):
    """
    Get list of schemas in a catalog

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key
        catalog (str): Catalog name

    Returns:
        list: List of schemas or None if failed
    """
    # Use SQL statement to get schemas
    statement = f"SHOW SCHEMAS IN {catalog}"
    result = execute_sql_statement(workspace, apikey, statement)

    if not result:
        return None

    # Extract schema names from result
    schemas = []
    result_data = result.get("result", {}).get("data_array", [])

    for row in result_data:
        if row and len(row) > 0:
            schemas.append({"name": row[0], "catalog": catalog})

    return schemas

def get_tables(workspace, apikey, catalog, schema):
    """
    Get list of tables in a schema

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key
        catalog (str): Catalog name
        schema (str): Schema name

    Returns:
        list: List of tables or None if failed
    """
    # Use SQL statement to get tables
    statement = f"SHOW TABLES IN {catalog}.{schema}"
    result = execute_sql_statement(workspace, apikey, statement)

    if not result:
        return None

    # Extract table names from result
    tables = []
    result_data = result.get("result", {}).get("data_array", [])

    for row in result_data:
        if row and len(row) >= 2:
            tables.append({
                "name": row[1],
                "schema": schema,
                "catalog": catalog,
                "is_temporary": row[2] if len(row) > 2 else False
            })

    return tables

def describe_table(workspace, apikey, catalog, schema, table):
    """
    Get table description

    Args:
        workspace (str): Databricks workspace
        apikey (str): API key
        catalog (str): Catalog name
        schema (str): Schema name
        table (str): Table name

    Returns:
        dict: Table description or None if failed
    """
    # Use SQL statement to describe table
    statement = f"DESCRIBE TABLE EXTENDED {catalog}.{schema}.{table}"
    result = execute_sql_statement(workspace, apikey, statement)

    if not result:
        return None

    # Extract table description from result
    description = {
        "name": table,
        "schema": schema,
        "catalog": catalog,
        "columns": [],
        "properties": {}
    }

    result_data = result.get("result", {}).get("data_array", [])

    # Process result data
    in_columns_section = True
    for row in result_data:
        if not row or len(row) < 2:
            continue

        col_name = row[0]
        col_value = row[1]

        # Check if we've moved from columns to properties
        if col_name == "# Detailed Table Information":
            in_columns_section = False
            continue

        if in_columns_section:
            # This is a column definition
            data_type = col_value
            comment = row[2] if len(row) > 2 else ""

            description["columns"].append({
                "name": col_name,
                "type": data_type,
                "comment": comment
            })
        else:
            # This is a property
            description["properties"][col_name] = col_value

    return description
