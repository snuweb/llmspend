"""Core monitor — wraps Anthropic and OpenAI clients to track costs.

Usage:
    from llmspend import monitor
    client = monitor.wrap(anthropic.Anthropic(), project="my-app")
    # Use client exactly as before — all calls are now tracked.
"""

import time
from datetime import datetime, timezone
from typing import Any

from llmspend.pricing import calculate_cost
from llmspend import transport


def configure(backend_url: str | None = None, api_key: str | None = None,
              local_path: str | None = None):
    """Configure where LLMSpend sends data.

    Args:
        backend_url: URL of the LLMSpend backend (e.g. "https://llmspend.dev").
                     If None, logs to local SQLite only.
        api_key: Your LLMSpend project API key (for hosted version).
        local_path: Path to local SQLite database. Defaults to ~/.llmspend/events.db.
    """
    transport.configure(backend_url=backend_url, api_key=api_key, local_path=local_path)


def wrap(client: Any, project: str = "default", **default_metadata) -> Any:
    """Wrap an Anthropic or OpenAI client to track all API calls.

    Args:
        client: An anthropic.Anthropic() or openai.OpenAI() instance.
        project: Project name for grouping costs (e.g. "my-chatbot").
        **default_metadata: Default metadata attached to every call
                           (e.g. environment="production").

    Returns:
        The same client object, with cost tracking enabled.
        The returned object has the identical API — no code changes needed.
    """
    provider = _detect_provider(client)
    if provider is None:
        # Unknown client — return as-is, don't break anything
        return client

    if provider == "anthropic":
        _wrap_anthropic(client, project, default_metadata)
    elif provider == "openai":
        _wrap_openai(client, project, default_metadata)

    return client


def _detect_provider(client: Any) -> str | None:
    """Detect whether this is an Anthropic or OpenAI client."""
    client_type = type(client).__module__ or ""
    client_name = type(client).__name__ or ""

    if "anthropic" in client_type or client_name in ("Anthropic", "AsyncAnthropic"):
        return "anthropic"
    if "openai" in client_type or client_name in ("OpenAI", "AsyncOpenAI"):
        return "openai"
    return None


def _wrap_anthropic(client: Any, project: str, default_meta: dict):
    """Patch anthropic.Anthropic().messages.create to track calls."""
    original_create = client.messages.create

    def tracked_create(*args, **kwargs):
        # Extract metadata from kwargs (we consume it, Anthropic API doesn't know about it)
        meta = kwargs.pop("llmspend", {})
        merged_meta = {**default_meta, **meta}

        start = time.monotonic()
        error = None
        response = None

        try:
            response = original_create(*args, **kwargs)
            return response
        except Exception as e:
            error = e
            raise
        finally:
            try:
                elapsed = int((time.monotonic() - start) * 1000)
                model = kwargs.get("model", "unknown")
                tokens_in = 0
                tokens_out = 0
                status = "error"

                if response is not None and hasattr(response, "usage"):
                    tokens_in = getattr(response.usage, "input_tokens", 0) or 0
                    tokens_out = getattr(response.usage, "output_tokens", 0) or 0
                    status = "success"

                cost = calculate_cost("anthropic", model, tokens_in, tokens_out)

                event = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "provider": "anthropic",
                    "model": model,
                    "tokens_in": tokens_in,
                    "tokens_out": tokens_out,
                    "cost_usd": cost,
                    "latency_ms": elapsed,
                    "status": status,
                    "error": str(error)[:200] if error else None,
                    "feature": merged_meta.get("feature"),
                    "user_id": merged_meta.get("user_id"),
                    "project": project,
                }
                transport.send(event)
            except Exception:
                pass  # Never crash the developer's app

    client.messages.create = tracked_create

    # Also wrap streaming if available
    if hasattr(client.messages, "stream"):
        _wrap_anthropic_stream(client, project, default_meta)


def _wrap_anthropic_stream(client: Any, project: str, default_meta: dict):
    """Patch anthropic streaming to track costs from the final message event."""
    original_stream = client.messages.stream

    def tracked_stream(*args, **kwargs):
        meta = kwargs.pop("llmspend", {})
        merged_meta = {**default_meta, **meta}
        start = time.monotonic()

        stream_ctx = original_stream(*args, **kwargs)

        class TrackedStreamContext:
            """Wrapper that tracks the stream's final usage."""

            def __init__(self, ctx):
                self._ctx = ctx
                self._response = None

            def __enter__(self):
                self._ctx.__enter__()
                return self

            def __exit__(self, *exc):
                result = self._ctx.__exit__(*exc)
                try:
                    msg = self._ctx.get_final_message()
                    if msg and hasattr(msg, "usage"):
                        elapsed = int((time.monotonic() - start) * 1000)
                        model = kwargs.get("model", "unknown")
                        tokens_in = getattr(msg.usage, "input_tokens", 0) or 0
                        tokens_out = getattr(msg.usage, "output_tokens", 0) or 0
                        cost = calculate_cost("anthropic", model, tokens_in, tokens_out)
                        transport.send({
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "provider": "anthropic",
                            "model": model,
                            "tokens_in": tokens_in,
                            "tokens_out": tokens_out,
                            "cost_usd": cost,
                            "latency_ms": elapsed,
                            "status": "success",
                            "feature": merged_meta.get("feature"),
                            "user_id": merged_meta.get("user_id"),
                            "project": project,
                        })
                except Exception:
                    pass
                return result

            def __iter__(self):
                return iter(self._ctx)

            def __getattr__(self, name):
                return getattr(self._ctx, name)

        return TrackedStreamContext(stream_ctx)

    client.messages.stream = tracked_stream


def _wrap_openai(client: Any, project: str, default_meta: dict):
    """Patch openai.OpenAI().chat.completions.create to track calls."""
    original_create = client.chat.completions.create

    def tracked_create(*args, **kwargs):
        meta = kwargs.pop("llmspend", {})
        merged_meta = {**default_meta, **meta}

        start = time.monotonic()
        error = None
        response = None

        try:
            response = original_create(*args, **kwargs)
            return response
        except Exception as e:
            error = e
            raise
        finally:
            try:
                elapsed = int((time.monotonic() - start) * 1000)
                model = kwargs.get("model", "unknown")
                tokens_in = 0
                tokens_out = 0
                status = "error"

                if response is not None and hasattr(response, "usage") and response.usage:
                    tokens_in = getattr(response.usage, "prompt_tokens", 0) or 0
                    tokens_out = getattr(response.usage, "completion_tokens", 0) or 0
                    status = "success"

                cost = calculate_cost("openai", model, tokens_in, tokens_out)

                event = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "provider": "openai",
                    "model": model,
                    "tokens_in": tokens_in,
                    "tokens_out": tokens_out,
                    "cost_usd": cost,
                    "latency_ms": elapsed,
                    "status": status,
                    "error": str(error)[:200] if error else None,
                    "feature": merged_meta.get("feature"),
                    "user_id": merged_meta.get("user_id"),
                    "project": project,
                }
                transport.send(event)
            except Exception:
                pass  # Never crash the developer's app

    client.chat.completions.create = tracked_create
