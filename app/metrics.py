"""Execution metrics for the AI Tutor Agent."""

from __future__ import annotations

import time
from typing import Dict


def start_timer() -> float:
    """Start a high-resolution timer."""
    return time.perf_counter()


def elapsed_ms(start_time: float) -> float:
    """Return elapsed time in milliseconds."""
    return round((time.perf_counter() - start_time) * 1000, 2)


def create_metrics() -> Dict[str, float]:
    """Create an empty execution metrics dictionary."""
    return {
        "total_ms": 0.0,
        "retrieve_ms": 0.0,
        "grade_ms": 0.0,
        "web_search_ms": 0.0,
        "generate_ms": 0.0,
    }