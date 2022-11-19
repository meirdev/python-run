import enum
import os
from typing import NamedTuple, Type

from .utils import parse_address


class PermissionName(str, enum.Enum):
    ENV = "env"
    NET = "net"
    READ = "read"
    WRITE = "write"
    RUN = "run"


class PermissionAll:
    pass


PermissonValue = str | Type[PermissionAll]


class Permission(NamedTuple):
    name: PermissionName
    value: PermissonValue


class Permissions:
    def __init__(self) -> None:
        self._permissions: set[Permission] = set()

    def _check(self, permission: Permission, full_match: bool = True) -> bool:
        if Permission(permission.name, PermissionAll) in self._permissions:
            return True

        if full_match:
            return permission in self._permissions

        return any(
            perm == permission.name and permission.value.startswith(val)  # type: ignore
            for perm, val in self._permissions
        )

    def _allow(self, permission: Permission) -> None:
        self._permissions.add(permission)

    def allow(self, permission: Permission) -> None:
        name, value = permission

        match name:
            case PermissionName.ENV:
                return self.allow_env(value)
            case PermissionName.NET:
                return self.allow_net(value)
            case PermissionName.READ:
                return self.allow_read(value)
            case PermissionName.WRITE:
                return self.allow_write(value)
            case PermissionName.RUN:
                return self.allow_run(value)

    def allow_env(self, value: PermissonValue) -> None:
        self._allow(Permission(PermissionName.ENV, value))

    def allow_net(self, value: PermissonValue) -> None:
        if value is PermissionAll:
            self._permissions.add(Permission(PermissionName.NET, PermissionAll))
            return

        host, port = parse_address(value)  # type: ignore

        if port is not None:
            self._permissions.add(Permission(PermissionName.NET, f"{host}:{port}"))
        else:
            self._permissions.add(Permission(PermissionName.NET, host))

    def allow_read(self, value: PermissonValue) -> None:
        if value is not PermissionAll:
            value = os.path.abspath(value)

        self._allow(Permission(PermissionName.READ, value))

    def allow_write(self, value: PermissonValue) -> None:
        if value is not PermissionAll:
            value = os.path.abspath(value)

        self._allow(Permission(PermissionName.WRITE, value))

    def allow_run(self, value: PermissonValue) -> None:
        self._allow(Permission(PermissionName.RUN, value))

    def check(self, permission: Permission) -> bool:
        name, value = permission

        match name:
            case PermissionName.ENV:
                return self.check_env(value)
            case PermissionName.NET:
                return self.check_net(value)
            case PermissionName.READ:
                return self.check_read(value)
            case PermissionName.WRITE:
                return self.check_write(value)
            case PermissionName.RUN:
                return self.check_run(value)

    def check_env(self, value: PermissonValue) -> bool:
        return self._check(Permission(PermissionName.ENV, value))

    def check_net(self, value: PermissonValue) -> bool:
        if Permission(PermissionName.NET, PermissionAll) in self._permissions:
            return True

        host, _ = parse_address(value)  # type: ignore

        return (
            Permission(PermissionName.NET, host) in self._permissions
            or Permission(PermissionName.NET, value) in self._permissions
        )

    def check_read(self, value: PermissonValue) -> bool:
        return self._check(Permission(PermissionName.READ, value), full_match=False)

    def check_write(self, value: PermissonValue) -> bool:
        return self._check(Permission(PermissionName.WRITE, value), full_match=False)

    def check_run(self, value: PermissonValue) -> bool:
        return self._check(Permission(PermissionName.RUN, value))
