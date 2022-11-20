import ipaddress
import socket
import urllib.request


def is_ip_address(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def host2ip(host: str, port: int | None = None) -> str | None:
    try:
        for *_, addr in socket.getaddrinfo(host, port):
            return addr[0]
    except socket.gaierror:
        pass


ip2host_cache: dict[str, str] = {}


def download_file(url: str) -> bytes:
    with urllib.request.urlopen(url) as response:
        return response.read()


def is_remote_file(file: str) -> bool:
    return file.startswith("http://") or file.startswith("https://")
