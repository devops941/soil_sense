# backend/data — Data Folder Guide

## Folder Structure

```
backend/data/
├── demo/
│   └── madurai_demo_samples.csv   # Synthetic demonstration records (see warning below)
├── templates/
│   └── soil_sample_upload_template.csv  # CSV upload format reference with example rows
├── uploads/                        # Runtime: user-uploaded CSVs (git-ignored, .gitkeep tracks dir)
│   └── .gitkeep
└── soilsense.db                    # Runtime: SQLite database (git-ignored, created on first run)
```

## Demo Data Warning

`demo/madurai_demo_samples.csv` contains **SYNTHETIC** records generated for development and demonstration purposes.

- Every row carries `notes` containing "DEMO (synthetic)".
- When loaded into the database these records are tagged `data_source=demo`.
- They **must never** be cited as real Madurai soil-testing results, used in agronomic recommendations, or presented as measured laboratory data.

## Real / Verified Data

Data entered manually through the app UI or uploaded via CSV is tagged `data_source=verified` in the database. Only verified data should be used for advisory outputs.

## Official Data Sources

No bulk, district-level Madurai soil dataset is publicly downloadable from government portals. For real soil data, refer to:

- **Soil Health Card portal** — https://soilhealth.dac.gov.in  
  Individual farm-level Soil Health Cards issued by state governments under the GoI scheme.
- **TNAU Agritech portal** — https://agritech.tnau.ac.in  
  Soil rating charts, testing guidelines, and crop-wise fertilizer recommendations for Tamil Nadu.

Contact the nearest Krishi Vigyan Kendra (KVK) or the Tamil Nadu Department of Agriculture for district soil survey reports.
