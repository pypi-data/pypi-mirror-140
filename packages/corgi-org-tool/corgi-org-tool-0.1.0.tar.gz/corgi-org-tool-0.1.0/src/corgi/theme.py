# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2022 Michał Góral

from corgi.ansi import Style


class Theme:
    def __init__(self, **kw):
        self.__dict__ = kw


DEFAULT_THEME = Theme(
    error=[Style.BOLD, Style.RED],
    warning=[Style.BOLD, Style.YELLOW],
    todo=[Style.GREEN],
    done=[Style.WHITE],
    tags=[Style.WHITE],
    priority_A=[Style.RED],
    priority_B=[Style.YELLOW],
    priority_C=[Style.BLUE],
    normal=Style.NORMAL,
    agenda_day=[Style.WHITE, Style.BOLD],
    agenda_today=[Style.NORMAL, Style.BOLD],
)
