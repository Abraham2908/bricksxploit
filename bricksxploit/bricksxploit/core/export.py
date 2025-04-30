import os
import json
import csv
from rich.console import Console
from rich.prompt import Prompt
from datetime import datetime
import requests

console = Console()

def export_user_info(workspace, profile):
    """
    Função que exporta as informações do usuário, como nome, e-mail, permissões, grupos, etc.
    """
    try:
        # Pega as informações detalhadas do usuário
        user_info = get_user_info(workspace, profile)
        
        if not user_info:
            console.print("[red]Failed to retrieve user information.[/red]")
            return

        # Escolhe o formato de exportação
        export_format = Prompt.ask("Choose export format (csv/json)", choices=["csv", "json"])

        if export_format == "csv":
            export_to_csv(user_info)
        elif export_format == "json":
            export_to_json(user_info)
        else:
            console.print("[red]Invalid format selected. Please choose csv or json.[/red]")

    except Exception as e:
        console.print(f"[red]Error exporting user info: {e}[/red]")

def get_user_info(workspace, profile):
    """
    Função para obter as informações detalhadas do usuário, incluindo permissões e grupos.
    """
    # Construir a URL de requisição
    url = f"https://{workspace}.databricks.com/api/2.0/preview/scim/v2/Users/{profile['emails'][0]['value']}"
    
    headers = {
        'Authorization': f"Bearer {profile['api_key']}",
        'Content-Type': 'application/json'
    }

    try:
        # Faz a requisição GET para obter as informações do usuário
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Retorna os dados JSON da resposta
        return response.json()

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error retrieving user information: {e}[/red]")
        return None

def export_to_csv(user_info):
    """
    Função que exporta os dados do usuário para um arquivo CSV.
    """
    try:
        filename = f"user_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        fields = ["username", "displayName", "emails", "groups", "permissions"]

        # Criar ou abrir o arquivo CSV para escrita
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fields)

            writer.writeheader()

            # Escreve as informações do usuário
            writer.writerow({
                "username": user_info.get("userName", "N/A"),
                "displayName": user_info.get("displayName", "N/A"),
                "emails": ", ".join([email['value'] for email in user_info.get("emails", [])]),
                "groups": ", ".join([group['display'] for group in user_info.get("groups", [])]),
                "permissions": ", ".join(user_info.get("roles", []))
            })

        console.print(f"[green]User information successfully exported to {filename}[/green]")

    except Exception as e:
        console.print(f"[red]Error exporting to CSV: {e}[/red]")

def export_to_json(user_info):
    """
    Função que exporta os dados do usuário para um arquivo JSON.
    """
    try:
        filename = f"user_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Criar ou abrir o arquivo JSON para escrita
        with open(filename, mode='w', encoding='utf-8') as file:
            json.dump(user_info, file, indent=4)

        console.print(f"[green]User information successfully exported to {filename}[/green]")

    except Exception as e:
        console.print(f"[red]Error exporting to JSON: {e}[/red]")
