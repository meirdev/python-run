from unittest import mock

import pytest

from python_run.network import download_file, host2ip, is_ip_address


@pytest.mark.parametrize(
    "value, expected",
    [
        ("127.220.49.63", True),
        ("b5f3:09b0:a6cc:1d08:4349:c382:d7f9:7402", True),
        ("github.com", False),
    ],
)
def test_is_ip_address(value, expected):
    assert is_ip_address(value) == expected


def test_host2ip():
    assert host2ip("localhost") == "127.0.0.1"


def test_host2ip_error():
    assert host2ip("home") is None


def test_download_file():
    open_mock = mock.Mock(
        __enter__=mock.Mock(
            return_value=mock.Mock(
                read=mock.Mock(return_value=b"hello"),
            ),
        ),
        __exit__=mock.Mock(),
    )

    with mock.patch("urllib.request.urlopen", return_value=open_mock):
        assert download_file("https://example.com") == b"hello"
