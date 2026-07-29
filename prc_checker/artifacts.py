"""
Artifact Builder Engine: Saves JPEG card images, HTML viewers, Markdown title reports, promoter/lawyer briefs, and JSON metadata.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

from .models import CardResult, TitleReportData
from .reports import (
    generate_clean_html,
    generate_title_report_md,
    generate_promoter_brief,
    generate_lawyer_brief,
)


def build_card_artifacts(
    b64: str,
    outdir: Path,
    fname: str,
    district: str | None = None,
    generate_briefs: bool = True
) -> CardResult:
    """Helper to save JPEG, HTML, Markdown Title Report, Promoter/Lawyer Briefs, and JSON metadata inside plot subfolder."""
    cts_num = fname.split("_")[-1]
    village_name = fname.split("_")[1] if len(fname.split("_")) > 1 else ""

    folder_name = fname.replace("propcard_", "")
    plot_dir = outdir / folder_name
    plot_dir.mkdir(parents=True, exist_ok=True)

    path = plot_dir / f"{fname}.jpg"
    path.write_bytes(base64.b64decode(b64))

    clean_html = generate_clean_html(fname)
    (plot_dir / f"{fname}.html").write_text(clean_html, encoding="utf-8")

    from .statutes import populate_statutory_mappings
    from .precedents import populate_precedents

    report_data = TitleReportData(cts=cts_num, village=village_name, district=district)
    populate_statutory_mappings(report_data)
    populate_precedents(report_data)

    report_md = generate_title_report_md(village_name, cts_num, report_data)
    report_path = plot_dir / f"title_report_{fname}.md"
    report_path.write_text(report_md, encoding="utf-8")

    promoter_path = None
    lawyer_path = None
    if generate_briefs:
        promoter_md = generate_promoter_brief(village_name, cts_num, report_data)
        promoter_path = plot_dir / f"promoter_brief_{fname}.md"
        promoter_path.write_text(promoter_md, encoding="utf-8")

        lawyer_md = generate_lawyer_brief(village_name, cts_num, report_data)
        lawyer_path = plot_dir / f"lawyer_brief_{fname}.md"
        lawyer_path.write_text(lawyer_md, encoding="utf-8")

    meta_path = plot_dir / f"{fname}.json"
    rel_jpg = f"{folder_name}/{fname}.jpg"
    rel_html = f"{folder_name}/{fname}.html"
    rel_report = f"{folder_name}/{report_path.name}"
    meta_data = {
        "cts": cts_num,
        "village": village_name,
        "district": district,
        "file_jpg": rel_jpg,
        "file_html": rel_html,
        "file_report": rel_report,
        "bytes": path.stat().st_size,
        "timestamp": path.stat().st_mtime
    }
    meta_path.write_text(json.dumps(meta_data, indent=2), encoding="utf-8")

    return CardResult(
        cts=cts_num,
        village=village_name,
        district=district or "23",
        status="ok",
        file_jpg=rel_jpg,
        file_html=rel_html,
        file_report=rel_report,
        file_promoter_brief=f"{folder_name}/{promoter_path.name}" if promoter_path else None,
        file_lawyer_brief=f"{folder_name}/{lawyer_path.name}" if lawyer_path else None,
        file_json=f"{folder_name}/{meta_path.name}",
        bytes=path.stat().st_size,
        report_data=report_data
    )
