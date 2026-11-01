# BillBandhu — Implementation Plan & Risk Analysis

## 1. Project Overview & Operational Methodology

This document outlines the step-by-step phased execution strategy for **BillBandhu**. 
Strict compliance with the workflow mandate will be maintained:
- **Before each step**: A concise, structured plan will be presented.
- **During the step**: Precise, isolated changes adhering to the 12 Hard Rules.
- **After each step**: Run automated tests, verify results (visual/screenshot check for UI), and **STOP to wait for explicit user approval** before advancing.
- **Zero scope creep**: No unrequested features will be introduced.

---

## 2. Implementation Phases

```
+---------------------------------------------------------------------------------+
| Phase 0: Foundations & Configuration Datasets                                   |
|   - Repo layout, /config/*.json definitions, Python & Node environment setup    |
+---------------------------------------+-----------------------------------------+
                                        v
+---------------------------------------------------------------------------------+
| Phase 1: Pure Deterministic Engine & Mathematical Test Suite                   |
|   - Decimal calculations (inclusive/exclusive), tax regimes, unit parser,       |
|     rapidfuzz catalog lookup, pytest test battery (>95% coverage)               |
+---------------------------------------+-----------------------------------------+
                                        v
+---------------------------------------------------------------------------------+
| Phase 2: Classical Image Preprocessing & Ephemeral Storage                      |
|   - OpenCV/Pillow deskewing, bilateral filter, adaptive thresholding            |
|   - Retention/deletion lifecycle (opt-in privacy, original image preservation)  |
+---------------------------------------+-----------------------------------------+
                                        v
+---------------------------------------------------------------------------------+
| Phase 3: Pluggable Model Adapter & Dual-Model Consensus Engine                  |
|   - Abstract ModelAdapter interface, provider configs via .env                  |
|   - Dual-model extraction comparison, cross-model agreement score,              |
|     red-flagging unreadable / conflicting values as null                        |
+---------------------------------------+-----------------------------------------+
                                        v
+---------------------------------------------------------------------------------+
| Phase 4: Export Engine (ReportLab PDF & OpenPyXL Excel)                         |
|   - Tax Invoice & Bill of Supply PDF with CA disclaimer                         |
|   - GSTR-1 structured Excel sheet generator                                     |
+---------------------------------------+-----------------------------------------+
                                        v
+---------------------------------------------------------------------------------+
| Phase 5: FastAPI Backend Endpoints & Integration Tests                          |
|   - Async endpoints for upload, extraction, calculation, and export             |
|   - Integration tests covering end-to-end request/response flows                |
+---------------------------------------+-----------------------------------------+
                                        v
+---------------------------------------------------------------------------------+
| Phase 6: Accessible Vernacular Frontend (React + Vite + Tailwind)              |
|   - i18n JSONs (en, hi, pa), >=16px text, 48px targets, color+icon+label cues    |
|   - Side-by-side original bill preview with zoom & pan                          |
|   - Editable table with live Decimal recalculation on pricing mode toggle       |
|   - Full undo/redo history, friendly shopkeeper error states                    |
+---------------------------------------+-----------------------------------------+
                                        v
+---------------------------------------------------------------------------------+
| Phase 7: Verification, Edge Case Auditing & Final Showcase                      |
|   - Real-world handwritten slips (Hindi, Punjabi, English, mixed numerals)      |
|   - CA disclaimer audit, secret leakage audit, cross-browser validation         |
+---------------------------------------------------------------------------------+
```

### Detailed Phase Breakdown

#### Phase 0: Foundations, Configuration & Environment
- **Objective**: Establish the directory structure, dependencies, and external configuration dictionaries.
- **Tasks**:
  1. Create folder structure: `backend/`, `frontend/`, `config/`, `tests/`.
  2. Populate `/config/gst_rates.json`, `/config/hsn_catalog.json`, `/config/units.json`, `/config/vernacular_shorthand.json`.
  3. Initialize backend virtual environment and `requirements.txt` (`fastapi`, `uvicorn`, `opencv-python-headless`, `pillow`, `rapidfuzz`, `openpyxl`, `reportlab`, `pytest`, `httpx`, `pydantic-settings`).
  4. Initialize frontend via Vite (`react`, `tailwindcss`, `lucide-react`, custom i18n store).
- **Deliverable**: Clean project scaffold, valid config JSONs, verified environment setup.

