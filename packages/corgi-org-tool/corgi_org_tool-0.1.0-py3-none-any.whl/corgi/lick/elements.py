# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2022 Michał Góral

"""Headline parser and parsing result"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import time

from corgi.functional import unwrap_or


@dataclass
class Timestamp:
    date: datetime.date
    time: Optional[datetime.time] = None
    repeater: Optional[str] = None
    active: bool = True

    def __lt__(self, other):
        return (self.date, unwrap_or(self.time, time())) < (
            other.date,
            unwrap_or(other.time, time()),
        )


@dataclass
class Section:
    _lines: List[str] = field(default_factory=list)
    scheduled: Optional[Timestamp] = None
    deadline: Optional[Timestamp] = None
    closed: Optional[Timestamp] = None

    def __post_init__(self):
        if isinstance(self._lines, str):
            self._lines = self._lines.splitlines()

    @property
    def text(self):
        return os.linesep.join(self._lines)

    def add_line(self, line):
        self._lines.append(line.rstrip())

    def __json__(self):
        return {"type": "section", "text": self.text}


@dataclass
class Headline:
    text: str
    level: int = 1
    keyword: Optional[str] = None
    priority: Optional[str] = None
    title: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def __json__(self):
        return {
            "type": "headline",
            "text": self.text,
            "level": self.level,
            "keyword": self.keyword,
            "priority": self.priority,
            "title": self.title,
            "tags": self.tags,
        }
