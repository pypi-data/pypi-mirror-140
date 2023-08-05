# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2022 Michał Góral

"""org-mode parser, which parses org files to the list of json-serializable
Python objects, which contain data about each parsed element and its children.

org-mode grammar is defined here: https://orgmode.org/worg/dev/org-syntax.html

Example json output could look like this:

<<EOF
#+TITLE

* TODO Hello  :tag1:tag2:
  This was a triumph
  I'm making a note here
** Goodbye
EOF

[
    { "type": "section", "text": "#+TITLE: My Document\n\n" },
    {
        "type": "headline",
        "text": "* Hello  :tag1:tag2:",
        "level": 1,
        "keyword": "TODO",
        "priority": null,
        "title": "Hello",
        "tags": ["tag1", "tag2"],
        "children": [
            {
                "type": "section",
                "text": "  This was a triumph\n  I'm making a note here\n"
            },
            {
                "type": "headline",
                "text": "** Goodbye",
                "level": 2,
                "keyword: null,
                priority: null,
                title: "Goodbye",
                "keyword": null
                "children": []
            }
        ]
    }
]
"""

from __future__ import annotations

import re
from datetime import date, time

from typing import Any, Optional

from corgi.utils import expect
from corgi.lick.elements import Headline, Section, Timestamp
from corgi.lick.node import Node
from corgi.node_predicates import has_at_most_level


class Parser:
    def __init__(self, config):
        self._config = config

        self._headline_re = re.compile(
            r"""^
                (?P<level>\*+)
                (?:\s+(?P<keyword>\w+))?
                (?:\s+\[\#(?P<priority>[A-Z])\])?
                (?:\s+(?P<title>.+))?
                $""",
            re.VERBOSE,
        )

        self._tags_re = re.compile(r"\s:(?P<tags>[\w@#%:]+):\s*$")

        self._timestamp_re = re.compile(
            r"""(?P<date>\d{4}-\d{2}-\d{2})
                \s+(?P<dayname>[^\s0-9+\]>]+)
                (?:\s+(?P<time>[0-2]?\d:\d{2}))?
                (?:\s+(?P<rep_mark>\+|\+\+|\.\+|-|--)){0,2}""",
            re.VERBOSE,
        )

        self._planning_re = re.compile(
            r"""(?P<keyword>DEADLINE|SCHEDULED|CLOSED):\s+
                (?P<timestamp><.+?>|\[.+?\])""",
            re.VERBOSE,
        )

        self._keywords = set(self._config.org.filter_todo_keywords())

    def parse(self, document):
        """Parse the whole org document"""

        root = Node()
        last_hl = root
        last_section = []

        for line in document.splitlines():
            hl = self.parse_headline(line)
            if hl:
                section = self.parse_section(last_section)
                if section:
                    last_hl.add_child(Node(section))

                hl_node = Node(hl)
                parent = last_hl.find_back(has_at_most_level(hl.level - 1)) or root
                parent.add_child(hl_node)

                last_section = []
                last_hl = hl_node
            else:
                last_section.append(line.rstrip())

        section = self.parse_section(last_section)
        if section:
            last_hl.add_child(Node(section))

        return root

    def parse_headline(self, text: str) -> Headline:
        m = self._headline_re.search(text)
        if not m:
            return None

        level = len(m.group("level"))
        kw = m.group("keyword")
        prio = m.group("priority")
        title = m.group("title")
        tags = []

        # Regular expression simplifies headline, but org syntax requires that
        # keywords are in org-todo-keywords set. We do a post-processing step
        # for that: if "what-looks-like-a-keyword" is not in org-todo-keywords
        # list, we consider everything from the start of such "fake keyword" as
        # a title and disregard other parsed elements (priority)
        if kw and kw not in self._keywords:
            kw_start = m.span("keyword")[0]
            title = text[kw_start:]
            prio = None
            kw = None

        if title:
            tm = self._tags_re.search(title)
            if tm:
                # span of the whole match, including the first colon and a
                # separating whitespace, not only P<tags> group.
                tags_start = tm.span()[0]
                tags = tm.group("tags").split(":")
                title = title[0:tags_start]

            title = title.strip()

        return Headline(
            text=text, level=level, keyword=kw, priority=prio, title=title, tags=tags
        )

    def parse_section(self, lines: List[str]) -> Optional[Section]:
        if _empty_section(lines):
            return None

        kw = {}
        kw.update(self._parse_planning(lines[0]))
        return Section(lines, **kw)

    def _parse_planning(self, line: str) -> Mapping[str, Timestamp]:
        ret = {}
        matches = self._planning_re.findall(line)
        for kw, ts_str in matches:
            ret[kw.lower()] = self._parse_timestamp(ts_str)
        return ret

    def _parse_timestamp(self, ts_str: str) -> Optional[Timestamp]:
        m = self._timestamp_re.search(ts_str[1:-1])
        if not m:
            return None

        try:
            ts = Timestamp(
                date.fromisoformat(m.group("date")), active=ts_str.startswith("<")
            )

            if m.group("time"):
                ts.time = time.fromisoformat(m.group("time"))
        except ValueError:
            return None

        if m.group("rep_mark"):
            ts.repeater = m.group("rep_mark")

        return ts


def _empty_section(lines: List[str]) -> bool:
    return not lines or all(not l for l in lines)
