import os
import sys


def bold(text: str) -> str:
    return f"\033[1m{text}\033[0m"


def italic(text: str) -> str:
    return f"\033[3m{text}\033[0m"


def clear_lines(num: int) -> None:
    sys.stdout.write(f"\033[{num}A\033[0J")


def split_string(string: str) -> list[str]:
    return string.split(",")


def parse_address(address: str) -> tuple[str, int | None]:
    host: str
    port: str | int | None

    if address[0] == "[":
        if address[-1] == "]":
            host, port = address[1:-1], None
        else:
            host, port = address.rsplit(":", 1)
            host = host[1:-1]
    else:
        if ":" in address:
            host, port = address.rsplit(":", 1)
        else:
            host, port = address, None

    if port is not None:
        port = int(port)

    return host, port


def is_env_set(name: str) -> bool:
    return os.environ.get(name, "0").lower() in ["1", "true", "yes"]
