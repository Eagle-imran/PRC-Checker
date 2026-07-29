"""
Unit tests for Statutory Mapping Engine in prc_checker.statutes.
"""
from prc_checker.models import TitleReportData
from prc_checker.statutes import get_statutory_mappings_for_tenure, populate_statutory_mappings


def test_statutory_mapping_collector_class_ii():
    """Verify Collector Land Class II maps to MLRC 1966 Section 29(2) and GR Class II Conversion."""
    mappings = get_statutory_mappings_for_tenure("Collector Land Class II (B-Category)")
    
    assert len(mappings) >= 2
    statutes = [m.statute for m in mappings]
    sections = [m.section for m in mappings]

    assert "Maharashtra Land Revenue Code, 1966" in statutes
    assert "Section 29(2) read with Section 38" in sections
    assert "GR No. Class-2019/CR-18/L-1" in sections


def test_statutory_mapping_freehold_class_i():
    """Verify Occupant Class I maps to Section 29(1) unrestricted ownership."""
    mappings = get_statutory_mappings_for_tenure("Occupant Class I (Freehold)")
    
    assert len(mappings) >= 1
    m = [m for m in mappings if m.statute == "Maharashtra Land Revenue Code, 1966"][0]
    assert m.section == "Section 29(1)"
    assert "Unrestricted Ownership" in m.implication


def test_statutory_mapping_bmc_leasehold():
    """Verify BMC Leasehold maps to MMC Act 1888 Section 92."""
    mappings = get_statutory_mappings_for_tenure("BMC Leasehold Plot")
    
    assert len(mappings) >= 1
    m = [m for m in mappings if "Municipal" in m.statute][0]
    assert "Section 92(dd)" in m.section


def test_populate_statutory_mappings():
    """Verify populate_statutory_mappings attaches mappings to TitleReportData model."""
    report_data = TitleReportData(cts="748", village="Worli", tenure="Collector Land Class II")
    populate_statutory_mappings(report_data)

    assert len(report_data.statutory_mappings) >= 1
    assert report_data.statutory_mappings[0].statute == "Maharashtra Land Revenue Code, 1966"
