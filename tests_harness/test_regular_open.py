"""Host-side opens refuse device nodes and FIFOs. No Docker."""
import errno, os, signal, stat, tempfile
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from harness.host_observe import _open_replacing, regular_file_opener


class Alarm(Exception):
    pass


def _alarm(_signum, _frame):
    raise Alarm()


def test_opener_reads_a_regular_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "plain")
        with open(path, "wb") as handle:
            handle.write(b"container-file\n")
        fd = regular_file_opener(path, os.O_RDONLY)
        try:
            assert os.read(fd, 32) == b"container-file\n"
        finally:
            os.close(fd)
        assert _open_replacing(path, "rb").read() == b"container-file\n"


def test_opener_follows_a_symlink_to_a_regular_file():
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, "target")
        link = os.path.join(tmp, "link")
        with open(target, "wb") as handle:
            handle.write(b"via-link\n")
        os.symlink(target, link)
        assert _open_replacing(link, "rb").read() == b"via-link\n"


def test_opener_refuses_zero_and_a_fifo():
    try:
        regular_file_opener("/dev/zero", os.O_RDONLY)
    except OSError as exc:
        assert exc.errno == errno.EINVAL, exc
    else:
        raise AssertionError("/dev/zero opened")
    try:
        _open_replacing("/dev/zero", "rb").read(16)
    except OSError as exc:
        assert exc.errno == errno.EINVAL, exc
    else:
        raise AssertionError("/dev/zero read returned bytes")
    with tempfile.TemporaryDirectory() as tmp:
        fifo = os.path.join(tmp, "fifo")
        os.mkfifo(fifo)
        old = signal.signal(signal.SIGALRM, _alarm)
        signal.alarm(2)
        try:
            try:
                regular_file_opener(fifo, os.O_RDONLY)
            except OSError as exc:
                assert exc.errno == errno.EINVAL, exc
            except Alarm:
                raise AssertionError("FIFO open blocked")
            else:
                raise AssertionError("FIFO opened")
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old)
        assert stat.S_ISFIFO(os.lstat(fifo).st_mode)


def test_truncate_is_not_applied_to_a_device():
    # Opening /dev/zero for write must fail before any truncate or read.
    try:
        regular_file_opener("/dev/zero", os.O_WRONLY | os.O_TRUNC)
    except OSError as exc:
        assert exc.errno == errno.EINVAL, exc
    else:
        raise AssertionError("truncated open of /dev/zero succeeded")


if __name__ == "__main__":
    test_opener_reads_a_regular_file()
    test_opener_follows_a_symlink_to_a_regular_file()
    test_opener_refuses_zero_and_a_fifo()
    test_truncate_is_not_applied_to_a_device()
    print("regular open checks: OK")
