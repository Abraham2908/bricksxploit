"""
Vertical bipartite UI for BricksXploit with content on the left and notifications on the right
"""

import os
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.box import ROUNDED
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

class VerticalUI:
    """
    Vertical bipartite UI for BricksXploit with content on the left and notifications on the right
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

    def clear_screen(self):
        """
        Clear the screen
        """
        self.console.clear()

    def draw_header(self):
        """
        Draw the header with the banner from banner.py as the main element
        """
        from utils.banner import MAIN_BANNER, __version__
        from rich.align import Align

        # Create the banner text - using MAIN_BANNER for a more compact display
        banner_text = Text(MAIN_BANNER, style=f"bold {self.colors['primary']}")

        # Add version information directly to the banner
        version_text = Text(f" v{self.version}", style=f"bold {self.colors['secondary']}")
        banner_text.append(version_text)

        # Create centered banner
        centered_banner = Align.center(banner_text)

        # Create the panel with just the banner - more compact
        self.console.print(Panel(
            centered_banner,
            style="white",
            border_style=self.colors['primary'],
            width=self.terminal_width,
            padding=(0, 0)
        ))

    def draw_footer(self, selected_option=None):
        """
        Draw the footer with menu options

        Args:
            selected_option (str, optional): Currently selected option
        """
        # Create menu items text - more compact
        menu_text = ""
        if self.menu_items:
            items = []
            for i, item in enumerate(self.menu_items, 1):
                # Use shorter display names for menu items to save space
                short_name = item
                if len(short_name) > 15:  # Truncate long menu item names
                    short_name = short_name[:12] + "..."

                if selected_option and selected_option == str(i):
                    items.append(f"[bold white on {self.colors['primary']}][{i}] {short_name}[/]")
                else:
                    items.append(f"[{i}] {short_name}")
            menu_text = " | ".join(items)

        # Create profile text - more compact
        if self.active_profile:
            profile_name = self.active_profile
            if len(profile_name) > 15:  # Truncate long profile names
                profile_name = profile_name[:12] + "..."

            profile_text = f"[bold {self.colors['success']}]{profile_name}"
            if self.active_organization:
                org_name = self.active_organization
                if len(org_name) > 15:  # Truncate long organization names
                    org_name = org_name[:12] + "..."
                profile_text += f" ({org_name})[/]"
            else:
                profile_text += "[/]"
        else:
            profile_text = f"[bold {self.colors['warning']}]No profile[/]"

        # Create footer panel - more compact
        self.console.print(Panel(
            f"{menu_text}",
            title=profile_text,
            title_align="right",
            style="white",
            border_style=self.colors['primary'],
            width=self.terminal_width,
            padding=(0, 0)  # No padding for more compact display
        ))

    def draw_content_and_notifications(self, content):
        """
        Draw the content area on the left and notifications on the right

        Args:
            content: Content to display
        """
        # Get terminal dimensions
        self.terminal_width = os.get_terminal_size().columns
        self.terminal_height = os.get_terminal_size().lines

        # Ensure minimum width but don't force it to be too large
        min_width = 80
        min_height = 20  # Reduced minimum height
        max_height = 30  # Maximum height to keep interface compact

        # Use actual terminal size within constraints
        effective_width = max(self.terminal_width, min_width)
        effective_height = min(max(self.terminal_height, min_height), max_height)

        # Calculate widths for content and notifications - adaptive based on terminal width
        # For smaller terminals, give more space to content
        if effective_width < 100:
            content_ratio = 0.7  # 70% for content in small terminals
        else:
            content_ratio = 0.65  # 65% for content in larger terminals

        content_width = int(effective_width * content_ratio)
        notifications_width = effective_width - content_width - 3  # 3 for spacing

        # Calculate available height for content (terminal height - header - footer - prompt)
        # Adaptive based on terminal height
        header_footer_space = 8  # Space taken by header, footer, and prompt
        content_height = min(15, max(10, effective_height - header_footer_space))  # Limit maximum height

        # Format content panel
        content_panel = Panel(
            content,
            title=f"— {self.menu_title.upper()} —",
            title_align="center",
            style="white",
            border_style=self.colors['primary'],
            width=content_width,
            height=content_height,
            padding=(0, 1)  # Minimal padding for smaller terminals
        )

        # Format notifications panel
        notifications_panel = self.create_notifications_panel(notifications_width, content_height)

        # Create a table to hold the panels side by side
        from rich.columns import Columns
        columns = Columns([content_panel, notifications_panel], equal=False, expand=True)
        self.console.print(columns)

    def create_notifications_panel(self, width, height):
        """
        Create the notifications panel

        Args:
            width (int): Panel width
            height (int): Panel height

        Returns:
            Panel: Rich Panel object
        """
        # Create notifications content
        if not self.notifications:
            notifications_content = Text("No notifications", style="dim")
        else:
            # Show only the most recent notifications that fit in the panel
            # Limit to fewer notifications for a more compact display
            max_notifications = min(height - 2, 8)  # Maximum of 8 notifications or panel height
            recent_notifications = self.notifications[-max_notifications:] if len(self.notifications) > max_notifications else self.notifications

            # Create notification text
            notifications_content = Text()
            for i, notification in enumerate(recent_notifications):
                if i > 0:
                    notifications_content.append("\n")

                message = notification["message"]
                level = notification["level"]
                timestamp = notification["timestamp"]

                # Set color based on level
                if level == "ERROR":
                    color = self.colors["error"]
                    level_display = "ERR"
                elif level == "WARNING":
                    color = self.colors["warning"]
                    level_display = "WRN"
                elif level == "SUCCESS":
                    color = self.colors["success"]
                    level_display = "OK "
                else:
                    color = self.colors["info"]
                    level_display = "INF"

                # Add timestamp and level indicator
                notifications_content.append(timestamp.strftime("%H:%M"), style="dim")  # Shorter time format
                notifications_content.append(" ")
                notifications_content.append(f"[{level_display}]", style=f"bold {color}")
                notifications_content.append(" ")

                # Handle message with proper wrapping for long messages
                max_message_length = width - 15  # Allow space for level and timestamp

                # If message is too long, wrap it nicely
                if len(message) > max_message_length:
                    # Add first line
                    notifications_content.append(f"{message[:max_message_length-3]}...", style="white")

                    # For important messages (ERROR, WARNING), show continuation on next line
                    if level in ["ERROR", "WARNING", "SUCCESS"]:
                        # Only add continuation for longer messages
                        if len(message) > max_message_length + 20:
                            notifications_content.append("\n    ")  # Indent continuation
                            second_part = message[max_message_length-3:]
                            # Truncate second part if still too long
                            if len(second_part) > max_message_length - 5:
                                second_part = second_part[:max_message_length-8] + "..."
                            notifications_content.append(second_part, style="white dim")
                else:
                    # Message fits in one line
                    notifications_content.append(f"{message}", style="white")

        # Create notifications panel - more compact
        return Panel(
            notifications_content,
            title="— NOTIFICATIONS —",
            title_align="center",
            style="white",
            border_style=self.colors['secondary'],
            width=width,
            height=height,
            padding=(0, 1)  # Reduced vertical padding
        )

    def display(self, content, selected_option=None):
        """
        Display the UI

        Args:
            content: Content to display
            selected_option (str, optional): Currently selected option for footer
        """
        # Update terminal dimensions
        self.terminal_width = os.get_terminal_size().columns
        self.terminal_height = os.get_terminal_size().lines

        # Clear the screen
        self.clear_screen()

        # Draw header
        self.draw_header()

        # Draw content and notifications
        self.draw_content_and_notifications(content)

        # Draw footer
        self.draw_footer(selected_option)

    def set_menu(self, title, items):
        """
        Set the menu title and items

        Args:
            title (str): Menu title
            items (list): Menu items
        """
        self.menu_title = title
        self.menu_items = items

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
            border_style=self.colors["primary"],
            header_style=f"bold {self.colors['primary']}",
            row_styles=["white", f"dim {self.colors['secondary']}"],
            padding=(0, 1),
            collapse_padding=True
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
        # Create spinner
        progress = Progress(
            SpinnerColumn(),
            TextColumn(f"[{self.colors['primary']}]{{task.description}}"),
            TimeElapsedColumn(),
            console=self.console
        )

        # Add task with message
        task_id = progress.add_task(message, total=None)

        # Start progress
        progress.start()

        try:
            # Run function
            result = func(*args, **kwargs)

            # Update spinner
            progress.update(task_id, description=f"{message} [green]Done![/green]")
            time.sleep(0.5)

            return result
        except Exception as e:
            # Update spinner
            progress.update(task_id, description=f"{message} [red]Failed![/red]")
            time.sleep(0.5)

            # Add notification
            self.add_notification(f"Error: {str(e)}", "ERROR")

            raise
        finally:
            # Stop progress
            progress.stop()
