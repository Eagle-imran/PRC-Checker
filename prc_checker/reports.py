"""
Title Audit Report & Legal Brief Generators powered by Jinja2 Templates & Pydantic Data Models.
"""
from __future__ import annotations

import time
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from .models import TitleReportData

TEMPLATES_DIR = Path(__file__).parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True
)


def generate_clean_html(fname: str) -> str:
    """Generate a clean, standalone, self-contained HTML5 card viewer using Jinja2."""
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    cts_num = fname.split("_")[-1]
    village_name = fname.split("_")[1] if len(fname.split("_")) > 1 else ""

    template = jinja_env.get_template("card.html.j2")
    return template.render(
        village=village_name,
        cts=cts_num,
        fname=fname,
        fetched_at=now_str
    )


def generate_title_report_md(village: str, cts: str, report_data: TitleReportData | None = None) -> str:
    """Generate 6-Block Lawyer-Ready Title Audit Report using Jinja2 templates & Pydantic models."""
    if report_data is None:
        report_data = TitleReportData(cts=cts, village=village)

    template = jinja_env.get_template("report.md.j2")
    return template.render(report=report_data)


def generate_promoter_brief(village: str, cts: str, report_data: TitleReportData | None = None) -> str:
    """Generate Executive Developer / Promoter Brief using Jinja2 templates & Pydantic models."""
    if report_data is None:
        report_data = TitleReportData(cts=cts, village=village)

    template = jinja_env.get_template("promoter.md.j2")
    return template.render(report=report_data)


def generate_lawyer_brief(village: str, cts: str, report_data: TitleReportData | None = None) -> str:
    """Generate Formal Lawyer Legal Brief using Jinja2 templates & Pydantic models."""
    if report_data is None:
        report_data = TitleReportData(cts=cts, village=village)

    template = jinja_env.get_template("lawyer.md.j2")
    return template.render(report=report_data)
