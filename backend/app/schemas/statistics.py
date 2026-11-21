from __future__ import annotations

from pydantic import BaseModel


class ParameterStat(BaseModel):
    parameter_code: str
    mean: float
    median: float
    std: float
    min: float
    max: float
    p25: float
    p75: float
    count: int


class NutrientIndex(BaseModel):
    parameter_code: str
    index_value: float
    class_label: str


class LocationComparisonItem(BaseModel):
    location_id: int
    location_name: str
    mean: float
    std: float
    count: int
