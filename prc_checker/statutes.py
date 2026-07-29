"""
Statutory Mapping Engine: Auto-maps tenure types to Maharashtra Land Revenue Code (MLRC) 1966,
BMC Lease Regulations, and Collector Land Rules. Populates Lawyer Legal Briefs with statutory implications.
"""
from __future__ import annotations

from .models import StatutoryMapping, TitleReportData

# Statutory Rulebook Registry
STATUTORY_REGISTRY: list[tuple[list[str], StatutoryMapping]] = [
    # 1. Occupant Class II / Collector Land
    (
        ["class ii", "class 2", "collector", "b-category", "भोगवटदार वर्ग-२"],
        StatutoryMapping(
            statute="Maharashtra Land Revenue Code, 1966",
            section="Section 29(2) read with Section 38",
            implication="Occupant Class II (Restricted Tenure). Prior written sanction of Collector of Mumbai required for transfer, sale, mortgage, or redevelopment. 50% unearned income premium payable on land value appreciation."
        )
    ),
    # 2. Collector Class II Conversion GR (2019 / 2024)
    (
        ["class ii", "class 2", "collector conversion", "conversion to class i"],
        StatutoryMapping(
            statute="Revenue & Forests Dept. Resolution (Class II Conversion)",
            section="GR No. Class-2019/CR-18/L-1",
            implication="Eligible for conversion from Occupant Class II to Occupant Class I (Unrestricted Ownership) upon payment of 15% (residential) or 50% (commercial) of current Ready Reckoner rate."
        )
    ),
    # 3. Government Land Lease Renewal
    (
        ["lease", "leasehold", "c.i.t.", "cit", "trust", "भाडेपट्टा"],
        StatutoryMapping(
            statute="Maharashtra Land Revenue (Disposal of Govt Lands) Rules",
            section="Rule 37 & Rule 43",
            implication="Government / Trust Leasehold land. Renewal required prior to lease expiration date. Annual ground rent revisable every 30 years with mandatory NOC from Revenue Department for TDR / FSI utilization."
        )
    ),
    # 4. BMC / Municipal Corporation Land
    (
        ["bmc", "mcgm", "municipal", "corporation", "नगरपालिका"],
        StatutoryMapping(
            statute="Mumbai Municipal Corporation Act, 1888",
            section="Section 92(dd) & Section 92(e)",
            implication="Municipal Leasehold Land. Transfer, assignment, or structural redevelopment requires prior approval of BMC Standing Committee and payment of municipal transfer premium."
        )
    ),
    # 5. Occupant Class I (Unrestricted Ownership)
    (
        ["class i", "class 1", "freehold", "भोगवटदार वर्ग-१", "unrestricted"],
        StatutoryMapping(
            statute="Maharashtra Land Revenue Code, 1966",
            section="Section 29(1)",
            implication="Occupant Class I (Unrestricted Ownership). Absolute title holder. No prior Collector sanction or unearned income transfer premium required for sale, mortgage, or redevelopment."
        )
    ),
]


def get_statutory_mappings_for_tenure(tenure: str | None) -> list[StatutoryMapping]:
    """Analyze tenure string and return applicable statutory mappings under Maharashtra land laws."""
    if not tenure:
        # Default fallback if tenure is pending verification
        return [
            StatutoryMapping(
                statute="Maharashtra Land Revenue Code, 1966",
                section="Section 29 read with MLR Rules",
                implication="Tenure verification pending. Land classification (Class I vs Class II vs Leasehold) dictates Collector transfer fees and redevelopment sanction requirements."
            )
        ]

    tenure_lower = tenure.lower()
    matched_mappings: list[StatutoryMapping] = []
    seen_sections = set()

    for keywords, mapping in STATUTORY_REGISTRY:
        if any(kw in tenure_lower for kw in keywords):
            if mapping.section not in seen_sections:
                matched_mappings.append(mapping)
                seen_sections.add(mapping.section)

    if not matched_mappings:
        # Generic fallback for unlisted tenure types
        matched_mappings.append(
            StatutoryMapping(
                statute="Maharashtra Land Revenue Code, 1966",
                section="General Provisions",
                implication=f"Tenure listed as '{tenure}'. Statutory compliance required under local Revenue & Municipal land disposal regulations."
            )
        )

    return matched_mappings


def populate_statutory_mappings(report_data: TitleReportData) -> TitleReportData:
    """Populate statutory_mappings field in TitleReportData based on its tenure attribute."""
    mappings = get_statutory_mappings_for_tenure(report_data.tenure)
    report_data.statutory_mappings = mappings
    return report_data
