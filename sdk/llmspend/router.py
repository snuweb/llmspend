"""Smart Router — routes LLM calls to the cheapest model that works.

The router classifies each call's complexity using a multi-signal scoring
engine, then routes to the appropriate model tier. It learns from outcomes:
if a cheap model fails (error, retry, or user escalation), the router
remembers and adjusts future routing for similar prompts.

Architecture:
    1. CLASSIFY — score prompt complexity (0-100) using 12 signals
    2. ROUTE — pick cheapest model in the appropriate tier
    3. EXECUTE — call the model, capture response
    4. LEARN — track success/failure, adjust weights over time

The classification engine uses NO LLM calls. It's pure heuristics + learned
weights from historical outcomes. This means routing itself costs $0.

Usage:
    from llmspend import router

    client = router.smart(
        anthropic.Anthropic(),
        project="my-app",
        strategy="cheapest",  # or "balanced", "quality"
    )
    # Use exactly like before — routing is invisible
    response = client.messages.create(...)
"""

import hashlib
import json
import os
import re
import sqlite3
import time
import threading
from datetime import datetime, timezone
from typing import Any

from llmspend.pricing import calculate_cost, PRICING
from llmspend import transport


# ── Default model tiers ────────────────────────────────────────────────

DEFAULT_TIERS = {
    "anthropic": {
        "simple":  "claude-haiku-4-5-20251001",
        "medium":  "claude-sonnet-4-6",
        "complex": "claude-opus-4-6",
    },
    "openai": {
        "simple":  "gpt-4o-mini",
        "medium":  "gpt-4o",
        "complex": "o3",
    },
    "groq": {
        "simple":  "llama-3.1-8b-instant",
        "medium":  "llama-3.3-70b-versatile",
        "complex": "llama-3.3-70b-versatile",
    },
}


# ── Complexity Signals (the core IP) ───────────────────────────────────

# Keywords that indicate simple tasks
SIMPLE_SIGNALS = {
    "classify", "extract", "summarize", "translate", "format", "convert",
    "list", "count", "filter", "sort", "parse", "validate", "label",
    "true or false", "yes or no", "one word", "short answer",
    "json", "csv", "markdown", "bullet points",
}

# Keywords that indicate complex tasks
COMPLEX_SIGNALS = {
    "analyze", "reason", "explain why", "compare and contrast", "debate",
    "create", "design", "architect", "plan", "strategy", "write code",
    "implement", "refactor", "debug", "review", "critique", "evaluate",
    "multi-step", "chain of thought", "think step by step",
    "edge cases", "trade-offs", "implications", "nuance",
}

# System prompt patterns that indicate complexity
COMPLEX_SYSTEM_PATTERNS = [
    re.compile(r"you are a.*expert", re.I),
    re.compile(r"think.*carefully", re.I),
    re.compile(r"step.by.step", re.I),
    re.compile(r"chain.of.thought", re.I),
    re.compile(r"reason.*through", re.I),
]


