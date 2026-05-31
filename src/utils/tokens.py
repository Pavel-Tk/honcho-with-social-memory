from functools import cache
from logging import getLogger

import tiktoken

from src.config import settings
from src.telemetry import prometheus_metrics
from src.telemetry.prometheus.metrics import (
    DeriverComponents,
    DeriverTaskTypes,
    TokenTypes,
)

logger = getLogger(__name__)


@cache
def _get_tokenizer() -> tiktoken.Encoding | None:
    """Return the preferred tokenizer, falling back when offline caches are cold."""
    for encoding_name in ("o200k_base", "cl100k_base"):
        try:
            return tiktoken.get_encoding(encoding_name)
        except Exception as exc:
            logger.warning(
                "Failed to load tiktoken encoding %s; falling back if possible: %s",
                encoding_name,
                exc,
            )
    return None


def _estimated_token_count(text: str) -> int:
    """Conservative token count fallback when tiktoken data is unavailable."""
    if not text:
        return 0
    return max(1, len(text) // 4)


def encode_text(text: str) -> list[int]:
    """Encode text for token counting, with an offline-safe approximate fallback."""
    tokenizer = _get_tokenizer()
    if tokenizer is not None:
        try:
            return tokenizer.encode(text)
        except Exception as exc:
            logger.warning("Failed to encode text with tiktoken; estimating: %s", exc)
    return list(range(_estimated_token_count(text)))


def estimate_tokens(text: str | list[str] | None) -> int:
    """Estimate token count using tiktoken for text or list of strings."""
    if not text:
        return 0
    if isinstance(text, list):
        text = "\n".join(text)
    return len(encode_text(text))


def track_deriver_input_tokens(
    task_type: DeriverTaskTypes,
    components: dict[DeriverComponents, int],
) -> None:
    """
    Helper method to track input token components for a given task type.

    Args:
        task_type: The type of task
        components: Dict mapping component names to token counts
    """
    for component, token_count in components.items():
        # Prometheus metrics
        if settings.METRICS.ENABLED:
            prometheus_metrics.record_deriver_tokens(
                count=token_count,
                task_type=task_type.value,
                token_type=TokenTypes.INPUT.value,
                component=component.value,
            )
