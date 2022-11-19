from python_run.permission import Permission, PermissionAll, PermissionName, Permissions


def test_permissons():
    permissions = Permissions()

    permissions.allow_env("FOO")
    permissions.allow_net("localhost:8080")
    permissions.allow_net("google.com")
    permissions.allow_read("/etc/passwd")
    permissions.allow_write("/etc/passwd")
    permissions.allow_run("/bin/ls")

    assert permissions.check(Permission(PermissionName.ENV, "FOO"))
    assert permissions.check_env("FOO")
    assert not permissions.check_env("BAR")

    assert permissions.check(Permission(PermissionName.NET, "localhost:8080"))
    assert permissions.check_net("localhost:8080")
    assert not permissions.check_net("localhost:8081")

    assert permissions.check(Permission(PermissionName.NET, "google.com"))
    assert permissions.check_net("google.com:7000")

    assert permissions.check(Permission(PermissionName.READ, "/etc/passwd"))
    assert permissions.check_read("/etc/passwd")
    assert not permissions.check_read("/etc/shadow")

    assert permissions.check(Permission(PermissionName.WRITE, "/etc/passwd"))
    assert permissions.check_write("/etc/passwd")
    assert not permissions.check_write("/etc/shadow")

    assert permissions.check(Permission(PermissionName.RUN, "/bin/ls"))
    assert permissions.check_run("/bin/ls")
    assert not permissions.check_run("/bin/cat")


def test_permissions_all():
    permissions = Permissions()

    permissions.allow_env(PermissionAll)
    permissions.allow_net(PermissionAll)
    permissions.allow_read(PermissionAll)
    permissions.allow_write(PermissionAll)
    permissions.allow_run(PermissionAll)

    assert permissions.check(Permission(PermissionName.ENV, "FOO"))
    assert permissions.check(Permission(PermissionName.NET, "localhost:8080"))
    assert permissions.check(Permission(PermissionName.READ, "/etc/passwd"))
    assert permissions.check(Permission(PermissionName.WRITE, "/etc/passwd"))
    assert permissions.check(Permission(PermissionName.RUN, "/bin/ls"))


def test_permissions_allow():
    permissions = Permissions()

    permissions.allow(Permission(PermissionName.ENV, "FOO"))
    permissions.allow(Permission(PermissionName.NET, "localhost:8080"))
    permissions.allow(Permission(PermissionName.READ, "/etc/passwd"))
    permissions.allow(Permission(PermissionName.WRITE, "/etc/passwd"))
    permissions.allow(Permission(PermissionName.RUN, "/bin/ls"))

    assert permissions.check(Permission(PermissionName.ENV, "FOO"))
    assert permissions.check(Permission(PermissionName.NET, "localhost:8080"))
    assert permissions.check(Permission(PermissionName.READ, "/etc/passwd"))
    assert permissions.check(Permission(PermissionName.WRITE, "/etc/passwd"))
    assert permissions.check(Permission(PermissionName.RUN, "/bin/ls"))
