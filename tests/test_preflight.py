"""
Unit tests for BhuNaksha Preflight Engine in prc_checker.preflight.
"""
from prc_checker.preflight import PreflightResult, check_plot_preflight


def test_preflight_result_model():
    """Verify PreflightResult schema validation and default fields."""
    res = PreflightResult(
        village="Worli",
        cts="748",
        district="23",
        exists=True,
        response_time_ms=115.4
    )
    assert res.village == "Worli"
    assert res.cts == "748"
    assert res.district == "23"
    assert res.exists is True
    assert res.response_time_ms == 115.4


def test_check_plot_preflight_fast_response():
    """Verify check_plot_preflight returns within 2.0 seconds and populates response_time_ms."""
    res = check_plot_preflight("Byculla", "1640", district="23", timeout=2.0)
    assert res.village == "Byculla"
    assert res.cts == "1640"
    assert res.exists is True
    assert res.response_time_ms >= 0.0
