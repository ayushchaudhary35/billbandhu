# BillBandhu (कच्चा to पक्का बिल) — Product & Technical Specification

## 1. Executive Summary & Vision

**BillBandhu** is a responsive web application designed to bridge the digital and formal divide for Indian micro, small, and medium shopkeepers (kirana stores, grain merchants, cloth traders, hardware shops). It converts photographs of handwritten Indian shop bills ("kacha" bills written in Hindi, Punjabi, English, or mixed scripts/numerals) into structured, compliant, GST-ready invoices ("pakka" bills) and GST filing data (GSTR-1 summary export).

The system serves two primary personas:
1. **Small Indian Shopkeepers**: Low digital literacy, high operational speed, vernacular language speakers who write kacha bills in local shorthand and need quick, reliable digitisation.
2. **Evaluators & Judges**: Testing on desktop/laptop web browsers across diverse edge cases, validating deterministic accuracy, compliance correctness, and structural elegance.

---

## 2. Core Architectural Principle

> **"AI reads, rules decide."**

* **Role of LLM / Vision Models**: Vision models are strictly limited to text detection, optical symbol recognition, and raw field extraction (reading raw tokens, line items, and quantities from messy handwritten ink).
* **Role of Deterministic Code**: All mathematical computations, tax breakdowns, HSN code lookups, unit conversions, confidence scoring, and validation rules are executed exclusively by deterministic Python algorithms.
* **No generative math**: Under no circumstances will a model be asked or permitted to calculate taxes, totals, or round-offs.

---

## 3. The 12 Immutable Hard Rules

1. **Config-Driven Domain Knowledge**: GST tax slabs, HSN/SAC mappings, vernacular shorthand keywords, and unit dictionaries must never be hardcoded. All must be loaded dynamically from `/config/*.json`.
2. **Zero Silent Guessing**: Ambiguous or unreadable text must never be guessed or fabricated. If a field cannot be deterministically resolved, it must be assigned `null` and flagged with a distinct UI warning ("red flag").
3. **Objective Confidence Metrics**: Confidence is determined via **cross-model consensus** (dual-model comparison) and **deterministic rule checks**, never through model self-reported probabilities.
4. **Dual Pricing Modes**:
   - Mode A: **Price includes GST** (default for retail kacha slips).
   - Mode B: **Add GST on top** (standard wholesale/B2B invoicing).
   - Dynamic real-time recalculation of taxable base, CGST, SGST, IGST, and final grand total upon toggle.
5. **Three Shopkeeper Regimes**:
   - **Unregistered Dealer**: Generates a clean, simple bill without tax breakdown or GSTIN requirements.
   - **Composition Scheme Dealer**: Generates a statutory *Bill of Supply* with the mandatory statutory line: *"Composition taxable person, not eligible to collect tax on supplies"*.
   - **Regular Taxpayer**: Generates a standard *Tax Invoice* with dual-split CGST + SGST (intra-state) or IGST (inter-state), HSN/SAC codes, and proper invoice numbering.
6. **Strict Secret Isolation**: API keys and secrets must only be loaded via environment variables (`.env`). Secrets must never be stored in source code or client bundles.
7. **Ephemeral Image Privacy**: Uploaded bill images must be immediately deleted from storage post-processing unless the user explicitly checks an opt-in consent box.
8. **No Direct Portal Submissions**: BillBandhu does not connect to or push data to any government GST portal. Every output display, PDF, and spreadsheet must prominently feature the disclaimer:
   > *"Please confirm with your CA before filing."*
9. **Classical Image Enhancement Only**: No generative AI deblurring, GANs, or super-resolution filters. Only classical computer vision algorithms (grayscale, adaptive thresholding, bilateral filtering, deskewing) may be applied. The raw original image must always be preserved for side-by-side inspection.
10. **Financial Precision**: All monetary values, taxes, and rates must use Python's `Decimal` type. Floating-point numbers are strictly prohibited for financial logic. 100% of deterministic calculation functions must be covered by comprehensive `pytest` test suites.
11. **Vernacular & Accessible UI**:
    - Primary languages: English (`en`), Hindi (`hi`), and Punjabi (`pa`).
    - Base typography: font size $\ge 16\text{px}$.
    - Touch targets: minimum $48\text{px} \times 48\text{px}$.
    - Zero accounting jargon: use simple, shopkeeper-friendly terminology.
    - Multi-sensory visual cues: always use **Colour + Icon + Text** together (never colour alone).
    - Full undo/redo capability for all user manual overrides.
    - Friendly, actionable error messages with guided remedies.
