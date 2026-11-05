"""Namespace clone is refused in the agent sandbox. A thread clone is not."""
import errno
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from harness.host_observe import _CLONE_NAMESPACE, _install_agent_seccomp

# Flags glibc uses for a thread. None of them create a namespace.
_THREAD_FLAGS = 0x3D0F00


def test_thread_flags_are_not_namespace_flags():
    assert _THREAD_FLAGS & _CLONE_NAMESPACE == 0


def test_namespace_clone_is_refused():
    read_fd, write_fd = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(read_fd)
        try:
            _install_agent_seccomp()
            import ctypes
            libc = ctypes.CDLL(None, use_errno=True)
            libc.syscall.restype = ctypes.c_long

            def call(number, *args):
                libc.syscall.argtypes = [ctypes.c_long] + [ctypes.c_ulong] * len(args)
                ctypes.set_errno(0)
                rc = libc.syscall(number, *args)
                return rc, ctypes.get_errno()

            clone3_rc, clone3_err = call(435, 0, 0)
            ns_rc, ns_err = call(56, 0x10000000 | 0x40000000, 0, 0, 0, 0)
            if ns_rc == 0:
                os._exit(0)
            thread_rc, thread_err = call(56, _THREAD_FLAGS, 0, 0, 0, 0)
            if thread_rc == 0:
                os._exit(0)
            started = {"ok": False}

            def mark():
                started["ok"] = True

            import threading
            thread = threading.Thread(target=mark)
            thread.start()
            thread.join(timeout=2)
            text = (
                f"clone3={clone3_rc}:{clone3_err} "
                f"ns={ns_rc}:{ns_err} "
                f"thread={thread_rc}:{thread_err} "
                f"pthread={started['ok']}\n"
            )
            os.write(write_fd, text.encode())
        except BaseException as exc:
            os.write(write_fd, f"EXC {type(exc).__name__}: {exc}\n".encode())
        os._exit(0)
    os.close(write_fd)
    _, status = os.waitpid(pid, 0)
    text = os.read(read_fd, 1000).decode()
    os.close(read_fd)
    assert os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0, (status, text)
    assert text.startswith("clone3=-1:"), text
    parts = dict(item.split("=", 1) for item in text.split())
    assert parts["clone3"] == f"-1:{errno.ENOSYS}", text
    assert parts["ns"] == f"-1:{errno.EPERM}", text
    # A null stack makes the kernel reject the thread clone. EPERM would mean
    # the filter blocked it.
    thread_rc, thread_err = parts["thread"].split(":")
    assert not (thread_rc == "-1" and int(thread_err) == errno.EPERM), text
    assert parts["pthread"] == "True", text


if __name__ == "__main__":
    test_thread_flags_are_not_namespace_flags()
    test_namespace_clone_is_refused()
    print("agent seccomp checks: OK")
