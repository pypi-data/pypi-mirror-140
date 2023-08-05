# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2022 Michał Góral

"""Somewhat functional helpers"""

from __future__ import annotations


def unwrap(val: Optional[T]) -> T:
    """Asserts that passed optional value is set and returns it"""
    assert val is not None
    return val


def unwrap_or(val: Optional[T], default: T) -> T:
    """If passed optional value is set, it is returned. Otherwise, a
    non-optional default is returned."""
    if val is None:
        return default
    return val


def unwrap_or_else(val: Optional[T], default_fn: Callable[[], T]) -> T:
    """If passed optional value is set, it is returned. Otherwise, a
    non-optional default is computed and returned."""
    if val is None:
        return default_fn()
    return val