12. **Unified Model Adapter Abstraction**: All LLM/Vision calls must pass through a single unified adapter interface (`ModelAdapter`). Provider credentials and model names are driven by `.env` (`PROVIDER_A/B`, `MODEL_A/B/FALLBACK`, `API_KEY_A/B`).

---

## 4. Scope & Non-Goals

### In Scope
- Web application responsive on mobile browsers (Android Chrome, iOS Safari) and desktop browsers (Chrome, Edge, Firefox, Safari).
- Single photo upload (PNG, JPEG, WebP, HEIC conversion).
- Multi-script transcription: Devanagari (Hindi), Gurmukhi (Punjabi), Roman (English), and mixed vernacular numerals (0-9, ०-९, ੦-੯).
- Deterministic parsing & validation pipeline.
- Interactive side-by-side review interface with inline cell editing and undo.
- GST-ready PDF generation (`reportlab`).
- GSTR-1 compliant Excel summary download (`openpyxl`).

### Explicit Non-Goals (Out of Scope)
- ❌ Progressive Web App (PWA) / Service Worker offline caching.
- ❌ Offline inference / on-device LLM execution.
- ❌ Voice / Speech-to-text input.
- ❌ Native camera auto-capture / automated edge detection viewfinder (standard file/camera input upload only).
- ❌ Direct GSTN / e-Way bill / NIC API integrations.

---

## 5. System Architecture & Components

