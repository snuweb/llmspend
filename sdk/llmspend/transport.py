"""Async log shipping — sends events to the LLMSpend backend.

Design rules:
- NEVER block the developer's code
- NEVER crash if the backend is down
- Buffer events and flush in batches
- Fall back to local SQLite if no backend configured
"""

import atexit
import json
import logging
import threading
import time
from collections import deque
from typing import Any

_backend_url: str | None = None
_api_key: str | None = None
_buffer: deque[dict[str, Any]] = deque(maxlen=10_000)
_flush_interval: float = 5.0  # seconds
_flush_thread: threading.Thread | None = None
_running = False
_local_path: str | None = None
_thread_lock = threading.Lock()

log = logging.getLogger("llmspend")


def configure(backend_url: str | None = None, api_key: str | None = None,
              local_path: str | None = None, flush_interval: float = 5.0):
    """Configure the transport layer."""
    global _backend_url, _api_key, _local_path, _flush_interval
    if backend_url and not backend_url.startswith("https://"):
        if not backend_url.startswith("http://localhost") and not backend_url.startswith("http://127.0.0.1"):
            log.warning("llmspend: backend_url uses HTTP — API key will be sent unencrypted. Use HTTPS in production.")
    _backend_url = backend_url.rstrip("/") if backend_url else None
    _api_key = api_key
    _local_path = local_path
    _flush_interval = flush_interval
    _ensure_flush_thread()


def send(event: dict[str, Any]):
    """Queue an event for async delivery. Never blocks, never throws."""
    try:
        _buffer.append(event)
        _ensure_flush_thread()
    except Exception:
        pass  # SDK rule: never crash the developer's app


def _ensure_flush_thread():
    """Start the background flush thread if not already running."""
    global _flush_thread, _running
    with _thread_lock:
        if _flush_thread is not None and _flush_thread.is_alive():
            return
        _running = True
        _flush_thread = threading.Thread(target=_flush_loop, daemon=True)
        _flush_thread.start()


def _flush_loop():
    """Background loop: flush buffered events every N seconds."""
    while _running:
        time.sleep(_flush_interval)
        _flush()


def _flush():
    """Send all buffered events to backend or local storage."""
    if not _buffer:
        return

    # Drain the buffer
    batch = []
    while _buffer:
        try:
            batch.append(_buffer.popleft())
        except IndexError:
            break

    if not batch:
        return

    # Try backend first
    if _backend_url:
        try:
            _send_to_backend(batch)
            return
        except Exception:
            pass  # Fall through to local

    # Fall back to local SQLite
    _save_local(batch)


def _send_to_backend(batch: list[dict]):
    """POST events to the LLMSpend backend. Uses urllib to avoid extra dependencies."""
    import urllib.request
    import urllib.error

    url = f"{_backend_url}/v1/events"
    data = json.dumps({"events": batch}).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    if _api_key:
        headers["Authorization"] = f"Bearer {_api_key}"

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        # If backend fails, save locally
        _save_local(batch)


def _save_local(batch: list[dict]):
    """Append events to local SQLite database."""
    import sqlite3
    import os
    import pwd

    # Use actual process user's home (not $HOME which may be wrong under sudo)
    if _local_path:
        db_path = _local_path
    else:
        try:
            real_home = pwd.getpwuid(os.getuid()).pw_dir
        except (KeyError, ImportError):
            real_home = os.path.expanduser("~")
        db_path = os.path.join(real_home, ".llmspend", "events.db")
    db_dir = os.path.dirname(db_path)
    os.makedirs(db_dir, mode=0o700, exist_ok=True)

    try:
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                provider TEXT,
                model TEXT,
                tokens_in INTEGER,
                tokens_out INTEGER,
                cost_usd REAL,
                latency_ms INTEGER,
                status TEXT,
                feature TEXT,
                user_id TEXT,
                project TEXT,
                raw_json TEXT
            )
        """)
        for event in batch:
            conn.execute(
                """INSERT INTO events
                   (timestamp, provider, model, tokens_in, tokens_out, cost_usd,
                    latency_ms, status, feature, user_id, project, raw_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event.get("timestamp"),
                    event.get("provider"),
                    event.get("model"),
                    event.get("tokens_in"),
                    event.get("tokens_out"),
                    event.get("cost_usd"),
                    event.get("latency_ms"),
                    event.get("status"),
                    event.get("feature"),
                    event.get("user_id"),
                    event.get("project"),
                    json.dumps(event),
                ),
            )
        conn.commit()
        conn.close()
    except Exception:
        pass  # Last resort: silently drop. Never crash the developer's app.


# Flush remaining events on process exit
atexit.register(_flush)
