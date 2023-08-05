# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2022 Michał Góral

from __future__ import annotations

import sys
import os
import bisect
from functools import partial

from corgi.args import ArgumentParser, EmptyIsNone
from corgi.org import Organicer, Document
from corgi.utils import CorgiError, eprint, read_input
from corgi.config import read_config
from corgi.agenda import agenda_view

from corgi.lick.parser import Parser
from corgi.lick.jsonizer import to_json, from_json
from corgi.lick.elements import Headline
from corgi.lick.node import Node

HOME = os.path.expanduser("~")

cli = ArgumentParser()
cli.parser.add_argument(
    "-c",
    "--config",
    nargs="?",
    default=os.path.join(
        os.getenv("XDG_CONFIG_HOME", os.path.join(HOME, ".config")),
        "corgi",
        "config.toml",
    ),
    help="specific path to corgi's configuration file.",
)


@cli.arg(
    "-f",
    "--filter-path",
    action="append",
    dest="filter_paths",
    help="filter output to the headlines given by path. This option can be used more than once.",
)
@cli.arg("--todo", action="store_true", help="list of all TODO entries")
@cli.arg(
    "documents",
    nargs="*",
    action=EmptyIsNone,
    help="agenda files or patterns used instead of the ones from the configuration file",
)
@cli.subcommand("agenda")
def agenda_cmd(args, config):
    """Show org-agenda of planned tasks"""
    return agenda_view(args, config)


@cli.subcommand("capture")
def capture(args, config):
    """
    org-capture implementation: quickly capture and refile org-mode
    headings from a template"""
    eprint("corgi capture is not yet implemented")
    return 1


@cli.arg("--pretty", action="store_true", help="pretty-print output json")
@cli.arg(
    "input",
    nargs="?",
    default="-",
    help="input source; can be a file path or dash '-' for interactive input",
)
@cli.subcommand("serialize")
def serialize(args, config):
    """
    Parse given string as org-mode format and serialize it to json. The
    input can be piped to corgi, interactively sent via stdin (stream is
    terminated with C-d) or read from the file."""
    doc = Document(args.input, config)
    print(to_json(doc(), pretty=args.pretty))


@cli.arg(
    "input",
    nargs="?",
    default="-",
    help="input source; can be a file path or dash '-' for interactive input",
)
@cli.subcommand("deserialize")
def deserialize(args, config):
    """
    Deserialize input json, which is in format outputted by `corgi parse`
    and rebuild the org document from it. Org document is equivalent to the
    originally serialized document, meaning that some whitespaces might be not
    preserved.

    The input can be piped to corgi, interactively sent via stdin
    (stream is terminated with C-d) or read from the file. Corgi understands
    json format outputted by `corgi parse.`"""
    text = read_input(args.input)
    ast = from_json(text)
    print(str(ast))


def main_():
    args = cli.parse_args()
    config = read_config(args.config)

    if not hasattr(args, "func"):
        eprint("No subcommand given. See corgi --help")
        return 1

    try:
        return args.func(args, config)
    except CorgiError as e:
        eprint(str(e))
        return 1


def main():
    sys.exit(main_())
