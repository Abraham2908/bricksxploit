import json
import os
from pathlib import Path

CONFIG_FILE = Path.home() / ".bricksxploit_config.json"

def load_config():
    """
    Carrega as configurações de perfis, criando um arquivo padrão caso não exista.
    """
    if not CONFIG_FILE.exists():
        # Arquivo não existe, então inicializamos com perfis vazios.
        initial_data = {"profiles": {}, "current": None}
        save_config(initial_data)
        print("[yellow]Profiles file not found, starting with empty profiles.[/yellow]")
        return initial_data
    else:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

def save_config(config):
    """
    Salva as configurações no arquivo.
    """
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def set_current_profile(config, profile_name):
    """
    Define o perfil ativo no arquivo de configuração.
    """
    config["current"] = profile_name
    save_config(config)
