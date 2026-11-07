"""Offline checks of the two API adapters' wire format (no network, no keys): a fake _post returns canned
responses shaped like the providers' documented replies, and we assert what the adapters send back."""
import json, os, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from harness import providers

os.environ.setdefault("OPENROUTER_API_KEY", "test-not-a-key")
os.environ.setdefault("GEMINI_API_KEY", "test-not-a-key")
sent = []

def fake_post(url, headers, body, **_):
    sent.append((url, headers, json.loads(json.dumps(body))))
    if "openrouter" in url:
        if len(body["messages"]) == 2:
            return {"choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": None, "tool_calls": [
                {"id": "c1", "type": "function", "function": {"name": "bash", "arguments": "{\"command\": \"df -h\"}"}}]}}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 10, "cost": 0.001,
                          "completion_tokens_details": {"reasoning_tokens": 3}}}
        return {"choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "done"}}],
                "usage": {"prompt_tokens": 150, "completion_tokens": 5}}
    if len(body["contents"]) == 1:
        return {"candidates": [{"finishReason": "STOP", "content": {"role": "model", "parts": [
            {"functionCall": {"name": "bash", "args": {"command": "df -h"}}, "thoughtSignature": "sig=="}]}}],
            "usageMetadata": {"promptTokenCount": 100, "candidatesTokenCount": 10, "thoughtsTokenCount": 50}}
    return {"candidates": [{"content": {"role": "model", "parts": [{"text": "done"}]}, "finishReason": "STOP"}]}

providers._post = fake_post
first = {}
for cls in (providers.OpenRouter, providers.Gemini):
    a = cls("m", temperature=0.5)
    a.start("sys", "user")
    t = a.step(); assert t.calls and t.calls[0][1] == "df -h", t
    first[cls.__name__] = t
    a.add_results([(t.calls[0][0], "exit_code=0\nok")])
    t2 = a.step(); assert not t2.calls and t2.text == "done", t2
or_body = sent[0][2]
assert "max_tokens" not in or_body
assert first["OpenRouter"].usage["finish_reason"] == "stop"
assert first["OpenRouter"].usage["output_tokens"] == 10
assert first["OpenRouter"].usage["reasoning_tokens"] == 3
or_body = sent[1][2]
assert or_body["messages"][-1] == {"role": "tool", "tool_call_id": "c1", "content": "exit_code=0\nok"}
assert sent[1][1]["Authorization"].startswith("Bearer ")
g_body = sent[2][2]
assert "maxOutputTokens" not in g_body["generationConfig"]
assert first["Gemini"].usage["finish_reason"] == "STOP"
assert first["Gemini"].usage["reasoning_tokens"] == 50
g_body = sent[3][2]
assert g_body["contents"][1]["parts"][0]["thoughtSignature"] == "sig=="           # echoed verbatim
assert g_body["contents"][2]["parts"][0]["functionResponse"]["response"]["output"] == "exit_code=0\nok"
assert "x-goog-api-key" in sent[3][1] and g_body["generationConfig"]["temperature"] == 0.5
sent.clear()
capped = providers.OpenRouter("m", max_tokens=11, reasoning_effort="high")
capped.start("sys", "user")
capped.step()
assert "max_tokens" not in sent[0][2]
assert "max_completion_tokens" not in sent[0][2]
assert sent[0][2]["reasoning"] == {"effort": "high"}
capped_g = providers.Gemini("m", max_tokens=11, reasoning_effort="xhigh")
capped_g.start("sys", "user")
capped_g.step()
assert "maxOutputTokens" not in sent[1][2]["generationConfig"]
assert sent[1][2]["generationConfig"]["thinkingConfig"]["thinkingLevel"] == "xhigh"
print("adapter wire-format checks: OK")
