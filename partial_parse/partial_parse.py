import argparse
import sys

from partial_parse.lib import IParsers, NameParserMixin, get_chains


class Parsers(NameParserMixin, IParsers):
    choices = ["tr", "uniq"]

    @property
    def tr_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("string1")
        parser.add_argument("string2")

        def replace(original: str, old: str, new: str) -> str:
            return original.replace(old, new)

        def func(namespace):
            params = {
                "name": "tr",
                "func": replace,
                "string1": namespace.string1,
                "string2": namespace.string2,
            }
            return params

        return parser, func

    @property
    def uniq_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--count", action="store_true")

        def uniq_wrapper(string: str, is_count: bool) -> str:
            from itertools import groupby

            def default_uniq(original: str) -> str:
                return "".join("%s" % (k,) for k, _ in groupby(original))

            def count_uniq(original: str) -> str:
                return "@".join(
                    "%s=%d" % (k, len(list(grouper)))
                    for k, grouper in groupby(original)
                )

            return count_uniq(string) if is_count else default_uniq(string)

        def func(namespace):
            params = {"name": "uniq", "func": uniq_wrapper, "count": namespace.count}
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
                line = item["func"](line, item["string1"], item["string2"])
            elif item["name"] == "uniq":
                line = item["func"](line, item["count"])

        sys.stdout.write("%s\n" % (line,))
