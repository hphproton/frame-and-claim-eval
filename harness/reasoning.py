"""Per-model reasoning effort. HPH chooses high or xhigh after this run.

The config field is required for a live model. TODO, a missing value, or any
other string refuses the run before a provider call. The flash pilot ran with
the provider default and no effort field; that result is annotated, not rerun.
This module does not send max_tokens.
"""

ALLOWED = ("high", "xhigh")
_CAP_KEYS = ("max_tokens", "max_completion_tokens", "maxOutputTokens")


class ReasoningUnset(Exception):
    """The live config has no usable reasoning effort."""


def require_effort(model_cfg):
    """Return high or xhigh. Any other value, including TODO, refuses the run."""
    if model_cfg.get("provider") == "scripted":
        return None
    value = model_cfg.get("reasoning_effort")
    if value not in ALLOWED:
        raise ReasoningUnset(
            f"reasoning_effort for {model_cfg.get('label', '?')} must be high or xhigh "
            f"(got {value!r}). HPH sets it before a live run. No request was sent."
        )
    return value


def request_fields(provider, effort):
    """The provider payload for this effort. Output caps are not included."""
    if effort not in ALLOWED:
        raise ReasoningUnset(f"reasoning effort {effort!r} is not high or xhigh")
    if provider == "openrouter":
        return {"reasoning": {"effort": effort}}
    if provider == "gemini":
        return {"generationConfig": {"thinkingConfig": {"thinkingLevel": effort}}}
    raise ReasoningUnset(f"no reasoning payload for provider {provider}")


def strip_output_caps(body):
    """Drop every output-limit field. The 8 KB tool-output limit is separate."""
    if not isinstance(body, dict):
        return body
    for key in _CAP_KEYS:
        body.pop(key, None)
    gen = body.get("generationConfig")
    if isinstance(gen, dict):
        gen.pop("maxOutputTokens", None)
    return body


def stamp_meta(meta, effort):
    meta["reasoning_effort"] = effort
    meta["max_tokens_sent"] = False
    return meta
