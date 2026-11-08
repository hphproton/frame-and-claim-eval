"""Per-model reasoning effort.

`high` and `xhigh` send the provider's reasoning field. `provider_default`
sends no reasoning field, which is how the flash pilot ran, and the string is
still recorded on the trial. TODO, a missing value, or any other string refuses
the run before a provider call. This module does not send max_tokens.
"""

ALLOWED = ("high", "xhigh", "provider_default")
# Keys a [[models]] block may carry. An unknown key is refused: `extra` was once
# written for the Terminus path, which never read it.
MODEL_KEYS = (
    "label", "provider", "model", "temperature", "reasoning_effort",
    "api_base", "model_info", "llm_kwargs", "price_table",
)
_CAP_KEYS = ("max_tokens", "max_completion_tokens", "maxOutputTokens")


class ReasoningUnset(Exception):
    """The live config has no usable reasoning effort."""


def check_model_keys(model_cfg):
    """Refuse a model block with a key this runner does not read."""
    unknown = sorted(set(model_cfg) - set(MODEL_KEYS))
    if unknown:
        raise ReasoningUnset(
            f"model {model_cfg.get('label', '?')} has keys the runner does not read: {unknown}. "
            f"Allowed: {list(MODEL_KEYS)}. No request was sent."
        )


def require_effort(model_cfg):
    """Return high, xhigh, or provider_default. Any other value refuses the run."""
    if model_cfg.get("provider") == "scripted":
        return None
    value = model_cfg.get("reasoning_effort")
    if value not in ALLOWED:
        raise ReasoningUnset(
            f"reasoning_effort for {model_cfg.get('label', '?')} must be high, xhigh, "
            f"or provider_default (got {value!r}). No request was sent."
        )
    return value


def request_fields(provider, effort):
    """The provider payload for this effort. Output caps are not included.

    provider_default is an empty payload: the request body gains no reasoning field.
    """
    if effort == "provider_default":
        return {}
    if effort not in ("high", "xhigh"):
        raise ReasoningUnset(f"reasoning effort {effort!r} is not high, xhigh, or provider_default")
    if provider == "openrouter":
        return {"reasoning": {"effort": effort}}
    if provider == "gemini":
        return {"generationConfig": {"thinkingConfig": {"thinkingLevel": effort}}}
    raise ReasoningUnset(f"no reasoning payload for provider {provider}")


def llm_call_kwargs(model_cfg, effort):
    """Kwargs for one live completion. provider_default removes reasoning fields."""
    merged = dict(model_cfg.get("llm_kwargs") or {})
    merged.update(request_fields(model_cfg.get("provider"), effort))
    if effort == "provider_default":
        merged.pop("reasoning", None)
        merged.pop("reasoning_effort", None)
        gen = merged.get("generationConfig")
        if isinstance(gen, dict):
            gen.pop("thinkingConfig", None)
            if not gen:
                merged.pop("generationConfig", None)
    for key in _CAP_KEYS:
        merged.pop(key, None)
    return merged


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


def harbor_agent_kwargs(model_cfg, effort):
    """Arguments for Harbor's Terminus constructor.

    provider_default leaves Harbor's reasoning_effort unset, so LiteLLM omits
    the field. high and xhigh use Harbor's own argument, which LiteLLM maps
    onto the provider request. The raw reasoning object is not also sent.
    """
    llm_kwargs = llm_call_kwargs(model_cfg, effort)
    llm_kwargs.pop("reasoning", None)
    kwargs = {"llm_kwargs": llm_kwargs}
    if effort in ("high", "xhigh"):
        kwargs["reasoning_effort"] = effort
    return kwargs


def stamp_meta(meta, effort):
    meta["reasoning_effort"] = effort
    meta["max_tokens_sent"] = False
    return meta
