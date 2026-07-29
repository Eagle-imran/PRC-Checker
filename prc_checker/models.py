"""
Pydantic Data Models for Property Cards, Title Reports, Briefs, and Manifests.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class RiskFlag(BaseModel):
    """Legal title risk or operational verification flag."""
    severity: str = Field(description="HIGH, MEDIUM, LOW, or INFO")
    risk_type: str = Field(description="Categorical risk type, e.g. LEASE_EXPIRATION, AREA_DEDUCTION")
    description: str = Field(description="Human-readable legal risk detail")


class TitleHolder(BaseModel):
    """Property record holder or title beneficiary."""
    name: str = Field(description="Holder or entity name")
    role: str = Field(default="Lessee", description="Lessee, Lessor, Owner, etc.")
    is_active: bool = Field(default=True, description="True if active unbracketed, False if cancelled/bracketed")
    deed_no: str | None = Field(default=None, description="Deed / Instrument registration number")
    deed_date: str | None = Field(default=None, description="Date of instrument execution or mutation")


class ActionItem(BaseModel):
    """Action item for developer/lawyer title clearance."""
    responsible: str = Field(description="Promoter, Lawyer, Surveyor, Municipal")
    priority: str = Field(description="HIGH, MEDIUM, LOW")
    task: str = Field(description="Description of legal/field task required")
    deadline_basis: str = Field(description="Deadline trigger or timeline basis")


class StatutoryMapping(BaseModel):
    """Statutory act & section mapping under Maharashtra land laws."""
    statute: str = Field(description="MLRC 1966, MMBC Act, etc.")
    section: str = Field(description="Section or clause reference")
    implication: str = Field(description="Legal implication for redevelopment/title")


class PrecedentRef(BaseModel):
    """Bombay High Court precedent reference."""
    case_name: str = Field(description="Case citation name")
    citation: str = Field(description="Law report citation e.g. 2018 (4) ABR 112")
    relevance: str = Field(description="Relevance summary to title tenure/leasehold")


class TitleReportData(BaseModel):
    """Structured data for generating 6-Block Title Reports, Lawyer Briefs & Promoter Briefs.
    All optional fields default to None / empty lists — zero hardcoded fake defaults.
    """
    cts: str
    village: str
    district: str | None = None
    sheet_no: str | None = None
    register_no: str | None = None
    page_no: str | None = None
    area_sqm: float | None = None
    tenure: str | None = None
    active_lessee: str | None = None
    active_lessor: str | None = None
    cancelled_holders: list[str] = Field(default_factory=list)
    active_lease_deed: str | None = None
    original_lease_grant: str | None = None
    lease_status: str | None = None
    transfer_chain: list[tuple[str, str]] = Field(default_factory=list)
    risk_flags: list[RiskFlag] = Field(default_factory=list)
    confidence_scores: list[dict] = Field(default_factory=list)
    total_score: int | None = None
    confidence_rating: str | None = None
    action_items: list[ActionItem] = Field(default_factory=list)
    statutory_mappings: list[StatutoryMapping] = Field(default_factory=list)
    precedents: list[PrecedentRef] = Field(default_factory=list)


class CardResult(BaseModel):
    """Execution result and output file paths for a single fetched plot."""
    cts: str
    village: str
    district: str
    status: str
    file_jpg: str | None = None
    file_html: str | None = None
    file_report: str | None = None
    file_promoter_brief: str | None = None
    file_lawyer_brief: str | None = None
    file_json: str | None = None
    bytes: int = 0
    detail: str = "Success"
    report_data: TitleReportData | None = None


class Manifest(BaseModel):
    """Batch execution summary manifest."""
    village: str
    district: str
    results: list[CardResult]
