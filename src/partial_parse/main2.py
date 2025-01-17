import argparse
import sys
from collections.abc import Callable

from partial_parse.lib import IParsers, NameParserMixin, get_chains


class Parsers(NameParserMixin, IParsers):
    choices = ["tac", "sort"]

    @property
    def tac_parser(self):
        parser = argparse.ArgumentParser(prog="tac", add_help=True)

        def func(namespace):
            params = {"name": "tac", "func": lambda s: list(reversed(s))}
            return params

        return parser, func

    @property
    def sort_parser(self):
        parser = argparse.ArgumentParser(prog="sort", add_help=True)
        parser.add_argument("-k", "--key", type=int)
        parser.add_argument("-n", "--numeric", action="store_true")
        parser.add_argument("-r", "--reverse", action="store_true")
        parser.add_argument("-t", "--field-separator")

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
