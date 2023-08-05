import os
import json

from corgi.lick.node import Node
from corgi.lick.elements import Section, Headline


class NodeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Node):
            if not obj.data:  # root node is serialized to a simple array
                return obj.children

            ret = {}
            if isinstance(obj.data, (Section, Headline)):
                ret.update(obj.data.__json__())
            else:
                raise ValueError(f"Unsupported data type for json {type(obj.data)}")
            if isinstance(obj.data, Headline):
                ret["children"] = obj.children
            return ret

        return super().default(obj.data)


def decode_json(dct):
    obj_type = dct.pop("type")
    if obj_type == "section":
        # split('\n') is different than Section's splitlines() when string ends
        # with a newline. Thanks to split('\n') we can preserve empty lines.
        return Node(Section(dct["text"].split(os.linesep)))
    elif obj_type == "headline":
        children = dct.pop("children", [])
        return Node(Headline(**dct), children=children)
    else:
        raise ValueError(f"Invalid type of org object: {obj_type}")


def to_json(node, pretty=False, ascii=False):
    indent = 4 if pretty else None
    return json.dumps(node, cls=NodeEncoder, indent=indent, ensure_ascii=ascii)


def from_json(text):
    nodes = json.loads(text, object_hook=decode_json)
    if not isinstance(nodes, list):
        raise ValueError(f"Expected list of elements, got {type(nodes)}")
    return Node(children=nodes)
