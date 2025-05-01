"""
Cursor-based dynamic UI for BricksXploit
"""

import os
import sys
import time
from datetime import datetime
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.text import Text
from rich.box import ROUNDED
from rich.live import Live
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.style import Style
from rich.align import Align
from rich.padding import Padding
from rich.columns import Columns
from rich.console import Group

class CursorUI:
    """
    Cursor-based dynamic UI for BricksXploit
    """
    def __init__(self, title="BricksXploit", version="1.0.0"):
        """
        Initialize the UI

        Args:
            title (str, optional): Application title
            version (str, optional): Application version
        """
        self.title = title
        self.version = version
        self.console = Console()
        self.notifications = []
        self.content = Text("Welcome to BricksXploit! Select an option from the menu.")
        self.menu_title = "Main Menu"
        self.menu_items = []
        self.active_profile = None
        self.active_organization = None
        self.terminal_width = os.get_terminal_size().columns
        self.terminal_height = os.get_terminal_size().lines
        self.live = None

        # Set color scheme
        self.colors = {
            "primary": "cyan",
            "secondary": "green",
            "accent": "magenta",
            "warning": "yellow",
            "error": "red",
            "success": "green",
            "info": "blue",
            "header": "bright_cyan",
            "footer": "bright_black"
        }

        # Create layout
        self.layout = self._create_layout()

    def _create_layout(self):
        """
        Create the layout

        Returns:
            Layout: Rich layout
        """
        layout = Layout()

        # Split into header, body, footer
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )

        # Split body into content and notifications
        layout["body"].split_row(
            Layout(name="content", ratio=3),
            Layout(name="sidebar", ratio=1, visible=len(self.notifications) > 0)
        )

        # Update all sections
        self._update_header(layout)
        self._update_content(layout)
        self._update_sidebar(layout)
        self._update_footer(layout)

        return layout

    def _update_header(self, layout=None):
        """
        Update the header

        Args:
            layout (Layout, optional): Layout to update
        """
        if layout is None:
            layout = self.layout

        # Create ASCII art title
        title_text = f"{self.title} v{self.version}"

        # Create header panel
        header_panel = Panel(
            Align.center(Text(title_text, style=f"bold {self.colors['header']}")),
            box=ROUNDED,
            style=self.colors["primary"],
            border_style=self.colors["primary"],
            padding=(0, 1)
        )

        layout["header"].update(header_panel)

    def _update_content(self, layout=None):
        """
        Update the content

        Args:
            layout (Layout, optional): Layout to update
        """
        if layout is None:
            layout = self.layout

        # Create menu panel
        menu_panel = Panel(
            Padding(
                self.content,
                (1, 2)
            ),
            title=self.menu_title,
            title_align="left",
            box=ROUNDED,
            style="white",
            border_style=self.colors["primary"],
            padding=(0, 1)
        )

        layout["content"].update(menu_panel)

    def _update_sidebar(self, layout=None):
        """
        Update the sidebar with notifications

        Args:
            layout (Layout, optional): Layout to update
        """
        if layout is None:
            layout = self.layout

        # Skip if no notifications
        if not self.notifications:
            layout["sidebar"].visible = False
            return

        # Show only the last 10 notifications
        recent_notifications = self.notifications[-10:]

        # Create notification panels
        notification_panels = []
        for notification in recent_notifications:
            message = notification["message"]
            level = notification["level"]
            timestamp = notification["timestamp"]

            # Set color based on level
            if level == "ERROR":
                color = self.colors["error"]
            elif level == "WARNING":
                color = self.colors["warning"]
            elif level == "SUCCESS":
                color = self.colors["success"]
            else:
                color = self.colors["info"]

            # Create panel
            panel = Panel(
                Text(message, style="white"),
                title=f"[{level}]",
                title_align="left",
                subtitle=timestamp.strftime("%H:%M:%S"),
                subtitle_align="right",
                box=ROUNDED,
                style="white",
                border_style=color,
                padding=(0, 1),
                width=30
            )

            notification_panels.append(panel)

        # Create notifications panel
        notifications_panel = Panel(
            Padding(
                Group(*notification_panels),
                (1, 1)
            ),
            title="Notifications",
            title_align="left",
            box=ROUNDED,
            style="white",
            border_style=self.colors["secondary"],
            padding=(0, 1)
        )

        layout["sidebar"].visible = True
        layout["sidebar"].update(notifications_panel)

    def _update_footer(self, layout=None):
        """
        Update the footer

        Args:
            layout (Layout, optional): Layout to update
        """
        if layout is None:
            layout = self.layout

        # Create menu items text
        menu_text = ""
        if self.menu_items:
            items = []
            for i, item in enumerate(self.menu_items, 1):
                items.append(f"[{i}] {item}")
            menu_text = " | ".join(items)

        # Create profile text
        profile_text = "No active profile"
        if self.active_profile:
            profile_text = f"Profile: {self.active_profile}"
            if self.active_organization:
                profile_text += f" ({self.active_organization})"

        # Create footer panel
        footer_panel = Panel(
            Columns([
                Text(menu_text, style=self.colors["footer"]),
                Align.right(Text(profile_text, style=self.colors["footer"]))
            ]),
            box=ROUNDED,
            style=self.colors["primary"],
            border_style=self.colors["primary"],
            padding=(0, 1)
        )

        layout["footer"].update(footer_panel)

    def update(self):
        """
        Update the layout
        """
        # Recreate layout to handle terminal resize
        self.terminal_width = os.get_terminal_size().columns
        self.terminal_height = os.get_terminal_size().lines

        # Update all sections
        self._update_header()
        self._update_content()
        self._update_sidebar()
        self._update_footer()

        # Update live display if active
        if self.live:
            self.live.update(self.layout)

    def set_menu(self, title, items):
        """
        Set the menu title and items

        Args:
            title (str): Menu title
            items (list): Menu items
        """
        self.menu_title = title
        self.menu_items = items
        self.update()

    def set_content(self, content):
        """
        Set the content

        Args:
            content (str or renderable): Content to display
        """
        self.content = content
        self.update()

    def set_active_profile(self, profile_name, organization=None):
        """
        Set the active profile

        Args:
            profile_name (str): Profile name
            organization (str, optional): Organization name
        """
        self.active_profile = profile_name
        self.active_organization = organization
        self.update()

    def add_notification(self, message, level="INFO"):
        """
        Add a notification

        Args:
            message (str): Notification message
            level (str, optional): Notification level (INFO, WARNING, ERROR, SUCCESS)
        """
        self.notifications.append({
            "message": message,
            "level": level,
            "timestamp": datetime.now()
        })
        self.update()

    def start(self):
        """
        Start the UI
        """
        # Clear the screen
        self.console.clear()

        # Start live display
        self.live = Live(
            self.layout,
            console=self.console,
            screen=True,
            refresh_per_second=10,
            transient=False
        )
        self.live.start()

    def stop(self):
        """
        Stop the UI
        """
        if self.live:
            self.live.stop()
            self.live = None

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
        # Temporarily stop live display
        if self.live:
            self.live.stop()

        # Show prompt
        if choices:
            result = Prompt.ask(message, choices=choices, default=default)
        elif password:
            result = Prompt.ask(message, password=True)
        else:
            result = Prompt.ask(message, default=default)

        # Restart live display
        self.live = Live(
            self.layout,
            console=self.console,
            screen=True,
            refresh_per_second=10,
            transient=False
        )
        self.live.start()

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
        # Temporarily stop live display
        if self.live:
            self.live.stop()

        # Show confirmation prompt
        result = Confirm.ask(message, default=default)

        # Restart live display
        self.live = Live(
            self.layout,
            console=self.console,
            screen=True,
            refresh_per_second=10,
            transient=False
        )
        self.live.start()

        return result

    def create_table(self, title=None, box=ROUNDED):
        """
        Create a table

        Args:
            title (str, optional): Table title
            box (Box, optional): Box style

        Returns:
            Table: Rich Table object
        """
        return Table(
            title=title,
            box=box,
            border_style=self.colors["primary"],
            header_style=f"bold {self.colors['primary']}",
            row_styles=["white", f"dim {self.colors['secondary']}"]
        )

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
            TextColumn(f"[{self.colors['primary']}]{{task.description}}"),
            TimeElapsedColumn(),
            console=self.console
        )
        # Add task with message
        task_id = progress.add_task(message, total=None)
        return progress, task_id

    def create_progress_bar(self, message="Processing..."):
        """
        Create a progress bar

        Args:
            message (str, optional): Progress message

        Returns:
            Progress: Rich Progress object with task added
        """
        progress = Progress(
            TextColumn(f"[{self.colors['primary']}]{{task.description}}"),
            BarColumn(complete_style=self.colors["primary"]),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        )
        # Add task with message
        task_id = progress.add_task(message, total=100)
        return progress, task_id

    def run_with_spinner(self, message, func, *args, **kwargs):
        """
        Run a function with a spinner

        Args:
            message (str): Spinner message
            func (callable): Function to run
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Any: Result of the function
        """
        # Create spinner
        progress, task_id = self.create_spinner(message)

        # Set content to spinner
        old_content = self.content
        self.content = progress
        self.update()

        try:
            # Run function
            result = func(*args, **kwargs)

            # Update spinner
            progress.update(task_id, description=f"{message} [green]Done![/green]")
            self.update()
            time.sleep(0.5)

            return result
        except Exception as e:
            # Update spinner
            progress.update(task_id, description=f"{message} [red]Failed![/red]")
            self.update()
            time.sleep(0.5)

            # Add notification
            self.add_notification(f"Error: {str(e)}", "ERROR")

            raise
        finally:
            # Restore content
            self.content = old_content
            self.update()
