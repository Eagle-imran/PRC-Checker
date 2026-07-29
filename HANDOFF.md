# PRC-Checker Operational Handoff Guide

## System Overview

**PRC-Checker** is a production-grade automated pipeline for fetching, validating, and auditing Property Register Cards (PR Cards) from the MahaBhulekh portal.

---

## Package Architecture (`prc_checker/`)

* **`prc_checker/models.py`**:
  Strict Pydantic data models (`TitleReportData`, `CardResult`, `Manifest`, `RiskFlag`, `TitleHolder`, `ActionItem`, `StatutoryMapping`, `PrecedentRef`). Ensures type safety and schema validation across execution results and reports with zero fake hardcoded defaults.
* **`prc_checker/templates/`**:
  Jinja2 templates directory containing:
  - `card.html.j2`: Standalone HTML card viewer template
  - `report.md.j2`: 6-Block Lawyer Title Audit Report template
  - `promoter.md.j2`: Developer & Promoter Executive Brief template
  - `lawyer.md.j2`: Legal Counsel Title Search Brief template
  - `dashboard.html.j2`: Interactive split-screen workspace dashboard template
  - `styles.css.j2`: Shared CSS design system tokens
* **`prc_checker/session.py`**:
  Pure Playwright web driver wrapper. Handles `page.on("dialog")` native JS alert interception, dropdown cascade synchronization (`select_cascade`, `wait_opts`), font route fulfillments (returning empty `200 OK`), sub-plot re-fetches (`refetch_subplot`), submit button click dispatching (`#ContentPlaceHolder1_btnmainsubmit`), and non-blocking file IPC on `.captcha_input.txt`.
* **`prc_checker/cli.py`**:
  Root package CLI entrypoint. Includes **Automated Slash CTS Parent Fallback Engine** (auto-detects ASP.NET `NOT_FOUND` alerts on slash queries like `695/10`, queries parent CTS `695`, matches sub-plot option `695/10` from the ASP.NET dropdown list, and fetches sub-plots seamlessly).
* **`prc_checker/statutes.py`**:
  Statutory mapping engine for MLRC 1966 Sections 29(1), 29(2) & 38, BMC MMC Act 1888 Section 92, and Revenue Dept GR Class II Conversion rates (15%/50%).
* **`prc_checker/precedents.py`**:
  Bombay High Court Precedents engine mapping tenure to landmark BHC rulings (*Dudhwala Builders*, *Reliance Realty*, *BEAG*, *Laxmanrao*).
* **`prc_checker/vision.py`**:
  AI Vision read schema (`CardVisionRead`), `.read.json` sidecar persistence, Mermaid flowchart generator, rule-based legal risk flags, and 5-dimension confidence scorecard generator.
* **`prc_checker/preflight.py`**:
  Fast HTTP plot screening engine with strict 2.0s timeout guardrails.
* **`prc_checker/reports.py`**:
  Renders standalone self-contained HTML documents (`generate_clean_html`), 6-Block Markdown Title Audit Reports (`generate_title_report_md`), Promoter Briefs (`generate_promoter_brief`), and Lawyer Briefs (`generate_lawyer_brief`) using Jinja2 and Pydantic.
* **`prc_checker/artifacts.py`**:
  Dedicated disk I/O engine (`build_card_artifacts`). Creates plot subfolders and saves lossless JPEGs, clean HTML viewers, title reports, promoter/lawyer briefs, and JSON metadata.
* **`prc_checker/exporters.py`**:
  Exports batch query index to Master Excel Workbook (`index.xlsx`) with clickable hyperlinks to per-plot subfolders and CSV master index (`index.csv`).
* **`prc_checker/dashboard.py`**:
  Builds the interactive split-screen dark-mode batch workspace (`dashboard.html`) using Jinja2 templates.
* **`prc_checker/logger.py`**:
  Structured console and file logging module supporting `--verbose`, `--quiet`, and severity level filters.
* **`fetch_prcards.py`**:
  Root CLI entrypoint preserving PEP 723 `# /// script` inline execution header for `uv` and main entrypoint for `prc-checker` console script.

---

## File IPC Protocol (`.captcha_input.txt`)

1. `fetch_card()` saves CAPTCHA screenshot to `prcards/<village>_<cts>/.captcha_<fname>.png`.
2. Emits console log: `CAPTCHA_IMAGE: <abs_path>` and `WAITING_FOR_CAPTCHA [attempt/3]...`.
3. Script polls `.captcha_input.txt` (inside plot folder or root outdir) every 300ms for up to 25 seconds.
4. An external AI Vision Agent or OCR solver inspects the screenshot and writes the 6-character code directly to `.captcha_input.txt`.
5. The script reads the code, deletes `.captcha_input.txt`, submits form button `#ContentPlaceHolder1_btnmainsubmit`, and verifies output.

---

## Output Organization (Dedicated Plot Subfolder & Excel Index)

```text
prcards/                                            # Main Output Directory
├── index.xlsx                                      # Master Excel Index (Hyperlinks to Plot Assets)
├── index.csv                                       # Master CSV Index
├── dashboard.html                                  # Interactive Batch Workspace
├── manifest.json                                   # Execution Manifest
│
├── Worli_748/                                      # Plot Query Subfolder
│   ├── propcard_Worli_748.jpg                      # Lossless Original PR Card Image
│   ├── propcard_Worli_748.html                     # Standalone Refined 1.6 KB HTML Viewer
│   ├── propcard_Worli_748.json                     # Structured Metadata Sidecar
│   ├── title_report_propcard_Worli_748.md          # 6-Block Lawyer Title Audit Report
│   ├── promoter_brief_propcard_Worli_748.md        # Promoter Executive Brief
│   └── lawyer_brief_propcard_Worli_748.md          # Lawyer Legal Counsel Brief
```

---

## Verification & Test Commands

```bash
# 1. Run Complete Pytest Suite (15 Tests)
uv run pytest

# 2. Run Single or Multi-CTS Fetch (e.g. Worli CTS 748)
uv run prc-checker --village Worli --district 23 --cts 748

# 3. Run CLI Command with Verbose Output & Anchor Verification
uv run prc-checker --village Byculla --cts 1640 --anchor --verbose
```
