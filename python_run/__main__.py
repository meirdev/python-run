import argparse
import os
import runpy
import sys

from .hook import Hook, add_os_getenv_audit, patch_socket_get_host_by_name
from .permission import Permission, PermissionAll, PermissionName, Permissions
from .utils import split_string


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        "--allow-env",
        nargs="?",
        const=True,
        default=False,
        type=split_string,
        help="Allow environment access for things like getting and setting of environment variables. You can specify an optional, comma-separated list of environment variables to provide an allow-list of allowed environment variables.",
    )
    arg_parser.add_argument(
        "--allow-net",
        nargs="?",
        const=True,
        default=False,
        type=split_string,
        help="Allow network access. You can specify an optional, comma-separated list of IP addresses or hostnames (optionally with ports) to provide an allow-list of allowed network addresses.",
    )
    arg_parser.add_argument(
        "--allow-read",
        nargs="?",
        const=True,
        default=False,
        type=split_string,
        help="Allow file system read access. You can specify an optional, comma-separated list of directories or files to provide an allow-list of allowed file system access.",
    )
    arg_parser.add_argument(
        "--allow-write",
        nargs="?",
        const=True,
        default=False,
        type=split_string,
        help="Allow file system write access. You can specify an optional, comma-separated list of directories or files to provide an allow-list of allowed file system access.",
    )
    arg_parser.add_argument(
        "--allow-run",
        nargs="?",
        const=True,
        default=False,
        type=split_string,
        help="Allow running subprocesses. You can specify an optional, comma-separated list of subprocesses to provide an allow-list of allowed subprocesses. ",
    )
    arg_parser.add_argument(
        "--allow-all",
        "-A",
        action="store_true",
        default=False,
        help="Allow all permissions.",
    )

    return arg_parser.parse_known_intermixed_args()


def get_permissions(opts: argparse.Namespace) -> Permissions:
    permissions = Permissions()

    if opts.allow_all:
        for i in PermissionName:
            permissions.allow(Permission(i, PermissionAll))
    else:
        for name, value in {
            PermissionName.ENV: opts.allow_env,
            PermissionName.NET: opts.allow_net,
            PermissionName.READ: opts.allow_read,
            PermissionName.WRITE: opts.allow_write,
            PermissionName.RUN: opts.allow_run,
        }.items():
            if value is True:
                permissions.allow(Permission(name, PermissionAll))
            elif isinstance(value, list):
                for i in value:
                    permissions.allow(Permission(name, i))

    return permissions


def main() -> None:
    opts, cmd = parse_args()

    file, *args = cmd
    file = os.path.abspath(file)

    permissions = get_permissions(opts)

    hook = Hook(file, permissions)

    add_os_getenv_audit()

    patch_socket_get_host_by_name()

    sys.dont_write_bytecode = True

    sys.argv[1:] = [file, *args]

    sys.addaudithook(hook)

    runpy.run_path(file, run_name="__main__")


if __name__ == "__main__":  # pragma: no cover
    main()
