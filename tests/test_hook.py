import io
import os
import re
import sys
from unittest import mock

import pytest

from python_run.hook import Hook, HookExit, add_os_getenv_audit
from python_run.permission import Permission, PermissionName, Permissions


def test_add_os_getenv_audit():
    mock_ = mock.Mock()

    sys.addaudithook(mock_)

    print(os.environ.get("TEST"))

    assert mock_.call_count == 0

    add_os_getenv_audit()

    print(os.environ.get("TEST"))

    mock_.assert_called_with("os.getenv", ("TEST",))


def test_hook_input():
    hook = Hook("", Permissions())

    assert hook("builtins.input", tuple()) is HookExit.INPUT
    assert hook("builtins.input/result", tuple()) is HookExit.INPUT


def test_hook_object_setattr():
    hook = Hook("", Permissions())

    with pytest.raises(RuntimeError):
        hook("object.__setattr__", (os.environ, "__class__", None))

    with pytest.raises(RuntimeError):
        hook("object.__setattr__", (os.environ, "__getitem__", None))


def test_hook_open():
    permissions = Permissions()
    permissions.allow_read("/tmp")
    permissions.allow_write("/tmp")

    hook = Hook("", permissions)
    hook("open", ("/tmp/file", "r", None)) is HookExit.PERMISSION_OK
    hook("open", ("/tmp/file", "w", None)) is HookExit.PERMISSION_OK


def test_hook_open_current_file():
    permissions = Permissions()

    hook = Hook("/myfile.py", permissions)
    hook("open", ("/myfile.py", "r", None)) is HookExit.OPEN_CURRENT_FILE


def test_hook_os_env():
    permissions = Permissions()

    permissions.allow_env("TEST")

    hook = Hook("", permissions)
    hook("os.putenv", ("TEST", "value")) is HookExit.PERMISSION_OK
    hook("os.unsetenv", ("TEST",)) is HookExit.PERMISSION_OK
    hook("os.getenv", ("TEST",)) is HookExit.PERMISSION_OK


def test_hook_os_exec():
    permissions = Permissions()

    permissions.allow_run("/bin/ls")

    hook = Hook("", permissions)
    hook("os.exec", ("/bin/ls", ".")) is HookExit.PERMISSION_OK


def test_hook_socket_connect():
    permissions = Permissions()

    permissions.allow_net("localhost")

    hook = Hook("", permissions)
    hook("socket.connect", (None, ("localhost", 80))) is HookExit.PERMISSION_OK


def test_hook_import():
    permissions = Permissions()

    hook = Hook("", permissions)
    hook("import", ("os",)) is HookExit.IMPORT
    hook("open", ("/tmp/file", "r", None)) is HookExit.OPEN_IMPORT


def test_hook_permission_granted():
    permissions = Permissions()

    hook = Hook("", permissions)

    with mock.patch.object(hook, "_prompt", return_value=True):
        hook("open", ("/tmp/file", "r", None)) is HookExit.PERMISSION_GRANTED


def test_hook_permission_denied():
    permissions = Permissions()

    hook = Hook("", permissions)

    with mock.patch.object(hook, "_prompt", return_value=False):
        with pytest.raises(SystemExit):
            hook("open", ("/tmp/file", "r", None))


def test_hook_prompt_granted(capsys):
    sys.stdin = io.StringIO("y")

    Hook._prompt(Permission(PermissionName.NET, "localhost"))

    out, _ = capsys.readouterr()

    assert "Python requests net to 'localhost'." in out
    assert "Run again with --allow-net to bypass this prompt." in out
    assert "Allow? [y/n] (y = yes, allow; n = no, deny) > " in out
    assert "Granted net." in out


def test_hook_prompt_denied(capsys):
    sys.stdin = io.StringIO("n")

    Hook._prompt(Permission(PermissionName.NET, "localhost"))

    out, _ = capsys.readouterr()

    assert "Python requests net to 'localhost'." in out
    assert "Run again with --allow-net to bypass this prompt." in out
    assert "Allow? [y/n] (y = yes, allow; n = no, deny) > " in out
    assert "Denied net." in out


def test_hook_prompt_unrecognized_option(capsys):
    sys.stdin = io.StringIO("ha\ny")

    Hook._prompt(Permission(PermissionName.NET, "localhost"))

    out, _ = capsys.readouterr()

    assert "Unrecognized option" in out

    assert (
        len(re.findall(r"Allow\? \[y/n\] \(y = yes, allow; n = no, deny\) >", out)) == 2
    )
