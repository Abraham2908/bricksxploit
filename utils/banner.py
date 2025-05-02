"""
ASCII art banners and UI elements for BricksXploit
"""

import random
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Versão do software
__version__ = "1.0.0"

console = Console()

# Compact ASCII art banner
MAIN_BANNER = """
██████╗ ██████╗ ██╗ ██████╗██╗  ██╗███████╗██╗  ██╗██████╗ ██╗      ██████╗ ██╗████████╗
██╔══██╗██╔══██╗██║██╔════╝██║ ██╔╝██╔════╝╚██╗██╔╝██╔══██╗██║     ██╔═══██╗██║╚══██╔══╝
██████╔╝██████╔╝██║██║     █████╔╝ ███████╗ ╚███╔╝ ██████╔╝██║     ██║   ██║██║   ██║
██╔══██╗██╔══██╗██║██║     ██╔═██╗ ╚════██║ ██╔██╗ ██╔═══╝ ██║     ██║   ██║██║   ██║
██████╔╝██║  ██║██║╚██████╗██║  ██╗███████║██╔╝ ██╗██║     ███████╗╚██████╔╝██║   ██║
╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝   ╚═╝
"""

# Very compact banner for smaller terminals
SMALL_BANNER = """
╔╗ ╦═╗╦╔═╗╦╔═╔═╗═╗ ╦╔═╗╦  ╔═╗╦╔╦╗
╠╩╗╠╦╝║║  ╠╩╗╚═╗╔╩╦╝╠═╝║  ║ ║║ ║
╚═╝╩╚═╩╚═╝╩ ╩╚═╝╩ ╚═╩  ╩═╝╚═╝╩ ╩
"""

# Ultra compact banner for tiny terminals
TINY_BANNER = """BRICKSXPLOIT"""

# Tagline not used in the new interface design
TAGLINES = [
    "Enumerate, Scan, Report, Secure",
    "Find Databricks Security Issues Before Others Do",
    "Databricks Security Testing Made Easy"
]
