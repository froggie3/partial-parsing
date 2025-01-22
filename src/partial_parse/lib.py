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
        name_parsed_success = False
        args_after_name = None
        curr_parser = None
        callback = None

        while not name_parsed_success:
            arg_name, args_after_name = parsers.name_parser.parse_known_args(args_ret)
            curr_parser, callback = parsers.get_parser(key=arg_name.name)

            if not args_after_name and (  # entire cli arguments were so far consumed
                help_stack  # -h/--help was specified
            ):
                # regard "--help" was specified at the end of the cli argument
                args_ret.append(help_stack.pop())
                continue
            # accepted
            name_parsed_success = True

        if curr_parser is None or args_after_name is None or callback is None:
            raise Exception("failed to parse an argument")

        arg_parsed_success = False
        parsed_so_far = None

        while not arg_parsed_success:
            parsed_so_far, args_ret = curr_parser.parse_known_args(args_after_name)

            if not args_ret and (  # entire cli arguments were so far consumed
                help_stack  # -h/--help was specified
            ):
                # regard "--help" was specified at the end of the cli argument
                args_after_name.append(help_stack.pop())
                continue
            # accepted
            arg_parsed_success = True

        if parsed_so_far is not None:
            chains.append(callback(parsed_so_far))

    return chains
