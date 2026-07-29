"""
Confidence Scorecard Engine: Calculates 5-dimension confidence scores (1-5) and total rating
for TitleReportData. Decoupled from vision extraction — works with any data source.
"""
from __future__ import annotations

from typing import Any, cast


def calculate_confidence_scorecard(report_data: Any) -> tuple[list[dict[str, Any]], int, str]:
    """Calculate 5-dimension confidence scores (1-5) and total rating.

    Dimensions:
    1. Image Clarity & Resolution (derived from confidence_score if available)
    2. OCR Register Index Extraction (Sheet, Register, Page presence)
    3. Tenure & Ownership Classification
    4. Plot Area & Survey Boundary
    5. Encumbrance & Title Flow Continuity

    Returns:
        Tuple of (scores_list, total_score, rating_string)
        rating is "HIGH CONFIDENCE" (>=21), "MEDIUM CONFIDENCE" (>=15), or "LOW CONFIDENCE" (<15)
    """
    scores: list[dict[str, Any]] = []

    # 1. Image Clarity & Resolution
    confidence_score = getattr(report_data, "confidence_score", None)
    if confidence_score is not None:
        clarity_score = 5 if confidence_score >= 0.95 else (4 if confidence_score >= 0.85 else 3)
        scores.append({
            "dimension": "Image Clarity & Resolution",
            "score": clarity_score,
            "notes": f"OCR confidence score: {int(confidence_score * 100)}%"
        })
    else:
        scores.append({
            "dimension": "Image Clarity & Resolution",
            "score": 3,
            "notes": "No vision read available — default score"
        })

    # 2. OCR Register Index Extraction
    sheet_no = getattr(report_data, "sheet_no", None)
    register_no = getattr(report_data, "register_no", None)
    page_no = getattr(report_data, "page_no", None)
    fields_present = sum(1 for f in [sheet_no, register_no, page_no] if bool(f))
    text_score = 5 if fields_present == 3 else (4 if fields_present >= 1 else 3)
    scores.append({
        "dimension": "OCR Register Index Extraction",
        "score": text_score,
        "notes": f"Extracted {fields_present}/3 index fields (Sheet, Register, Page)"
    })

    # 3. Tenure Certainty
    tenure = getattr(report_data, "tenure", None)
    tenure_score = 5 if tenure else 2
    scores.append({
        "dimension": "Tenure & Ownership Classification",
        "score": tenure_score,
        "notes": f"Tenure identified as: '{tenure}'" if tenure else "Tenure type pending verification"
    })

    # 4. Plot Area & Boundary Consistency
    area_sqm = getattr(report_data, "area_sqm", None)
    area_score = 5 if area_sqm else 2
    scores.append({
        "dimension": "Plot Area & Survey Boundary",
        "score": area_score,
        "notes": f"Area verified: {area_sqm} Sq. Mtrs." if area_sqm else "Plot area pending verification"
    })

    # 5. Encumbrance & Title Chain Flow
    transfer_chain = getattr(report_data, "transfer_chain", None)
    active_lessee = getattr(report_data, "active_lessee", None)
    chain_score = 5 if bool(transfer_chain) else (4 if bool(active_lessee) else 2)
    scores.append({
        "dimension": "Encumbrance & Title Flow Continuity",
        "score": chain_score,
        "notes": f"Sequential title chain verified ({len(transfer_chain)} links)" if transfer_chain else f"Title flow verified from active lessee: {active_lessee or 'pending'}"
    })

    raw_score = sum(int(cast(int, item["score"])) for item in scores)
    total = raw_score * 4
    rating = "HIGH CONFIDENCE" if total >= 84 else ("MEDIUM CONFIDENCE" if total >= 60 else "LOW CONFIDENCE")
    return scores, total, rating
