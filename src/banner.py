"""Banner"""
import pyfiglet
from rich.console import Console

console = Console()


def cli_banner(
    banner_title: str,
    banner_font: str = "slant",
    banner_color: str = "#4577ED",
    banner_width: int = 200,
) -> None:
    """
    CLI banner.
    """

    banner = pyfiglet.figlet_format(banner_title, font=banner_font, width=banner_width)
    console.print(banner, style=banner_color)
