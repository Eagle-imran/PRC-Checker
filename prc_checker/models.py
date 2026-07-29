"""
Pydantic Data Models for Property Cards, Title Reports, Briefs, and Manifests.
"""
from __future__ import annotations

from typing import List, Optional, Tuple
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
    deed_no: Optional[str] = Field(default=None, description="Deed / Instrument registration number")
    deed_date: Optional[str] = Field(default=None, description="Date of instrument execution or mutation")


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
    district: Optional[str] = None
    sheet_no: Optional[str] = None
    register_no: Optional[str] = None
    page_no: Optional[str] = None
    area_sqm: Optional[float] = None
    tenure: Optional[str] = None
    active_lessee: Optional[str] = None
    active_lessor: Optional[str] = None
    cancelled_holders: List[str] = Field(default_factory=list)
    active_lease_deed: Optional[str] = None
    original_lease_grant: Optional[str] = None
    lease_status: Optional[str] = None
    transfer_chain: List[Tuple[str, str]] = Field(default_factory=list)
    risk_flags: List[RiskFlag] = Field(default_factory=list)
    confidence_scores: List[dict] = Field(default_factory=list)
    total_score: Optional[int] = None
    confidence_rating: Optional[str] = None
    action_items: List[ActionItem] = Field(default_factory=list)
    statutory_mappings: List[StatutoryMapping] = Field(default_factory=list)
    precedents: List[PrecedentRef] = Field(default_factory=list)


class CardResult(BaseModel):
    """Execution result and output file paths for a single fetched plot."""
    cts: str
    village: str
    district: str
    status: str
    file_jpg: Optional[str] = None
    file_html: Optional[str] = None
    file_report: Optional[str] = None
    file_promoter_brief: Optional[str] = None
    file_lawyer_brief: Optional[str] = None
    file_json: Optional[str] = None
    bytes: int = 0
    detail: str = "Success"
    report_data: Optional[TitleReportData] = None


class Manifest(BaseModel):
    """Batch execution summary manifest."""
    village: str
    district: str
    results: List[CardResult]
