import os
from unittest import mock

import pytest

from python_run.utils import (
    bold,
    clear_lines,
    is_env_set,
    italic,
    parse_address,
    split_string,
)


@pytest.mark.parametrize(
    "address, expected",
    [
        ("127.220.49.63:80", ("127.220.49.63", 80)),
        ("127.220.49.63", ("127.220.49.63", None)),
        (
            "[b5f3:09b0:a6cc:1d08:4349:c382:d7f9:7402]:443",
            ("b5f3:09b0:a6cc:1d08:4349:c382:d7f9:7402", 443),
        ),
        (
            "[b5f3:09b0:a6cc:1d08:4349:c382:d7f9:7402]",
            ("b5f3:09b0:a6cc:1d08:4349:c382:d7f9:7402", None),
        ),
    ],
)
def test_parse_address(address, expected):
    assert parse_address(address) == expected


def test_is_env_set():
    with mock.patch.dict(os.environ, {"PYTHON_NO_PROMPT": ""}):
        assert not is_env_set("PYTHON_NO_PROMPT")

    with mock.patch.dict(os.environ, {"PYTHON_NO_PROMPT": "1"}):
        assert is_env_set("PYTHON_NO_PROMPT")


def test_split_string():
    assert split_string("github.com,127.0.0.1") == ["github.com", "127.0.0.1"]


def test_bold():
    assert bold("hello") == "\033[1mhello\033[0m"


def test_italic():
    assert italic("hello") == "\033[3mhello\033[0m"


def test_clear_lines(capsys):
    clear_lines(1)

    out, _ = capsys.readouterr()

    assert out == "\033[1A\033[0J"
