"""Core monitor — wraps Anthropic and OpenAI clients to track costs.

Usage:
    from llmspend import monitor
    client = monitor.wrap(anthropic.Anthropic(), project="my-app")
    # Use client exactly as before — all calls are now tracked.
"""

import time
from datetime import datetime, timezone
from typing import Any

import re

from llmspend.pricing import calculate_cost
from llmspend import transport

# Pattern to detect API keys/tokens in error messages
_SECRET_PATTERN = re.compile(
    r'(sk-[a-zA-Z0-9]{10,}|Bearer\s+[a-zA-Z0-9_\-]{10,}|key-[a-zA-Z0-9]{10,})',
    re.IGNORECASE
)


def _safe_error(error: Exception) -> str:
    """Extract error type and message, redacting any API keys or tokens."""
    msg = f"{type(error).__name__}: {str(error)[:200]}"
    return _SECRET_PATTERN.sub("[REDACTED]", msg)


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
    # Prevent double-wrapping the same client
    if getattr(client, "_llmspend_wrapped", False):
        return client

    provider = _detect_provider(client)
    if provider is None:
        # Unknown client — return as-is, don't break anything
        return client

    if provider == "anthropic":
        _wrap_anthropic(client, project, default_metadata)
    elif provider in ("openai", "groq"):
        # Groq uses OpenAI-compatible API
        _wrap_openai(client, project, default_metadata, provider=provider)
    elif provider == "mistral":
        _wrap_openai_style(client, project, default_metadata, provider="mistral")

    client._llmspend_wrapped = True
    return client


def _detect_provider(client: Any) -> str | None:
    """Detect whether this is an Anthropic or OpenAI client."""
    client_type = type(client).__module__ or ""
    client_name = type(client).__name__ or ""

    if "anthropic" in client_type or client_name in ("Anthropic", "AsyncAnthropic"):
        return "anthropic"
    if "openai" in client_type or client_name in ("OpenAI", "AsyncOpenAI"):
        return "openai"
    if "google" in client_type or "genai" in client_type or client_name == "GenerativeModel":
        return "google"
    if "groq" in client_type or client_name in ("Groq", "AsyncGroq"):
        return "groq"
    if "mistralai" in client_type or client_name in ("Mistral", "MistralClient"):
        return "mistral"
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
                    "error": _safe_error(error) if error else None,
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


def _wrap_openai(client: Any, project: str, default_meta: dict, provider: str = "openai"):
    """Patch OpenAI-compatible client (OpenAI, Groq) to track calls."""
    original_create = client.chat.completions.create

    def tracked_create(*args, **kwargs):
        meta = kwargs.pop("llmspend", {})
        merged_meta = {**default_meta, **meta}

        is_stream = kwargs.get("stream", False)

        start = time.monotonic()
        error = None
        response = None

        try:
            response = original_create(*args, **kwargs)
            if is_stream:
                return _TrackedOpenAIStream(
                    response, start, kwargs.get("model", "unknown"),
                    merged_meta, project, provider=provider
                )
            return response
        except Exception as e:
            error = e
            raise
        finally:
            if not is_stream:
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

                    cost = calculate_cost(provider, model, tokens_in, tokens_out)

                    transport.send({
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "provider": provider,
                        "model": model,
                        "tokens_in": tokens_in,
                        "tokens_out": tokens_out,
                        "cost_usd": cost,
                        "latency_ms": elapsed,
                        "status": status,
                        "error": _safe_error(error) if error else None,
                        "feature": merged_meta.get("feature"),
                        "user_id": merged_meta.get("user_id"),
                        "project": project,
                    })
                except Exception:
                    pass

    client.chat.completions.create = tracked_create


def _wrap_openai_style(client: Any, project: str, default_meta: dict, provider: str = "mistral"):
    """Wrap Mistral and other OpenAI-style clients that use client.chat.complete()."""
    # Mistral uses client.chat.complete() not client.chat.completions.create()
    chat_obj = getattr(client, "chat", None)
    if chat_obj is None:
        return

    original_fn = getattr(chat_obj, "complete", None) or getattr(chat_obj, "create", None)
    if original_fn is None:
        return

    def tracked(*args, **kwargs):
        meta = kwargs.pop("llmspend", {})
        merged_meta = {**default_meta, **meta}
        start = time.monotonic()
        error = None
        response = None
        try:
            response = original_fn(*args, **kwargs)
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
                    tokens_in = getattr(response.usage, "prompt_tokens", 0) or getattr(response.usage, "total_tokens", 0) or 0
                    tokens_out = getattr(response.usage, "completion_tokens", 0) or 0
                    status = "success"
                cost = calculate_cost(provider, model, tokens_in, tokens_out)
                transport.send({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "provider": provider,
                    "model": model,
                    "tokens_in": tokens_in,
                    "tokens_out": tokens_out,
                    "cost_usd": cost,
                    "latency_ms": elapsed,
                    "status": status,
                    "error": _safe_error(error) if error else None,
                    "feature": merged_meta.get("feature"),
                    "user_id": merged_meta.get("user_id"),
                    "project": project,
                })
            except Exception:
                pass

    if hasattr(chat_obj, "complete"):
        chat_obj.complete = tracked
    else:
        chat_obj.create = tracked


class _TrackedOpenAIStream:
    """Wraps an OpenAI streaming response to capture usage from the final chunk."""

    def __init__(self, stream, start: float, model: str, meta: dict, project: str, provider: str = "openai"):
        self._stream = stream
        self._start = start
        self._model = model
        self._meta = meta
        self._project = project
        self._provider = provider
        self._tokens_in = 0
        self._tokens_out = 0
        self._logged = False

    def __iter__(self):
        try:
            for chunk in self._stream:
                # OpenAI sends usage in the final chunk when stream_options={"include_usage": True}
                if hasattr(chunk, "usage") and chunk.usage:
                    self._tokens_in = getattr(chunk.usage, "prompt_tokens", 0) or 0
                    self._tokens_out = getattr(chunk.usage, "completion_tokens", 0) or 0
                yield chunk
        finally:
            self._log_event()

    def __enter__(self):
        if hasattr(self._stream, "__enter__"):
            self._stream.__enter__()
        return self

    def __exit__(self, *exc):
        result = None
        if hasattr(self._stream, "__exit__"):
            result = self._stream.__exit__(*exc)
        self._log_event()
        return result

    def __getattr__(self, name):
        return getattr(self._stream, name)

    def _log_event(self):
        if self._logged:
            return
        self._logged = True
        try:
            elapsed = int((time.monotonic() - self._start) * 1000)
            cost = calculate_cost(self._provider, self._model, self._tokens_in, self._tokens_out)
            transport.send({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "provider": self._provider,
                "model": self._model,
                "tokens_in": self._tokens_in,
                "tokens_out": self._tokens_out,
                "cost_usd": cost,
                "latency_ms": elapsed,
                "status": "success",
                "feature": self._meta.get("feature"),
                "user_id": self._meta.get("user_id"),
                "project": self._project,
            })
        except Exception:
            pass
