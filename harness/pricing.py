"""Cost of a live trial from a dated price table in the run config.

LiteLLM's own cost field for Gemini counted prompt tokens only (output tokens
stored as 0 on many calls), and the harness stored cost_usd 0 for the provider.
The config names the rates and the date they were read, and the trial's cost is
computed from the token counts of its recorded calls:

    uncached prompt tokens * input + cached tokens * cached_input + output tokens * output

Rates are USD per 1M tokens. Output tokens include thinking tokens. Per call the
output count is the larger of completion_tokens and reasoning_tokens, so a call
whose completion_tokens LiteLLM stored as 0 is not billed as free; this can still
under-count when both are missing, and the calls without any output count are
reported in the result. The figure is an estimate of the provider bill, not the bill.

A table past its valid_until date is refused before any request.
"""
import datetime as dt

REQUIRED = ("input", "cached_input", "output", "read", "valid_until", "source")


class PriceTableError(ValueError):
    pass


def validate(table, today=None):
    """Return the table or raise. Rates must be positive numbers and the table must be in date."""
    if not isinstance(table, dict):
        raise PriceTableError("price_table is missing")
    missing = [key for key in REQUIRED if key not in table]
    if missing:
        raise PriceTableError(f"price_table lacks {missing}")
    for key in ("input", "cached_input", "output"):
        value = table[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise PriceTableError(f"price_table.{key} must be a positive number (USD per 1M tokens)")
    try:
        read = dt.date.fromisoformat(str(table["read"]))
        until = dt.date.fromisoformat(str(table["valid_until"]))
    except ValueError as exc:
        raise PriceTableError(f"price_table dates must be YYYY-MM-DD: {exc}")
    today = today or dt.datetime.now(dt.timezone.utc).date()
    if until < today:
        raise PriceTableError(f"price_table is past valid_until {until}; read the provider's page again and update the config")
    if read > today:
        raise PriceTableError(f"price_table.read {read} is in the future")
    if not str(table["source"]).strip():
        raise PriceTableError("price_table.source is empty")
    return table


def _int(value):
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else 0


def trial_cost(records, table):
    """Cost of the recorded calls. Returns a dict that goes under meta['usage']."""
    prompt = cached = output = no_output = 0
    for row in records or []:
        p, c = _int(row.get("prompt_tokens")), min(_int(row.get("cached_tokens")), _int(row.get("prompt_tokens")))
        o = max(_int(row.get("completion_tokens")), _int(row.get("reasoning_tokens")))
        prompt += p
        cached += c
        output += o
        if o == 0:
            no_output += 1
    per_m = 1_000_000.0
    cost = ((prompt - cached) * table["input"] + cached * table["cached_input"] + output * table["output"]) / per_m
    return {
        "cost_usd": round(cost, 6),
        "cost_source": "price_table",
        "price_table_read": str(table["read"]),
        "price_table_valid_until": str(table["valid_until"]),
        "priced_prompt_tokens": prompt,
        "priced_cached_tokens": cached,
        "priced_output_tokens": output,
        "calls_without_output_count": no_output,
    }
