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
        "claude-3-5-sonnet": (3.00, 15.00),
        "claude-3-5-haiku": (0.80, 4.00),
        "claude-3-opus": (15.00, 75.00),
        "claude-3-sonnet": (3.00, 15.00),
        "claude-3-haiku": (0.25, 1.25),
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
        "gpt-4-turbo": (10.00, 30.00),
        "gpt-4": (30.00, 60.00),
        "gpt-3.5-turbo": (0.50, 1.50),
    },
    "google": {
        "gemini-2.5-pro": (1.25, 10.00),
        "gemini-2.5-flash": (0.15, 0.60),
        "gemini-2.0-flash": (0.10, 0.40),
        "gemini-1.5-pro": (1.25, 5.00),
        "gemini-1.5-flash": (0.075, 0.30),
    },
    "groq": {
        "llama-3.3-70b": (0.59, 0.79),
        "llama-3.1-8b": (0.05, 0.08),
        "mixtral-8x7b": (0.24, 0.24),
        "gemma2-9b": (0.20, 0.20),
    },
    "mistral": {
        "mistral-large": (2.00, 6.00),
        "mistral-small": (0.20, 0.60),
        "codestral": (0.30, 0.90),
        "mistral-nemo": (0.15, 0.15),
    },
    "deepseek": {
        "deepseek-chat": (0.14, 0.28),
        "deepseek-reasoner": (0.55, 2.19),
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
