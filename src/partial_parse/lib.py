import abc
import argparse
from collections.abc import Callable


class NameParserMixin:
    choices: list[str]

    @property
    def name_parser(self):
        parser = argparse.ArgumentParser(
            # setting this as True interferes any other rest parsers
            # showing their help messages :(
            add_help=False
        )
        parser.add_argument("name", choices=self.choices)

        return parser


class ParserGettable:
    @abc.abstractmethod
    def get_parser(self, key: str) -> tuple[argparse.ArgumentParser, Callable]: ...


class NameParser:
    @property
    @abc.abstractmethod
    def name_parser(self) -> argparse.ArgumentParser: ...


class IParsers(ParserGettable, NameParser):
    pass


def get_chains(args_ret: list[str], parsers: IParsers):
    chains = []

    while args_ret:
        arg_name, args_after_name = parsers.name_parser.parse_known_args(args_ret)
        curr_parser, callback = parsers.get_parser(key=arg_name.name)
        parsed_so_far, args_ret = curr_parser.parse_known_args(args_after_name)
        chains.append(callback(parsed_so_far))

    return chains
