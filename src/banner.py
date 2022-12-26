# -*- coding: utf-8 -*-
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
    CLI banner

    Parameters
    ----------
    banner_title : str
        Main file.
    banner_font : str, optional
        Banner font type. The default is "slant".
    banner_color : str, optional
        Banner color. The default is "#4577ED" (orange).
    banner_width : int, optional
        Banner width. The default is 200.

    Returns
    -------
    None.

    """

    banner = pyfiglet.figlet_format(banner_title, font=banner_font, width=banner_width)
    console.print(banner, style=banner_color)
