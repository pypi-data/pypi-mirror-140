# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2022 Michał Góral

import colorama
from colorama.ansi import code_to_chars

colorama.init()

# https://en.wikipedia.org/wiki/ANSI_escape_code#SGR


class Style:
    """Extension to colorama's style and color definitions"""

    BLACK = colorama.Fore.BLACK
    RED = colorama.Fore.RED
    GREEN = colorama.Fore.GREEN
    YELLOW = colorama.Fore.YELLOW
    BLUE = colorama.Fore.BLUE
    MAGENTA = colorama.Fore.MAGENTA
    CYAN = colorama.Fore.CYAN
    WHITE = colorama.Fore.WHITE

    BG_BLACK = colorama.Back.BLACK
    BG_RED = colorama.Back.RED
    BG_GREEN = colorama.Back.GREEN
    BG_YELLOW = colorama.Back.YELLOW
    BG_BLUE = colorama.Back.BLUE
    BG_MAGENTA = colorama.Back.MAGENTA
    BG_CYAN = colorama.Back.CYAN
    BG_WHITE = colorama.Back.WHITE

    BOLD = colorama.Style.BRIGHT
    ITALIC = code_to_chars(3)
    UNDERLINE = code_to_chars(4)
    NORMAL = colorama.Style.NORMAL

    RESET_ALL = colorama.Style.RESET_ALL


def rgb(r, g, b, bg=False):
    # 38 for foreground, 48 for background
    base = 48 if bg else 38
    return code_to_chars(f"{base};2;{r};{g};{b}")
