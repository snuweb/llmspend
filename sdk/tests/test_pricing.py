"""Tests for pricing calculation."""

from llmspend.pricing import calculate_cost, _match_model


def test_anthropic_haiku_cost():
    # 1000 input + 500 output tokens on Haiku
    # Input: 1000/1M * $0.80 = $0.0008
    # Output: 500/1M * $4.00 = $0.002
    cost = calculate_cost("anthropic", "claude-haiku-4-5-20251001", 1000, 500)
    assert cost is not None
    assert abs(cost - 0.0028) < 0.0001


def test_anthropic_sonnet_cost():
    cost = calculate_cost("anthropic", "claude-sonnet-4-6", 1000, 500)
    assert cost is not None
    # Input: 1000/1M * $3.00 = $0.003
    # Output: 500/1M * $15.00 = $0.0075
    assert abs(cost - 0.0105) < 0.0001


def test_openai_gpt4o_mini_cost():
    cost = calculate_cost("openai", "gpt-4o-mini", 1000, 500)
    assert cost is not None
    # Input: 1000/1M * $0.15 = $0.00015
    # Output: 500/1M * $0.60 = $0.0003
    assert abs(cost - 0.00045) < 0.0001


def test_unknown_model_returns_none():
    cost = calculate_cost("anthropic", "claude-unknown-99", 1000, 500)
    assert cost is None


def test_unknown_provider_returns_none():
    cost = calculate_cost("google", "gemini-pro", 1000, 500)
    assert cost is None


def test_prefix_matching():
    # "claude-haiku-4-5-20251001" should match "claude-haiku-4" prefix
    prices = _match_model("anthropic", "claude-haiku-4-5-20251001")
    assert prices is not None
    assert prices == (0.80, 4.00)


def test_zero_tokens():
    cost = calculate_cost("anthropic", "claude-haiku-4-5-20251001", 0, 0)
    assert cost == 0.0
