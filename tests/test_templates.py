"""
Pytest Unit Tests for Jinja2 Template Rendering & Briefs.
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from prc_checker.dashboard import generate_dashboard_html
from prc_checker.models import CardResult, TitleReportData
from prc_checker.reports import (
    generate_clean_html,
    generate_title_report_md,
    generate_promoter_brief,
    generate_lawyer_brief,
)


def test_clean_html_jinja2_rendering():
    html = generate_clean_html("propcard_Byculla_1640")
    assert "<!DOCTYPE html>" in html
    assert "Property Card — Byculla CTS 1640" in html
    assert 'src="propcard_Byculla_1640.jpg"' in html


def test_title_report_jinja2_rendering_with_none():
    report_data = TitleReportData(cts="1644", village="Byculla")
    md = generate_title_report_md("Byculla", "1644", report_data)
    assert "# Property Title Audit Report — Byculla CTS 1644" in md
    assert "[Pending Verification]" in md  # Clean fallback when None!


def test_promoter_brief_jinja2_rendering():
    report_data = TitleReportData(cts="1640", village="Byculla", area_sqm=825.25)
    md = generate_promoter_brief("Byculla", "1640", report_data)
    assert "# Promoter Executive Brief — Byculla CTS 1640" in md
    assert "825.25 Sq. Mtrs." in md
    assert "### 3. Action Items Register" in md


def test_lawyer_brief_jinja2_rendering():
    report_data = TitleReportData(cts="1640", village="Byculla")
    md = generate_lawyer_brief("Byculla", "1640", report_data)
    assert "# Legal Counsel Brief — Title & Tenure Opinion" in md
    assert "Maharashtra Land Revenue Code" in md


def test_dashboard_jinja2_rendering():
    with tempfile.TemporaryDirectory() as tmpdir:
        outdir = Path(tmpdir)
        results = [
            CardResult(cts="1640", village="Byculla", district="23", status="ok", file_jpg="propcard_Byculla_1640.jpg", bytes=407102)
        ]
        generate_dashboard_html(outdir, "Byculla", "23", results)
        dash_file = outdir / "dashboard.html"
        assert dash_file.exists()
        content = dash_file.read_text(encoding="utf-8")
        assert "Property Cards Batch Dashboard — Byculla" in content
        assert "propcard_Byculla_1640.jpg" in content
