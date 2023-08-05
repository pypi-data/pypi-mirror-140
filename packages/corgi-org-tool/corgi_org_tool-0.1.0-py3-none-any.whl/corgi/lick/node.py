# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2022 Michał Góral

from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
from weakref import ref, ReferenceType
from typing import List, Any, Generator, Callable, Optional


def iter_dfs(root: Node) -> NodeGenerator:
    stack = deque([root])

    while stack:
        curr = stack.popleft()
        yield curr
        stack.extendleft(reversed(curr.children))


def iter_bfs(root: Node) -> NodeGenerator:
    stack = deque([root])

    while stack:
        curr = stack.popleft()
        yield curr
        stack.extend(curr.children)


def iter_back(node: Node) -> NodeGenerator:
    while node:
        yield node
        node = node.parent


@dataclass
class Node:
    data: Optional[Any] = None
    children: List[Node] = field(default_factory=list)
    _parent: Optional[ReferenceType[Node]] = field(
        default=None, init=False, compare=False, repr=False
    )
    metadata: Mapping[str, Any] = field(default=dict, compare=False, repr=False)

    def __post_init__(self):
        for ch in self.children:
            ch._parent = ref(self)

    def add_child(self, node: Node):
        self.children.append(node)
        node._parent = ref(self)

    def remove_child(self, node: Node):
        self.children.remove(node)
        node._parent = None

    @property
    def parent(self):
        if not self._parent:
            return None
        return self._parent()

    def find(
        self, pred: NodePredicate, iterator: NodeIterator = iter_dfs
    ) -> Optional[Node]:
        for node in iterator(self):
            if pred(node):
                return node

    def find_all(
        self, pred: NodePredicate, iterator: NodeIterator = iter_dfs
    ) -> Optional[Node]:
        for node in iterator(self):
            if pred(node):
                yield node

    def find_back(self, pred: NodePredicate) -> Optional[Node]:
        return self.find(pred, iter_back)

    def __getitem__(self, index):
        return self.children[index]

    def __str__(self):
        strings = []
        for node in iter_dfs(self):
            if not node.data:
                continue
            strings.append(node.data.text)
        return "\n".join(strings)


NodeGenerator = Generator[Node, None, None]
NodeIterator = Callable[[Node], NodeGenerator]
NodePredicate = Callable[[Node], bool]
