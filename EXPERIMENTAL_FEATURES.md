# Experimental Features Roadmap & Technical Specification — PRC-Checker 🧪

> [!NOTE]
> **PRIORITY STATUS: LOW / BACKLOG**  
> All features documented in this specification are currently **low priority** for future consideration. Development will focus on core extraction speed, reliability, and maintenance. These experimental concepts will be evaluated at a much later date.

---

## 🏛️ Architecture & Ingestion Strategy

All compliance, valuation, spatial, and regulatory features utilize a **3-Tier Data Ingestion Architecture**:
1. **Tier 1: Pre-Indexed Local SQLite Engine (`data/mumbai_land.sqlite`)**: Pre-indexes official Maharashtra Government Gazette PDFs, SRA notifications, CZMP Shapefiles, and ASR Ready Reckoner tables for **sub-millisecond (<1ms) offline queries** with zero network failure risk.
2. **Tier 2: Public HTTP JSON Endpoints**: Direct API probes to IGR Maharashtra and SRA GIS portals with strict 2.0s timeout guardrails.
3. **Tier 3: Permissive Fallback Engine**: Ensures property card extraction never fails due to external server downtime.

---

## 📦 Category 1: Export, Portfolio & Notification Engines

### 1. 📄 Court-Ready Styled PDF Exporter (`prc_checker/exporters/pdf.py`)
* **Objective**: Render 6-Block Title Audit Reports, Promoter Briefs, and Lawyer Briefs into styled, publication-ready PDF files (`title_report_*.pdf`).
* **Components**: Official law firm headers, watermark stamps, signature blocks, and embedded high-resolution property card scans.
* **Tech Stack**: WeasyPrint / ReportLab with modern HTML5/CSS print tokens.

### 2. 🗺️ GeoJSON & KML GIS Survey Boundary Exporter (`prc_checker/exporters/gis.py`)
* **Objective**: Convert extracted CTS plot area measurements, sheet numbers, and survey coordinates into standard GeoJSON and KML Shapefile formats.
* **Target Audience**: Architects, GIS surveyors, and urban planners dropping plot boundaries into Google Earth or AutoCAD.

### 3. 📊 Multi-Plot Executive Portfolio Dashboard (`prc_checker/reports/portfolio.py`)
* **Objective**: Expand `dashboard.html` with a single-page matrix comparing all fetched plots across Mumbai.
* **Key Metrics**: Combined Land Bank Area (Sq. Mtrs.), Freehold vs. Collector Class II ratio, Expired Leasehold count, and Combined Title Risk Level.

### 4. 🔔 Slack & Webhook Risk Alert Dispatcher (`prc_checker/notify.py`)
* **Objective**: Dispatch instant Webhook payloads, Slack messages, or Email alerts when high-risk title flags are detected during batch queries.
* **Trigger Conditions**: Collector Class II restricted tenure, expired lease grants, C.I.T. NOC requirements.

---

## 📜 Category 2: Domain Title Audit & Legal Intelligence

### 5. 🏗️ DCRP 2034 Development Potential & FSI Calculator (`prc_checker/domain/fsi.py`)
* **Objective**: Calculate buildable gross construction area (BUA in Sq. Ft.) based on extracted plot area (Sq. Mtrs.) and village zoning under **Mumbai DCRP 2034**.
* **Formulae**:
  * **Base Zonal FSI**: 1.33 (City District 23) / 2.0 (Suburban District 22).
  * **Permissible TDR**: Regulation 32 calculations.
  * **Additional Premium FSI**: Regulation 30 calculations.

### 6. 📜 Mutation Entry (Ferfar) Historic Timeline Engine (`prc_checker/domain/mutation.py`)
* **Objective**: Extract historical mutation entry numbers (*Ferfar No. 1204*, *Ferfar No. 3409*) from card margin notes to reconstruct a 50-year chronological title chain audit.
* **Output**: Identifies missing mutation links, un-recorded probate transfers, and historic encumbrances.

### 7. 🔒 CERSAI & Sub-Registrar Encumbrance Cross-Check (`prc_checker/domain/encumbrance.py`)
* **Objective**: Cross-check extracted lessee names and CTS plot details against bank mortgage registries (CERSAI) and IGR Maharashtra search indices.
* **Output**: Flags active bank mortgages, equitable charges, lis pendens litigation, or court attachment notices.

### 8. 🔍 Government Digital Signature & QR Code Authenticator (`prc_checker/domain/qr_verify.py`)
* **Objective**: Decode and verify embedded QR codes and PKI digital signatures on official e-PR Cards issued by MahaBhulekh.
* **Output**: 100% fraud protection confirming official government provenance.

---

## 💰 Category 3: Regulatory Compliance, Valuation & Localization

### 9. 💰 Ready Reckoner Valuation & Premium Estimator (`prc_checker/compliance/valuation.py`)
* **Objective**: Cross-reference plot location (Village, CTS) with current **Maharashtra Stamp Duty Ready Reckoner Rates (e-ASR)**.
* **Output**:
  * Total Land Market Valuation (₹ Crores).
  * Estimated **15% / 50% Collector Class II Freehold Conversion Fee** (under GR 2019/2024).
  * Estimated Stamp Duty payable on title assignment.

### 10. 🌐 Marathi ↔ English Legal Terminology Translator (`prc_checker/compliance/translator.py`)
* **Objective**: Translate legacy Marathi legal terms on physical property cards into standardized English terminology.
* **Dictionary**:
  * *भोगवटदार* $\rightarrow$ Occupant / Title Holder
  * *अज्ञानपालक* $\rightarrow$ Legal Guardian (Minor)
  * *बक्षीसपत्र* $\rightarrow$ Gift Deed
  * *गहाणखत* $\rightarrow$ Mortgage Deed
  * *वारस नोंद* $\rightarrow$ Heirship Mutation

### 11. 🏚️ SRA Slum Scheme Overlay Screener (`prc_checker/compliance/sra.py`)
* **Objective**: Cross-check CTS plot numbers against the **Slum Rehabilitation Authority (SRA)** database under Section 3C of the Maharashtra Slum Areas Act 1971.
* **Output**: Flags whether the plot falls within a declared slum cluster or sanctioned SRA scheme (Letter of Intent issued).

### 12. 🌊 Coastal Regulation Zone (CRZ) Buffer Screener (`prc_checker/compliance/crz.py`)
* **Objective**: Cross-check coastal plots (Worli, Bandra, Malabar Hill, Juhu) against **MCZMA CZMP 2019** spatial maps.
* **Output**: Flags CRZ-I (Ecological Buffer), CRZ-II (Urban Coastal Zone), or 500m High Tide Line (HTL) restrictions.

### 13. 🏛️ Externalized Legal Knowledge Base Engine (`data/legal_knowledge_base.sqlite` / `.json`)
* **Objective**: Externalize static registries in `statutes.py` and `precedents.py` into a SQLite database or version-controlled JSON schema file (`data/legal_knowledge_base.sqlite`).
* **Output**: Allows lawyers, legal researchers, and developers to update statutory sections, Revenue Dept GR rates, and Bombay High Court case ratios dynamically without modifying Python source code.
* **Features**: LRU result caching (`@lru_cache`), queryable tenure schemas, and zero network external dependency.
