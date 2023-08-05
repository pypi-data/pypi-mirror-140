# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2022 Michał Góral

import argparse
import textwrap


class ArgumentParser:
    def __init__(self, *a, **kw):
        self._parser = argparse.ArgumentParser(*a, **kw)
        self._subparsers = None
        self._subpmap = {}

    @property
    def parser(self):
        return self._parser

    def parse_args(self, *a, **kw):
        return self.parser.parse_args(*a, **kw)

    def subcommand(self, name: str = None):
        """Decorator for subcommands. Decorated function will be available as a
        subcommand, which is available via args.func. For example:

            cli = args.ArgumentParser()

            @cli.subcommand()
            def mycommand():
                pass

            args = parse_args()
            args.func()
        """

        def _deco(fn):
            if not self._subparsers:
                self._subparsers = self.parser.add_subparsers()

            subpname = name if name else fn.__name__
            parser = self._subparsers.add_parser(
                subpname,
                description=textwrap.dedent(fn.__doc__),
                formatter_class=argparse.RawDescriptionHelpFormatter,
            )
            parser.set_defaults(func=fn)
            self._subpmap[fn] = parser
            return fn

        return _deco

    def arg(self, *a, **kw):
        """Decorator to add arguments to a subcommand. It passes its arguments
        directly to parser.add_argument().

        @cli.arg("foo", default=42, help="some help")
        @cli.subcommand()
        def mycommand():
            pass
        """

        def _deco(fn):
            subp = self._subpmap[fn]
            subp.add_argument(*a, **kw)
            return fn

        return _deco


class EmptyIsNone(argparse.Action):
    """An action particularily useful with nargs='*', for which default=None is
    automatically changed by argparse to the empty list. Corgi, however, uses
    a convention that unset optional value use None, not a value for which
    bool(val) == False."""

    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) == 0:
            values = None
        setattr(namespace, self.dest, values)
