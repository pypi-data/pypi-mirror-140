# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2022 Michał Góral

from __future__ import annotations

import os
import sys
import glob
from dataclasses import dataclass, field
from functools import partial
from operator import itemgetter

from corgi.config import Config
from corgi.utils import read_input, expect

from corgi._org import *

from corgi.lick.parser import Parser
from corgi.lick.elements import Headline, Section
from corgi.lick.node import Node, NodePredicate
from corgi.node_predicates import all_match, any_match_l, any_child_of


lazy = partial(field, init=False, repr=False)


@dataclass
class Document:
    """Class which is used for lazy initialization of Nodes"""

    _path: str
    _config: Config
    _ast: Optional[Node] = field(default=None, init=False, repr=False)

    def __call__(self):
        if not self._ast:
            parser = Parser(self._config)
            md = {"filepath": self.path}
            self._ast = parser.parse(read_input(self.path))

        return self._ast

    @property
    def path(self):
        return self._path

    @property
    def org_name(self):
        return org_name(self.path)


@dataclass
class Organicer:
    config: Config = field(repr=False)

    _documents: Mapping[str, Document] = field(
        init=False, repr=False, default_factory=dict
    )

    _org_path_map: Mapping[str, str] = field(
        init=False, repr=False, default_factory=dict
    )
    _todo_kw: Optional[List[str]] = field(init=False, repr=False)
    _done_kw: Optional[List[str]] = field(init=False, repr=False)

    def __post_init__(self):
        self._todo_kw, self._done_kw = partition_keywords(self.config.org.todo_keywords)

    def load_documents(self, patterns):
        for path in get_org_files(patterns):
            self._documents[path] = Document(path, self.config)
            self._org_path_map.setdefault(os.path.basename(path), path)

    def document(self, path: str) -> Document:
        """Support fetching documents either by their full (absolute) path or
        by their basename."""
        try:
            return self._documents[self._org_path_map[path]]
        except KeyError:
            return self._documents.get(path)

    @property
    def todo_keywords(self):
        return self._todo_kw

    @property
    def done_keywords(self):
        return self._done_kw

    def find_nodes(
        self, pred: NodePredicate, paths: Optional[List[str]] = None
    ) -> Generator[Tuple[Document, Node], None, None]:
        """Quality of life function, which handles the burden of checking for
        the emptiness of list of paths."""
        if paths:
            return self.find_nodes_under_paths(paths, pred)
        else:
            return self.find_all_nodes(pred)

    def find_all_nodes(
        self, pred: NodePredicate
    ) -> Generator[Tuple[Document, Node], None, None]:
        for doc in self._documents.values():
            for node in doc().find_all(pred):
                yield doc, node

    def find_nodes_under_paths(
        self, paths: List[str], pred: NodePredicate
    ) -> Generator[Tuple[Document, Node], None, None]:
        partitioned = {}
        for p in paths:
            path, hl_path = partition_headline_path(p)
            hl_paths = partitioned.setdefault(path, []).append(hl_path)

        for path, hl_paths in partitioned.items():
            doc = self.document(path)
            if doc:
                node_matcher = all_match(
                    pred, any_match_l([any_child_of(hlp) for hlp in hl_paths])
                )

                for node in doc().find_all(node_matcher):
                    yield doc, node
