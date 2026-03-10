# LLMSpend

**Know where your AI money goes.**

Track LLM API costs per feature, per model, per user. 2 lines of code. Zero config.

## Install

```bash
pip install llmspend
```

## Quick Start

```python
import anthropic
from llmspend import monitor

# Wrap your client — that's it
client = monitor.wrap(anthropic.Anthropic(), project="my-app")

# Use it exactly as before
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=500,
    messages=[{"role": "user", "content": "Hello"}]
)
# Cost, tokens, and latency are now tracked automatically
```

## Tag by Feature

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1000,
    messages=[{"role": "user", "content": query}],
    llmspend={"feature": "chatbot", "user_id": "u_123"}
)
```

## View Your Costs

```bash
# Last 24 hours, grouped by model
llmspend stats

# Last 7 days, grouped by feature
llmspend stats --last 7d --by feature

# Most expensive calls
llmspend top

# Export as JSON
llmspend export
```

```
  LLMSpend — Last 7d
  ──────────────────────────────────────────────────
  Total: $12.4320 across 2,847 calls

  Group                      Calls       Cost    Avg ms
  ───────────────────────── ────── ────────── ────────
  claude-sonnet-4-6            312   $8.9400     1240ms
  claude-haiku-4-5             1893   $2.1200      430ms
  gpt-4o-mini                  642   $1.3720      380ms
```

## Works with OpenAI too

```python
import openai
from llmspend import monitor

client = monitor.wrap(openai.OpenAI(), project="my-app")
# All chat.completions.create calls are now tracked
```

## What Gets Tracked

Per API call:
- Provider, model, timestamp
- Input/output tokens
- Cost in USD
- Latency in ms
- Your custom tags (feature, user_id)

What is **never** tracked:
- Prompt content
- Response content
- API keys

## Self-Hosted Dashboard

Coming soon — React dashboard for visualizing costs locally.

## Hosted Version

Coming soon at [llmspend.dev](https://llmspend.dev) — team dashboards, alerts, cost forecasting.

## License

MIT
