"""LLMSpend — Stop overpaying for AI inference.

Track costs:
    from llmspend import monitor
    client = monitor.wrap(anthropic.Anthropic(), project="my-app")

Smart routing (auto-picks cheapest model per task):
    from llmspend import router
    client = router.smart(anthropic.Anthropic(), project="my-app")
"""

__version__ = "0.2.0"

from llmspend.monitor import wrap, configure  # noqa: F401
from llmspend import router  # noqa: F401
