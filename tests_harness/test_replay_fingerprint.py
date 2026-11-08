"""The replayed environment's mirror key differs from the saved one; the saved fingerprint moves with it."""
import base64, os, pathlib, shutil, subprocess, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from harness.replay import fingerprint_translation, primary_fingerprint, translate_fingerprints


def make_key():
    """A throwaway ed25519 key, exported as base64 like baseline.json's vendor_gpg_b64."""
    home = tempfile.mkdtemp(prefix="fpr-test-")
    try:
        os.chmod(home, 0o700)
        env = dict(os.environ, GNUPGHOME=home)
        spec = "%no-protection\nKey-Type: eddsa\nKey-Curve: ed25519\nName-Real: T\nName-Email: t@internal\nExpire-Date: 2035-01-01\n%commit\n"
        subprocess.run(["gpg", "--batch", "--generate-key"], input=spec, text=True, env=env, check=True, capture_output=True)
        out = subprocess.run(["gpg", "--batch", "--export", "t@internal"], env=env, check=True, capture_output=True).stdout
        return base64.b64encode(out).decode()
    finally:
        shutil.rmtree(home, ignore_errors=True)


old_key, new_key = make_key(), make_key()
old, new = primary_fingerprint(old_key), primary_fingerprint(new_key)
assert len(old) == 40 and len(new) == 40 and old != new, (old, new)
assert primary_fingerprint("") == "" and primary_fingerprint("not base64!!") == ""

mapping = fingerprint_translation({"vendor_gpg_b64": old_key}, {"vendor_gpg_b64": new_key})
assert mapping == {old: new}
assert fingerprint_translation({"vendor_gpg_b64": old_key}, {"vendor_gpg_b64": old_key}) == {}
assert fingerprint_translation({}, {"vendor_gpg_b64": new_key}) == {}

# 40-hex, long id, short id; case follows the text; longer hex runs are left alone.
text = f'echo "{old}" ; echo {old.lower()} ; gpg --recv {old[-16:]} ; id={old[-8:]}'
got = translate_fingerprints(text, mapping)
assert old not in got and old.lower() not in got and old[-16:] not in got
assert f'"{new}"' in got and new.lower() in got and new[-16:] in got and f"id={new[-8:]}" in got
longer = "0" + old
assert translate_fingerprints(longer, mapping) == longer
assert translate_fingerprints("unrelated text", mapping) == "unrelated text"
assert translate_fingerprints(text, {}) == text and translate_fingerprints(None, mapping) is None
print("replay fingerprint translation: OK")
