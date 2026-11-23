from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.classification import ClassificationResultRead
from app.schemas.location import LocationRead


class ParameterValueIn(BaseModel):
    parameter_code: str
    value: float
    unit: str
    test_method: str

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: float, info: object) -> float:
        # Access values already validated via model_fields_set trick
        return v

    @field_validator("value", mode="after")
    @classmethod
    def validate_range(cls, v: float) -> float:
        # Generic non-negative guard for nutrients; ph validated at model level
        return v


class ParameterValueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    parameter_code: str
    display_name: str
    value: float
    unit: str
    test_method: str
    is_flagged: bool
    flag_reason: Optional[str] = None


class SampleCreate(BaseModel):
    sample_code: str
    location_id: Optional[int] = None
    location_name: Optional[str] = None
    district: str = "Madurai"
    taluk_block: Optional[str] = None
    village: Optional[str] = None
    sample_date: date
    depth_cm: Optional[float] = None
    land_use: Optional[str] = None
    collector_name: Optional[str] = None
    notes: Optional[str] = None
    data_source: str = "verified"
    parameters: List[ParameterValueIn]

    @field_validator("district")
    @classmethod
    def validate_district(cls, v: str) -> str:
        if not v or v.strip().lower() != "madurai":
            raise ValueError(
                f"SoilSense is strictly restricted to Madurai District, Tamil Nadu only. Provided district: '{v}'."
            )
        return "Madurai"

    @field_validator("parameters")
    @classmethod
    def validate_parameters(cls, params: List[ParameterValueIn]) -> List[ParameterValueIn]:
        for param in params:
            if param.parameter_code == "ph":
                if not (0.0 <= param.value <= 14.0):
                    raise ValueError(
                        f"pH value {param.value} is out of range [0, 14]."
                    )
            else:
                if param.value < 0:
                    raise ValueError(
                        f"Nutrient value for '{param.parameter_code}' must be >= 0."
                    )
        return params


class SampleUpdate(BaseModel):
    sample_code: Optional[str] = None
    location_id: Optional[int] = None
    location_name: Optional[str] = None
    district: Optional[str] = "Madurai"
    taluk_block: Optional[str] = None
    village: Optional[str] = None
    sample_date: Optional[date] = None
    depth_cm: Optional[float] = None
    land_use: Optional[str] = None
    collector_name: Optional[str] = None
    notes: Optional[str] = None
    data_source: Optional[str] = None
    parameters: Optional[List[ParameterValueIn]] = None

    @field_validator("parameters")
    @classmethod
    def validate_parameters(cls, params: Optional[List[ParameterValueIn]]) -> Optional[List[ParameterValueIn]]:
        if params is None:
            return None
        for param in params:
            if param.parameter_code == "ph":
                if not (0.0 <= param.value <= 14.0):
                    raise ValueError(f"pH value {param.value} is out of range [0, 14].")
            else:
                if param.value < 0:
                    raise ValueError(f"Nutrient value for '{param.parameter_code}' must be >= 0.")
        return params


class SampleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sample_code: str
    location: Optional[LocationRead] = None
    sample_date: date
    depth_cm: Optional[float] = None
    land_use: Optional[str] = None
    collector_name: Optional[str] = None
    notes: Optional[str] = None
    data_source: str
    parameter_values: List[ParameterValueRead] = []
    classification: Optional[ClassificationResultRead] = None
    created_at: datetime
    updated_at: datetime
