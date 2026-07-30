"""
MahaBhulekh PR Card Fetcher & Title Auditor — Package CLI Entrypoint.
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from .dashboard import generate_dashboard_html
from .exporters import generate_excel_and_csv, generate_sqlite
from .logger import setup_logger
from .models import CardResult, Manifest
from .preflight import check_plot_preflight
from .session import ANCHOR, SUBURBAN_OFFICES, Session


def run(args) -> int:
    # 1. Configure Structured Logging
    log_level = logging.INFO
    if getattr(args, "verbose", False):
        log_level = logging.DEBUG
    elif getattr(args, "quiet", False):
        log_level = logging.WARNING

    logger = setup_logger("prc_checker.cli", level=log_level)

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    numbers = list(args.cts or [])
    if args.cts_file:
        numbers += [l.strip() for l in Path(args.cts_file).read_text().splitlines()
                    if l.strip() and not l.startswith("#")]
    if not numbers:
        logger.error("No CTS numbers given")
        return 2

    if args.anchor:
        numbers.insert(0, ANCHOR["cts"])
        logger.info(f"Anchor verification enabled: {ANCHOR['village']} {ANCHOR['cts']} (expects {ANCHOR['expect']} sq.m)")

    # Advisory Preflight probe: fast HTTP ping before Playwright launch
    for cts in numbers:
        pf = check_plot_preflight(args.village, cts, district=args.district)
        if pf.exists:
            logger.info(f"Preflight probe OK for CTS {cts}: {pf.response_time_ms:.1f} ms")
        else:
            logger.info(f"Preflight probe info for CTS {cts}: {pf.detail} (proceeding to browser query)")

    results: list[CardResult] = []
    t = len(numbers)
    logger.info(f"{t} plot(s), ~15-30 s each once you clear the captcha.")

    with sync_playwright() as pw:
        is_headless = not getattr(args, 'headed', False)
        browser = pw.chromium.launch(headless=is_headless, slow_mo=20 if is_headless else 60)
        page = browser.new_page(viewport={"width": 1400, "height": 950})

        # Resource blocking: Fulfill heavy fonts with empty 200 OK to resolve document.fonts.ready instantly
        def block_heavy_resources(route):
            url = route.request.url.lower()
            if any(ext in url for ext in [".woff", ".woff2", ".ttf", "font", "fontawesome"]):
                route.abort()
            else:
                route.continue_()
        page.route("**/*", block_heavy_resources)

        s = Session(page)

        office = village_val = None
        for i, cts in enumerate(numbers, 1):
            logger.info(f"[{i}/{t}] CTS {cts}")
            try:
                s.reset()
                if office is None:
                    office, village_val = s.locate_village(args.district, args.village, getattr(args, 'office', None))
                    logger.info(f"Located office={office} ({SUBURBAN_OFFICES.get(office, 'Mumbai City')})")
                else:
                    s.select_cascade(args.district, office, village_val or "")
                page.wait_for_timeout(1500)

                found = s.search(cts)
                if found["status"] != "ok" and "/" in cts:
                    parent_cts = cts.split("/")[0]
                    logger.info(f"Slash CTS query '{cts}' returned {found['status']}. Attempting parent fallback for '{parent_cts}'...")
                    parent_found = s.search(parent_cts)
                    if parent_found["status"] == "ok":
                        found = parent_found
                        # Filter options for the requested sub-plot if present
                        sub_matches = [opt for opt in found["options"] if opt[1] == cts or opt[1].endswith(f"/{cts.split('/')[-1]}")]
                        if sub_matches:
                            found["options"] = sub_matches
                            logger.info(f"Matched sub-plot option '{sub_matches[0][1]}' via parent CTS '{parent_cts}'")

                if found["status"] != "ok":
                    logger.warning(f"Search status for CTS {cts}: {found['status']} - {found.get('detail','')}")
                    results.append(CardResult(
                        cts=cts,
                        village=args.village,
                        district=args.district,
                        status=found["status"],
                        detail=found.get("detail", "")
                    ))
                    continue

                opts = found["options"]
                if len(opts) > 1:
                    logger.info(f"Sub-plots detected for CTS {cts}: {[t for _, t in opts]} — fetching all")
                for idx, (val, label) in enumerate(opts):
                    safe = re.sub(r"[^\w.-]", "-", f"{args.village}_{label}")
                    r = s.fetch_card(val, args.mobile, outdir, f"propcard_{safe}", district=args.district, generate_briefs=not getattr(args, 'no_briefs', False))
                    logger.info(f"Fetched -> {r.status} {r.file_jpg or ''}")
                    results.append(r)
                    if len(opts) > 1 and idx < len(opts) - 1:
                        s.refetch_subplot(args.district, office, village_val or "", cts)
            except Exception as e:
                logger.error(f"Error fetching CTS {cts}: {e}")
                results.append(CardResult(
                    cts=cts,
                    village=args.village,
                    district=args.district,
                    status="error",
                    detail=str(e)
                ))

        browser.close()

    manifest = Manifest(village=args.village, district=args.district, results=results)
    (outdir / "manifest.json").write_text(json.dumps(
        manifest.model_dump(exclude={"results": {"__all__": {"report_data"}}}),
        ensure_ascii=False, indent=2))

    generate_dashboard_html(outdir, args.village, args.district, results)
    generate_excel_and_csv(outdir, args.village, args.district, results)
    if getattr(args, 'sqlite', False):
        generate_sqlite(outdir, args.village, args.district, results)
        logger.info(f"sqlite db : {outdir/'database.sqlite'}")
    logger.info(f"dashboard: {outdir/'dashboard.html'}")
    logger.info(f"excel index: {outdir/'index.xlsx'}")
    logger.info(f"csv index  : {outdir/'index.csv'}")

    ok = sum(r.status == "ok" for r in results)
    logger.info(f"{ok}/{len(results)} saved -> {outdir}/")
    for r in results:
        if r.status != "ok":
            logger.warning(f"  EXCEPTION  {r.cts}: {r.status} {r.detail}")
    logger.info(f"manifest: {outdir/'manifest.json'}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch MahaBhulekh PR Card images.")
    ap.add_argument("--village", required=True,
                    help="English for Mumbai City (Byculla), Marathi for Suburban (मरोळ)")
    ap.add_argument("--district", default="23",
                    help="23 = Mumbai City (default), 22 = Mumbai Suburban")
    ap.add_argument("--office", help="CSO office code (e.g. 2206 for Vile Parle / Marol)")
    ap.add_argument("--cts", nargs="*", help="CTS numbers")
    ap.add_argument("--cts-file", help="file with one CTS per line")
    ap.add_argument("--mobile", default="9821114112")
    ap.add_argument("--out", default="prcards")
    ap.add_argument("--anchor", action="store_true",
                    help="fetch Byculla 1640 first to confirm the site hasn't changed")
    ap.add_argument("--headed", action="store_true",
                    help="run browser in visible headed mode (default is silent headless)")
    ap.add_argument("--verbose", "-v", action="store_true", help="enable verbose debug output")
    ap.add_argument("--quiet", "-q", action="store_true", help="suppress non-error console output")
    ap.add_argument("--sqlite", action="store_true", help="also generate database.sqlite relational database")
    ap.add_argument("--no-briefs", action="store_true", help="disable automatic promoter/lawyer brief generation")
    return run(ap.parse_args())


if __name__ == "__main__":
    sys.exit(main())
