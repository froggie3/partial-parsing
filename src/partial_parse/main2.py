import argparse
import sys
from collections.abc import Callable

from partial_parse.lib import IParsers, NameParserMixin, get_chains


class Parsers(NameParserMixin, IParsers):
    choices = ["tac", "sort"]

    @property
    def tac_parser(self):
        parser = argparse.ArgumentParser(
            prog="tac", add_help=True, description="Reverse the order of lines."
        )

        def func(namespace):
            params = {"name": "tac", "func": lambda s: list(reversed(s))}
            return params

        return parser, func

    @property
    def sort_parser(self):
        parser = argparse.ArgumentParser(
            prog="sort",
            add_help=True,
            description="Sort lines based on specified criteria.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=int,
            help="sort by the specified column (starting from 0)",
        )
        parser.add_argument(
            "-n", "--numeric", action="store_true", help="sort numerically"
        )
        parser.add_argument(
            "-r", "--reverse", action="store_true", help="sort in reverse order"
        )
        parser.add_argument(
            "-t", "--field-separator", help="field separator for columns"
        )

        def sortfunc(
            reverse: bool, numeric: bool, separator: str | None, key: int | None = None
        ) -> Callable:
            if key is None:
                key = 0

            def key_func(line: str) -> str | int:
                if separator is None:
                    return int(line) if numeric else line

                columns = line.split(separator)
                column = columns[key]
                return int(column) if numeric else column

            def inner(lines: list[str]):
                return sorted(lines, key=key_func, reverse=reverse)

            return inner

        def func(namespace):
            params = {
                "name": "sort",
                "func": sortfunc(
                    namespace.reverse,
                    namespace.numeric,
                    namespace.field_separator,
                    namespace.key,
                ),
            }
            return params

        return parser, func

    def get_parser(self, key: str):
        if key == "tac":
            return self.tac_parser
        elif key == "sort":
            return self.sort_parser
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

    buffer = []
    func_chains = get_chains(sys.argv[1:], Parsers())

    while line := sys.stdin.readline():
        buffer.append(line.strip())

    for item in func_chains:
        if item["name"] == "tac":
            buffer = item["func"](buffer)
        elif item["name"] == "sort":
            buffer = item["func"](buffer)

    for line in buffer:
        sys.stdout.write("%s\n" % (line,))
