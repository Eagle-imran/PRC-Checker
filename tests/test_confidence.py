"""
Unit tests for Confidence Scorecard Engine in prc_checker.confidence.
"""
from prc_checker.confidence import calculate_confidence_scorecard
from prc_checker.models import TitleReportData


def test_confidence_scorecard_high_confidence():
    """Verify HIGH CONFIDENCE rating for complete data."""
    report = TitleReportData(
        cts="748",
        village="Worli",
        district="23",
        area_sqm=1250.0,
        tenure="Occupant Class I (Freehold)",
        sheet_no="54",
        register_no="12",
        page_no="340",
        transfer_chain=[("A", "B"), ("B", "C")]
    )
    scores, total, rating = calculate_confidence_scorecard(report)
    assert len(scores) == 5
    assert total >= 21
    assert rating == "HIGH CONFIDENCE"


def test_confidence_scorecard_low_confidence():
    """Verify LOW CONFIDENCE rating for minimal data."""
    report = TitleReportData(cts="123", village="Test")
    scores, total, rating = calculate_confidence_scorecard(report)
    assert len(scores) == 5
    assert total < 15
    assert rating == "LOW CONFIDENCE"


def test_confidence_scorecard_medium_confidence():
    """Verify MEDIUM CONFIDENCE rating for partial data."""
    report = TitleReportData(
        cts="456",
        village="Test",
        area_sqm=500.0,
        tenure="Leasehold",
        active_lessee="Test Party"
    )
    _scores, total, rating = calculate_confidence_scorecard(report)
    assert 15 <= total < 21
    assert rating == "MEDIUM CONFIDENCE"
