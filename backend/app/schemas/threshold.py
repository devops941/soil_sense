from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ThresholdBase(BaseModel):
    standard: str
    class_label: str
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    lower_inclusive: bool = True
    upper_inclusive: bool = False
    unit: str
    recommendation: Optional[str] = None
    sort_order: int = 0
    status: str = "active"
    version: int = 1
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    notes: Optional[str] = None


class ThresholdCreate(ThresholdBase):
    parameter_def_id: int


class ThresholdUpdate(BaseModel):
    standard: Optional[str] = None
    class_label: Optional[str] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    lower_inclusive: Optional[bool] = None
    upper_inclusive: Optional[bool] = None
    unit: Optional[str] = None
    recommendation: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[str] = None
    version: Optional[int] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    notes: Optional[str] = None


class ThresholdRead(ThresholdBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parameter_def_id: int
    parameter_code: str
    created_at: datetime
    updated_at: datetime
