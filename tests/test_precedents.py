"""
Unit tests for Bombay High Court Precedents Engine in prc_checker.precedents.
"""
from prc_checker.models import TitleReportData
from prc_checker.precedents import get_precedents_for_tenure, populate_precedents


def test_precedent_collector_class_ii():
    """Verify Collector Land Class II maps to State of Maharashtra v. Dudhwala Builders."""
    precedents = get_precedents_for_tenure("Collector Land Class II")
    
    assert len(precedents) >= 1
    cases = [p.case_name for p in precedents]
    citations = [p.citation for p in precedents]

    assert "State of Maharashtra v. Dudhwala Builders" in cases
    assert "2018 (4) ABR 112 (Bombay High Court)" in citations


def test_precedent_occupant_class_i():
    """Verify Occupant Class I maps to State of Maharashtra v. Laxmanrao."""
    precedents = get_precedents_for_tenure("Occupant Class I (Freehold)")
    
    assert len(precedents) >= 1
    p = [p for p in precedents if "Laxmanrao" in p.case_name][0]
    assert "Laxmanrao" in p.case_name
    assert "AIR 1985 Bom 320" in p.citation
    assert "unrestricted ownership" in p.relevance.lower()


def test_precedent_bmc_leasehold():
    """Verify BMC Leasehold maps to MCGM v. M/S Reliance Realty Ltd."""
    precedents = get_precedents_for_tenure("BMC Municipal Lease")
    
    assert len(precedents) >= 1
    p = [p for p in precedents if "Reliance Realty" in p.case_name][0]
    assert "MCGM v. M/S Reliance Realty Ltd." in p.case_name


def test_populate_precedents():
    """Verify populate_precedents attaches BHC precedent citations to TitleReportData model."""
    report_data = TitleReportData(cts="748", village="Worli", tenure="Collector Land Class II")
    populate_precedents(report_data)

    assert len(report_data.precedents) >= 1
    assert report_data.precedents[0].case_name == "State of Maharashtra v. Dudhwala Builders"
