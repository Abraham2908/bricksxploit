import requests
from rich.console import Console
from .auth import validate_credentials

console = Console()

def run_full_scan(workspace, profile):
    """
    Função que executa um scan completo no Databricks para obter todas as informações de segurança.
    """
    try:
        # Validar credenciais do usuário
        user_info = validate_credentials(workspace, profile)

        if not user_info:
            console.print("[red]Failed to validate credentials. Scan cannot proceed.[/red]")
            return

        console.print(f"[green]Credentials validated successfully! Starting full scan...[/green]")

        # A partir daqui, podemos chamar funções que realizam o scan de diferentes recursos do Databricks.
        # Aqui, você pode personalizar para realizar o scan de grupos, permissões, recursos e outros.

        scan_users(workspace, profile)
        scan_permissions(workspace, profile)
        scan_clusters(workspace, profile)

    except Exception as e:
        console.print(f"[red]Error during full scan: {e}[/red]")

def scan_users(workspace, profile):
    """
    Função que escaneia usuários no Databricks.
    """
    try:
        url = f"https://{workspace}.databricks.com/api/2.0/preview/scim/v2/Users"
        headers = {
            'Authorization': f"Bearer {profile['api_key']}",
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        users_data = response.json()
        console.print("[green]Users scan complete![/green]")
        # Aqui, você pode armazenar ou processar os dados de usuários conforme necessário
        console.print(users_data)

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error scanning users: {e}[/red]")

def scan_permissions(workspace, profile):
    """
    Função que escaneia permissões no Databricks.
    """
    try:
        url = f"https://{workspace}.databricks.com/api/2.0/preview/scim/v2/Permissions"
        headers = {
            'Authorization': f"Bearer {profile['api_key']}",
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        permissions_data = response.json()
        console.print("[green]Permissions scan complete![/green]")
        # Aqui, você pode armazenar ou processar os dados de permissões conforme necessário
        console.print(permissions_data)

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error scanning permissions: {e}[/red]")

def scan_clusters(workspace, profile):
    """
    Função que escaneia clusters no Databricks.
    """
    try:
        url = f"https://{workspace}.databricks.com/api/2.0/clusters/list"
        headers = {
            'Authorization': f"Bearer {profile['api_key']}",
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        clusters_data = response.json()
        console.print("[green]Clusters scan complete![/green]")
        # Aqui, você pode armazenar ou processar os dados de clusters conforme necessário
        console.print(clusters_data)

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error scanning clusters: {e}[/red]")
