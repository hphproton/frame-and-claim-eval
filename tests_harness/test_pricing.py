"""Gemini trials record a nonzero cost from a dated price table; a bad config is refused before a request."""
import datetime as dt, json, pathlib, sys, tomllib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from harness import cli, pricing
from harness.reasoning import MODEL_KEYS, ReasoningUnset, check_model_keys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TABLE = {"input": 2.0, "cached_input": 0.10, "output": 10.0, "read": "2026-11-07",
         "valid_until": "2026-11-30", "source": "test"}


def test_one_call_matches_the_litellm_step_figure_for_prompt_only():
    # Saved Gemini pilot step: 3206 prompt tokens, 0 completion tokens, LiteLLM cost_usd 0.006412.
    got = pricing.trial_cost([{"prompt_tokens": 3206, "completion_tokens": 0}], TABLE)
    assert got["cost_usd"] == 0.006412 and got["calls_without_output_count"] == 1


def test_cached_prompt_tokens_use_the_cached_rate_and_output_the_output_rate():
    rec = [{"prompt_tokens": 1_000_000, "cached_tokens": 400_000, "completion_tokens": 100_000, "reasoning_tokens": 60_000}]
    got = pricing.trial_cost(rec, TABLE)
    assert abs(got["cost_usd"] - (600_000 * 2.0 + 400_000 * 0.10 + 100_000 * 10.0) / 1e6) < 1e-9
    assert got["priced_output_tokens"] == 100_000  # reasoning is part of completion; not added twice


def test_a_call_with_zero_completion_but_reasoning_is_billed_for_the_reasoning():
    got = pricing.trial_cost([{"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 5000}], TABLE)
    assert got["priced_output_tokens"] == 5000 and got["cost_usd"] == 0.05


def test_cached_cannot_exceed_prompt_and_bad_values_count_as_zero():
    got = pricing.trial_cost([{"prompt_tokens": 100, "cached_tokens": 900, "completion_tokens": None}], TABLE)
    assert got["priced_cached_tokens"] == 100
    assert pricing.trial_cost([], TABLE)["cost_usd"] == 0.0


def test_a_saved_gemini_trial_prices_to_a_nonzero_amount():
    meta = json.loads((ROOT / "runs/pilot-gemini-api-20261107/apt-expired-signing-key/gemini-4-argon/trial-1/meta.json").read_text())
    assert meta["usage"]["cost_usd"] == 0.0  # what the harness stored before this change
    got = pricing.trial_cost(meta["llm_calls_detail"], TABLE)
    assert 0.01 < got["cost_usd"] < 0.5, got
    assert got["cost_source"] == "price_table" and got["price_table_read"] == "2026-11-07"


def test_table_validation():
    assert pricing.validate(dict(TABLE), today=dt.date(2026, 11, 8))
    for bad in (None, {}, dict(TABLE, input=0), dict(TABLE, output=-1), dict(TABLE, input=True),
                dict(TABLE, valid_until="2026-11-07"), dict(TABLE, read="2026-12-01"), dict(TABLE, source=" "),
                dict(TABLE, read="yesterday")):
        try:
            pricing.validate(bad, today=dt.date(2026, 11, 8))
        except pricing.PriceTableError:
            continue
        raise AssertionError(bad)


def test_run_refuses_a_gemini_model_without_a_table_and_unknown_keys():
    try:
        cli._require_price({"provider": "gemini", "label": "g"})
    except pricing.PriceTableError:
        pass
    else:
        raise AssertionError("gemini without a price table was accepted")
    cli._require_price({"provider": "openrouter", "label": "o"})
    for bad in ({"label": "x", "extra": {}}, {"label": "x", "max_tokens": 5}):
        try:
            check_model_keys(bad)
        except ReasoningUnset:
            continue
        raise AssertionError(bad)


def test_committed_configs_pass_the_checks():
    for name in ("pilot", "flash-hardened", "offline-controls", "calibration-gemini-20261108", "official-gemini-20261108"):
        cfg = tomllib.loads((ROOT / "configs" / f"{name}.toml").read_text())
        for model in cfg["models"]:
            check_model_keys(model)
    for name, budget in (("calibration-gemini-20261108", 1.0), ("official-gemini-20261108", 4.0)):
        cfg = tomllib.loads((ROOT / "configs" / f"{name}.toml").read_text())
        assert cfg["session_budget_usd"] == budget
        model = cfg["models"][0]
        assert model["reasoning_effort"] == "high" and model["temperature"] == 1.0
        assert not (set(model) & {"max_tokens", "max_completion_tokens", "maxOutputTokens"})
        pricing.validate(model["price_table"])


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("pricing: OK")
