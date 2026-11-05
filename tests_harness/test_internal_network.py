"""Active tasks join the internal upstream. Legacy tasks stay offline.

The DNS answers are pure. The live mirror, replica, and no-route checks are
scripts/check_internal_network.sh.
"""
import importlib.util, pathlib, struct, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from harness.terminus_pin import active_task_ids

spec = importlib.util.spec_from_file_location("upstream_dns", ROOT / "network" / "dns" / "dns.py")
dns = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dns)


def query(name, qtype=1):
    body = b""
    for label in name.split("."):
        body += bytes([len(label)]) + label.encode()
    body += b"\x00" + struct.pack("!HH", qtype, 1)
    return b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00" + body


def rcode(response):
    return response[3] & 0x0F


mirror = dns.reply(query("mirror.internal"))
assert rcode(mirror) == 0, mirror
assert len(mirror) == 12 + 21 + 16, len(mirror)
assert mirror[12] == 6 and mirror[33:35] == b"\xc0\x0c", mirror
assert mirror[-4:] == bytes(map(int, "172.30.28.10".split("."))), mirror
assert dns.reply(query("replica.internal"))[-4:] == bytes(map(int, "172.30.28.12".split(".")))
assert dns.reply(query("primary.internal"))[-4:] == bytes(map(int, "172.30.28.11".split(".")))
assert rcode(dns.reply(query("deb.debian.org"))) == 3
assert rcode(dns.reply(query("mirror.internal", 28))) == 0
assert struct.unpack("!H", dns.reply(query("mirror.internal", 28))[6:8])[0] == 0

compose = (ROOT / "network" / "docker-compose.yaml").read_text()
assert "internal: true" in compose
assert "172.30.28.10" in compose and "172.30.28.12" in compose and "172.30.28.53" in compose
assert "name: micro1eval-upstream" in compose

ids = sorted(p.name for p in (ROOT / "tasks").iterdir() if (p / "task.toml").exists())
active = active_task_ids(ids)
assert active == ids, active
assert len(active) == 9, active
for task_id in active:
    text = (ROOT / "tasks" / task_id / "environment" / "docker-compose.yaml").read_text()
    assert "micro1eval-upstream" in text, task_id
    assert "172.30.28.53" in text, task_id
    assert "network_mode:" not in text, task_id
    toml = (ROOT / "tasks" / task_id / "task.toml").read_text()
    assert 'network_mode = "no-network"' in toml, task_id
print("internal network checks: OK")
