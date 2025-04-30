import requests
from rich.console import Console
from rich.table import Table
from bricksxploit.utils.storage import load_config

console = Console()

def get_workspace_url(workspace):
    """
    Constrói a URL completa para o workspace do Databricks, com suporte para o domínio correto.
    """
    if not workspace:
        console.print("[red]Workspace is missing! Please provide a valid workspace identifier.[/red]")
        return None

    # Verificando o formato correto do domínio
    if 'cloud.databricks.com' not in workspace:
        # Se o domínio não contém 'cloud.databricks.com', assume-se que é o formato antigo
        workspace_url = f"https://{workspace}.cloud.databricks.com"
    else:
        # Se já tem o domínio correto, usamos diretamente
        workspace_url = f"https://{workspace}"

    console.print(f"[yellow]Generated URL: {workspace_url}[/yellow]")  # Debug: imprimindo a URL gerada
    return workspace_url

def validate_credentials(workspace, apikey):
    """
    Valida as credenciais fornecidas, retornando informações do perfil do usuário.
    """
    url = f"{get_workspace_url(workspace)}/api/2.0/preview/scim/v2/Me"
    headers = {"Authorization": f"Bearer {apikey}"}

    if not workspace or not apikey:
        console.print("[red]Missing workspace or API key! Please provide valid credentials.[/red]")
        return None

    try:
        console.print(f"[blue]Sending request to: {url}[/blue]")
        response = requests.get(url, headers=headers)
        
        # Verificando se a resposta foi bem-sucedida
        response.raise_for_status()
        
        # Caso a resposta seja válida, retorna os dados do usuário
        return response.json()

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Connection Error: {e}[/red]")
        return None

def display_user_info_table(profile):
    """
    Exibe as informações do usuário em uma tabela interativa no console.
    """
    if not profile:
        console.print("[red]No profile data available![/red]")
        return

    # Exibindo as informações do usuário de forma organizada
    table = Table(title="User Information", style="bold cyan")

    table.add_column("Field", justify="right", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    # Adicionando as informações de perfil
    table.add_row("User ID", profile.get("id", "N/A"))
    table.add_row("User Name", profile.get("userName", "N/A"))
    table.add_row("Full Name", profile.get("displayName", "N/A"))
    table.add_row("Email", profile.get("emails", [{}])[0].get("value", "N/A"))
    table.add_row("Active", str(profile.get("active", False)))

    # Exibindo roles e grupos, se disponíveis
    roles = ", ".join(profile.get("roles", [])) or "No roles assigned"
    groups = ", ".join(profile.get("groups", [])) or "No groups assigned"
    
    table.add_row("Roles", roles)
    table.add_row("Groups", groups)

    console.print(table)

def get_warehouses(workspace, apikey):
    """
    Obtém informações sobre os warehouses no Databricks.
    """
    url = f"{get_workspace_url(workspace)}/api/2.0/sql/warehouses"
    headers = {"Authorization": f"Bearer {apikey}"}

    if not workspace or not apikey:
        console.print("[red]Missing workspace or API key! Please provide valid credentials.[/red]")
        return None

    try:
        console.print(f"[blue]Sending request to: {url}[/blue]")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Caso a resposta seja válida, retorna informações dos warehouses
        return response.json()

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error fetching warehouses: {e}[/red]")
        return None
