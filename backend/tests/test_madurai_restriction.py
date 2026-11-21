from __future__ import annotations

import pytest
from app.core.madurai_geography import is_valid_madurai_district
from app.services.validation_service import validate_dataframe
import pandas as pd


def test_madurai_district_helper():
    assert is_valid_madurai_district("Madurai") is True
    assert is_valid_madurai_district("madurai") is True
    assert is_valid_madurai_district(" MADURAI ") is True
    assert is_valid_madurai_district("Coimbatore") is False
    assert is_valid_madurai_district("Dindigul") is False
    assert is_valid_madurai_district("") is False
    assert is_valid_madurai_district(None) is False


def test_manual_sample_creation_rejects_non_madurai(client):
    payload = {
        "sample_code": "TEST-REJECT-001",
        "location_name": "Pollachi",
        "district": "Coimbatore",
        "sample_date": "2024-05-10",
        "parameters": [
            {"parameter_code": "ph", "value": 7.2, "unit": "pH", "test_method": "electrometric"},
            {"parameter_code": "nitrogen", "value": 250, "unit": "kg/ha", "test_method": "Alkaline KMnO4"},
            {"parameter_code": "phosphorus", "value": 15, "unit": "kg/ha", "test_method": "Olsen"},
            {"parameter_code": "potassium", "value": 200, "unit": "kg/ha", "test_method": "Ammonium Acetate"},
        ],
    }
    response = client.post("/api/v1/samples", json=payload)
    assert response.status_code == 422
    assert "Madurai" in response.text


def test_manual_sample_creation_accepts_madurai(client):
    import uuid
    code = f"MDU-VERIF-{uuid.uuid4().hex[:6].upper()}"
    payload = {
        "sample_code": code,
        "location_name": "Melur North",
        "district": "Madurai",
        "taluk_block": "Melur",
        "sample_date": "2024-05-15",
        "land_use": "Agricultural (Paddy)",
        "collector_name": "A. Ramanathan",
        "parameters": [
            {"parameter_code": "ph", "value": 7.5, "unit": "pH", "test_method": "electrometric"},
            {"parameter_code": "nitrogen", "value": 310, "unit": "kg/ha", "test_method": "Alkaline KMnO4"},
            {"parameter_code": "phosphorus", "value": 16, "unit": "kg/ha", "test_method": "Olsen"},
            {"parameter_code": "potassium", "value": 220, "unit": "kg/ha", "test_method": "Ammonium Acetate"},
        ],
    }
    response = client.post("/api/v1/samples", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["sample_code"] == code
    assert data["classification"] is not None
    assert data["classification"]["fertility_class"] in ["Low", "Medium", "High"]


def test_csv_validation_rejects_outside_district():
    df = pd.DataFrame([
        {
            "sample_code": "CSV-FAIL-01",
            "location_name": "Theni Town",
            "district": "Theni",
            "sample_date": "2024-03-01",
            "depth_cm": "0-20",
            "land_use": "Agricultural",
            "collector_name": "Tester",
            "ph": 7.0,
            "ph_method": "1:2.5 electrometric",
            "nitrogen_kg_ha": 250,
            "nitrogen_method": "Alkaline KMnO4",
            "phosphorus_kg_ha": 15,
            "phosphorus_method": "Olsen",
            "potassium_kg_ha": 200,
            "potassium_method": "Ammonium Acetate",
        }
    ])
    report = validate_dataframe(df)
    assert report.valid_rows == 0
    assert report.error_rows == 1
    assert any("Madurai District, Tamil Nadu only" in err.message for err in report.errors)
