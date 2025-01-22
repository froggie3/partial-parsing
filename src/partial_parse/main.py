import argparse
import sys
from collections.abc import Callable

from partial_parse.lib import IParsers, NameParserMixin, get_chains


class Parsers(NameParserMixin, IParsers):
    choices = ["tr", "uniq"]

    @property
    def tr_parser(self):
        parser = argparse.ArgumentParser(
            prog="tr",
            add_help=True,
            description="Translate characters using string replacement.",
        )
        parser.add_argument(
            "string1", help="the string set the character should be replaced."
        )
        parser.add_argument(
            "string2", help="the string set the character to be replaced."
        )

        def translate(old: str, new: str) -> Callable:
            def inner(original: str) -> str:
                return original.translate(str.maketrans(old, new))

            return inner

        def func(namespace):
            params = {
                "name": "tr",
                "func": translate(namespace.string1, namespace.string2),
            }
            return params

        return parser, func

    @property
    def uniq_parser(self):
        parser = argparse.ArgumentParser(
            prog="uniq",
            add_help=True,
            description="Filter adjacent duplicates with counts.",
        )
        parser.add_argument(
            "-c", "--count", action="store_true", help="show counts of each duplicate"
        )

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
    # Handle top-level help before processing chains
    if len(sys.argv) == 1 or sys.argv[1] in ["-h", "--help"]:
        print(f"Usage: {sys.argv[0]} COMMAND [ARGS]...\n")
        print("Available commands:")
        parsers = Parsers()
        for cmd in parsers.choices:
            parser, _ = parsers.get_parser(cmd)
            description = (
                parser.description
                if parser.description
                else "No description available."
            )
            print(f"  {cmd:10} {description}")
        print(f"\nUse '{sys.argv[0]} COMMAND --help' for command-specific help.")
        sys.exit(0)

    func_chains = get_chains(sys.argv[1:], Parsers())
    while line := sys.stdin.readline():
        line = line.strip()

        for item in func_chains:
            if item["name"] == "tr":
                line = item["func"](line)
            elif item["name"] == "uniq":
                line = item["func"](line)

        sys.stdout.write("%s\n" % (line,))
