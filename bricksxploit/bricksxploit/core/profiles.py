import json
from rich.console import Console

console = Console()

# Simulando o arquivo de configuração dos perfis. 
# Você pode armazenar os perfis em um arquivo JSON ou banco de dados, se necessário.
config_file = "profiles.json"

def load_profiles():
    """ Carrega os perfis salvos do arquivo JSON. """
    try:
        with open(config_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        console.print("[yellow]Profiles file not found, starting with empty profiles.[/yellow]")
        return {}

def save_profiles(profiles):
    """ Salva os perfis no arquivo JSON. """
    with open(config_file, "w") as file:
        json.dump(profiles, file, indent=4)

def list_saved_profiles(config):
    """
    Função que lista todos os perfis salvos.
    """
    profiles = load_profiles()
    active_profile = config.get('active_profile', 'None')

    if not profiles:
        console.print("[red]No profiles found![/red]")
        return

    console.print("[blue]Listing saved profiles...[/blue]")
    for name, profile in profiles.items():
        status = "[green]Active[/green]" if name == active_profile else "[red]Inactive[/red]"
        console.print(f"[bold]{name}[/bold] - {status}")

def switch_profile(config):
    """
    Função para alternar entre os perfis salvos.
    """
    profiles = load_profiles()
    if not profiles:
        console.print("[red]No profiles available to switch![/red]")
        return

    console.print("[blue]Switching profile...[/blue]")
    profile_name = input("Enter the profile name to switch: ")

    if profile_name in profiles:
        config["active_profile"] = profile_name
        save_profiles(profiles)  # Salva a mudança do perfil
        console.print(f"[green]Switched to profile {profile_name}[/green]")
    else:
        console.print("[red]Profile not found![/red]")

def get_profile(config):
    """
    Função que retorna o perfil ativo.
    """
    active_profile = config.get('active_profile')
    if not active_profile:
        console.print("[red]No active profile found! Please switch to a profile first.[/red]")
        return None

    profiles = load_profiles()
    return profiles.get(active_profile)
