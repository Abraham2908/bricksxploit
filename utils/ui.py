"""
UI components and helpers for BricksXploit
"""

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich import box
from rich.tree import Tree
from rich.text import Text
from rich.style import Style
from rich.live import Live
import time

console = Console()

def create_menu(title, options, active_profile=None):
    """
    Create a beautiful menu with options
    
    Args:
        title (str): The menu title
        options (list): List of (key, description) tuples
        active_profile (str, optional): Currently active profile
    
    Returns:
        str: The selected option key
    """
    panel = Panel(
        "\n".join([f"[bold cyan]{key}.[/bold cyan] {desc}" for key, desc in options]),
        title=f"[bold yellow]{title}[/bold yellow]",
        subtitle=f"[dim]Active Profile: {active_profile or 'None'}[/dim]",
        box=box.ROUNDED,
        border_style="blue",
        padding=(1, 2)
    )
    
    console.print(panel)
    
    valid_choices = [key for key, _ in options]
    choice = Prompt.ask("Select an option", choices=valid_choices, default=valid_choices[0])
    
    return choice

def progress_spinner(description="Processing"):
    """
    Create a progress spinner for long-running operations
    
    Args:
        description (str): Description of the operation
    
    Returns:
        Progress: A Rich Progress object
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        TimeElapsedColumn(),
        console=console
    )

def progress_bar(description="Processing", total=100):
    """
    Create a progress bar for operations with known steps
    
    Args:
        description (str): Description of the operation
        total (int): Total number of steps
    
    Returns:
        tuple: (Progress object, task_id)
    """
    progress = Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(complete_style="green", finished_style="bold green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    )
    
    task_id = progress.add_task(description, total=total)
    return progress, task_id

def create_table(title, columns, border_style="blue"):
    """
    Create a styled table
    
    Args:
        title (str): Table title
        columns (list): List of (name, justify, style) tuples
        border_style (str): Border style color
    
    Returns:
        Table: A Rich Table object
    """
    table = Table(title=title, box=box.ROUNDED, border_style=border_style)
    
    for name, justify, style in columns:
        table.add_column(name, justify=justify, style=style, no_wrap=True)
    
    return table

def print_tree(title, data, guide_style="dim"):
    """
    Print data as a tree structure
    
    Args:
        title (str): Tree title
        data (dict): Nested dictionary to display as tree
        guide_style (str): Style for tree guides
    """
    tree = Tree(f"[bold]{title}[/bold]", guide_style=guide_style)
    
    def add_nodes(parent, items):
        if isinstance(items, dict):
            for key, value in items.items():
                if isinstance(value, (dict, list)):
                    node = parent.add(f"[bold cyan]{key}[/bold cyan]")
                    add_nodes(node, value)
                else:
                    parent.add(f"[bold cyan]{key}:[/bold cyan] {value}")
        elif isinstance(items, list):
            for item in items:
                if isinstance(item, (dict, list)):
                    node = parent.add("[bold green]Item[/bold green]")
                    add_nodes(node, item)
                else:
                    parent.add(f"{item}")
    
    add_nodes(tree, data)
    console.print(tree)

def ask_for_input(prompt, password=False, choices=None, default=None):
    """
    Ask for user input with proper styling
    
    Args:
        prompt (str): The prompt to display
        password (bool): Whether to hide input (for passwords)
        choices (list): List of valid choices
        default (str): Default value
    
    Returns:
        str: User input
    """
    if password:
        return Prompt.ask(prompt, password=True)
    elif choices:
        return Prompt.ask(prompt, choices=choices, default=default)
    else:
        return Prompt.ask(prompt, default=default)

def confirm(question, default=False):
    """
    Ask for confirmation
    
    Args:
        question (str): The question to ask
        default (bool): Default value
    
    Returns:
        bool: True if confirmed, False otherwise
    """
    return Confirm.ask(question, default=default)

def print_json(data, title=None):
    """
    Print JSON data in a nicely formatted way
    
    Args:
        data (dict): The data to print
        title (str, optional): Optional title
    """
    if title:
        console.print(f"[bold]{title}[/bold]")
    
    console.print_json(data=data)

def print_error(message):
    """
    Print an error message
    
    Args:
        message (str): The error message
    """
    console.print(f"[bold red]ERROR:[/bold red] {message}")

def print_warning(message):
    """
    Print a warning message
    
    Args:
        message (str): The warning message
    """
    console.print(f"[bold yellow]WARNING:[/bold yellow] {message}")

def print_success(message):
    """
    Print a success message
    
    Args:
        message (str): The success message
    """
    console.print(f"[bold green]SUCCESS:[/bold green] {message}")

def print_info(message):
    """
    Print an info message
    
    Args:
        message (str): The info message
    """
    console.print(f"[bold blue]INFO:[/bold blue] {message}")
