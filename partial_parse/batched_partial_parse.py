import argparse
import sys

from partial_parse.lib import IParsers, NameParserMixin, get_chains


class Parsers(NameParserMixin, IParsers):
    choices = ["tac", "sort"]

    @property
    def tac_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-s", "--separator")

        def func(namespace):
            params = {
                "name": "tac",
                "func": lambda s: list(reversed(s)),
                "separator": namespace.separator,
            }
            return params

        return parser, func

    @property
    def sort_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-r", "--reverse", action="store_true")

        def func(namespace):
            params = {
                "name": "sort",
                "func": lambda lines: sorted(lines),
                "reverse": namespace.reverse,
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
