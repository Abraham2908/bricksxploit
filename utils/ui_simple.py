"""
Simple dynamic UI for BricksXploit using cursor control
"""

import os
import sys
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.box import ROUNDED
from rich.live import Live
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

class SimpleUI:
    """
    Simple dynamic UI for BricksXploit
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
        self.active_profile = None
        self.active_organization = None
        
    def clear_screen(self):
        """
        Clear the screen
        """
        self.console.clear()
        
    def display_header(self):
        """
        Display the header
        """
        header = Panel(
            Text(f"{self.title} v{self.version}", style="bold cyan"),
            box=ROUNDED,
            border_style="cyan",
            padding=(0, 2)
        )
        self.console.print(header)
        
    def display_footer(self):
        """
        Display the footer
        """
        profile_text = "No active profile"
        if self.active_profile:
            profile_text = f"Profile: {self.active_profile}"
            if self.active_organization:
                profile_text += f" ({self.active_organization})"
                
        footer = Panel(
            Text(profile_text, style="dim"),
            box=ROUNDED,
            border_style="cyan",
            padding=(0, 2)
        )
        self.console.print(footer)
        
    def display_menu(self, title, items):
        """
        Display a menu
        
        Args:
            title (str): Menu title
            items (list): Menu items
        """
        # Create menu text
        menu_text = ""
        for i, item in enumerate(items, 1):
            menu_text += f"[{i}] {item}  "
            
        menu = Panel(
            Text(menu_text, style="cyan"),
            box=ROUNDED,
            border_style="cyan",
            padding=(0, 2)
        )
        self.console.print(menu)
        
    def display_content(self, content):
        """
        Display content
        
        Args:
            content: Content to display (Text, Table, Panel, etc.)
        """
        if isinstance(content, str):
            content = Text(content)
            
        self.console.print(content)
        
    def display_notifications(self):
        """
        Display notifications
        """
        if not self.notifications:
            return
            
        # Show only the last 5 notifications
        recent = self.notifications[-5:]
        
        for notification in recent:
            message = notification["message"]
            level = notification["level"]
            timestamp = notification["timestamp"]
            
            # Set color based on level
            if level == "ERROR":
                color = "red"
            elif level == "WARNING":
                color = "yellow"
            elif level == "SUCCESS":
                color = "green"
            else:
                color = "blue"
                
            # Create notification panel
            notification_panel = Panel(
                Text(message),
                title=f"[{level}]",
                title_align="left",
                subtitle=timestamp.strftime("%H:%M:%S"),
                subtitle_align="right",
                box=ROUNDED,
                border_style=color,
                padding=(0, 1)
            )
            
            self.console.print(notification_panel)
            
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
        
    def set_active_profile(self, profile_name, organization=None):
        """
        Set the active profile
        
        Args:
            profile_name (str): Profile name
            organization (str, optional): Organization name
        """
        self.active_profile = profile_name
        self.active_organization = organization
        
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
        if choices:
            return Prompt.ask(message, choices=choices, default=default)
        elif password:
            return Prompt.ask(message, password=True)
        else:
            return Prompt.ask(message, default=default)
        
    def confirm(self, message, default=False):
        """
        Confirm prompt
        
        Args:
            message (str): Confirmation message
            default (bool, optional): Default value
            
        Returns:
            bool: User confirmation
        """
        return Confirm.ask(message, default=default)
        
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
            border_style="cyan",
            header_style="bold cyan",
            row_styles=["white", "dim"]
        )
        
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
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]{task.description}"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task(message, total=None)
            
            try:
                # Run function
                result = func(*args, **kwargs)
                
                # Update spinner
                progress.update(task, description=f"{message} [green]Done![/green]")
                time.sleep(0.5)
                
                return result
            except Exception as e:
                # Update spinner
                progress.update(task, description=f"{message} [red]Failed![/red]")
                time.sleep(0.5)
                
                # Add notification
                self.add_notification(f"Error: {str(e)}", "ERROR")
                
                raise
                
    def update_screen(self, title, menu_items, content):
        """
        Update the entire screen
        
        Args:
            title (str): Menu title
            menu_items (list): Menu items
            content: Content to display
        """
        self.clear_screen()
        self.display_header()
        self.display_menu(title, menu_items)
        self.display_content(content)
        self.display_notifications()
        self.display_footer()
