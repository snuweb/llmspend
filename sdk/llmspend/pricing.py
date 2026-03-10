"""Token-to-cost calculation for supported LLM providers.

Prices in USD per 1M tokens. Updated manually from provider pricing pages.
Last verified: 2026-03-10
"""

# {provider: {model_prefix: (input_per_mtok, output_per_mtok)}}
PRICING = {
    "anthropic": {
        "claude-opus-4": (15.00, 75.00),
        "claude-sonnet-4": (3.00, 15.00),
        "claude-haiku-4": (0.80, 4.00),
    },
    "openai": {
        "gpt-4o-mini": (0.15, 0.60),
        "gpt-4o": (2.50, 10.00),
        "gpt-4.1-nano": (0.10, 0.40),
        "gpt-4.1-mini": (0.40, 1.60),
        "gpt-4.1": (2.00, 8.00),
        "o4-mini": (1.10, 4.40),
        "o3-mini": (1.10, 4.40),
        "o3": (2.00, 8.00),
    },
}


def _match_model(provider: str, model: str) -> tuple[float, float] | None:
    """Find pricing by matching model name to known prefixes."""
    provider_prices = PRICING.get(provider)
    if not provider_prices:
        return None

    # Try exact match first, then prefix match (longest prefix wins)
    if model in provider_prices:
        return provider_prices[model]

    best_match = None
    best_len = 0
    for prefix, prices in provider_prices.items():
        if model.startswith(prefix) and len(prefix) > best_len:
            best_match = prices
            best_len = len(prefix)

    return best_match


def calculate_cost(provider: str, model: str, tokens_in: int, tokens_out: int) -> float | None:
    """Calculate cost in USD for a single API call.

    Returns None if the model pricing is unknown.
    """
    prices = _match_model(provider, model)
    if prices is None:
        return None

    input_price, output_price = prices
    cost = (tokens_in / 1_000_000) * input_price + (tokens_out / 1_000_000) * output_price
    return round(cost, 8)
