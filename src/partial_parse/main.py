import argparse
import sys
from collections.abc import Callable

from partial_parse.lib import IParsers, NameParserMixin, get_chains


class Parsers(NameParserMixin, IParsers):
    choices = ["tr", "uniq"]

    @property
    def tr_parser(self):
        parser = argparse.ArgumentParser(prog="tr", add_help=True)
        parser.add_argument("string1")
        parser.add_argument("string2")

        def replace(old: str, new: str) -> Callable:
            def inner(original: str) -> str:
                return original.replace(old, new)

            return inner

        def func(namespace):
            params = {
                "name": "tr",
                "func": replace(namespace.string1, namespace.string2),
            }
            return params

        return parser, func

    @property
    def uniq_parser(self):
        parser = argparse.ArgumentParser(prog="uniq", add_help=True)
        parser.add_argument("-c", "--count", action="store_true")

        def uniq_wrapper(is_count: bool) -> Callable:
            from itertools import groupby

            def default_uniq(original: str) -> str:
                return "".join("%s" % (k,) for k, _ in groupby(original))

            def count_uniq(original: str) -> str:
                return "@".join(
                    "%s=%d" % (k, len(list(grouper)))
                    for k, grouper in groupby(original)
                )

            def inner(string: str) -> str:
                return count_uniq(string) if is_count else default_uniq(string)

            return inner

        def func(namespace):
            params = {"name": "uniq", "func": uniq_wrapper(namespace.count)}
            return params

        return parser, func

    def get_parser(self, key):
        if key == "tr":
            return self.tr_parser
        if key == "uniq":
            return self.uniq_parser
        else:
            raise KeyError


if __name__ == "__main__":
    func_chains = get_chains(sys.argv[1:], Parsers())
    while line := sys.stdin.readline():
        line = line.strip()

        for item in func_chains:
            if item["name"] == "tr":
                line = item["func"](line)
            elif item["name"] == "uniq":
                line = item["func"](line)

        sys.stdout.write("%s\n" % (line,))
