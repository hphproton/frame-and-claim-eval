"""Deltas that `make replay` and `make reproduce` are allowed to report.

A replay or a regrade rebuilds a verdict from saved inputs and compares it with
the saved ``grade.json``. Some differences are understood: the mirror key is
regenerated on every network build, a parser or a spec changed after a run, a
live count is read at a different time. Each one is listed in
``results/known-deltas.json`` with its cause and the evidence for that cause.

The check passes only when the observed deltas equal the listed deltas:

* an observed delta with no entry is *unexplained* and fails;
* an entry that no longer occurs is *stale* and fails;
* an entry whose ``saved`` or ``observed`` value differs from the observed one
  does not match, so the observed delta is unexplained and the entry is stale.

Score bits are never compared loosely here. A listed delta only says why a
difference exists; it does not hide it, and both lists are printed.

``added_in`` is the commit the delta was first observed on.

An entry may set ``observed_varies`` to true when the observed value is
different on every build (a regenerated key fingerprint). The saved value must
still differ from the observed one.
"""
import json

from . import storage

PATH = storage.ROOT / "results" / "known-deltas.json"
CAUSES = ("mirror_key_regenerated", "parser_fixed_after_run", "spec_v2_not_seen", "other")
CHECKS = ("replay", "reproduce")
REQUIRED = ("check", "run", "task", "model", "trial", "field", "saved", "observed", "cause", "evidence", "added_in")


class KnownDeltaError(ValueError):
    pass


def load(path=None):
    path = PATH if path is None else path
    if not path.is_file():
        return []
    entries = json.loads(path.read_text())
    if not isinstance(entries, list):
        raise KnownDeltaError(f"{path}: expected a JSON list")
    seen = set()
    for index, entry in enumerate(entries):
        where = f"{path} entry {index}"
        if not isinstance(entry, dict):
            raise KnownDeltaError(f"{where}: not an object")
        missing = [key for key in REQUIRED if key not in entry]
        if missing:
            raise KnownDeltaError(f"{where}: missing {missing}")
        if entry["check"] not in CHECKS:
            raise KnownDeltaError(f"{where}: check {entry['check']!r} not in {CHECKS}")
        if entry["cause"] not in CAUSES:
            raise KnownDeltaError(f"{where}: cause {entry['cause']!r} not in {CAUSES}")
        for key in ("evidence", "added_in"):
            if not isinstance(entry[key], str) or not entry[key].strip():
                raise KnownDeltaError(f"{where}: {key} is empty")
        ident = identity(entry)
        if ident in seen:
            raise KnownDeltaError(f"{where}: duplicate entry {ident}")
        seen.add(ident)
    return entries


def identity(item):
    return (item["check"], item["run"], item["task"], item["model"], item["trial"], item["field"])


def _same(left, right):
    return json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


def reconcile(check, observed, entries, scope=None):
    """Split ``observed`` against ``entries`` of this ``check``.

    ``observed`` items carry run, task, model, trial, field, saved, observed.
    ``scope`` is a set of (run, task) pairs that were actually checked. It limits which
    entries can be stale, so replaying part of the saved trials does not report the entries
    of trials that were not replayed.
    Returns ``(explained, unexplained, stale)``.
    """
    listed = {identity(entry): entry for entry in entries
              if entry["check"] == check and (scope is None or (entry["run"], entry["task"]) in scope)}
    explained, unexplained, matched = [], [], set()
    for item in observed:
        item = dict(item, check=check)
        entry = listed.get(identity(item))
        ok = (
            entry is not None
            and _same(entry["saved"], item["saved"])
            and (entry.get("observed_varies") is True and not _same(item["saved"], item["observed"])
                 or _same(entry["observed"], item["observed"]))
        )
        if ok:
            explained.append((item, entry))
            matched.add(identity(item))
        else:
            unexplained.append(item)
    stale = [entry for ident, entry in listed.items() if ident not in matched]
    return explained, unexplained, stale


def _short(value, limit=90):
    text = json.dumps(value, sort_keys=True)
    return text if len(text) <= limit else text[: limit - 3] + "..."


def describe(item):
    where = f"{item['run']}/{item['task']}/{item['model']}/{item['trial']}"
    return f"{where} {item['field']}: saved {_short(item['saved'])} -> observed {_short(item['observed'])}"


def report(check, observed, entries=None, scope=None):
    """Print both lists. Return ``(unexplained, stale)`` counts."""
    entries = load() if entries is None else entries
    explained, unexplained, stale = reconcile(check, observed, entries, scope)
    print(f"{check} deltas explained by results/known-deltas.json: {len(explained)}")
    for item, entry in explained:
        print(f"  KNOWN       {describe(item)}  [{entry['cause']}]")
    print(f"{check} deltas with no matching entry (unexplained): {len(unexplained)}")
    for item in unexplained:
        print(f"  UNEXPLAINED {describe(item)}")
    print(f"known-deltas entries that did not occur (stale): {len(stale)}")
    for entry in stale:
        print(f"  STALE       {describe(entry)}  [{entry['cause']}]")
    return len(unexplained), len(stale)


def leaf_diff(saved, new, path=""):
    """Differing leaves of two JSON values as ``(path, saved, new)``. A list is one leaf."""
    if isinstance(saved, dict) and isinstance(new, dict):
        out = []
        for key in sorted(set(saved) | set(new)):
            sub = f"{path}.{key}" if path else str(key)
            if key not in saved:
                out.append((sub, None, new[key]))
            elif key not in new:
                out.append((sub, saved[key], None))
            else:
                out.extend(leaf_diff(saved[key], new[key], sub))
        return out
    return [] if _same(saved, new) else [(path, saved, new)]
