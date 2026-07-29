"""
Pytest Unit Tests for Title Audit Reports, Promoter Briefs, Lawyer Briefs & HTML rendering.
"""
from __future__ import annotations

from prc_checker.models import TitleReportData, RiskFlag
from prc_checker.reports import (
    generate_clean_html,
    generate_title_report_md,
    generate_promoter_brief,
    generate_lawyer_brief,
)


def test_generate_clean_html():
    html = generate_clean_html("propcard_Byculla_1640")
    assert "<!DOCTYPE html>" in html
    assert "Property Card — Byculla CTS 1640" in html
    assert 'src="propcard_Byculla_1640.jpg"' in html
    assert "data:image/jpeg;base64" not in html


def test_generate_title_report_md_with_data_model():
    report_data = TitleReportData(
        cts="748",
        village="Worli",
        district="23",
        area_sqm=1250.50,
        tenure="CIT / Leasehold",
        transfer_chain=[("MCGB", "Party A"), ("Party A", "Party B")],
        risk_flags=[RiskFlag(severity="HIGH", risk_type="LEASE_EXPIRATION", description="Lease expired 2020")]
    )
    report = generate_title_report_md("Worli", "748", report_data)
    assert "# Property Title Audit Report — Worli CTS 748" in report
    assert "## Block 1: Property Identification & Details" in report
    assert "Worli" in report
    assert "748" in report
    assert "1250.5" in report
    assert "CIT / Leasehold" in report
    assert "N0[\"MCGB\"] --> N1[\"Party A\"]" in report
    assert "N1[\"Party A\"] --> N2[\"Party B\"]" in report
    assert "LEASE_EXPIRATION" in report


def test_generate_promoter_brief():
    report_data = TitleReportData(cts="518", village="Malabar Hill", district="23", area_sqm=850.0)
    brief = generate_promoter_brief("Malabar Hill", "518", report_data)
    assert "# Promoter Executive Brief — Malabar Hill CTS 518" in brief
    assert "Malabar Hill" in brief
    assert "518" in brief


def test_generate_lawyer_brief():
    report_data = TitleReportData(cts="1590", village="मरोळ", district="22", area_sqm=2478.8)
    brief = generate_lawyer_brief("मरोळ", "1590", report_data)
    assert "# Legal Counsel Brief — Title & Tenure Opinion" in brief
    assert "मरोळ" in brief
    assert "1590" in brief
