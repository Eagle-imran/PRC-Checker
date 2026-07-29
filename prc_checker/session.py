"""
Browser session driver and MahaBhulekh DOM interaction primitives.
"""
from __future__ import annotations

import re
import time
from pathlib import Path

from playwright.sync_api import TimeoutError as PWTimeout

from .artifacts import build_card_artifacts
from .logger import setup_logger
from .models import CardResult

logger = setup_logger("prc_checker.session")

BASE = "https://bhulekh.mahabhumi.gov.in"
P = "#ContentPlaceHolder1_"

# Suburban City Survey Offices (CSOs) mapping.
SUBURBAN_OFFICES = {
    "2201": "Borivali",
    "2202": "Malad",
    "2203": "Goregaon",
    "2204": "Andheri",
    "2205": "Bandra",
    "2206": "Vile Parle",
    "2207": "Ghatkopar",
    "2208": "Chembur",
    "2209": "Mulund",
    "2210": "Kurla",
}

NOT_FOUND = ("Please Enter Valid CTS", "उपलब्ध नाही")

ANCHOR = {
    "village": "Byculla",
    "district": "23",
    "cts": "1640",
    "expect": "825.25"
}


class Session:
    def __init__(self, page):
        self.page = page
        self.last_dialog: str | None = None
        page.on("dialog", self._dialog)

    def _dialog(self, d):
        self.last_dialog = d.message
        d.dismiss()

    def opts(self, sel: str) -> list[tuple[str, str]]:
        return self.page.eval_on_selector(
            P + sel,
            "s => [...s.options].slice(1).map(o => [o.value, o.text.trim()])",
        )

    def wait_opts(self, sel: str, minimum: int = 1, timeout: int = 20000):
        """Wait for an UpdatePanel postback to repopulate a dependent dropdown."""
        self.page.wait_for_selector(P + sel, state="attached", timeout=timeout)
        self.page.wait_for_function(
            "([sel, n]) => { const s = document.querySelector(sel);"
            " return s && !s.disabled && s.options.length > n; }",
            arg=[P + sel, minimum],
            timeout=timeout,
        )

    def select(self, sel: str, value: str, then: str | None = None):
        target_sel = P + sel
        self.page.wait_for_selector(target_sel, state="attached", timeout=20000)
        self.page.wait_for_function(
            "([sel, val]) => { const s = document.querySelector(sel);"
            " return s && [...s.options].some(o => o.value === val); }",
            arg=[target_sel, value],
            timeout=20000,
        )
        self.page.select_option(target_sel, value=value)
        self.page.eval_on_selector(target_sel, """function(s, val) {
            s.value = val;
            s.dispatchEvent(new Event('change', { bubbles: true }));
        }""", value)
        if then:
            self.wait_opts(then)

    def reset(self):
        """Full reset of form cascade."""
        self.page.goto(BASE, wait_until="domcontentloaded")
        self.page.check(P + "rbtnULPIN_1")
        self.page.check(P + "rbtnSelectType_2")
        self.page.wait_for_selector(P + "ddlMainDist", timeout=20000)

    def select_cascade(self, district: str, office: str, village_val: str):
        """Encapsulate complete district -> office -> village dropdown cascade selection."""
        self.select("ddlMainDist", district, then="ddlTalForAll")
        self.select("ddlTalForAll", office, then="ddlVillForAll")
        self.select("ddlVillForAll", village_val)

    def locate_village(self, district: str, village: str, office_override: str | None = None) -> tuple[str, str]:
        """Return (office_value, village_value). Scan offices if suburban."""
        self.select("ddlMainDist", district, then="ddlTalForAll")
        self.wait_opts("ddlTalForAll", minimum=1)
        if office_override:
            offices = [office_override]
        else:
            offices = ["2301"] if district == "23" else list(SUBURBAN_OFFICES)
        for off in offices:
            if district == "22":
                logger.info(f"Scanning CSO {off} ({SUBURBAN_OFFICES.get(off, '')})...")
            self.select("ddlTalForAll", off, then="ddlVillForAll")
            self.wait_opts("ddlVillForAll", minimum=1)

            clean_target = re.sub(r"[^\w]", " ", village.lower()).strip()
            target_tokens = [t for t in clean_target.split() if len(t) > 2]

            for val, text in self.opts("ddlVillForAll"):
                clean_text = re.sub(r"[^\w]", " ", text.lower()).strip()
                if clean_target in clean_text or (target_tokens and any(t in clean_text for t in target_tokens)):
                    self.select("ddlVillForAll", val)
                    return off, val
        raise LookupError(f"village {village!r} not found in district {district}")

    def set_cts(self, cts: str) -> bool:
        """Verify CTS input holds value after village postback."""
        for _ in range(5):
            self.page.fill(P + "txtcsno", cts)
            if self.page.input_value(P + "txtcsno") == cts:
                return True
            self.page.wait_for_timeout(200)
        return False

    def search(self, cts: str) -> dict:
        self.page.wait_for_timeout(1000)
        if not self.set_cts(cts):
            return {"status": "error", "detail": "CTS field would not hold value"}
        self.page.wait_for_timeout(300)
        self.last_dialog = None
        self.page.click(P + "btnsearchfind")
        try:
            self.wait_opts("ddlsurveyno", timeout=15000)
        except PWTimeout:
            msg = self.last_dialog or ""
            if any(k in msg for k in NOT_FOUND):
                return {"status": "not_found", "detail": msg.strip()}
            return {"status": "error", "detail": msg.strip() or "search timed out"}
        return {"status": "ok", "options": self.opts("ddlsurveyno")}

    def refetch_subplot(self, district: str, office: str, village_val: str, cts: str):
        """Encapsulate ASP.NET cascade reset and re-search for multi-plot sub-plots."""
        self.reset()
        self.select_cascade(district, office, village_val)
        self.page.wait_for_timeout(1200)
        self.search(cts)

    def _save_card_artifacts(self, b64: str, outdir: Path, fname: str, district: str = "23", generate_briefs: bool = True) -> CardResult:
        """Helper to delegate saving JPEG, HTML, Markdown Reports, Briefs, and JSON metadata."""
        return build_card_artifacts(b64, outdir, fname, district=district, generate_briefs=generate_briefs)

    def fetch_card(self, option_value: str, mobile: str, outdir: Path,
                   fname: str, district: str = "23", tries: int = 3, generate_briefs: bool = True) -> CardResult:
        """Fetch card image and return validated Pydantic CardResult model."""
        cts_num = fname.split("_")[-1]
        village_name = fname.split("_")[1] if len(fname.split("_")) > 1 else ""
        folder_name = fname.replace("propcard_", "")
        plot_dir = outdir / folder_name

        self.select("ddlsurveyno", option_value)
        self.page.wait_for_timeout(2000)

        for attempt in range(1, tries + 1):
            if self.page.is_visible(P + "ImgPC"):
                src = self.page.get_attribute(P + "ImgPC", "src") or ""
                b64 = src.split(",", 1)[1] if "," in src else ""
                if b64:
                    return self._save_card_artifacts(b64, outdir, fname, district=district, generate_briefs=generate_briefs)

            self.page.wait_for_timeout(1000)
            self.page.fill(P + "txtmobile1", mobile)

            shot = plot_dir / f".captcha_{fname}.png"
            try:
                self.page.locator(P + "captchaImage").screenshot(path=str(shot), timeout=10000, animations="disabled")
            except Exception as e:
                logger.warning(f"CAPTCHA image screenshot warning: {e}")

            # Check both plot_dir and main outdir for IPC captcha code file
            code_file1 = plot_dir / ".captcha_input.txt"
            code_file2 = outdir / ".captcha_input.txt"
            code_file1.unlink(missing_ok=True)
            code_file2.unlink(missing_ok=True)

            print(f"CAPTCHA_IMAGE: {shot.resolve()}", flush=True)
            print(f"WAITING_FOR_CAPTCHA [{attempt}/{tries}]...", flush=True)

            start_time = time.time()
            code = ""
            while time.time() - start_time < 25:
                for cf in (code_file1, code_file2):
                    if cf.exists():
                        try:
                            code = cf.read_text().strip()
                            cf.unlink(missing_ok=True)
                        except Exception:
                            pass
                        if code:
                            break
                if code:
                    break
                time.sleep(0.1)

            if not code:
                logger.info("Solver timeout — skipping plot")
                shot.unlink(missing_ok=True)
                return CardResult(
                    cts=cts_num,
                    village=village_name,
                    district=district,
                    status="skipped",
                    detail="captcha solver timeout"
                )

            self.page.fill(P + "txtcaptcha", code)
            self.last_dialog = None
            if self.page.is_visible(P + "btnmainsubmit"):
                self.page.click(P + "btnmainsubmit", timeout=5000)
            elif self.page.is_visible(P + "btnsearch"):
                self.page.click(P + "btnsearch", timeout=5000)
            elif self.page.is_visible(P + "btnsearchfind"):
                self.page.click(P + "btnsearchfind", timeout=5000)
            else:
                self.page.press(P + "txtcaptcha", "Enter")
            self.page.wait_for_timeout(500)

            if self.last_dialog:
                logger.info(f"Rejected ({self.last_dialog}) — refreshing")
                try:
                    if self.page.is_visible(P + "btnreferesh"):
                        self.page.click(P + "btnreferesh")
                    elif self.page.is_visible(P + "ImageButton3"):
                        self.page.click(P + "ImageButton3")
                    self.page.wait_for_timeout(1000)
                except Exception:
                    pass
                continue

            logger.info("PRC opened! Fetching card image data URI...")

            b64 = ""
            start_wait = time.time()
            while time.time() - start_wait < 15:
                try:
                    src = self.page.get_attribute(P + "ImgPC", "src") or ""
                    if "," in src:
                        b64 = src.split(",", 1)[1]
                        if b64:
                            break
                except Exception:
                    pass
                time.sleep(0.1)
            if not b64:
                return CardResult(
                    cts=cts_num,
                    village=village_name,
                    district=district,
                    status="error",
                    detail="card element had no data URI"
                )

            shot.unlink(missing_ok=True)
            return self._save_card_artifacts(b64, outdir, fname, district=district, generate_briefs=generate_briefs)

        return CardResult(
            cts=cts_num,
            village=village_name,
            district=district,
            status="captcha_failed",
            detail=f"{tries} attempts rejected"
        )
