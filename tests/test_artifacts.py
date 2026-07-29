"""
Unit tests for build_card_artifacts engine in prc_checker.artifacts.
"""
from pathlib import Path

from prc_checker.artifacts import build_card_artifacts


def test_build_card_artifacts(tmp_path: Path):
    """Verify build_card_artifacts creates JPEG, HTML, Markdown reports, and JSON metadata."""
    # 1x1 transparent PNG / JPEG base64 payload
    dummy_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

    res = build_card_artifacts(
        b64=dummy_b64,
        outdir=tmp_path,
        fname="propcard_Bandra_123",
        district="22",
        generate_briefs=True
    )

    assert res.status == "ok"
    assert res.cts == "123"
    assert res.village == "Bandra"
    assert res.district == "22"
    assert res.file_jpg == "Bandra_123/propcard_Bandra_123.jpg"
    assert res.file_html == "Bandra_123/propcard_Bandra_123.html"
    assert res.file_report == "Bandra_123/title_report_propcard_Bandra_123.md"
    assert res.file_promoter_brief == "Bandra_123/promoter_brief_propcard_Bandra_123.md"
    assert res.file_lawyer_brief == "Bandra_123/lawyer_brief_propcard_Bandra_123.md"
    assert res.file_json == "Bandra_123/propcard_Bandra_123.json"

    # Verify physical file existence
    plot_dir = tmp_path / "Bandra_123"
    assert (plot_dir / "propcard_Bandra_123.jpg").exists()
    assert (plot_dir / "propcard_Bandra_123.html").exists()
    assert (plot_dir / "title_report_propcard_Bandra_123.md").exists()
    assert (plot_dir / "promoter_brief_propcard_Bandra_123.md").exists()
    assert (plot_dir / "lawyer_brief_propcard_Bandra_123.md").exists()
    assert (plot_dir / "propcard_Bandra_123.json").exists()
