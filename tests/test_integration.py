"""
Integration tests for combined statutory mapping + precedent population on TitleReportData.
"""
from prc_checker.models import TitleReportData
from prc_checker.precedents import populate_precedents
from prc_checker.statutes import populate_statutory_mappings


def test_integration_class_ii_tenure():
    """Verify Collector Land Class II gets correct statutory + precedent mappings."""
    report = TitleReportData(cts="123", village="Worli", tenure="Collector Land Class II (B-Category)")
    populate_statutory_mappings(report)
    populate_precedents(report)

    # Statutory: should get MLRC 29(2) + GR Conversion
    statutes = [m.section for m in report.statutory_mappings]
    assert "Section 29(2) read with Section 38" in statutes
    assert "GR No. Class-2019/CR-18/L-1" in statutes

    # Precedents: should get Dudhwala Builders
    cases = [p.case_name for p in report.precedents]
    assert "State of Maharashtra v. Dudhwala Builders" in cases


def test_integration_private_trust_not_matched():
    """Verify Private Trust tenure does NOT match government trust precedent."""
    report = TitleReportData(cts="456", village="Test", tenure="Private Trust Leasehold")
    populate_precedents(report)

    # Should NOT match Entry 2 (C.I.T. Trust) — only generic fallback
    cases = [p.case_name for p in report.precedents]
    assert "Bombay Environmental Action Group v. State of Maharashtra" not in cases


def test_integration_bmc_leasehold_no_cit_match():
    """Verify BMC Leasehold does NOT match C.I.T. Trust precedent."""
    report = TitleReportData(cts="789", village="Test", tenure="BMC Municipal Lease")
    populate_precedents(report)

    cases = [p.case_name for p in report.precedents]
    assert "Bombay Environmental Action Group v. State of Maharashtra" not in cases
    assert "MCGM v. M/S Reliance Realty Ltd." in cases


def test_integration_complex_tenure():
    """Verify complex tenure string gets all applicable mappings without duplicates."""
    report = TitleReportData(cts="999", village="Test", tenure="C.I.T. Trust Leasehold Collector Land Class II")
    populate_statutory_mappings(report)
    populate_precedents(report)

    statutes = [m.section for m in report.statutory_mappings]
    assert "Section 29(2) read with Section 38" in statutes
    assert "Rule 37 & Rule 43" in statutes

    cases = [p.case_name for p in report.precedents]
    assert "State of Maharashtra v. Dudhwala Builders" in cases
    assert "Bombay Environmental Action Group v. State of Maharashtra" in cases
