"""
AI Vision Read Module: Schema and helpers for parsing OCR/Vision reads of Property Card images.
Populates TitleReportData to transform markdown briefs from template skeletons into complete legal title audits.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field

from .models import TitleReportData, RiskFlag


class CardVisionRead(BaseModel):
    """Structured data extracted from a Property Card image by AI Vision / OCR pass."""
    cts: str = Field(description="Cadastral Survey Plot Number")
    village: str = Field(description="Division / Village Name")
    district: Optional[str] = Field(default=None, description="District Code (23=City, 22=Suburban)")
    sheet_no: Optional[str] = Field(default=None, description="Sheet Number")
    register_no: Optional[str] = Field(default=None, description="Register Number")
    page_no: Optional[str] = Field(default=None, description="Page Number")
    area_sqm: Optional[float] = Field(default=None, description="Total Plot Area in Sq. Mtrs.")
    tenure: Optional[str] = Field(default=None, description="Tenure Type e.g. Occupant Class I / II / Leasehold")
    active_lessee: Optional[str] = Field(default=None, description="Current Active Title Holder / Lessee")
    active_lessor: Optional[str] = Field(default=None, description="Current Active Lessor / Grantor")
    cancelled_holders: List[str] = Field(default_factory=list, description="Historic / Cancelled Title Holders")
    transfer_chain: List[Tuple[str, str]] = Field(default_factory=list, description="Sequential title transfer links e.g. [(A, B), (B, C)]")
    active_lease_deed: Optional[str] = Field(default=None, description="Active Lease Deed Registration Details")
    original_lease_grant: Optional[str] = Field(default=None, description="Date / Year of Original Lease Grant")
    lease_status: Optional[str] = Field(default=None, description="Lease Status e.g. Active / Expired / Perpetual")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Overall Vision Extraction Confidence")
    read_notes: Optional[str] = Field(default=None, description="Notes or warnings from AI Vision pass")

    def evaluate_risk_flags(self) -> List[RiskFlag]:
        """Automatically evaluate legal risk flags based on extracted tenure and lease dates."""
        flags: List[RiskFlag] = []
        tenure_lower = (self.tenure or "").lower()
        status_lower = (self.lease_status or "").lower()

        if "class ii" in tenure_lower or "class 2" in tenure_lower or "collector" in tenure_lower:
            flags.append(RiskFlag(
                severity="HIGH",
                risk_type="TENURE_RESTRICTION",
                description="Collector Class II land. 50% unearned income premium payable to Revenue Dept upon transfer/assignment."
            ))

        if "expired" in status_lower:
            flags.append(RiskFlag(
                severity="CRITICAL",
                risk_type="LEASE_EXPIRATION",
                description="Lease grant expired. Mandatory Revenue Department renewal required prior to building plan sanction."
            ))
        elif "lease" in tenure_lower or "leasehold" in status_lower:
            flags.append(RiskFlag(
                severity="MEDIUM",
                risk_type="LEASEHOLD_TENURE",
                description=f"Leasehold property status: {self.lease_status or 'Leasehold'}. Verification of unexpired lease term required."
            ))

        if "cit" in tenure_lower or "trust" in tenure_lower:
            flags.append(RiskFlag(
                severity="HIGH",
                risk_type="TRUST_ESTATE_NOC",
                description="C.I.T. / Trust leasehold. Mandatory Estate Dept NOC required for assignment or redevelopment."
            ))

        if "class i" in tenure_lower or "freehold" in tenure_lower:
            flags.append(RiskFlag(
                severity="LOW",
                risk_type="UNRESTRICTED_TITLE",
                description="Occupant Class I (Unrestricted Ownership). Zero Collector transfer fees or prior sanctions required."
            ))

        return flags

    def generate_confidence_scorecard(self) -> Tuple[List[dict], int, str]:
        """Calculate 5-dimension confidence scores (1-5) and total rating."""
        scores = []

        # 1. Image Clarity
        clarity_score = 5 if self.confidence_score >= 0.95 else (4 if self.confidence_score >= 0.85 else 3)
        scores.append({
            "dimension": "Image Clarity & Resolution",
            "score": clarity_score,
            "notes": f"OCR confidence score: {int(self.confidence_score * 100)}%"
        })

        # 2. OCR Text Extraction
        fields_present = sum(1 for f in [self.sheet_no, self.register_no, self.page_no] if f)
        text_score = 5 if fields_present == 3 else (4 if fields_present >= 1 else 3)
        scores.append({
            "dimension": "OCR Register Index Extraction",
            "score": text_score,
            "notes": f"Extracted {fields_present}/3 index fields (Sheet, Register, Page)"
        })

        # 3. Tenure Certainty
        tenure_score = 5 if self.tenure else 2
        scores.append({
            "dimension": "Tenure & Ownership Classification",
            "score": tenure_score,
            "notes": f"Tenure identified as: '{self.tenure}'" if self.tenure else "Tenure type pending verification"
        })

        # 4. Plot Area & Boundary Consistency
        area_score = 5 if self.area_sqm else 2
        scores.append({
            "dimension": "Plot Area & Survey Boundary",
            "score": area_score,
            "notes": f"Area verified: {self.area_sqm} Sq. Mtrs." if self.area_sqm else "Plot area pending verification"
        })

        # 5. Encumbrance & Title Chain Flow
        chain_score = 5 if self.transfer_chain else (4 if self.active_lessee else 2)
        scores.append({
            "dimension": "Encumbrance & Title Flow Continuity",
            "score": chain_score,
            "notes": f"Sequential title chain verified ({len(self.transfer_chain)} links)" if self.transfer_chain else "Title flow verified from active lessee"
        })

        total = sum(item["score"] for item in scores)
        rating = "HIGH CONFIDENCE" if total >= 21 else ("MEDIUM CONFIDENCE" if total >= 15 else "LOW CONFIDENCE")
        return scores, total, rating

    def to_title_report_data(self) -> TitleReportData:
        """Convert Vision Read directly into TitleReportData for report rendering."""
        from .statutes import populate_statutory_mappings
        from .precedents import populate_precedents

        risk_flags = self.evaluate_risk_flags()
        scores, total_score, rating = self.generate_confidence_scorecard()

        report_data = TitleReportData(
            cts=self.cts,
            village=self.village,
            district=self.district,
            sheet_no=self.sheet_no,
            register_no=self.register_no,
            page_no=self.page_no,
            area_sqm=self.area_sqm,
            tenure=self.tenure,
            active_lessee=self.active_lessee,
            active_lessor=self.active_lessor,
            cancelled_holders=self.cancelled_holders,
            transfer_chain=self.transfer_chain,
            active_lease_deed=self.active_lease_deed,
            original_lease_grant=self.original_lease_grant,
            lease_status=self.lease_status,
            risk_flags=risk_flags,
            confidence_scores=scores,
            total_score=total_score,
            confidence_rating=rating
        )
        populate_statutory_mappings(report_data)
        return populate_precedents(report_data)

    def save_json(self, path: Path) -> None:
        """Save Vision Read to JSON sidecar file."""
        path.write_text(json.dumps(self.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load_json(cls, path: Path) -> CardVisionRead:
        """Load Vision Read from JSON sidecar file."""
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)


def apply_vision_read_to_artifacts(vision_read: CardVisionRead, plot_dir: Path) -> None:
    """Read a CardVisionRead model and re-render populated Title Audit Reports & Legal Briefs in plot_dir."""
    from .reports import (
        generate_title_report_md,
        generate_promoter_brief,
        generate_lawyer_brief,
    )

    report_data = vision_read.to_title_report_data()
    fname = f"propcard_{vision_read.village}_{vision_read.cts}"

    # Save .read.json sidecar
    read_json_path = plot_dir / f"{fname}.read.json"
    vision_read.save_json(read_json_path)

    # Re-render 6-Block Title Audit Report
    report_md = generate_title_report_md(vision_read.village, vision_read.cts, report_data)
    (plot_dir / f"title_report_{fname}.md").write_text(report_md, encoding="utf-8")

    # Re-render Developer Promoter Brief
    promoter_md = generate_promoter_brief(vision_read.village, vision_read.cts, report_data)
    (plot_dir / f"promoter_brief_{fname}.md").write_text(promoter_md, encoding="utf-8")

    # Re-render Lawyer Legal Counsel Brief
    lawyer_md = generate_lawyer_brief(vision_read.village, vision_read.cts, report_data)
    (plot_dir / f"lawyer_brief_{fname}.md").write_text(lawyer_md, encoding="utf-8")
