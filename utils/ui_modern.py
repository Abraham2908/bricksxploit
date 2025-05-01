"""
Modern UI components for BricksXploit
"""

import time
import os
import sys
from datetime import datetime
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

# Use a predefined box style
MODERN_BOX = ROUNDED

# MODERN_BOX is already defined above

class ModernUI:
    """
    Modern UI for BricksXploit
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
            box=MODERN_BOX,
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
            box=MODERN_BOX,
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
                box=MODERN_BOX,
                style="white",
                border_style=color,
                padding=(0, 1),
                width=30
            )

            notification_panels.append(panel)

        # Create notifications panel
        notifications_panel = Panel(
            Padding(
                Columns(notification_panels, align="center"),
                (1, 1)
            ),
            title="Notifications",
            title_align="left",
            box=MODERN_BOX,
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
            box=MODERN_BOX,
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

    def set_menu(self, title, items):
        """
        Set the menu title and items

        Args:
            title (str): Menu title
            items (list): Menu items
        """
        self.menu_title = title
        self.menu_items = items

    def set_content(self, content):
        """
        Set the content

        Args:
            content (str or renderable): Content to display
        """
        self.content = content

    def set_active_profile(self, profile_name, organization=None):
        """
        Set the active profile

        Args:
            profile_name (str): Profile name
            organization (str, optional): Organization name
        """
        self.active_profile = profile_name
        self.active_organization = organization

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

    def display(self, refresh_per_second=10):
        """
        Display the UI

        Args:
            refresh_per_second (int, optional): Refresh rate

        Returns:
            Live: Live display context
        """
        # Use auto_refresh=True and transient=False to maintain visibility
        return Live(
            self.layout,
            refresh_per_second=refresh_per_second,
            screen=False,
            transient=False,
            auto_refresh=True
        )

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
        # Show prompt directly
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
        # Show confirmation prompt directly
        result = Confirm.ask(message, default=default)

        return result

    def create_table(self, title=None, box=MODERN_BOX):
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
            TextColumn(f"[{self.colors['primary']}]{{task.description}}"),
            BarColumn(complete_style=self.colors["primary"]),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        )
        # Add task with message
        progress.add_task(message, total=100)
        return progress
