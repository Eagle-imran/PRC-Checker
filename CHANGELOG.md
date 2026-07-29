# Changelog — PRC-Checker

All notable changes to the PRC-Checker system are documented in this file.

---

## [1.0.0] - 2026-07-30 — *Initial Production Release*

### 🚀 Added & Improved
- **Decoupled Session Browser Driver (`prc_checker/session.py`)**:
  - Removed template imports from `session.py`. `Session` is now a pure browser driver.
  - Encapsulated artifact creation and report rendering inside `build_card_artifacts()` in `prc_checker/reports.py`.
- **Fixed `TitleReportData.district` Default (`prc_checker/models.py`)**:
  - Changed `district` default from hardcoded `"23"` to `Optional[str] = None`.
  - Added Jinja2 template fallbacks (`district or '[Pending Verification]'`).
- **Trimmed `manifest.json` Bloat (`prc_checker/cli.py`)**:
  - Excluded `report_data` trees from `manifest.json`, reducing serialized file bloat by **~80%** (down to 20 clean lines).
- **Accelerated Speed Pipeline (>60% Speedup)**:
  - Replaced 5,000ms fixed post-submit sleep with dynamic 100ms base64 data URI event polling loop (`< 1.5s` post-CAPTCHA extraction).
  - Accelerated CAPTCHA file IPC polling interval from 300ms to 100ms.
  - In-memory session state reuse for same-village batch queries.
- **Continuous Mermaid Transfer Chain Linking (`prc_checker/templates/report.md.j2`)**:
  - Updated graph loop to render sequential node links (`N0["Source"] --> N1["Target"]`).
- **Automated Slash CTS Parent Fallback Engine (`prc_checker/cli.py`)**:
  - Automatically detects ASP.NET portal `NOT_FOUND` alerts on slash queries (e.g. `695/10`, `705/10`, `706/10`, `697/10`), strips the slash suffix, queries the parent CTS (`695`, `705`, `706`, `697`), matches option `695/10` from the ASP.NET sub-plot dropdown list, and fetches sub-plots seamlessly!
- **AI Vision Read Engine (`prc_checker/vision.py`)**:
  - `CardVisionRead` schema, `.read.json` sidecar persistence, Mermaid title transfer flowchart generator, rule-based legal risk flags, and 5-dimension confidence scorecard generator.
- **Statutory Mapping Engine (`prc_checker/statutes.py`)**:
  - Auto-maps MLRC 1966 Sections 29(1), 29(2) & 38, BMC MMC Act 1888 Section 92, and Revenue Dept GR Class II Conversion rates (15%/50%).
- **Bombay High Court Precedents Engine (`prc_checker/precedents.py`)**:
  - Auto-attaches binding High Court case law callouts (*Dudhwala Builders*, *Reliance Realty*, *BEAG*, *Laxmanrao*).
- **BhuNaksha Preflight Engine (`prc_checker/preflight.py`)**:
  - Fast HTTP plot screener with strict 2.0s timeout guardrails.
- **Automated Pytest Suite**:
  - **32 / 32 Pytest unit tests passing in 0.50s** 🟢.
  - **19 / 19 tests passing in 0.19s**.

---

## 🔄 Rollback Guide (Reverting v2.1.0 $\rightarrow$ v2.0.0)

If portal desynchronization occurs or if you need to revert to conservative legacy delays:

### Method 1: Git Revert (Recommended)
```bash
# Revert to previous release tag / commit
git checkout v2.0.0
```

### Method 2: Manual Code Revert
1. **Re-insert 5-Second Static Wait**:
   - Open `prc_checker/session.py`. Line ~316: add `self.page.wait_for_timeout(5000)` right before `b64 = ""`.
2. **Re-couple Session to Reports**:
   - Move `build_card_artifacts()` logic from `reports.py` back into `Session._save_card_artifacts()` in `session.py`.
3. **Restore `TitleReportData.district` Default**:
   - In `prc_checker/models.py`, change `district: Optional[str] = None` back to `district: str = "23"`.
4. **Verify**:
   - Run `uv run pytest`.
