"""OpenRouter key usage for the session cap.

The poll reads the key's cumulative usage and returns this session's delta.
The API key stays in the Authorization header. It is not written to disk and
it is not put in an error string. This module does not send a completion.
"""
import json, os, pathlib, urllib.error, urllib.request

KEY_URL = "https://openrouter.ai/api/v1/key"


def fetch_usage(urlopen=None):
    """Cumulative USD charged to OPENROUTER_API_KEY. Raises if the poll fails."""
    key = os.environ.get("OPENROUTER_API_KEY") or ""
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
    opener = urlopen or urllib.request.urlopen
    request = urllib.request.Request(KEY_URL, headers={"Authorization": f"Bearer {key}"})
    try:
        with opener(request, timeout=30) as response:
            payload = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")[:300].replace(key, "[redacted]")
        raise RuntimeError(f"openrouter key poll HTTP {exc.code}: {body}") from None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        raise RuntimeError("openrouter key poll failed") from None
    data = payload.get("data") if isinstance(payload, dict) else None
    usage = data.get("usage") if isinstance(data, dict) else None
    if not isinstance(usage, (int, float)):
        raise RuntimeError("openrouter key poll returned no usage")
    return float(usage)


def session_poller(state_path, limit_usd, fetch=None):
    """A SessionBudget poller. The first successful read fixes the session baseline.

    A later process that loads the same state file keeps that baseline, so the
    cap covers the smoke and the full run together.
    """
    fetch = fetch or fetch_usage
    path = pathlib.Path(state_path)
    if path.exists():
        data = json.loads(path.read_text())
        start = float(data["key_usage_at_start"])
    else:
        start = float(fetch())
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "key_usage_at_start": start,
            "limit_usd": float(limit_usd),
        }, indent=2) + "\n")

    def poll():
        usage = float(fetch())
        return {"spent_usd": max(0.0, usage - start)}

    return poll
