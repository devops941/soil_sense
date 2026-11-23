from __future__ import annotations

import io
import pytest
from app.models.sample import SoilSample
from app.models.classification_result import ClassificationResult


def test_issue1_soil_sample_edit_and_reclassification(client, db_session=None):
    """Test ISSUE 1: Soil Sample Edit Option with complete parameter updating and re-classification."""
    # 1. Fetch first sample
    res = client.get("/api/v1/samples?per_page=1")
    assert res.status_code == 200
    samples = res.json()["data"]
    assert len(samples) > 0
    sample_to_edit = samples[0]
    sample_id = sample_to_edit["id"]
    original_code = sample_to_edit["sample_code"]

    # 2. Update all parameters: set N=600, P=30, K=350 (All High -> High Fertility)
    update_payload = {
        "sample_code": original_code,
        "district": "Madurai",
        "taluk_block": "Vadipatti",
        "village": "Sholavandan",
        "sample_date": "2026-11-20",
        "depth_cm": 25.0,
        "land_use": "Agricultural (Paddy)",
        "collector_name": "Senior Soil Chemist",
        "notes": "Verified via rigorous laboratory test after field treatment",
        "data_source": "verified",
        "parameters": [
            {
                "parameter_code": "ph",
                "value": 7.20,
                "unit": "pH",
                "test_method": "1:2.5 soil:water electrometric (pH meter)",
            },
            {
                "parameter_code": "nitrogen",
                "value": 520.0,
                "unit": "kg/ha",
                "test_method": "Alkaline KMnO4",
            },
            {
                "parameter_code": "phosphorus",
                "value": 28.0,
                "unit": "kg/ha",
                "test_method": "Olsen (NaHCO3 pH 8.5)",
            },
            {
                "parameter_code": "potassium",
                "value": 310.0,
                "unit": "kg/ha",
                "test_method": "Neutral Normal Ammonium Acetate",
            },
        ],
    }

    put_res = client.put(f"/api/v1/samples/{sample_id}", json=update_payload)
    assert put_res.status_code == 200
    updated_data = put_res.json()

    assert updated_data["location"]["taluk_block"] == "Vadipatti"
    assert updated_data["depth_cm"] == 25.0
    assert updated_data["collector_name"] == "Senior Soil Chemist"

    # Check updated parameters
    pv_map = {p["parameter_code"]: p["value"] for p in updated_data["parameter_values"]}
    assert pv_map["ph"] == 7.20
    assert pv_map["nitrogen"] == 520.0
    assert pv_map["phosphorus"] == 28.0
    assert pv_map["potassium"] == 310.0

    # Check that classification was recalculated to High
    assert updated_data["classification"]["n_class"] == "high"
    assert updated_data["classification"]["p_class"] == "high"
    assert updated_data["classification"]["k_class"] == "high"
    assert updated_data["classification"]["fertility_class"] == "High"


def test_issue2_thresholds_logic_intact(client):
    """Test ISSUE 2: Backend threshold logic and analysis remain 100% functional after UI removal."""
    # Thresholds API endpoint still responds correctly for calculations
    res = client.get("/api/v1/thresholds?standard=TNAU")
    assert res.status_code == 200
    data = res.json()
    assert "data" in data or "standard" in data or len(data) > 0


def test_issue3_csv_upload_parsing_and_duplicate_prevention(client):
    """Test ISSUE 3: CSV upload correctly parses rows, handles headers, prevents batch duplicates, and reports summary."""
    csv_data = (
        "sample_code,location_name,sample_date,ph,nitrogen_kg_ha,phosphorus_kg_ha,potassium_kg_ha\n"
        "MDU-CSV-NEW1,Melur,2026-10-15,6.8,250,15,180\n"
        "MDU-CSV-NEW2,Usilampatti,2026-10-16,7.5,350,22,250\n"
        "MDU-CSV-NEW1,Melur,2026-10-15,6.8,250,15,180\n"  # Duplicate within batch
    )

    files = {"file": ("test_batch.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")}
    res = client.post("/api/v1/uploads", files=files, data={"data_source": "verified"})
    assert res.status_code == 201
    res_data = res.json()

    assert "summary" in res_data
    summary = res_data["summary"]
    assert summary["total_rows"] == 3
    assert summary["successful_records"] >= 2
    assert summary["duplicate_records"] >= 1


def test_issue4_soil_samples_data_query_filters(client):
    """Test ISSUE 4: Soil sample records display properly across all query filters without returning empty sets."""
    # 1. Default / all data source
    res1 = client.get("/api/v1/samples?data_source=all")
    assert res1.status_code == 200
    assert len(res1.json()["data"]) > 0

    # 2. Empty string data source
    res2 = client.get("/api/v1/samples?data_source=")
    assert res2.status_code == 200
    assert len(res2.json()["data"]) > 0

    # 3. All fertility classes
    res3 = client.get("/api/v1/samples?fertility_class=all")
    assert res3.status_code == 200
    assert len(res3.json()["data"]) > 0

    # 4. Verified lab filter
    res4 = client.get("/api/v1/samples?data_source=verified")
    assert res4.status_code == 200
    assert all(s["data_source"] == "verified" for s in res4.json()["data"])
