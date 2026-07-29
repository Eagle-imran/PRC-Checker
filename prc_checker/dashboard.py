"""
Interactive Dark-Mode Batch Dashboard Builder powered by Jinja2 Templates & Pydantic Data Models.
"""
from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .models import CardResult

TEMPLATES_DIR = Path(__file__).parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True
)


def generate_dashboard_html(outdir: Path, village: str, district: str, results: list[CardResult]):
    """Generate an interactive split-screen dark-mode dashboard using Pydantic CardResult models."""
    template = jinja_env.get_template("dashboard.html.j2")
    raw_results = [r.model_dump() for r in results]
    cards_js_json = json.dumps(raw_results, ensure_ascii=False)
    
    dashboard_content = template.render(
        village=village,
        district=district,
        results=raw_results,
        cards_js_json=cards_js_json
    )
    (outdir / "dashboard.html").write_text(dashboard_content, encoding="utf-8")
