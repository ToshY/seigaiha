"""Rich and pyfiglet imports"""
from rich.console import Console
import pyfiglet

c = Console()


def banner(title: str, banner_font: str = "standard", banner_width: int = 200) -> None:
    """
    Adds banner based on user specified name and font.
    """
    figlet_banner = pyfiglet.figlet_format(title, font=banner_font, width=banner_width)
    c.print(f"{figlet_banner}", style="#4577ed")
