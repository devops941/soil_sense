from __future__ import annotations

import pytest


def test_dashboard_summary_endpoint(client):
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_samples" in data
    assert "high_fertility_count" in data
    assert "medium_fertility_count" in data
    assert "low_fertility_count" in data
    assert "fertility_distribution" in data
    assert "nutrient_distribution" in data
    assert "ph_distribution" in data
    assert "location_wise_stats" in data
    assert "nutrient_indices" in data
    assert data["geographical_scope"] == "Madurai District, Tamil Nadu"


def test_fertility_distribution_endpoint(client):
    response = client.get("/api/v1/analysis/fertility-distribution")
    assert response.status_code == 200
    data = response.json()
    assert "fertility_distribution" in data
    assert "nutrient_distribution" in data
    assert "ph_distribution" in data


def test_analysis_summary_stats(client):
    response = client.get("/api/v1/analysis/summary-stats?data_source=all")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    codes = [item["parameter_code"] for item in data["data"]]
    assert "ph" in codes
    assert "nitrogen" in codes
    assert "phosphorus" in codes
    assert "potassium" in codes


def test_analysis_distribution(client):
    response = client.get("/api/v1/analysis/distribution?parameter=ph&bins=10&data_source=all")
    assert response.status_code == 200
    data = response.json()
    assert "bins" in data
    assert "counts" in data
    assert data["parameter_code"] == "ph"


def test_location_comparison(client):
    response = client.get("/api/v1/statistics/location-comparison?parameter_code=ph&data_source=all")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "location_name" in data[0]
        assert "mean" in data[0]
