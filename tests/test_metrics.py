import time

from app.metrics import (
    create_metrics,
    elapsed_ms,
    start_timer,
)


# ============================================================
# METRICS STRUCTURE
# ============================================================

def test_create_metrics_contains_expected_fields():

    metrics = create_metrics()

    assert "total_ms" in metrics
    assert "retrieve_ms" in metrics
    assert "grade_ms" in metrics
    assert "web_search_ms" in metrics
    assert "generate_ms" in metrics


def test_create_metrics_starts_at_zero():

    metrics = create_metrics()

    assert metrics["total_ms"] == 0.0
    assert metrics["retrieve_ms"] == 0.0
    assert metrics["grade_ms"] == 0.0
    assert metrics["web_search_ms"] == 0.0
    assert metrics["generate_ms"] == 0.0


# ============================================================
# TIMER
# ============================================================

def test_start_timer_returns_numeric_value():

    timer = start_timer()

    assert isinstance(timer, float)


def test_elapsed_ms_returns_non_negative_value():

    timer = start_timer()

    time.sleep(0.01)

    elapsed = elapsed_ms(timer)

    assert isinstance(elapsed, float)
    assert elapsed >= 0


def test_elapsed_ms_measures_elapsed_time():

    timer = start_timer()

    time.sleep(0.05)

    elapsed = elapsed_ms(timer)

    # Should be approximately 50 ms.
    # Allow a generous lower bound because system scheduling
    # can vary between machines.
    assert elapsed >= 40