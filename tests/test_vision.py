"""
Unit tests for CardVisionRead and apply_vision_read_to_artifacts in prc_checker.vision.
"""
from pathlib import Path

from prc_checker.vision import CardVisionRead, apply_vision_read_to_artifacts


def test_card_vision_read_model(tmp_path: Path):
    """Verify CardVisionRead schema validation, JSON load/dump, and TitleReportData conversion."""
    vision_read = CardVisionRead(
        cts="748",
        village="Worli",
        district="23",
        sheet_no="54",
        register_no="12",
        page_no="340",
        area_sqm=1250.75,
        tenure="Collector Land Class II",
        active_lessee="M/S Worli Developers Pvt Ltd",
        active_lessor="State Government of Maharashtra",
        cancelled_holders=["Historic Textile Mill Co."],
        transfer_chain=[
            ("Historic Textile Mill Co.", "M/S Worli Developers Pvt Ltd")
        ],
        confidence_score=0.98,
        read_notes="Clear high-resolution scan"
    )

    # 1. Test TitleReportData conversion & risk flag evaluation
    report_data = vision_read.to_title_report_data()
    assert report_data.cts == "748"
    assert report_data.village == "Worli"
    assert report_data.area_sqm == 1250.75
    assert report_data.tenure == "Collector Land Class II"
    assert report_data.active_lessee == "M/S Worli Developers Pvt Ltd"
    assert len(report_data.transfer_chain) == 1
    assert report_data.transfer_chain[0] == ("Historic Textile Mill Co.", "M/S Worli Developers Pvt Ltd")

    # 2. Test Risk Flags & Confidence Scorecard
    assert len(report_data.risk_flags) >= 1
    assert report_data.risk_flags[0].severity == "HIGH"
    assert report_data.total_score >= 20
    assert report_data.confidence_rating == "HIGH CONFIDENCE"

    # 3. Test JSON load / dump
    json_path = tmp_path / "propcard_Worli_748.read.json"
    vision_read.save_json(json_path)
    assert json_path.exists()

    loaded = CardVisionRead.load_json(json_path)
    assert loaded.cts == "748"
    assert loaded.area_sqm == 1250.75
    assert loaded.confidence_score == 0.98


def test_apply_vision_read_to_artifacts(tmp_path: Path):
    """Verify apply_vision_read_to_artifacts re-renders populated reports & briefs in plot subfolder."""
    plot_dir = tmp_path / "Worli_748"
    plot_dir.mkdir(parents=True, exist_ok=True)

    vision_read = CardVisionRead(
        cts="748",
        village="Worli",
        district="23",
        sheet_no="54",
        register_no="102",
        page_no="45",
        area_sqm=1450.0,
        tenure="Collector Land Class II",
        active_lessee="Reliance Realty Ltd",
        active_lessor="Collector of Mumbai",
        transfer_chain=[
            ("Bombay Dyeing & Mfg Co. Ltd.", "Reliance Realty Ltd")
        ],
        confidence_score=0.95
    )

    apply_vision_read_to_artifacts(vision_read, plot_dir)

    # Assert output markdown files exist and contain populated data
    report_md_file = plot_dir / "title_report_propcard_Worli_748.md"
    promoter_md_file = plot_dir / "promoter_brief_propcard_Worli_748.md"
    lawyer_md_file = plot_dir / "lawyer_brief_propcard_Worli_748.md"

    assert report_md_file.exists()
    assert promoter_md_file.exists()
    assert lawyer_md_file.exists()

    report_content = report_md_file.read_text(encoding="utf-8")
    assert "1450.0 Sq. Mtrs." in report_content
    assert "Collector Land Class II" in report_content
    assert "Reliance Realty Ltd" in report_content
    assert "graph TD" in report_content  # Mermaid graph assertion
    assert 'N0["Bombay Dyeing & Mfg Co. Ltd."]' in report_content
    assert 'N1["Reliance Realty Ltd"]' in report_content
