# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2022 Michał Góral

from __future__ import annotations

import os
import copy
from functools import cache
from dataclasses import dataclass, field

import tomli

from corgi.utils import expect


def init_table(cls, val):
    if isinstance(val, dict):
        return cls(**val)
    if isinstance(val, (tuple, list)):
        return type(val)(cls(**elem) for elem in val)
    if isinstance(val, cls):
        return val
    return cls(val)


def init_dict_of_tables(cls, dct):
    return {key: cls(**val) for key, val in dct.items()}


@dataclass
class OrgCaptureTemplate:
    # https://orgmode.org/manual/Template-elements.html
    # name: str  # name is not a part of org-mode, but is required by corgi's architecture
    template: str = "* TODO"
    target: Optional[str] = None


@dataclass
class OrgTable:
    default_notes_file: str = "~/org/notes.org"
    todo_keywords: List[str] = field(default_factory=lambda: ["TODO", "|", "DONE"])

    agenda_files: List[str] = field(default_factory=lambda: ["~/org/*.org"])
    capture_templates: dict[str, OrgCaptureTemplate] = field(default_factory=dict)

    def __post_init__(self):
        self.capture_templates = init_dict_of_tables(
            OrgCaptureTemplate, self.capture_templates
        )

    def filter_todo_keywords(self):
        return [kw for kw in self.todo_keywords if kw != "|"]

    def documents(self):
        expect(isinstance(self.agenda_files, list), "org.agenda_files must be a list")
        return self.agenda_files + [self.default_notes_file]


@dataclass
class CorgiTable:
    default_editor: str = os.getenv("EDITOR", "vim") + " {}"


@dataclass
class Config:
    corgi: CorgiTable = CorgiTable()
    org: OrgTable = OrgTable()

    def __post_init__(self):
        self.corgi = init_table(CorgiTable, self.corgi)
        self.org = init_table(OrgTable, self.org)


@cache
def read_config(path):
    try:
        with open(path) as f:
            config_dct = tomli.loads(f.read())
    except FileNotFoundError:
        config_dct = {}

    return Config(**config_dct)