#### Phase 1: Pure Deterministic Engine & Mathematical Test Suite
- **Objective**: Implement the heart of "AI reads, rules decide" — zero LLM involvement in math.
- **Tasks**:
  1. Implement `backend/engine/tax_calculator.py` using `Decimal` exclusively:
     - Mode 1: Price includes GST (reverse calculation).
     - Mode 2: Add GST on top (forward calculation).
     - Regime 1: Unregistered (no tax columns).
     - Regime 2: Composition (Bill of Supply, composite tax statement).
     - Regime 3: Regular (Tax Invoice with intra-state CGST+SGST or inter-state IGST).
  2. Implement `backend/engine/matcher.py`:
     - Fuzzy item lookup via `rapidfuzz` against `hsn_catalog.json`.
     - Standard unit normalisation via `units.json`.
     - Vernacular shorthand expansion.
  3. Implement `backend/engine/validator.py`:
     - Rule checks: Line item math consistency ($\text{Qty} \times \text{Rate} \equiv \text{Total}$), grand total consistency, zero/negative price traps.
     - Ambiguity flagger: Mark missing/unparseable values as `null` with red flag markers.
  4. Build exhaustive `pytest` test suite (`tests/test_calculator.py`, `tests/test_matcher.py`, `tests/test_validator.py`).
- **Deliverable**: 100% green pytest suite verifying all arithmetic, rounding (`ROUND_HALF_UP`), and edge cases.

#### Phase 2: Classical Image Preprocessing & Ephemeral Storage
- **Objective**: Clean and standardize incoming photos without any generative AI hallucination.
- **Tasks**:
  1. Implement `backend/vision/preprocessor.py`:
     - Grayscale conversion, Otsu thresholding, bilateral filter, contour-based deskewing.
     - Preservation of untouched raw image for the user's side-by-side inspection.
  2. Implement storage manager with automatic deletion lifecycle:
     - Temporary file creation with secure UUID paths.
     - Background cleanup task ensuring image removal unless `opt_in_retention=True`.
  3. Pytest suite covering image rotation, format handling, and cleanup guarantees.
- **Deliverable**: Reliable image enhancer producing clean inputs and verifiable deletion routines.

#### Phase 3: Pluggable Model Adapter & Dual-Model Consensus Engine
- **Objective**: Abstract LLM vision calls and implement cross-model agreement logic.
- **Tasks**:
  1. Create abstract base class `ModelAdapter` (`backend/vision/adapter.py`).
  2. Implement concrete adapters supporting Google Gemini / OpenAI / Anthropic APIs driven purely by environment variables (`PROVIDER_A`, `MODEL_A`, `API_KEY_A`, etc.).
  3. Design strict JSON prompt specifying extraction schema (raw strings/tokens only; no math).
  4. Implement `backend/vision/consensus.py`:
     - Run extraction on Provider A and Provider B (or fallback).
     - Align detected line items using fuzzy string similarity.
     - Compute cross-model agreement score.
     - If discrepancy > tolerance, mark field `null` + assign `RED_FLAG`.
  5. Mock tests verifying consensus evaluation, disagreement handling, and error resilience.
- **Deliverable**: Decoupled, multi-provider extraction pipeline with deterministic agreement scoring.

#### Phase 4: Export Engine (ReportLab PDF & OpenPyXL Excel)
- **Objective**: Output GST-compliant documentation with mandatory legal disclaimers.
- **Tasks**:
  1. Implement `backend/export/pdf_generator.py` via `reportlab`:
     - Generates clean Tax Invoice or Bill of Supply based on shopkeeper regime.
     - Prominent, inescapable disclaimer: *"Please confirm with your CA before filing."*
  2. Implement `backend/export/excel_generator.py` via `openpyxl`:
     - Generates GSTR-1 formatted tables (B2B / B2CS invoice summary).
     - Includes statutory CA disclaimer in header row.
  3. Pytest suite checking PDF/Excel file creation and byte-stream integrity.
- **Deliverable**: Pixel-perfect invoice PDFs and standardized GSTR-1 Excel spreadsheets.

#### Phase 5: FastAPI Backend Endpoints & Integration
- **Objective**: Connect modules into a cohesive REST API.
- **Tasks**:
  1. Implement routes:
     - `POST /api/process-bill`: Image upload, preprocessing, consensus extraction, and deterministic calculation.
     - `POST /api/recalculate`: Instant recalculation upon manual edits or mode toggle.
     - `POST /api/export/pdf`: Stream generated invoice PDF.
     - `POST /api/export/excel`: Stream generated GSTR-1 Excel.
  2. Integration tests testing end-to-end request lifecycles.
