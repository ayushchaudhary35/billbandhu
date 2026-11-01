# BillBandhu (कच्चा to पक्का बिल)

> **"AI reads, rules decide."**  
> LLMs only extract raw tokens and text fields from handwritten shop slips. All mathematics, tax calculations, HSN lookups, unit conversions, and validation logic are executed by 100% deterministic code.

BillBandhu converts photographs of handwritten Indian shop bills (in Hindi, Punjabi, English, and mixed scripts/numerals) into GST-ready invoices and GSTR-1 filing export summaries.

---

## 🚀 Key Features

- **Vernacular-First OCR Extraction:** Handles Hindi, Punjabi, English, and mixed regional numbers/shorthand (sawa, dedh, etc.).
- **Deterministic Calculation Engine:** Financial precision using Python's `Decimal` type to avoid floating-point errors.
- **Config-Driven GST Slabs:** All tax rates, HSN codes, and unit conversions reside in JSON config files—never hardcoded.
- **Zero Silent Guessing:** Unreadable values are explicitly flagged as `null` with a red flag for manual review.
- **Compliance Safeguards:** Built-in disclaimers and structured checks for safe, CA-verified tax workflows.

---

## 📂 Project Structure

```text
billbandhu/
├── README.md                 # System overview & operations guide
├── SPEC.md                   # Full product & technical specification
├── PLAN.md                   # Implementation roadmap & risk analysis
├── .env.example              # Provider and model configuration template
├── .gitignore                # Secret and temporary upload guards
├── config/                   # Domain configuration files (No hardcoded rules!)
│   ├── gst_rates.json        # Statutory GST slabs and composition rates
│   ├── hsn_items.json        # 60 common kirana commodities with tri-script variants
│   ├── shorthand.json        # Vernacular fractions (sawa, dedh, etc.) & digit maps
│   ├── units.json            # Canonical units and conversion factors
│   ├── thresholds.json       # Blur limits, match thresholds, timeouts
│   └── price_ranges.json     # Plausible item price ranges
├── frontend/                 # Vernacular-first responsive React web app
│   ├── components/           # Accessible UI components (Navbar, Tables, Cards)
│   ├── pages/                # Home, Scan, Review, Bills, Reports, Settings
│   └── i18n/                 # Localization dictionaries (en.json, hi.json, pa.json)
├── backend/                  # FastAPI deterministic backend
│   ├── routes/               # API endpoints (/process-bill, /recalculate, /export)
│   ├── services/             # Preprocessing, consensus, calculations
│   ├── prompts/              # Strict vision model extraction JSON schemas
│   ├── adapters/             # Unified ModelAdapter interface (Provider A / B)
│   ├── cache/                # Ephemeral session cache
│   └── tests/                # Backend specific unit and integration tests
├── tests/                    # Project test suite
│   ├── sample_bills/         # Test handwritten kacha bill photographs
│   └── gold/                 # Ground truth JSONs and benchmark outputs
└── docs/                     # Architectural documentation and guides
```

---

## 🛠️ Quick Setup & Local Run Guide

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/billbandhu.git
cd billbandhu
```

### Step 2: Environment Variables Set Up (API Connection)
Copy the template and set up your API keys in `.env`:
```bash
cp .env.example .env
```
Open `.env` in your text editor and add your model configuration and keys:
```env
# Unified Model Adapter Configuration
PRIMARY_LLM_PROVIDER=openai  # options: openai, anthropic, gemini
GEMINI_API_KEY=AQ.Ab8RN6J7GNds4-r_5Qk85Y_wvHcNHV6ojK4BwgWTrUHa_6-OSA

# App Settings
ENVIRONMENT=development
PORT=8000
```

### Step 3: Setup & Run Backend (FastAPI)
```bash
cd backend
python -m venv venv

# Activate Virtual Environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Run Configuration Integrity Test
pytest tests/test_config_integrity.py -v

# Start FastAPI Server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Backend will run at `http://localhost:8000`.

### Step 4: Setup & Run Frontend (React)
Open a new terminal tab/window:
```bash
cd frontend
npm install
npm run dev
```
Frontend will run at `http://localhost:3000` or `http://localhost:5173`.

---

## ⚙️ How to Update GST Rates

> **Important:** GST rates, slabs, and item classifications are **never hardcoded** in Python or React code. All rates are strictly driven by JSON configurations.

To update or verify statutory GST rates:

1. **Locate the Configuration File**: Open [`config/gst_rates.json`](config/gst_rates.json).
2. **Edit JSON Only (No Code Modifications Required)**:
   - Identify the rate key you need to update (e.g., `rate_5_percent`, `rate_12_percent`, `rate_18_percent`, `rate_28_percent`, `rate_exempt`).
   - Change the `"percent"` string value to the new statutory rate (e.g., `"5.00"`).
   - Once verified against an official Gazette or CBIC circular, set `"verified": true`.
   - Update `"verified_notification_ref"` with the official circular number (e.g., `"CBIC Notification No. 06/2022-Central Tax (Rate)"`).
3. **Verify Configuration Integrity**: Run the automated configuration integrity test:
   ```bash
   python -m pytest tests/test_config_integrity.py -v
   ```
   The application will immediately use the updated rates on the next calculation without requiring any code rebuild or redeployment.

---

## 📏 12 Hard Rules Summary

1. **Config-Driven:** Never hardcode GST rates, item codes, shorthand, or units. Read `/config/*.json`.
2. **Zero Silent Guessing:** Unreadable value = `null` + red flag.
3. **Objective Confidence:** Computed via cross-model consensus and rule validation, never model self-confidence.
4. **Dual Pricing Modes:** Price includes GST (default) vs. Add GST on top.
5. **Shopkeeper Regimes:** Unregistered (simple bill), Composition (Bill of Supply), Regular (Tax Invoice).
6. **Strict Secrets:** Load keys via `.env` only.
7. **Ephemeral Storage:** Uploaded bill images are immediately purged post-processing unless opt-in is enabled.
8. **No Direct Portal Submissions:** Always display: *"Please confirm with your CA before filing."*
9. **Classical Enhancement Only:** OpenCV/Pillow denoising and deskewing only. No generative AI deblurring.
10. **Financial Precision:** All calculations use Python's `Decimal` type.
11. **Vernacular Accessibility:** Font size $\ge 16\text{px}$, tap targets $\ge 48\text{px}$, triple cues (color + icon + text).
12. **Unified Model Adapter:** All model calls pass through one unified interface configured in `.env`.

---

## ⚠️ Compliance Disclaimer

**Please confirm with your CA before filing.** BillBandhu is an assistive digitisation tool and does not replace professional tax advisory or direct government GST portal filings.
