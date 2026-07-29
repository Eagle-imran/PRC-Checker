"""
Pytest Unit Tests for Pydantic Models.
"""
from __future__ import annotations

from prc_checker.models import CardResult, Manifest, RiskFlag, TitleReportData


def test_risk_flag_model():
    flag = RiskFlag(severity="HIGH", risk_type="LEASE_EXPIRATION", description="Test risk")
    assert flag.severity == "HIGH"
    assert flag.risk_type == "LEASE_EXPIRATION"


def test_title_report_data_model_defaults():
    report = TitleReportData(cts="1640", village="Byculla")
    assert report.cts == "1640"
    assert report.village == "Byculla"
    assert report.area_sqm is None  # Zero hardcoded fake defaults!
    assert report.active_lessee is None
    assert len(report.risk_flags) == 0


def test_card_result_model():
    res = CardResult(
        cts="1640",
        village="Byculla",
        district="23",
        status="ok",
        file_jpg="propcard_Byculla_1640.jpg",
        file_html="propcard_Byculla_1640.html",
        file_report="title_report_propcard_Byculla_1640.md",
        file_json="propcard_Byculla_1640.json",
        bytes=407102
    )
    assert res.cts == "1640"
    assert res.status == "ok"
    assert res.bytes == 407102


def test_manifest_model():
    res = CardResult(cts="1640", village="Byculla", district="23", status="ok", bytes=407102)
    manifest = Manifest(village="Byculla", district="23", results=[res])
    assert manifest.village == "Byculla"
    assert len(manifest.results) == 1
