import enum
import os
import socket
import sys
from typing import Any

from .network import ip2host_cache
from .permission import Permission, PermissionName, Permissions
from .utils import bold, clear_lines, is_env_set, italic, parse_address

PYTHON_NO_PROMPT = is_env_set("PYTHON_NO_PROMPT")


class HookExit(enum.IntEnum):
    INPUT = 1
    IMPORT = 2
    OPEN_IMPORT = 3
    OPEN_CURRENT_FILE = 4
    PERMISSION_OK = 5
    PERMISSION_GRANTED = 6


class Hook:
    def __init__(self, file: str, permissions: Permissions) -> None:
        self._file = file
        self._permissions = permissions
        self._imports = 0

    @classmethod
    def _prompt(cls, permission: Permission) -> bool:
        name, value = permission

        if permission.name == PermissionName.NET:
            host, _ = parse_address(permission.value)  # type: ignore

            if host in ip2host_cache:
                value = f"{permission.value} ({ip2host_cache[host]})"

        print("⚠️ ", bold(f"Python requests {name} to {value!r}."))
        print(italic(f"Run again with --allow-{name} to bypass this prompt."))

        while True:
            in_ = input(bold("Allow? [y/n] (y = yes, allow; n = no, deny) > "))
            in_ = in_.lower()

            if in_ == "y":
                clear_lines(3)
                print(f"✅ Granted {name}.")
                return True
            elif in_ == "n":
                clear_lines(3)
                print(f"❌ Denied {name}.")
                return False
            else:
                print("Unrecognized option.")

    @classmethod
    def _is_protected_os_env_attr(cls, obj: Any, attr: str) -> bool:
        return (obj is os.environ or obj is os.environb) and attr in [
            "__class__",
            "__getitem__",
        ]

    def __call__(self, event: str, args: tuple[Any, ...]) -> HookExit | None:
        permission: Permission | None = None

        match event:
            # Since we call `input` in this hook we need to avoid infinite recursion
            case "builtins.input" | "builtins.input/result":
                return HookExit.INPUT

            # Prevents the user from overriding the changes we made to `os.environ`
            case "object.__setattr__":
                obj, name, _ = args

                if self._is_protected_os_env_attr(obj, name):
                    raise RuntimeError(f"Cannot change the {name!r} of os.environ")

            # read/write access

            case "open":
                # Ignores all calls to `open` that occur due to an `import` statement
                if self._imports:
                    self._imports -= 1
                    return HookExit.OPEN_IMPORT

                path, mode, _ = args
                path = os.path.abspath(path)

                # Ignores calls to `open` the file we are running
                if path == self._file and mode == "r":
                    return HookExit.OPEN_CURRENT_FILE

                if "r" in mode:
                    permission = Permission(PermissionName.READ, path)
                elif "w" in mode or "a" in mode:
                    permission = Permission(PermissionName.WRITE, path)

            # run access

            case "os.exec":
                path, _ = args

                permission = Permission(PermissionName.RUN, path)

            # env access

            case "os.putenv" | "os.unsetenv" | "os.getenv":
                key, *_ = args

                permission = Permission(PermissionName.ENV, key)

            # net access

            case "socket.connect":
                _, address = args

                host, port = address

                permission = Permission(PermissionName.NET, f"{host}:{port}")

            case "__socket_get_host_by_name":
                host, ip = args

                ip2host_cache[ip] = host

            case "import":
                self._imports += 1
                return HookExit.IMPORT

            # End the program if the user tries to exit
            case "sys.excepthook":
                _, type, _, _ = args

                if type is KeyboardInterrupt:
                    os._exit(1)

        if permission:
            if self._permissions.check(permission):
                return HookExit.PERMISSION_OK

            if not PYTHON_NO_PROMPT and self._prompt(permission):
                self._permissions.allow(permission)
                return HookExit.PERMISSION_GRANTED
            else:
                # Throwing an exception doesn't work well because it will
                # be caught by the try...except block
                sys.exit(
                    f"Requires {permission.name} access to {permission.value!r}, "
                    f"run again with the --allow-{permission.name} flag"
                )


def add_os_getenv_audit() -> None:
    # There is no hook for `os.getenv`, so we create it
    # The user still can use `os.environ._data` to get the dict!

    class _Environ(os._Environ):
        def __getitem__(self, key):
            sys.audit("os.getenv", key)
            return super().__getitem__(key)

    os.environ.__class__ = _Environ
    os.environb.__class__ = _Environ


def patch_socket_get_host_by_name() -> None:
    # This patch helps us to convert hostname to IP address

    __socket_getaddrinfo = socket.getaddrinfo
    __socket_gethostbyname = socket.gethostbyname

    def _getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        ret = __socket_getaddrinfo(host, port, family, type, proto, flags)
        for i in ret:
            sys.audit("__socket_get_host_by_name", host, i[4][0])  # 4: address, 0: host
        return ret

    def _gethostbyname(hostname):
        ret = __socket_gethostbyname(hostname)
        sys.audit("__socket_get_host_by_name", hostname, ret)
        return ret

    socket.getaddrinfo = _getaddrinfo
    socket.gethostbyname = _gethostbyname
