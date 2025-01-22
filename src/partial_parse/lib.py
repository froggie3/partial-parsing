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


def _drive_last_help(args_ret: list[str]) -> int:
    help_count = 0
    length = len(args_ret)

    for i in range(length):
        if args_ret[i] in ("--help", "-h"):
            args_ret[i], args_ret[length - 1] = args_ret[length - 1], args_ret[i]
            help_count += 1

    help_division_at = (length - help_count) % length
    return help_division_at


def _split_help(args_ret: list[str]):
    help = []
    new_args = []

    for item in args_ret:
        if item in ("--help", "-h"):
            help.append(item)
            continue
        new_args.append(item)
    return new_args, help


def get_chains(args_ret: list[str], parsers: IParsers):
    chains = []
    args_ret, help_stack = _split_help(args_ret)

    while args_ret:
        arg_name, args_after_name = parsers.name_parser.parse_known_args(args_ret)
        curr_parser, callback = parsers.get_parser(key=arg_name.name)

        parsed_success = False
        while not parsed_success:
            parsed_so_far, args_ret = curr_parser.parse_known_args(args_after_name)

            if not args_ret and (  # entire cli arguments were so far consumed
                help_stack  # -h/--help was specified
            ):
                # regard "--help" was specified at the end of the cli argument
                args_after_name.append(help_stack.pop())
            else:
                # accepted
                chains.append(callback(parsed_so_far))
                parsed_success = True

    return chains