- **Deliverable**: Fully tested, documented FastAPI server.

#### Phase 6: Accessible Vernacular Frontend (React + Vite + Tailwind)
- **Objective**: Build a high-contrast, shopkeeper-friendly, responsive interface.
- **Tasks**:
  1. Build multi-language architecture with JSON dictionaries for English (`en`), Hindi (`hi`), Punjabi (`pa`).
  2. Implement layout adhering to UI Hard Rules:
     - Typography $\ge 16\text{px}$, tap targets $\ge 48\text{px}$.
     - Colour + Icon + Word triples for all states (e.g. 🟢 Verified, 🟡 Low Confidence, 🔴 Attention Needed).
     - Pricing Mode toggle (live reactive total updates).
     - Shopkeeper Regime selector (Unregistered, Composition, Regular).
  3. Side-by-side verification pane: Original bill viewer on left/top with zoom/pan, interactive table on right/bottom.
  4. Cell editing with full Undo/Redo history stack.
  5. Prominent CA disclaimer banner and friendly, actionable error dialogs.
- **Deliverable**: Functional, accessible web UI with automated/visual validation.

#### Phase 7: Edge Case Auditing, Testing & Final Verification
- **Objective**: Comprehensive end-to-end testing with realistic sample bills across scripts.
- **Tasks**:
  1. Test with mixed Hindi (Devanagari numerals), Punjabi (Gurmukhi), and English bills.
  2. Verify rounding stability across large datasets.
  3. Security check: confirm zero keys exposed in frontend bundles or logs.
  4. User acceptance check against all 12 Hard Rules.
- **Deliverable**: Final production-ready demonstration package.

---

## 3. Risk Matrix & Mitigation Strategies

| Risk Category | Specific Risk Description | Severity | Impact | Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **Script & Numerals** | Ambiguity between Devanagari numerals (e.g., ४ vs ५ vs ९) and cursive Gurmukhi numbers. | High | Incorrect quantities or rates. | Dual-model consensus flags disagreements immediately as `null` + red flag. Validation checks ($\text{Qty} \times \text{Rate} \neq \text{Total}$) catch numeral misreads. Shopkeeper can tap cell to edit. |
| **Arithmetic / Rounding** | Discrepancies between line-item reverse GST calculation and grand total rounding. | High | Non-compliant invoice math. | Enforce `Decimal` with `ROUND_HALF_UP` everywhere. Calculate item-by-item taxable base, then derive GST residual ($\text{GST} = \text{Total} - \text{Taxable}$) to guarantee exact sum equality. Exhaustive pytest edge cases. |
| **LLM Hallucination** | Model invents plausible-sounding items, taxes, or numbers not present on the receipt. | Critical | Erroneous invoices, trust failure. | "AI reads, rules decide." Strict schema restricts model output to raw character strings. Confidence is computed by cross-model agreement + deterministic validation, never model self-confidence. |
| **Model Disagreement / Latency** | Provider A and Provider B disagree significantly or have slow response times. | Medium | Processing delay or unparsed fields. | Async parallel execution via `httpx.AsyncClient`. Configurable fallback model. Conflicting fields default to `null` with a friendly "Please check this item" prompt. |
| **Privacy & Compliance** | Sensitive merchant slips or customer details stored permanently. | High | Privacy violation, legal risk. | Ephemeral storage lifecycle: files automatically purged post-processing unless user explicitly opts in. No data transmission to government GST portals. |
| **Digital Literacy / UI Friction** | Shopkeeper confused by complex dropdowns or accounting jargon. | High | Abandonment of application. | Local-language first (Hindi/Punjabi default capability). Clear visual hierarchy: big buttons, text $\ge 16\text{px}$, color + icon + label (never color alone), full undo support, zero technical tax jargon. |
| **Scope Creep** | Temptation to add offline PWA, native camera capture, or voice input. | Medium | Missed hackathon deadlines & bloated architecture. | Hard rule enforcement: strictly a responsive website. Keep architecture lean, modular, and laser-focused on the core pipeline. |

---

## 4. Next Step & Protocol

We are currently at **Phase 0 (Initial Setup & Specification Approval)**.
Per instructions:
1. No code has been written yet.
2. Awaiting your explicit approval of `SPEC.md` and `PLAN.md` before proceeding to Phase 0 execution.

