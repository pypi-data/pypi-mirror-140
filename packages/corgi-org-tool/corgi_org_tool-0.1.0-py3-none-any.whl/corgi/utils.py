# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2022 Michał Góral

from __future__ import annotations

import sys
import bisect
import itertools
from dataclasses import dataclass, field

from corgi.theme import DEFAULT_THEME as th
from corgi.format import prints


class CorgiError(Exception):
    pass


def eprint(text, **kw):
    kw["file"] = sys.stderr
    prints(text, styles=th.error, **kw)


def expect(cond: bool, msg: str, exc: Exception = CorgiError):
    if not cond:
        raise exc(msg)


def read_input(path: str):
    if not sys.stdin.isatty() or path == "-":
        input_stream = sys.stdin
    else:
        input_stream = open(path)

    text = input_stream.read()
    input_stream.close()
    return text
