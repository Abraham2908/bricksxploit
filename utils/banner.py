"""
ASCII art banners and UI elements for BricksXploit
"""

import sys
import os
import random
from rich.console import Console
from rich.panel import Panel
from rich import box
from rich.text import Text

# Versão do software
__version__ = "1.0.0"

console = Console()

MAIN_BANNER = """
██████╗ ██████╗ ██╗ ██████╗██╗  ██╗███████╗██╗  ██╗██████╗ ██╗      ██████╗ ██╗████████╗
██╔══██╗██╔══██╗██║██╔════╝██║ ██╔╝██╔════╝╚██╗██╔╝██╔══██╗██║     ██╔═══██╗██║╚══██╔══╝
██████╔╝██████╔╝██║██║     █████╔╝ ███████╗ ╚███╔╝ ██████╔╝██║     ██║   ██║██║   ██║
██╔══██╗██╔══██╗██║██║     ██╔═██╗ ╚════██║ ██╔██╗ ██╔═══╝ ██║     ██║   ██║██║   ██║
██████╔╝██║  ██║██║╚██████╗██║  ██╗███████║██╔╝ ██╗██║     ███████╗╚██████╔╝██║   ██║
╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝   ╚═╝
"""

SMALL_BANNER = """
╔╗ ╦═╗╦╔═╗╦╔═╔═╗═╗ ╦╔═╗╦  ╔═╗╦╔╦╗
╠╩╗╠╦╝║║  ╠╩╗╚═╗╔╩╦╝╠═╝║  ║ ║║ ║
╚═╝╩╚═╩╚═╝╩ ╩╚═╝╩ ╚═╩  ╩═╝╚═╝╩ ╩
"""

TAGLINES = [
    "Databricks Security Testing Made Easy",
    "Enumerate, Scan, Report, Secure",
    "Your Databricks Security Companion",
    "Find Databricks Security Issues Before Others Do",
    "Databricks Security at Your Fingertips"
]

def print_banner(small=False):
    """
    Print the BricksXploit banner with a random tagline
    """
    tagline = random.choice(TAGLINES)
    banner = SMALL_BANNER if small else MAIN_BANNER

    banner_text = Text(banner, style="bold cyan")

    panel = Panel(
        banner_text,
        title=f"[bold yellow]BricksXploit v{__version__}[/bold yellow]",
        subtitle=f"[bold green]{tagline}[/bold green]",
        box=box.ROUNDED,
        border_style="blue",
        padding=(1, 2)
    )

    console.print(panel)

def print_section_header(title):
    """
    Print a section header with a title
    """
    console.print(f"\n[bold blue]{'=' * 20} {title} {'=' * 20}[/bold blue]\n")

def print_result_header(title):
    """
    Print a result header with a title
    """
    panel = Panel(
        f"[bold white]{title}[/bold white]",
        box=box.ROUNDED,
        border_style="green",
        padding=(1, 2)
    )
    console.print(panel)

def print_footer():
    """
    Print a footer with version information
    """
    console.print(f"\n[dim]BricksXploit v{__version__} - Databricks Security Testing Tool[/dim]")
