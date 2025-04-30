from rich.console import Console
from rich.prompt import Prompt
from bricksxploit.core.auth import validate_credentials
from bricksxploit.core.export import export_user_info
from bricksxploit.core.scan import run_full_scan
from bricksxploit.core.report import generate_and_send_report  # Atualizado para importar a função correta
from bricksxploit.core.profiles import list_saved_profiles, switch_profile, get_profile

console = Console()

def show_menu(config):
    """
    Função que exibe o menu principal e chama as opções conforme a escolha do usuário.
    """
    while True:
        console.print("────────────────────────────────────────── bricksxploit Menu ──────────────────────────────────────────")
        print(f"Active profile: {config.get('active_profile', 'None')}")
        
        # Exibindo as opções do menu
        choice = Prompt.ask("Choose an option [1/2/3/4/5/6]: ", choices=["1", "2", "3", "4", "5", "6"])

        if choice == "1":
            # Alternar entre os perfis salvos
            switch_profile(config)
        elif choice == "2":
            # Listar perfis salvos
            list_saved_profiles(config)
        elif choice == "3":
            # Executar o scan completo
            workspace = Prompt.ask("Enter the workspace (e.g., dbc-xxxx.databricks.com): ")
            profile = get_profile(config)
            if profile:
                run_full_scan(workspace, profile)  # Chamando o scan completo
            else:
                console.print("[red]No active profile found! Please set an active profile first.[/red]")
        elif choice == "4":
            # Exportar as informações do usuário
            workspace = Prompt.ask("Enter the workspace (e.g., dbc-xxxx.databricks.com): ")
            profile = get_profile(config)
            if profile:
                export_user_info(workspace, profile)
            else:
                console.print("[red]No active profile found! Please set an active profile first.[/red]")
        elif choice == "5":
            # Gerar o relatório
            workspace = Prompt.ask("Enter the workspace (e.g., dbc-xxxx.databricks.com): ")
            apikey = Prompt.ask("Enter the API key: ")
            output = Prompt.ask("Enter the output file name (or leave blank to skip): ", default="")
            notify = Prompt.ask("Do you want to send a Discord notification? (y/n): ", choices=["y", "n"], default="n")

            notify = True if notify == "y" else False
            
            # Gerando o relatório com as opções fornecidas
            generate_and_send_report(workspace, apikey, output if output else None, notify)
        elif choice == "6":
            # Sair do programa
            console.print("[green]Exiting...[/green]")
            break
