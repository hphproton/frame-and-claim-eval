"""A connected socket is trusted only when its peer is a postmaster backend."""
import os, pathlib, socket, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from harness.host_observe import _postgres_socket_ok


def main():
    directory = tempfile.mkdtemp(prefix="m1e-pg-peer-")
    path = os.path.join(directory, "sock")
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(path)
    server.listen(1)
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(path)
    conn, _addr = server.accept()
    try:
        assert _postgres_socket_ok(conn, path) is False
        link = os.path.join(directory, "link")
        os.symlink(path, link)
        assert _postgres_socket_ok(conn, link) is False
    finally:
        conn.close()
        client.close()
        server.close()
        os.unlink(path)
        os.unlink(link)
        os.rmdir(directory)
    print("postgres peer checks: OK")


if __name__ == "__main__":
    main()