```
+-------------------------------------------------------------------------+
|                                FRONTEND                                 |
|          React + Vite + Tailwind CSS + i18n JSON (en / hi / pa)         |
|  - High-contrast, Accessible (>=16px font, 48px targets)                |
|  - Dual pricing mode toggle (live Decimal recalculation)               |
|  - Side-by-side original bill preview vs. editable table with Undo      |
|  - Mandatory CA warning banner & Multi-cue error indicators             |
+------------------------------------+------------------------------------+
                                     | JSON / Multipart HTTP (FastAPI)
                                     v
+-------------------------------------------------------------------------+
|                             FASTAPI BACKEND                             |
+-------------------------------------------------------------------------+
| 1. Classical Preprocessor (OpenCV & Pillow)                            |
|    - Grayscale, Deskew, Bilateral Denoise, Adaptive Threshold           |
|    - Retain untouched original; ephemeral storage cleanup               |
+------------------------------------+------------------------------------+
| 2. Unified Vision Model Adapter (`ModelAdapter`)                       |
|    - Provider A & Provider B execution (async httpx)                    |
|    - Strict JSON output schema enforcement                              |
+------------------------------------+------------------------------------+
| 3. Consensus & Agreement Engine                                         |
|    - Token & Line-item alignment across Provider A and Provider B       |
|    - Agreement scoring; mismatch/ambiguity -> `null` + RED FLAG         |
+------------------------------------+------------------------------------+
| 4. Deterministic Business Rules Engine (Pure Python Decimal)           |
|    - Rule-based fuzzy matcher against `/config/*.json` (rapidfuzz)      |
|      * HSN lookup & GST rate matching                                   |
|      * Unit normalisation (kilo, packet, dozen, peti, bore, etc.)        |
|      * Vernacular shorthand mapping                                     |
|    - Tax Regime logic: Unregistered vs Composition vs Regular           |
|    - Pricing calculation: Inclusive (reverse tax) vs Exclusive (forward)|
|    - Confidence aggregator (Agreement + Validations)                    |
+------------------------------------+------------------------------------+
| 5. Output Generators                                                    |
|    - `ReportLab` Tax Invoice / Bill of Supply PDF generator             |
|    - `OpenPyXL` GSTR-1 tabular Excel workbook export                    |
+-------------------------------------------------------------------------+
```

---

## 6. Detailed Functional Specifications

### 6.1 Configuration System (`/config/*.json`)
The application relies on modular JSON configuration files:
- `gst_rates.json`: Current statutory tax slabs (e.g., 0%, 5%, 12%, 18%, 28%) and composition rate rules.
- `hsn_catalog.json`: Common kirana/retail product classifications, vernacular synonyms, and default HSN codes.
- `units.json`: Standard units (`KGS`, `PCS`, `LTR`, `BOX`, `BAG`, `MTR`, `DOZ`) and their vernacular representations (`किलो`, `ਕਿਲੋ`, `pk`, `pkt`, `बोरी`, `पेटी`).
- `vernacular_shorthand.json`: Shorthand notation mappings for commodity names and quantity representations.

### 6.2 Classical Image Preprocessing Pipeline
- Reads raw image via Pillow and OpenCV.
- Performs orientation check (EXIF metadata handling).
- Applies bilateral filter (preserves handwritten ink strokes while reducing grain noise).
- Deskews document using Otsu's thresholding and minAreaRect rotation.
- Prepares dual output:
  1. **Original Raw Image**: Retained for the user's side-by-side editing pane.
  2. **Optimized Enhanced Copy**: Grayscale/contrast-stretched image piped to vision models.
- **Privacy Enforcement**: Temporary files are assigned UUIDs and erased via a background task / `finally` block once downstream extraction completes, unless the explicit opt-in parameter `retain_image=true` is sent.

### 6.3 Vision Model Adapter & Consensus Engine
- Abstract base class `ModelAdapter` with standardized `extract_bill(image_bytes: bytes) -> RawBillExtraction`.
- Concrete implementations for configured providers (e.g. Gemini, OpenAI, Claude, or local OpenAI-compatible endpoints) configured via:
  ```env
  PROVIDER_A=google
  MODEL_A=gemini-2.5-flash
  API_KEY_A=...
  PROVIDER_B=google
  MODEL_B=gemini-2.5-flash
  MODEL_FALLBACK=gemini-2.5-flash
  API_KEY_B=...
  ```
- Strict JSON Schema prompting: requires extracted lines containing `raw_item_name`, `raw_quantity`, `raw_unit`, `raw_rate`, `raw_line_total`.
- **Cross-Model Consensus Evaluator**:
  - Compares extraction outputs from Model A and Model B.
  - Item lines are aligned using string similarity (rapidfuzz token sort ratio) and numeric matching.
  - If both models agree within tolerance ($\pm 0$), confidence is boosted.
  - If models disagree, or if a model returns unreadable/low confidence markers, the field value is set to `null` and flagged as `AMBIGUOUS_VALUE` / `UNREADABLE`.

### 6.4 Deterministic Business Rules Engine
- **Math Specification**:
  - `Decimal` with `ROUND_HALF_UP` precision to 2 decimal places.
  - **Inclusive Mode**:
    $$\text{Taxable Value} = \text{round}\left(\frac{\text{Line Total}}{1 + \text{Rate}}, 2\right)$$
    $$\text{Total GST} = \text{Line Total} - \text{Taxable Value}$$
  - **Exclusive Mode**:
    $$\text{Taxable Value} = \text{round}(\text{Quantity} \times \text{Rate}, 2)$$
    $$\text{Total GST} = \text{round}(\text{Taxable Value} \times \text{Rate}, 2)$$
    $$\text{Line Total} = \text{Taxable Value} + \text{Total GST}$$
  - **Tax Splits**:
    - Intra-state: $\text{CGST} = \text{round}(\text{Total GST} / 2, 2)$, $\text{SGST} = \text{Total GST} - \text{CGST}$, $\text{IGST} = 0.00$.
    - Inter-state: $\text{CGST} = 0.00$, $\text{SGST} = 0.00$, $\text{IGST} = \text{Total GST}$.
- **Fuzzy Dictionaries**:
  - Matches item descriptions to `/config/hsn_catalog.json` using Levenshtein distance and RapidFuzz scoring. Matches below 75% threshold are marked unclassified (`HSN: null`).
  - Unit string matching against `/config/units.json`.
- **Validation Rules**:
  - Rule V1: $\text{Quantity} \times \text{Rate} \approx \text{Line Total}$ check.
  - Rule V2: Sum of line items $\approx$ Bill Grand Total.
  - Rule V3: Flag any negative numbers, zero quantities, or duplicate line items.

### 6.5 User Interface & Experience
- **Language Switcher**: Prominent header buttons for English, हिन्दी, ਪੰਜਾਬੀ.
- **Input Screen**: Large drag-and-drop / click-to-upload card with clear instructions and camera/file picker.
- **Review Screen (Split Screen)**:
  - Left / Top: Interactive viewer for original handwritten receipt (zoom, pan).
  - Right / Bottom: Editable table with prominent status chips (Green Check = Verified, Yellow Alert = Low Confidence, Red Warning = Unreadable/Null).
- **Controls**:
  - Shopkeeper Type Radio: [Unregistered] [Composition] [Regular]
  - Pricing Mode Toggle: [Price includes GST] vs [Add GST on top]
  - Global Undo / Redo action buttons.
- **Export Actions**:
  - [Download PDF Bill]
  - [Export GSTR-1 Excel]
- **Mandatory Compliance Disclaimer Banner**:
  - Always visible on footer, PDF, and Excel: *"Please confirm with your CA before filing."*

---

## 7. Testing & Quality Assurance Mandate
- Pytest unit tests for all mathematical algorithms, tax breakdown logic, rounding edge cases, and fuzzy lookup dictionaries.
- Verification tests for all 12 hard rules.
- Test coverage for JSON configuration loaders and schema validators.
- Frontend rendering tests for font sizes, contrast ratios, and multilingual text display.

