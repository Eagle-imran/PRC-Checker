"""
Pytest Unit Tests for Session Driver, Behavior, and Dialog Interception using Mocks.
"""
from __future__ import annotations

import base64
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
from prc_checker.session import Session, ANCHOR, SUBURBAN_OFFICES


def test_session_initialization():
    mock_page = MagicMock()
    s = Session(mock_page)
    mock_page.on.assert_called_once_with("dialog", s._dialog)


def test_session_dialog_handler():
    mock_page = MagicMock()
    s = Session(mock_page)

    mock_dialog = MagicMock()
    mock_dialog.message = "Please Enter Valid CTS"
    s._dialog(mock_dialog)

    assert s.last_dialog == "Please Enter Valid CTS"
    mock_dialog.dismiss.assert_called_once()


def test_suburban_offices_provenance():
    assert SUBURBAN_OFFICES["2206"] == "Vile Parle"
    assert ANCHOR["cts"] == "1640"
    assert ANCHOR["expect"] == "825.25"


def test_set_cts_retry_success():
    mock_page = MagicMock()
    mock_page.input_value.side_effect = ["", "1640"]
    s = Session(mock_page)
    res = s.set_cts("1640")
    assert res is True
    assert mock_page.fill.call_count >= 1


def test_save_card_artifacts_suburban_district():
    mock_page = MagicMock()
    s = Session(mock_page)
    dummy_b64 = base64.b64encode(b"fake_jpeg_bytes").decode("ascii")

    with tempfile.TemporaryDirectory() as tmpdir:
        outdir = Path(tmpdir)
        # Test Suburban District 22 (e.g. Marol CTS 1590)
        res = s._save_card_artifacts(dummy_b64, outdir, "propcard_Marol_1590", district="22")
        assert res.district == "22"
        assert res.village == "Marol"
        assert res.cts == "1590"
        assert res.file_jpg == "Marol_1590/propcard_Marol_1590.jpg"
        assert (outdir / "Marol_1590" / "propcard_Marol_1590.jpg").exists()
        assert (outdir / "Marol_1590" / "propcard_Marol_1590.json").exists()
