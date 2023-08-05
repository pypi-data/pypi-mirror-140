# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2022 Michał Góral

from __future__ import annotations

import os
import glob

"""This is private module, which mostly contains free helpers for org.Organice
and org.Document."""


def get_org_files(globs: List[str]) -> List[str]:
    """Returns absolute paths to the org files found via globbing expressions
    or inside directories passed as the argument."""
    paths = []
    for gl in globs:
        expanded = os.path.expanduser(gl)
        if os.path.isdir(expanded):
            expanded = os.path.join(expanded, "*.org")
        paths.extend(
            os.path.abspath(f) for f in glob.glob(expanded) if os.path.exists(f)
        )
    return sorted(set(paths))


def partition_keywords(keywords):
    """Partition org-todo-keywords, which is a list of keywords, optionally
    separated into 2 groups with "|" separator bar, to TODO keywords and DONE
    keywords. If separator is not found, the last keyword is considered as DONE
    keyword and all the others are TODO keywords.

    ref: https://orgmode.org/manual/Workflow-states.html"""

    try:
        sep_i = keywords.index("|")
    except ValueError:
        return tuple(keywords[:-1]), tuple(keywords[-1:])
    return tuple(keywords[:sep_i]), tuple(keywords[sep_i + 1 :])


def partition_headline_path(path):
    """Partition a notation of 'path.org/some headline/sub headline' into 2
    parts: org path and a list of headlines part"""

    path = path.strip()
    if path.endswith(".org"):
        return path, []

    end_index = path.rfind(".org/")
    if end_index == -1:
        return path, []

    # 4 == len(".org/")
    org_path = path[0 : end_index + 4]
    headlines = [title for title in path[end_index + 5 :].split("/") if title]
    return org_path, headlines


def org_name(filepath):
    """Return the name, without an extension, of a file path. This format is
    used by org-mode in many places."""
    bn = os.path.basename(filepath)
    return os.path.splitext(bn)[0]
