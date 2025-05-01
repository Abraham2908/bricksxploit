"""
Dynamic UI components for BricksXploit
"""

import os
import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.style import Style
from rich import box
from rich.align import Align
from rich.spinner import Spinner
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()

class DynamicUI:
    """
    Dynamic UI manager for BricksXploit
    """
    def __init__(self, title="BricksXploit", version="1.0.0"):
        """
        Initialize the dynamic UI

        Args:
            title (str): Application title
            version (str): Application version
        """
        self.title = title
        self.version = version
        self.console = Console()
        self.layout = Layout()
        self.active_profile = None
        self.active_organization = None
        self.notifications = []
        self.content = ""
        self.menu_title = "Main Menu"
        self.menu_items = []
        self.menu_options = []
        self.breadcrumbs = []
        self.setup_layout()

    def setup_layout(self):
        """
        Setup the layout structure
        """
        self.layout.split(
            Layout(name="header", size=7),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )

        self.layout["body"].split_row(
            Layout(name="main", ratio=1),
        )

        self.layout["main"].split(
            Layout(name="notifications", size=3),
            Layout(name="content"),
            Layout(name="menu", size=10)
        )

    def update_header(self):
        """
        Update the header with application title and version
        """
        header_text = f"""
  ██████╗ ██████╗ ██╗ ██████╗██╗  ██╗███████╗██╗  ██╗██████╗ ██╗      ██████╗ ██╗████████╗
  ██╔══██╗██╔══██╗██║██╔════╝██║ ██╔╝██╔════╝╚██╗██╔╝██╔══██╗██║     ██╔═══██╗██║╚══██╔══╝
  ██████╔╝██████╔╝██║██║     █████╔╝ ███████╗ ╚███╔╝ ██████╔╝██║     ██║   ██║██║   ██║
  ██╔══██╗██╔══██╗██║██║     ██╔═██╗ ╚════██║ ██╔██╗ ██╔═══╝ ██║     ██║   ██║██║   ██║
  ██████╔╝██║  ██║██║╚██████╗██║  ██╗███████║██╔╝ ██╗██║     ███████╗╚██████╔╝██║   ██║
  ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝   ╚═╝
"""
        self.layout["header"].update(
            Panel(
                Align.center(Text(header_text, style="bold cyan")),
                title=f"{self.title} v{self.version}",
                subtitle="Enumerate, Scan, Report, Secure",
                border_style="cyan",
                box=box.DOUBLE
            )
        )

    def update_footer(self):
        """
        Update the footer with active profile information
        """
        profile_text = "None"
        if self.active_profile:
            profile_text = f"{self.active_profile}"
            if self.active_organization:
                profile_text = f"{self.active_profile} ({self.active_organization})"

        self.layout["footer"].update(
            Panel(
                Align.center(Text(f"Active Profile: {profile_text}", style="bold")),
                border_style="cyan",
                box=box.DOUBLE
            )
        )

    def update_notifications(self):
        """
        Update the notifications area
        """
        if not self.notifications:
            self.layout["notifications"].update("")
            return

        notification_text = "\n".join([f"{n['type']}: {n['message']}" for n in self.notifications[-3:]])
        self.layout["notifications"].update(
            Panel(
                Text(notification_text),
                title="Notifications",
                border_style="cyan",
                box=box.SIMPLE
            )
        )

    def update_content(self):
        """
        Update the main content area
        """
        self.layout["content"].update(
            Panel(
                Align.center(self.content) if isinstance(self.content, Text) else self.content,
                title=self.menu_title,
                border_style="cyan",
                box=box.DOUBLE
            )
        )

    def update_menu(self):
        """
        Update the menu area
        """
        menu_text = ""
        for i, item in enumerate(self.menu_items, 1):
            menu_text += f"{i}. {item}\n"

        self.layout["menu"].update(
            Panel(
                Text(menu_text),
                title="Menu",
                border_style="cyan",
                box=box.SIMPLE
            )
        )

    def update(self):
        """
        Update all layout components
        """
        self.update_header()
        self.update_footer()
        self.update_notifications()
        self.update_content()
        self.update_menu()

    def add_notification(self, message, type="INFO"):
        """
        Add a notification

        Args:
            message (str): Notification message
            type (str): Notification type (INFO, SUCCESS, ERROR, WARNING)
        """
        self.notifications.append({
            "message": message,
            "type": type,
            "timestamp": time.time()
        })

        # Keep only the last 10 notifications
        if len(self.notifications) > 10:
            self.notifications.pop(0)

    def set_active_profile(self, profile, organization=None):
        """
        Set the active profile

        Args:
            profile (str): Profile name
            organization (str, optional): Organization name
        """
        self.active_profile = profile
        self.active_organization = organization

    def set_menu(self, title, items, options=None):
        """
        Set the menu items

        Args:
            title (str): Menu title
            items (list): Menu items
            options (list, optional): Menu options for selection
        """
        self.menu_title = title
        self.menu_items = items
        self.menu_options = options or [str(i) for i in range(1, len(items) + 1)]

    def set_content(self, content):
        """
        Set the main content

        Args:
            content: Content to display (can be Text, Table, or other Rich renderable)
        """
        self.content = content

    def add_breadcrumb(self, title):
        """
        Add a breadcrumb

        Args:
            title (str): Breadcrumb title
        """
        self.breadcrumbs.append(title)

    def pop_breadcrumb(self):
        """
        Remove the last breadcrumb

        Returns:
            str: Removed breadcrumb title
        """
        if self.breadcrumbs:
            return self.breadcrumbs.pop()
        return None

    def clear_breadcrumbs(self):
        """
        Clear all breadcrumbs
        """
        self.breadcrumbs = []

    def get_breadcrumb_path(self):
        """
        Get the breadcrumb path

        Returns:
            str: Breadcrumb path
        """
        return " > ".join(self.breadcrumbs)

    def prompt(self, message, choices=None, default=None, password=False):
        """
        Prompt for input

        Args:
            message (str): Prompt message
            choices (list, optional): Valid choices
            default (str, optional): Default value
            password (bool, optional): Whether to hide input

        Returns:
            str: User input
        """
        # Mostrar o prompt diretamente, sem contexto Live adicional
        # para evitar o erro "Only one live display may be active at once"
        if choices:
            result = Prompt.ask(message, choices=choices, default=default)
        elif password:
            result = Prompt.ask(message, password=True)
        else:
            result = Prompt.ask(message, default=default)

        return result

    def confirm(self, message, default=False):
        """
        Confirm prompt

        Args:
            message (str): Confirmation message
            default (bool, optional): Default value

        Returns:
            bool: User confirmation
        """
        # Mostrar o prompt de confirmação diretamente, sem contexto Live adicional
        # para evitar o erro "Only one live display may be active at once"
        result = Confirm.ask(message, default=default)

        return result

    def display(self, refresh_per_second=4):
        """
        Display the UI

        Args:
            refresh_per_second (int, optional): Refresh rate

        Returns:
            Live: Live display context
        """
        # Usar auto_refresh=True e transient=False para manter a interface visível
        # e atualizada mesmo após sair do contexto
        return Live(
            self.layout,
            refresh_per_second=refresh_per_second,
            screen=False,
            transient=False,
            auto_refresh=True
        )

    def clear_notifications(self):
        """
        Clear all notifications
        """
        self.notifications = []

    def create_table(self, title=None, box=box.SIMPLE):
        """
        Create a table

        Args:
            title (str, optional): Table title
            box: Box style

        Returns:
            Table: Rich Table object
        """
        table = Table(title=title, box=box, border_style="cyan")
        return table

    def create_spinner(self, message="Processing..."):
        """
        Create a spinner

        Args:
            message (str, optional): Spinner message

        Returns:
            Progress: Rich Progress object with task added
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[cyan]{task.description}"),
            TimeElapsedColumn(),
            console=self.console
        )
        # Adicionar a tarefa com a mensagem fornecida
        progress.add_task(message, total=None)
        return progress

    def create_progress_bar(self, message="Processing..."):
        """
        Create a progress bar

        Args:
            message (str, optional): Progress message

        Returns:
            Progress: Rich Progress object with task added
        """
        progress = Progress(
            TextColumn("[cyan]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        )
        # Adicionar a tarefa com a mensagem fornecida
        progress.add_task(message, total=100)
        return progress

    def print_success(self, message):
        """
        Print a success message and add notification

        Args:
            message (str): Success message
        """
        self.add_notification(message, "SUCCESS")
        self.console.print(f"[green]SUCCESS: {message}[/green]")

    def print_error(self, message):
        """
        Print an error message and add notification

        Args:
            message (str): Error message
        """
        self.add_notification(message, "ERROR")
        self.console.print(f"[red]ERROR: {message}[/red]")

    def print_warning(self, message):
        """
        Print a warning message and add notification

        Args:
            message (str): Warning message
        """
        self.add_notification(message, "WARNING")
        self.console.print(f"[yellow]WARNING: {message}[/yellow]")

    def print_info(self, message):
        """
        Print an info message and add notification

        Args:
            message (str): Info message
        """
        self.add_notification(message, "INFO")
        self.console.print(f"[cyan]INFO: {message}[/cyan]")