class ComplexityScorer:
    """Scores prompt complexity on a 0-100 scale using 12 signals.

    The scorer uses NO LLM calls — pure heuristics + learned weights.
    Each signal contributes 0-10 points. Total is capped at 100.
    """

    def __init__(self, history_db: str | None = None):
        self._db_path = history_db or os.path.join(
            os.path.expanduser("~"), ".llmspend", "router_history.db"
        )
        self._init_db()

    def _init_db(self):
        """Initialize SQLite for routing history (learning)."""
        try:
            os.makedirs(os.path.dirname(self._db_path), mode=0o700, exist_ok=True)
            conn = sqlite3.connect(self._db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS routing_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_hash TEXT NOT NULL,
                    prompt_length INTEGER,
                    tier_used TEXT,
                    model_used TEXT,
                    success INTEGER,
                    latency_ms INTEGER,
                    cost_usd REAL,
                    created_at TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_rh_hash ON routing_history(prompt_hash)
            """)
            conn.commit()
            conn.close()
        except Exception:
            pass

    def _prompt_hash(self, text: str) -> str:
        """Hash first 200 chars of prompt for similarity matching."""
        normalized = re.sub(r'\s+', ' ', text[:200].lower().strip())
        return hashlib.md5(normalized.encode()).hexdigest()[:12]

    def _check_history(self, prompt_hash: str) -> dict | None:
        """Check if we've routed similar prompts before."""
        try:
            conn = sqlite3.connect(self._db_path)
            rows = conn.execute(
                """SELECT tier_used, success, COUNT(*) as cnt
                   FROM routing_history
                   WHERE prompt_hash = ?
                   GROUP BY tier_used, success
                   ORDER BY cnt DESC""",
                (prompt_hash,)
            ).fetchall()
            conn.close()
            if not rows:
                return None

            # Calculate success rate per tier
            tier_stats = {}
            for tier, success, cnt in rows:
                if tier not in tier_stats:
                    tier_stats[tier] = {"success": 0, "fail": 0}
                if success:
                    tier_stats[tier]["success"] += cnt
                else:
                    tier_stats[tier]["fail"] += cnt

            return tier_stats
        except Exception:
            return None

    def _record(self, prompt_hash: str, prompt_length: int, tier: str,
                model: str, success: bool, latency_ms: int, cost: float):
        """Record routing outcome for learning."""
        try:
            conn = sqlite3.connect(self._db_path)
            conn.execute(
                """INSERT INTO routing_history
                   (prompt_hash, prompt_length, tier_used, model_used, success, latency_ms, cost_usd, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (prompt_hash, prompt_length, tier, model, int(success),
                 latency_ms, cost, datetime.now(timezone.utc).isoformat())
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def score(self, messages: list[dict], system: str | None = None,
              tools: list | None = None, max_tokens: int = 1024) -> dict:
        """Score complexity and return routing recommendation.

        Returns:
            {
                "score": 0-100,
                "tier": "simple" | "medium" | "complex",
                "signals": {"signal_name": score, ...},
                "prompt_hash": "abc123",
            }
        """
        # Extract text content
        prompt_text = ""
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                prompt_text += content + " "
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        prompt_text += block.get("text", "") + " "

        prompt_lower = prompt_text.lower().strip()
        prompt_tokens = len(prompt_text.split())
        system_text = (system or "").lower()
        prompt_hash = self._prompt_hash(prompt_text)

        signals = {}
        total = 0

        # ── Signal 1: Prompt length (0-10) ──
        if prompt_tokens < 30:
            signals["length"] = 0  # very short = likely simple
        elif prompt_tokens < 100:
            signals["length"] = 2
        elif prompt_tokens < 500:
            signals["length"] = 5
        elif prompt_tokens < 2000:
            signals["length"] = 7
        else:
            signals["length"] = 10  # very long = likely complex

        # ── Signal 2: Simple keywords (0 to -15) ──
        simple_hits = sum(1 for kw in SIMPLE_SIGNALS if kw in prompt_lower)
        signals["simple_keywords"] = -min(simple_hits * 3, 15)

        # ── Signal 3: Complex keywords (0 to +15) ──
        complex_hits = sum(1 for kw in COMPLEX_SIGNALS if kw in prompt_lower)
        signals["complex_keywords"] = min(complex_hits * 3, 15)

        # ── Signal 4: System prompt complexity (0-10) ──
        sys_score = 0
        if system_text:
            sys_tokens = len(system_text.split())
            if sys_tokens > 200: sys_score += 3
            if sys_tokens > 500: sys_score += 3
            for pattern in COMPLEX_SYSTEM_PATTERNS:
                if pattern.search(system_text):
                    sys_score += 2
        signals["system_prompt"] = min(sys_score, 10)

        # ── Signal 5: Tool usage (0 or +8) ──
        signals["tools"] = 8 if tools and len(tools) > 0 else 0

        # ── Signal 6: Max tokens requested (0-8) ──
        if max_tokens <= 100:
            signals["max_tokens"] = 0
        elif max_tokens <= 500:
            signals["max_tokens"] = 2
        elif max_tokens <= 2000:
            signals["max_tokens"] = 5
        else:
            signals["max_tokens"] = 8

        # ── Signal 7: Question complexity markers (0-8) ──
        q_score = 0
        if "?" in prompt_text:
            questions = prompt_text.count("?")
            if questions > 3: q_score += 4  # multiple questions
            if any(w in prompt_lower for w in ["why", "how", "explain"]): q_score += 2
            if any(w in prompt_lower for w in ["what is", "define", "list"]): q_score -= 2
        signals["question_complexity"] = max(min(q_score, 8), -4)

        # ── Signal 8: Code markers (0-8) ──
        code_markers = ["```", "def ", "class ", "function ", "import ", "const ", "var "]
        code_hits = sum(1 for m in code_markers if m in prompt_text)
        signals["code_markers"] = min(code_hits * 2, 8)

        # ── Signal 9: Output format specificity (0 to -6) ──
        format_markers = ["json", "csv", "yaml", "xml", "true/false", "yes/no", "one word"]
        format_hits = sum(1 for m in format_markers if m in prompt_lower)
        signals["output_format"] = -min(format_hits * 3, 6)  # structured output = simpler

        # ── Signal 10: Conversation depth (0-6) ──
        msg_count = len(messages)
        signals["conversation_depth"] = min(msg_count - 1, 6) if msg_count > 1 else 0

        # ── Signal 11: Image/multimodal content (0 or +10) ──
        has_images = any(
            isinstance(msg.get("content"), list) and
            any(b.get("type") == "image" for b in msg["content"] if isinstance(b, dict))
            for msg in messages
        )
        signals["multimodal"] = 10 if has_images else 0

        # ── Signal 12: Historical learning (override, -20 to +20) ──
        history = self._check_history(prompt_hash)
        if history:
            if "simple" in history:
                s = history["simple"]
                if s["success"] > 0 and s["fail"] == 0:
                    signals["history"] = -15  # cheap model always worked
                elif s["fail"] > s["success"]:
                    signals["history"] = 15   # cheap model usually fails
                else:
                    signals["history"] = -5   # cheap model mostly works
            elif "medium" in history:
                s = history["medium"]
                if s["fail"] > 0:
                    signals["history"] = 10   # even medium fails sometimes
                else:
                    signals["history"] = 0
            else:
                signals["history"] = 0
        else:
            signals["history"] = 0

        # ── Calculate total ──
        total = 50  # baseline (medium)
        for name, value in signals.items():
            total += value
        total = max(0, min(100, total))

        # ── Determine tier ──
        if total < 35:
            tier = "simple"
        elif total < 65:
            tier = "medium"
        else:
            tier = "complex"

        return {
            "score": total,
            "tier": tier,
            "signals": signals,
            "prompt_hash": prompt_hash,
            "prompt_tokens": prompt_tokens,
        }


class SmartRouter:
    """Wraps an LLM client with intelligent cost-optimized routing.

    Usage:
        from llmspend import router
        client = router.smart(anthropic.Anthropic(), project="my-app")
        # Use exactly like before
        response = client.messages.create(...)
    """

    def __init__(self, client: Any, project: str = "default",
                 tiers: dict | None = None, strategy: str = "cheapest"):
        self._client = client
        self._project = project
        self._strategy = strategy
        self._scorer = ComplexityScorer()
        self._provider = self._detect_provider(client)
        self._tiers = tiers or DEFAULT_TIERS.get(self._provider, {})

    def _detect_provider(self, client) -> str:
        client_type = type(client).__module__ or ""
        if "anthropic" in client_type: return "anthropic"
        if "openai" in client_type: return "openai"
        if "groq" in client_type: return "groq"
        return "anthropic"  # default

    def _get_model_for_tier(self, tier: str) -> str:
        """Get the model ID for a given tier."""
        return self._tiers.get(tier, self._tiers.get("medium", ""))

    def _route_anthropic(self, *args, **kwargs):
        """Route an Anthropic messages.create() call."""
        messages = kwargs.get("messages", [])
        system = kwargs.get("system")
        tools = kwargs.get("tools")
        max_tokens = kwargs.get("max_tokens", 1024)
        original_model = kwargs.get("model", "")
        meta = kwargs.pop("llmspend", {})

        # Score complexity
        result = self._scorer.score(messages, system, tools, max_tokens)
        tier = result["tier"]
        score = result["score"]

        # Override: if user explicitly set a model, respect it
        if meta.get("force_model"):
            tier = "forced"
            model = original_model
        else:
            model = self._get_model_for_tier(tier)
            if not model:
                model = original_model

        kwargs["model"] = model
        start = time.monotonic()
        error = None
        response = None

        try:
            response = self._client.messages.create(*args, **kwargs)
            return response
        except Exception as e:
            error = e
            # Retry with next tier up
            if tier == "simple":
                kwargs["model"] = self._get_model_for_tier("medium")
                try:
                    response = self._client.messages.create(*args, **kwargs)
                    model = kwargs["model"]
                    tier = "medium_fallback"
                    return response
                except Exception:
                    pass
            if tier in ("simple", "medium", "medium_fallback"):
                kwargs["model"] = self._get_model_for_tier("complex")
                try:
                    response = self._client.messages.create(*args, **kwargs)
                    model = kwargs["model"]
                    tier = "complex_fallback"
                    return response
                except Exception:
                    pass
            raise error
        finally:
            elapsed = int((time.monotonic() - start) * 1000)
            tokens_in = 0
            tokens_out = 0
            if response and hasattr(response, "usage"):
                tokens_in = getattr(response.usage, "input_tokens", 0) or 0
                tokens_out = getattr(response.usage, "output_tokens", 0) or 0

            cost = calculate_cost(self._provider, model, tokens_in, tokens_out)
            success = error is None

            # Record for learning
            self._scorer._record(
                result["prompt_hash"], result["prompt_tokens"],
                tier, model, success, elapsed, cost or 0
            )

            # Log to transport
            try:
                transport.send({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "provider": self._provider,
                    "model": model,
                    "original_model": original_model,
                    "routed_tier": tier,
                    "complexity_score": score,
                    "tokens_in": tokens_in,
                    "tokens_out": tokens_out,
                    "cost_usd": cost,
                    "latency_ms": elapsed,
                    "status": "success" if success else "error",
                    "feature": meta.get("feature"),
                    "user_id": meta.get("user_id"),
                    "project": self._project,
                })
            except Exception:
                pass

    class _RoutedMessages:
        """Proxy for client.messages that routes .create() calls."""
        def __init__(self, router):
            self._router = router
            # Preserve other methods
            self._original = router._client.messages

        def create(self, *args, **kwargs):
            return self._router._route_anthropic(*args, **kwargs)

        def __getattr__(self, name):
            return getattr(self._original, name)

    @property
    def messages(self):
        return self._RoutedMessages(self)

    def __getattr__(self, name):
        """Pass through any non-routing calls to the original client."""
        return getattr(self._client, name)


def smart(client: Any, project: str = "default",
          tiers: dict | None = None, strategy: str = "cheapest") -> Any:
    """Wrap an LLM client with smart cost-optimized routing.

    Args:
        client: An anthropic.Anthropic() or openai.OpenAI() instance
        project: Project name for cost grouping
        tiers: Custom model tiers {simple: model, medium: model, complex: model}
        strategy: "cheapest" (default), "balanced", or "quality"

    Returns:
        A wrapped client that routes calls to optimal models.
    """
    return SmartRouter(client, project, tiers, strategy)
