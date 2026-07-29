"""
Pytest Unit Tests for Session Driver, Behavior, and Dialog Interception using Mocks.
"""
from __future__ import annotations

import base64
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from prc_checker.session import ANCHOR, SUBURBAN_OFFICES, Session


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


def test_search_not_found_dialog():
    """Verify search() returns not_found status when dialog contains not found message."""
    from unittest.mock import patch

    from playwright.sync_api import TimeoutError as PWTimeout

    mock_page = MagicMock()
    s = Session(mock_page)

    mock_dialog = MagicMock()
    mock_dialog.message = "Please Enter Valid CTS"

    def trigger_dialog(*args, **kwargs):
        s._dialog(mock_dialog)

    mock_page.click.side_effect = trigger_dialog

    with patch.object(s, "set_cts", return_value=True), patch.object(s, "wait_opts", side_effect=PWTimeout("timeout")):
        res = s.search("9999")

    assert res["status"] == "not_found"
    assert "Please Enter Valid CTS" in res["detail"]


def test_refetch_subplot_cascade_flow():
    """Verify refetch_subplot() invokes reset, select_cascade, and search."""
    from unittest.mock import patch

    mock_page = MagicMock()
    s = Session(mock_page)

    with patch.object(s, "reset") as mock_reset, \
         patch.object(s, "select_cascade") as mock_cascade, \
         patch.object(s, "search", return_value={"status": "ok", "options": []}) as mock_search:
        s.refetch_subplot("23", "2301", "Byculla", "1640")

    mock_reset.assert_called_once()
    mock_cascade.assert_called_once_with("23", "2301", "Byculla")
    mock_search.assert_called_once_with("1640")
