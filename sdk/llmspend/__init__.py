"""LLMSpend — Know where your AI money goes.

Usage:
    from llmspend import monitor
    client = monitor.wrap(anthropic.Anthropic(), project="my-app")

That's it. Every API call is now tracked with cost, tokens, and latency.
"""

__version__ = "0.1.2"

from llmspend.monitor import wrap, configure  # noqa: F401
