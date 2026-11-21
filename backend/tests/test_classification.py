from __future__ import annotations

import pytest
from app.services.classification_service import (
    classify_value,
    determine_fertility_class,
    nutrient_index,
    ThresholdRule,
)


def test_determine_fertility_class():
    # Low fertility cases (< 1.67)
    assert determine_fertility_class("low", "low", "low") == "Low"
    assert determine_fertility_class("low", "low", "medium") == "Low"  # (1+1+2)/3 = 1.33 < 1.67

    # Medium fertility cases (1.67 - 2.33)
    assert determine_fertility_class("low", "medium", "medium") == "Medium"  # (1+2+2)/3 = 1.67
    assert determine_fertility_class("medium", "medium", "medium") == "Medium"  # 2.0
    assert determine_fertility_class("low", "medium", "high") == "Medium"  # (1+2+3)/3 = 2.0

    # High fertility cases (> 2.33)
    assert determine_fertility_class("medium", "high", "high") == "High"  # (2+3+3)/3 = 2.67 > 2.33
    assert determine_fertility_class("high", "high", "high") == "High"  # 3.0


def test_nutrient_index_formula():
    # NI = (1*L + 2*M + 3*H) / Total
    # All low: NI = 1.0 -> "Low"
    ni, label = nutrient_index({"low": 10, "medium": 0, "high": 0})
    assert ni == 1.0
    assert label == "Low"

    # All medium: NI = 2.0 -> "Medium"
    ni, label = nutrient_index({"low": 0, "medium": 15, "high": 0})
    assert ni == 2.0
    assert label == "Medium"

    # All high: NI = 3.0 -> "High"
    ni, label = nutrient_index({"low": 0, "medium": 0, "high": 20})
    assert ni == 3.0
    assert label == "High"

    # Empty
    ni, label = nutrient_index({"low": 0, "medium": 0, "high": 0})
    assert ni == 0.0
    assert label == "N/A"


def test_classify_value_bounds():
    rules = [
        ThresholdRule("nitrogen", "low", None, 240.0, True, False, "kg/ha"),
        ThresholdRule("nitrogen", "medium", 240.0, 480.0, True, False, "kg/ha"),
        ThresholdRule("nitrogen", "high", 480.0, None, True, True, "kg/ha"),
    ]
    assert classify_value(100.0, rules) == "low"
    assert classify_value(239.9, rules) == "low"
    assert classify_value(240.0, rules) == "medium"
    assert classify_value(400.0, rules) == "medium"
    assert classify_value(480.0, rules) == "high"
    assert classify_value(650.0, rules) == "high"
