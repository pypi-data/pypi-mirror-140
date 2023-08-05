# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2022 Michał Góral

from __future__ import annotations

from functools import wraps
from datetime import date

from corgi.lick.elements import Headline, Section
from corgi.lick.node import NodePredicate, Node, iter_back


def node_predicate(fn: Callable[[Node, ...], bool]) -> Callable[[...], bool]:
    """Decorator which creates a closure in place of decorated function, which
    is equivalent to:

        def fn(*args, **kwargs):
            def pred(node):
                # return code
            return pred

    Decorated functions should be used later without passing the first (Node)
    argument, just like that:

        ast.find_all(decorated_fn(arg1, arg2)
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        def pred(node):
            return fn(node, *args, **kwargs)

        return pred

    return wrapper


def _get_headlines_path(node):
    path = []

    for node in iter_back(node):
        if not node.data or not isinstance(node.data, Headline):
            break
        path.append(node.data.title)

    path.reverse()
    return path


@node_predicate
def all_match(node: Node, *predicates: NodePredicate) -> bool:
    return all(pred(node) for pred in predicates)


@node_predicate
def all_match_l(node: Node, predicates: List[NodePredicate]) -> bool:
    return all(pred(node) for pred in predicates)


@node_predicate
def any_match(node: Node, *predicates: NodePredicate) -> bool:
    return any(pred(node) for pred in predicates)


@node_predicate
def any_match_l(node: Node, predicates: List[NodePredicate]) -> bool:
    return any(pred(node) for pred in predicates)


@node_predicate
def is_visible_task(node: Node, visible_keywords: List[str]) -> bool:
    """Returns whether a node points to a visible task, i.e. the one which is a
    headline with a todo state, which is not considered "done" (on the right of
    "|" bar in org-todo-keywords). It souldn't be archived as well."""
    return (
        isinstance(node.data, Headline)
        and node.data.keyword
        and node.data.keyword in visible_keywords
        and not "ARCHIVE" in node.data.tags
    )


@node_predicate
def in_file(node: Node, filepath: str) -> bool:
    """Checks Node's metadata if it is created from a given file path. Filepath
    can be given as a basename as well."""

    fp = node.metadata.get("filepath")
    return fp == filepath or os.path.basename(fp) == filepath


@node_predicate
def has_path(node: Node, hl_path: List[str]) -> bool:
    """Returns whether a node is accessible via a given headlines path, which
    is a list of headline titles."""
    node_path = _get_headlines_path(node)
    return node_path == hl_path


@node_predicate
def any_child_of(node: Node, hl_path: List[str]) -> bool:
    """Returns whether a node is a (possibly undirect) child of another node
    under a give headlines path."""

    node_path = _get_headlines_path(node)
    return len(node_path) > len(hl_path) and node_path[0 : len(hl_path)] == hl_path


@node_predicate
def has_at_most_level(node: Node, level) -> bool:
    """Returns a headline whose level is set and at most of that given by
    `level`."""
    try:
        return node.data.level <= level
    except:
        return False


@node_predicate
def headline_with_section(node: Node) -> bool:
    return (
        isinstance(node.data, Headline)
        and node.children
        and isinstance(node.children[0].data, Section)
    )


@node_predicate
def planned_between(
    node: Node, start: Optional[date] = None, end: Optional[date] = None
) -> bool:
    """Returns whether a headline is planned (via SCHEDULE or DEADLINE) between
    the start date and end date (inclusive). Both start date and end date can
    be skipped, in which case they won't be considered when checking the dates"""

    if not headline_with_section()(node):
        return False

    def date_matches(lhs: Optional[Timestamp]):
        return lhs and (not start or lhs.date >= start) and (not end or lhs.date <= end)

    s = node.children[0].data
    return date_matches(s.deadline) or date_matches(s.scheduled)


@node_predicate
def planned_on(node: Node, when: date) -> bool:
    """Simplification of planned_between, where node's scheduled time is
    checked against a specific, non-optional date"""

    if not headline_with_section()(node):
        return False

    def date_matches(lhs: Optional[Timestamp]):
        return lhs and lhs.date == when

    s = node.children[0].data

    ret = date_matches(s.deadline) or date_matches(s.scheduled)
    return ret


@node_predicate
def deadline_between(
    node: Node, start: Optional[date] = None, end: Optional[date] = None
) -> bool:
    """Same as planned_between, but only section's deadline is checked"""

    if not headline_with_section()(node):
        return False

    def date_matches(lhs: Optional[Timestamp]):
        return lhs and (not start or lhs.date >= start) and (not end or lhs.date <= end)

    s = node.children[0].data
    return date_matches(s.deadline)


@node_predicate
def deadline_on(node: Node, when: date) -> bool:
    """Simplification of deadline_on, where node's scheduled time is
    checked against a specific, non-optional date"""

    if not headline_with_section()(node):
        return False

    def date_matches(lhs: Optional[Timestamp]):
        return lhs and lhs.date == date

    s = node.children[0].data
    return date_matches(s.deadline)


@node_predicate
def scheduled_between(
    node: Node, start: Optional[date] = None, end: Optional[date] = None
) -> bool:
    """Same as planned_between, but only section's schedule time is checked"""

    if not headline_with_section()(node):
        return False

    def date_matches(lhs: Optional[Timestamp]):
        return lhs and (not start or lhs.date >= start) and (not end or lhs.date <= end)

    s = node.children[0].data
    return date_matches(s.scheduled)


@node_predicate
def scheduled_on(node: Node, when: date) -> bool:
    """Simplification of scheduled_between, where node's scheduled time is
    checked against a specific, non-optional date"""

    if not headline_with_section()(node):
        return False

    def date_matches(lhs: Optional[Timestamp]):
        return lhs and lhs.date == when

    s = node.children[0].data
    return date_matches(s.scheduled)
