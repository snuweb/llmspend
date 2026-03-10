# LLMSpend

**Know where your AI money goes.**

Track LLM API costs per feature, per model, per user. 2 lines of code. Zero dependencies. Local-first.

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
    model="claude-sonnet-4-6",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Hello"}]
)
# Cost, tokens, and latency are now tracked automatically
```

Works with OpenAI too:

```python
import openai
from llmspend import monitor

client = monitor.wrap(openai.OpenAI(), project="my-app")
# All chat.completions.create calls are now tracked
```

## Tag by Feature

See exactly which part of your app is burning money:

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1000,
    messages=[{"role": "user", "content": query}],
    llmspend={"feature": "chatbot", "user_id": "u_123"}
)
```

## CLI

```bash
# Cost summary (last 24h by default)
llmspend stats

# Last 7 days, grouped by feature
llmspend stats --last 7d --by feature

# Most expensive individual calls
llmspend top

# Export all events as JSON
llmspend export
```

Output:

```
  LLMSpend — Last 7d
  ──────────────────────────────────────────────────────
  Total: $12.4320 across 2,847 calls

  Group                      Calls       Cost    Avg ms
  ───────────────────────── ────── ────────── ────────
  chatbot                     1204   $7.2100     1180ms
  search                       893   $3.8900      640ms
  summarizer                   750   $1.3320      380ms
```

## Local Dashboard

```bash
llmspend dashboard
```

Opens a local web dashboard at `localhost:8888` — cost breakdown by model, feature, and time. Auto-refreshes. No account needed.

## How It Works

1. `monitor.wrap()` patches `client.messages.create` (Anthropic) or `client.chat.completions.create` (OpenAI)
2. Every API call is intercepted — tokens, cost, latency, and your tags are recorded
3. Events flush to a local SQLite database at `~/.llmspend/events.db` every 5 seconds via a background thread
4. Zero overhead on your API calls — logging happens asynchronously after the response returns

## What Gets Tracked

Per API call:
- Provider, model, timestamp
- Input/output tokens
- Cost in USD (calculated from published pricing)
- Latency in ms
- Your custom tags (feature, user_id, or any key-value pair)

What is **never** tracked:
- Prompt content
- Response content
- API keys

## Supported Models

**Anthropic**: Claude Opus 4, Sonnet 4, Haiku 4.5, and all dated variants

**OpenAI**: GPT-4o, GPT-4.1, o3, o4-mini, and all variants

Cost calculation uses prefix matching — `claude-haiku-4-5-20251001` matches the `claude-haiku-4` pricing tier. Unknown models are tracked with `null` cost (tokens and latency still recorded).

## Configuration

```python
from llmspend import monitor

# Default: logs to ~/.llmspend/events.db
monitor.configure()

# Custom local path
monitor.configure(local_path="/var/log/my-app/llmspend.db")

# Future: send to hosted dashboard
monitor.configure(backend_url="https://llmspend.dev", api_key="ls_...")
```

## Design Principles

- **Never crash your app.** All tracking runs in try/except. If LLMSpend fails, your API call still works.
- **Never store prompts.** Only metadata (tokens, cost, timing). Your data stays private.
- **Zero dependencies.** Pure Python stdlib. No requests, no aiohttp, no protobuf.
- **Local-first.** Works offline. No account required. Your data stays on your machine.

## Hosted Version

Coming soon at [llmspend.dev](https://llmspend.dev) — team dashboards, alerts, budget caps, and cost forecasting.

## License

MIT — use it however you want.
