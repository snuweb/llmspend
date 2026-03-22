# Contributing to LLMSpend

Thanks for your interest in contributing! LLMSpend is intentionally simple — we want to keep it that way.

## Quick Start

```bash
git clone https://github.com/snuweb/llmspend.git
cd llmspend/sdk
pip install -e .
```

## What We Need Help With

### Easy (good first issue)
- **Add model pricing** — new models get released constantly. Update `llmspend/pricing.py` with the correct per-MTok rates from the provider's pricing page.
- **Test with your provider** — try `monitor.wrap()` with your Anthropic/OpenAI/Groq/Mistral client and report if anything breaks.
- **Improve CLI output** — make `llmspend stats` output cleaner or more informative.

### Medium
- **Add provider support** — we support 6 providers but there are more (Cohere, AI21, Together, Replicate). Each provider needs a wrapper in `monitor.py` and pricing in `pricing.py`.
- **Cost alerts** — detect when daily spend exceeds a threshold and print a warning.
- **CSV/JSON export improvements** — better export formats for accounting tools.

### Hard
- **Async client support** — `AsyncAnthropic()` and `AsyncOpenAI()` need async-aware wrappers.
- **Cost forecasting** — predict next 7d spend based on historical trends.
- **Budget caps** — hard-stop API calls when a budget limit is hit.

## Rules

1. **Keep it simple** — LLMSpend is 2 lines to integrate. Don't add complexity.
2. **Zero new dependencies** — we use only Python stdlib. No exceptions.
3. **Never store prompts** — privacy is a feature, not a limitation.
4. **Never crash the developer's app** — all SDK code must be wrapped in try/except.
5. **Test your changes** — run `python -m pytest tests/` before submitting.

## PR Process

1. Fork the repo
2. Create a branch (`git checkout -b add-cohere-support`)
3. Make your changes
4. Run tests
5. Submit a PR with a clear description

We review PRs within 48 hours. Small PRs get merged faster.

## Adding a New Provider

1. Add pricing to `sdk/llmspend/pricing.py`:
```python
"your_provider": {
    "model-name": (input_per_mtok, output_per_mtok),
},
```

2. Add detection in `monitor.py` → `_detect_provider()`:
```python
if "your_provider" in client_type:
    return "your_provider"
```

3. Add wrapper — most providers use OpenAI-compatible APIs, so you can reuse `_wrap_openai()`.

4. Update README with the new provider.

That's it. Most provider additions are under 20 lines of code.
