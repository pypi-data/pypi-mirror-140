# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2022 Michał Góral

import re

from corgi.ansi import Style


def style_text(s, styles=None):
    """Return a string with attached styles."""
    if not styles:
        return s

    if isinstance(styles, (list, tuple)):
        styles = "".join(styles)

    return f"{styles}{s}{Style.RESET_ALL}"


def prints(text, styles=None, **kw):
    """Styled print"""
    styled = style_text(text, styles)
    print(styled, **kw)
