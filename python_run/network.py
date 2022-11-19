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


def download_file(url: str) -> bytes:
    with urllib.request.urlopen(url) as response:
        return response.read()
