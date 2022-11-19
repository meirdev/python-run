import sys
from unittest import mock

from python_run.__main__ import main


def test_main():
    sys.argv = [
        "python-run",
        "myfile.py",
        "--allow-env",
        "--allow-read",
        "--allow-write",
        "--allow-run",
        "cat,echo",
    ]

    with mock.patch("runpy.run_path"), mock.patch(
        "python_run.hook.Hook._is_protected_os_env_attr", return_value=False
    ):
        main()


def test_main_allow_all():
    sys.argv = ["python-run", "myfile.py", "--allow-all"]

    with mock.patch("runpy.run_path"), mock.patch(
        "python_run.hook.Hook._is_protected_os_env_attr", return_value=False
    ):
        main()
