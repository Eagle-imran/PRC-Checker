# MahaBhulekh Property Card Fetcher & Legal Title Auditor

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Chromium-green.svg)](https://playwright.dev)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2.0%2B-red.svg)](https://docs.pydantic.dev)
[![Jinja2](https://img.shields.io/badge/Jinja2-v3.1%2B-black.svg)](https://jinja.palletsprojects.com)
[![openpyxl](https://img.shields.io/badge/openpyxl-Excel%20Index-green.svg)](https://openpyxl.readthedocs.io)
[![Pytest](https://img.shields.io/badge/Pytest-32%2F32%20Passed-brightgreen.svg)](https://pytest.org)
[![Engine](https://img.shields.io/badge/uv-Standalone-purple.svg)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

An automated, high-performance, silent headless system for fetching, parsing, and auditing **Mumbai City and Mumbai Suburban Property Cards (PR Cards)** from the Maharashtra Revenue Portal ([MahaBhulekh](https://bhulekh.mahabhumi.gov.in)).

Every query fetch organizes its output assets into **1 dedicated subfolder per plot query** (e.g. `prcards/Worli_748/`, `prcards/Malabar-Hill_518/`), accompanied by a **Master Excel Index Workbook** (`index.xlsx`) featuring clickable file links, optional **SQLite Relational Export** (`--sqlite`), dynamic Suburban/City district integrity (`22` vs `23`), non-blocking file IPC CAPTCHA solving, font-loading route optimization, Jinja2 template rendering, Pydantic type safety, **Automated Slash CTS Parent Fallback Engine**, **6-Block Lawyer Title Audit Reports**, **Promoter Executive Briefs**, **Lawyer Legal Counsel Briefs**, CSV summaries, and an interactive dark-mode batch dashboard (`dashboard.html`).

---

## 🏛️ Key Architectural Features

* **Automated Slash CTS Parent Fallback Engine**: Passing slash sub-plots directly (e.g. `695/10`) automatically detects ASP.NET portal `NOT_FOUND` alerts, strips the slash suffix, queries the parent CTS (`695`), matches option `695/10` from the ASP.NET sub-plot dropdown list, and fetches sub-plots seamlessly!
* **District Data Integrity**: Dynamically records District `22` (Suburban) vs District `23` (City) across all Pydantic models, JSON sidecars, CSV summary rows, Excel workbooks, and Markdown title reports.
* **Dedicated Subfolder Per Plot Query**: All assets for a plot (card JPG, clean HTML viewer, 6-block Markdown title report, promoter brief, lawyer brief, JSON metadata) are grouped inside a dedicated plot folder (e.g. `prcards/Worli_748/`).
* **Master Excel Index (`index.xlsx`)**: Generates a formatted Excel workbook with clickable hyperlinks pointing directly to each plot subfolder asset, styled headers (`#1E293B`), status color coding, and auto-adjusted column widths.
* **Optional Relational SQLite Database (`--sqlite`)**: Generates `database.sqlite` when passed `--sqlite` for SQL queryability across large batches.
* **Pydantic Data Models**: Enforces strict schema validation across results, metadata, risk flags, title holders, and execution manifests (`prc_checker/models.py`). Zero fake hardcoded defaults!
* **Jinja2 Template Engine & Continuous Mermaid Graphs**: Renders self-contained HTML cards, promoter briefs, lawyer briefs, workspace dashboard, and Markdown title reports with continuously linked Mermaid title transfer graphs.
* **100% Silent Headless Engine**: Drives Chromium in headless mode (`headless=True`) with zero GUI popups or window flickering.
* **Non-Blocking File IPC CAPTCHA Solver**: Intercepts CAPTCHAs via `.captcha_input.txt` file polling (300ms interval), bypassing IDE `stdin` prompt banners.

---

## 🚀 Quick Start

### 1. Prerequisites & Setup

Ensure [`uv`](https://github.com/astral-sh/uv) is installed:

```bash
# Install Playwright Chromium dependencies (once)
uv run --with playwright python -m playwright install chromium
```

### 2. Basic Execution

```bash
# Run registered CLI command directly
uv run prc-checker --village Worli --district 23 --cts 748

# Fetch Suburban plot with SQLite export enabled
uv run prc-checker --village "मरोळ" --district 22 --office 2206 --cts 1590 --sqlite

# Run with Ground-Truth Anchor Verification
uv run prc-checker --village Byculla --cts 1640 1641 --anchor
```

---

## 📋 CLI Reference

```text
usage: prc-checker [-h] --village VILLAGE [--district DISTRICT]
                   [--office OFFICE] [--cts [CTS ...]] [--cts-file CTS_FILE]
                   [--mobile MOBILE] [--out OUT] [--anchor] [--headed]
                   [--sqlite] [--no-briefs] [--verbose] [--quiet]

Options:
  --village VILLAGE    Village name in English for Mumbai City (e.g. Worli / Byculla),
                       or Marathi for Suburban (e.g. मरोळ)
  --district DISTRICT  District code: 23 = Mumbai City (default), 22 = Mumbai Suburban
  --office OFFICE      CSO Office Code (e.g. 2206 for Vile Parle / Marol)
  --cts [CTS ...]      List of CTS plot numbers to fetch
  --cts-file FILE      Path to file containing one CTS number per line
  --out OUT            Output directory (default: prcards)
  --anchor             Fetch Byculla 1640 first to verify DOM integrity
  --headed             Run in visual browser mode (default: silent headless)
  --sqlite             Also generate database.sqlite relational database
  --no-briefs          Disable promoter and lawyer brief generation
  --verbose, -v        Enable verbose debug output
  --quiet, -q          Suppress non-error console output
```

---

## 📂 Structured Output Directory Layout (`prcards/`)

```text
prcards/                                            # Main Output Directory
├── index.xlsx                                      # Master Excel Index (Hyperlinked to Plot Subfolders)
├── index.csv                                       # Master CSV Index
├── database.sqlite                                 # Optional SQLite Relational Database (--sqlite)
├── dashboard.html                                  # Interactive Split-Screen Batch Viewer
├── manifest.json                                   # Execution Manifest
│
├── Worli_748/                                      # Dedicated Subfolder for Worli CTS 748
│   ├── propcard_Worli_748.jpg                      # Lossless Original PR Card Image
│   ├── propcard_Worli_748.html                     # Standalone Refined 1.6 KB HTML Viewer
│   ├── propcard_Worli_748.json                     # Structured Metadata Sidecar
│   ├── title_report_propcard_Worli_748.md          # 6-Block Lawyer Title Audit Report
│   ├── promoter_brief_propcard_Worli_748.md        # Promoter Executive Brief
│   └── lawyer_brief_propcard_Worli_748.md          # Lawyer Legal Counsel Brief
```

---

## 🧪 Testing

Run the automated 20-test suite offline using `pytest`:

```bash
uv run pytest
```

Output:
```text
============================= test session starts ==============================
platform darwin -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/imranpatel/Developer/playground/PRC-Checker
configfile: pyproject.toml
testpaths: tests
collected 20 items

tests/test_artifacts.py .                                                [  5%]
tests/test_exporters.py .                                                [ 10%]
tests/test_models.py ....                                                [ 30%]
tests/test_reports.py ....                                               [ 50%]
tests/test_session.py .....                                              [ 75%]
tests/test_templates.py .....                                            [100%]

============================== 20 passed in 0.26s ==============================
```

---

## ⚖️ License & Disclaimers

This software is designed for legal title verification and land record audit workflows under section 282 of the Maharashtra Land Revenue Act, 1966. Property Cards fetched from MahaBhulekh are digitally signed public records for informational and title search purposes.
