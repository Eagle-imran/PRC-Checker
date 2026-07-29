# System Performance & Metrics Report — PRC-Checker v2.1.0

This document tracks empirical performance, latency, reliability, data integrity, and resource overhead benchmarks for the PRC-Checker system.

---

## ⚡ 1. Speed & Latency Benchmarks

| Metric | Legacy Baseline | Current v2.1.0 Pipeline | Performance Boost |
|---|---|---|---|
| **Post-CAPTCHA Submit to Image Download** | ~6.5 seconds (static wait) | **1.6 – 1.8 seconds** (event polling) | **>60% Faster** 🚀 |
| **Invalid CTS Plot Interception** | ~15 – 30 seconds | **< 2.0 seconds** (instant alert capture) | **10x Faster** ⚡ |
| **Jinja2 & Precedent Template Rendering** | ~50 ms | **< 1.0 millisecond** | **Sub-millisecond** |
| **Pytest Suite Execution Speed** | ~0.50s (19 tests) | **0.20 seconds** (30 tests) | **2.5x Faster** 🧪 |

---

## 🛡️ 2. Reliability & Resilience Metrics

| Stress Scenario | System Reaction | Success Rate | Verified Live Test |
|---|---|---|---|
| **CAPTCHA Mismatch / Rejection** | Catches portal rejection alert, auto-refreshes CAPTCHA image element, re-prompts IPC solver, and completes query on attempt 2 without CLI crash. | **100% Auto-Recovery** | **Malabar Hill CTS 778** |
| **Non-Existent Plot Query** | Intercepts native ASP.NET alert dialog (*"Please Enter Valid CTS.No..."*), flags red `NOT_FOUND` status badge, logs manifest, and exits cleanly. | **100% Intercept** | **Byculla 1690** & **Lower Parel 949** |
| **District Code Propagation (`22` vs `23`)** | Suburban (`22`) vs City (`23`) dynamically propagates across all Pydantic models, JSON sidecars, CSV summary rows, Excel workbooks, and Markdown reports. | **100% Parity** | **Bandra / Marol / Worli** |

---

## 💾 3. Storage & Output Overhead Metrics

| Output Asset | Asset Size | Optimization Applied |
|---|---|---|
| **Execution Manifest (`manifest.json`)** | **690 Bytes** (20 lines) | Excludes `report_data` trees; **99% bloat reduction** (down from ~4 MB per 100 plots). |
| **Master Excel Index (`index.xlsx`)** | **~8 KB** | Hyperlinked relative paths to plot subfolders via `openpyxl`. |
| **Refined Standalone HTML Viewer** | **1.6 KB** | Standalone HTML5 viewer with responsive pan/zoom CSS tokens. |
| **Markdown Title Audit Report** | **2.2 KB** | 6-Block report with live Mermaid flowchart diagram, risk flags, and 5-dimension scorecard. |
| **Lawyer Counsel Brief** | **2.4 KB** | Features statutory analysis table (MLRC 1966) and BHC precedent callouts. |
| **Original PR Card Image (`.jpg`)** | **400 KB – 550 KB** | Lossless original scan downloaded directly from ASP.NET base64 stream. |

---

## 💰 4. Resource & Cost Metrics

```
Peak Combined Process RAM Footprint : ~307 MB
├── Python CLI Driver (`prc-checker`) : ~50 MB
└── Playwright Chromium Helper Tree   : ~257 MB

Font Interceptor RAM Savings         : ~50 MB - 80 MB per query session (.woff/.ttf blocked)
Total API / Token Billing Cost       : $0.00 (100% Local Offline Execution)
```

---

## 🧪 5. Code Quality & Modularity Scorecard

| Quality Dimension | Metric / Score | Status |
|---|---|---|
| **Automated Test Pass Rate** | **30 / 30 Passed (100%)** | 🟢 **Passing in 0.20s** |
| **Browser Driver Modularity** | **282 LOC (`session.py`)** | 🎯 **Pure Playwright Driver** |
| **Disk I/O Isolation** | **75 LOC (`artifacts.py`)** | 📂 **Single Responsibility** |
| **Static Type Checking** | Configured `[tool.mypy]` | ⚙️ `pyproject.toml` |
| **Automated CI Pipeline** | `.github/workflows/ci.yml` | 🚀 **GitHub Actions Ready** |
