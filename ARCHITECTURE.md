# PRC-Checker Technical Architecture & Protocol Specification

## Component Mapping

```text
PRC-Checker/
├── pyproject.toml         # Packaging, Dependencies & Console Scripts
├── .gitignore             # Repo Guardrails
├── fetch_prcards.py       # Main CLI Entrypoint
├── prc_checker/           # Modular Package Core
│   ├── __init__.py        # Package Init
│   ├── models.py          # Pydantic Data Models (Type Safety & Validation)
│   ├── session.py         # Pure Playwright Browser Driver & Form Interceptor
│   ├── reports.py         # Jinja2 Report, Brief & HTML Renderer
│   ├── artifacts.py       # Disk I/O & Artifact Builder Engine
│   ├── exporters.py       # Master Excel Index (.xlsx), CSV & SQLite Exporters
│   ├── dashboard.py       # Jinja2 Dark-Mode Workspace Builder
│   ├── logger.py          # Structured Logger
│   └── templates/         # Jinja2 Template Files
│       ├── card.html.j2   # HTML Card Template
│       ├── report.md.j2   # 6-Block Title Audit Report Template
│       ├── promoter.md.j2 # Promoter Executive Brief Template
│       ├── lawyer.md.j2   # Lawyer Legal Counsel Brief Template
│       ├── dashboard.html.j2 # Workspace Dashboard Template
│       └── styles.css.j2  # Shared CSS Token Design System
├── tests/                 # Pytest Test Suite
│   ├── __init__.py
│   ├── test_artifacts.py # Artifact Builder Unit Tests
│   ├── test_models.py     # Pydantic Model Tests
│   ├── test_templates.py  # Jinja2 Rendering Tests
│   ├── test_reports.py    # Report & Brief Unit Tests
│   ├── test_exporters.py  # Excel & CSV Exporter Tests
│   └── test_session.py    # Session Driver & Mock Tests
├── prcards/               # Main Output Directory
│   ├── index.xlsx         # Master Excel Index (Hyperlinked)
│   ├── index.csv          # Tabular CSV Index
│   ├── dashboard.html     # Interactive Batch Workspace
│   ├── manifest.json      # Execution Manifest
│   └── <Plot_Folder>/     # Dedicated Per-Plot Query Subfolder (e.g. Worli_748/)
│       ├── propcard_<village>_<cts>.jpg
│       ├── propcard_<village>_<cts>.html
│       ├── propcard_<village>_<cts>.json
│       ├── title_report_propcard_<village>_<cts>.md
│       ├── promoter_brief_propcard_<village>_<cts>.md
│       └── lawyer_brief_propcard_<village>_<cts>.md
├── README.md              # Project Overview & Quick Start Guide
├── HANDOFF.md             # Operational Manual & Handoff Guide
└── ARCHITECTURE.md        # Technical System Specification (This File)
```

---

## Sequence Flow Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as User / CLI
    participant Driver as prc-checker / fetch_prcards.py
    participant Models as prc_checker.models
    participant Session as prc_checker.Session
    participant Portal as MahaBhulekh Portal
    participant Solver as AI Vision / IPC Solver
    participant Reports as prc_checker.reports (Jinja2)
    participant Exporters as prc_checker.exporters

    User->>Driver: Run prc-checker --village Worli --cts 748
    Driver->>Session: Initialize Headless Browser & Route Interceptor
    Session->>Portal: Intercept .woff/.ttf/font & Fulfill 200 OK Empty
    Session->>Portal: Select District/Taluka/Village (select_cascade)
    Portal-->>Session: UpdatePanel Cascade Rendered
    Session->>Portal: Fill CTS & Click Search
    Portal-->>Session: CAPTCHA Image Rendered
    Session->>Solver: Save .captcha_fname.png & Poll .captcha_input.txt
    Solver-->>Session: Write Solved CAPTCHA Code
    Session->>Portal: Submit #ContentPlaceHolder1_btnmainsubmit
    Portal-->>Session: PR Card Base64 Data URI Rendered
    Session->>Models: Construct CardResult & TitleReportData Pydantic Models
    Session->>Reports: Create dedicated plot subfolder (e.g. Worli_748/) & save JPG/HTML/MD/JSON
    Session->>Exporters: Write index.csv & generate index.xlsx with hyperlinks
    Exporters-->>Driver: Save index.xlsx & index.csv
    Reports-->>Driver: Save dashboard.html
    Driver-->>User: Complete Execution (Exit Code 0)
```
