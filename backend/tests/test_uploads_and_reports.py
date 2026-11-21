from __future__ import annotations

import io
import pytest


def test_template_download(client):
    response = client.get("/api/v1/uploads/template")
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
    content = response.text
    assert "sample_code" in content
    assert "district" in content
    assert "Madurai" in content


def test_csv_export_samples(client):
    response = client.get("/api/v1/exports/samples.csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
    text = response.text
    assert "sample_code" in text
    assert "district" in text
    assert "fertility_class" in text


def test_pdf_report_sample(client):
    # Get first sample
    samples_res = client.get("/api/v1/samples?per_page=1")
    assert samples_res.status_code == 200
    samples_data = samples_res.json()["data"]
    if samples_data:
        sample_id = samples_data[0]["id"]
        pdf_res = client.get(f"/api/v1/reports/samples/{sample_id}/pdf")
        assert pdf_res.status_code == 200
        assert pdf_res.headers.get("content-type") == "application/pdf"
        assert len(pdf_res.content) > 1000
        # Verify PDF header magic bytes %PDF
        assert pdf_res.content[:4] == b"%PDF"


def test_pdf_report_dataset(client):
    pdf_res = client.get("/api/v1/reports/dataset/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers.get("content-type") == "application/pdf"
    assert len(pdf_res.content) > 1000
    assert pdf_res.content[:4] == b"%PDF"


def test_csv_upload_valid_madurai(client):
    csv_content = (
        "sample_code,location_name,district,sample_date,depth_cm,land_use,collector_name,ph,ph_method,nitrogen_kg_ha,nitrogen_method,phosphorus_kg_ha,phosphorus_method,potassium_kg_ha,potassium_method,notes\n"
        "MDU-TST-901,Melur,Madurai,2024-06-15,0-20,Agricultural,R. Kumar,7.2,1:2.5 electrometric,290,Alkaline KMnO4,18,Olsen,210,Ammonium Acetate,Automated Test\n"
    )
    files = {"file": ("test_upload.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = client.post("/api/v1/uploads", files=files, data={"data_source": "verified"})
    assert response.status_code == 201
    data = response.json()
    assert data["batch"]["valid_rows"] == 1
    assert data["batch"]["error_rows"] == 0
