"""The ssh login key is the host copy, not /opt/ssh/console at grade time."""
import os, pathlib, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from harness import host_observe


def main():
    assert host_observe._read_host_console_key(None) is None
    assert host_observe._read_host_console_key("/tmp/does-not-exist-console-key") is None
    fd, path = tempfile.mkstemp(prefix="m1e-console-test-")
    try:
        os.write(fd, b"not a key\n")
        os.close(fd)
        fd = None
        assert host_observe._read_host_console_key(path) is None
        key = b"-----BEGIN OPENSSH PRIVATE KEY-----\nA\n"
        with open(path, "wb") as handle:
            handle.write(key)
        assert host_observe._read_host_console_key(path) == key
        with open(path, "wb") as handle:
            handle.write(b"-----BEGIN " + b"K" * 8192)
        assert host_observe._read_host_console_key(path) is None
    finally:
        if fd is not None:
            os.close(fd)
        os.unlink(path)

    previous_mnt = host_observe._HOST_MNT
    previous_key = host_observe._CONSOLE_KEY
    import builtins
    real_open = builtins.open

    def refuse(file, *args, **kwargs):
        raise AssertionError(f"login opened {file!r}")

    try:
        host_observe._HOST_MNT = 0
        host_observe._CONSOLE_KEY = None
        builtins.open = refuse
        assert host_observe.console_login() is False
    finally:
        builtins.open = real_open
        host_observe._HOST_MNT = previous_mnt
        host_observe._CONSOLE_KEY = previous_key
    print("console key checks: OK")


if __name__ == "__main__":
    main()
