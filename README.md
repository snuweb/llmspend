# LLMSpend

**Know where your AI money goes.**

Track LLM API costs per feature, per model, per user. 2 lines of code. Zero dependencies. Local-first.

```bash
pip install llmspend
```

```python
import anthropic
from llmspend import monitor

client = monitor.wrap(anthropic.Anthropic(), project="my-app")

# Use it exactly as before — costs are tracked automatically
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Hello"}],
    llmspend={"feature": "chatbot", "user_id": "u_123"}
)
```

```bash
$ llmspend stats --last 7d --by feature

  LLMSpend — Last 7d
  ──────────────────────────────────────────────────────
  Total: $12.4320 across 2,847 calls

  Group                      Calls       Cost    Avg ms
  ───────────────────────── ────── ────────── ────────
  chatbot                     1204   $7.2100     1180ms
  search                       893   $3.8900      640ms
  summarizer                   750   $1.3320      380ms
```

## Features

- **2 lines to integrate** — wrap your client, done
- **Per-feature cost tracking** — tag calls with `llmspend={"feature": "chatbot"}`
- **CLI** — `llmspend stats`, `llmspend top`, `llmspend export`
- **Local dashboard** — `llmspend dashboard` opens a web UI at localhost:8888
- **Anthropic + OpenAI** — Claude and GPT models with automatic cost calculation
- **Zero dependencies** — pure Python stdlib, no bloat
- **Privacy-first** — never stores prompts or responses, only metadata
- **Never crashes your app** — all tracking runs in try/except

## Know What Each User Costs You

Building a SaaS app with AI? You need to know which users are burning your budget.

```python
# Tag every call with the user
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=500,
    messages=[{"role": "user", "content": user_message}],
    llmspend={"feature": "chatbot", "user_id": current_user.id}
)
```

```bash
$ llmspend stats --last 7d --by user_id

  LLMSpend — Last 7d — By User
  ──────────────────────────────────────────────────────
  Total: $47.82 across 8,291 calls

  User                       Calls       Cost    Avg ms
  ───────────────────────── ────── ────────── ────────
  u_8832 (power user)        3,102  $28.4100     890ms
  u_1204                       912   $6.2300     430ms
  u_5519                       488   $3.1800     380ms
  ... 47 more users
```

One user is 59% of your AI spend. Without LLMSpend, you'd find out when the invoice arrives.

## How It Works

`monitor.wrap()` patches your client's create method. Every API call is intercepted after it completes — tokens, cost, and latency are logged to a local SQLite database (`~/.llmspend/events.db`) via a background thread. Zero overhead on your API calls.

## Documentation

Full docs in the [SDK README](sdk/README.md).

## Project Structure

```
sdk/          — Python package (pip install llmspend)
frontend/    — Landing page (llmspend.dev)
backend/     — Hosted dashboard API (coming soon)
```

## License

MIT

---

If this saved you from a surprise AI bill, consider giving it a ⭐
