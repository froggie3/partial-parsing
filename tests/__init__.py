from partial_parse.lib import _drive_last_help, _split_help


def _test_split_help():
    test_cases = [
        (["foo", "--help", "bar", "baz"], ["foo", "bar", "baz"], ["--help"]),
        (["foo", "bar", "baz"], ["foo", "bar", "baz"], []),
        (["--help"], [], ["--help"]),
    ]

    for test_case, expected_left, expected_right in test_cases:
        left, right = _split_help(test_case)
        assert left == expected_left and right == expected_right


def _test_drive_last_help():
    test_cases = [
        (["foo", "--help", "bar", "baz"], 2),
        (["foo", "bar", "baz"], 0),
        (["--help"], 0),
    ]
    for test_case, expected in test_cases:
        return_code = _drive_last_help(test_case)
        assert return_code == expected


_test_drive_last_help()
_test_split_help()
