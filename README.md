# SoilSense — Soil Nutrient Intelligence & Fertility Classification System

**Geographical Scope:** Madurai District, Tamil Nadu, India ONLY  
**Agronomic Standards:** TNAU Agritech Soil Rating Chart (Tamil Nadu Agricultural University, default) & ICAR Soil Health Card (SHC) Scheme  
**Analytical Standard:** Rammoorthy & Bajaj (1969) / Parker Nutrient Index (NI)

---

> **Disclaimer:** SoilSense is intended for **educational and soil-test advisory purposes only**. It is not a substitute for accredited laboratory analysis or official government soil-health recommendations. Always consult a certified agronomist or the nearest Krishi Vigyan Kendra (KVK) at the Agricultural College & Research Institute, Madurai, before making fertilizer decisions.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend API** | FastAPI, Pydantic v2, SQLAlchemy 2.0 |
| **Data Analytics** | Pandas 2.2, NumPy 1.26, SciPy 1.13 |
| **Agronomic Reports** | ReportLab 4.2 (Individual Soil Health Card & District Summary PDFs) |
| **Interactive Frontend** | React 18, Vite 5, Plotly.js 2.35, Lucide Icons |
| **Database** | SQLite 3 |
| **Testing** | Pytest 9.2 (100% pass rate across 17 unit & integration tests) |

---

## Monorepo Layout

```
Soil_sense/
├── backend/                  # FastAPI application, database, and classification engine
│   ├── app/
│   │   ├── api/v1/           # REST endpoints (dashboard, samples, uploads, analysis, reports, exports)
│   │   ├── core/             # Database session, config, Madurai geography, seed loader
│   │   ├── models/           # SQLAlchemy models (SoilSample, Location, ParameterValue, Classification)
│   │   ├── repositories/     # Database repository patterns
│   │   ├── schemas/          # Pydantic validation schemas
│   │   ├── services/         # Business logic (analysis_engine, classification, dashboard, reports, uploads)
│   │   └── main.py           # FastAPI entrypoint (serves API & mounts built frontend SPA)
│   ├── config/
│   │   └── default_thresholds.json # Sourced thresholds (TNAU & SHC)
│   ├── data/
│   │   ├── demo/             # Synthetic demonstration records
│   │   ├── templates/        # CSV upload template
│   │   └── soilsense.db      # SQLite database
│   ├── tests/                # Automated pytest suite (17 tests)
│   └── requirements.txt
├── frontend/                 # React SPA (Vite + Plotly)
│   ├── src/
│   │   ├── components/       # Navbar, Sidebar, PlotlyChart wrapper
│   │   ├── constants/        # Madurai blocks & testing methods
│   │   ├── services/         # Centralized API client
│   │   ├── views/            # Dashboard, Samples, ManualEntry, Upload, Analytics, Reports, Thresholds
│   │   ├── App.jsx           # Tab router and global filter state
│   │   ├── main.jsx          # React DOM entry
│   │   └── index.css         # Modern light theme (white & blue palette)
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## Data Integrity & Madurai Restriction

- **Strict Geographical Verification:** SoilSense exclusively accepts records from **Madurai District, Tamil Nadu**. CSV ingestion and manual sample entry reject any records from non-Madurai districts with clear descriptive errors.
- **Official Taluks & Blocks Supported:** Madurai East, Madurai West, Melur, Vadipatti, Usilampatti, Thirumangalam, Thirupparankundram, Peraiyur, Sedapatti, Kottampatti, Alanganallur, Chellampatti, T.Kallupatti.
- **Verified vs. Demonstration Data:** All demonstration records in `backend/data/demo/` are tagged `data_source=demo` and explicitly marked as **SYNTHETIC**. Real field and laboratory records are tagged `data_source=verified`.
- **Classification Engine:**
  - **pH Reaction:** 9-tier system (Extremely Acidic to Very Strongly Alkaline) from IARI Soil Survey Manual (1970).
  - **Available Macronutrients:** Critical levels for Nitrogen (Alkaline KMnO4), Phosphorus (Olsen NaHCO3), and Potassium (Ammonium Acetate) under TNAU and SHC standards.
  - **Overall Sample Fertility:** Evaluated as **Low**, **Medium**, or **High** using composite nutrient scores.
  - **Nutrient Index (NI):** Evaluated according to Rammoorthy & Bajaj (1969) (<1.67 Low, 1.67–2.33 Medium, >2.33 High).

---

## Execution Instructions

### 1. Run the Backend API

```bash
cd backend
# Activate Python virtual environment
.venv\Scripts\activate      # On Windows
# source .venv/bin/activate  # On macOS / Linux

# Start the FastAPI server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- API Base URL: `http://127.0.0.1:8000`
- Swagger Interactive Docs: `http://127.0.0.1:8000/docs`
- Built Frontend SPA (direct via FastAPI): `http://127.0.0.1:8000/`

### 2. Run the Frontend (Development Server with Hot Reload)

```bash
cd frontend
npm start
```

- Web Application URL: `http://localhost:3000` (auto-proxies `/api` to port 8000)

### 3. Run the Automated Test Suite

```bash
cd backend
.venv\Scripts\pytest.exe -v
```

All 17 tests pass with 100% success rate across classification, Madurai restriction, upload ingestion, dashboard KPIs, and PDF report generation.
