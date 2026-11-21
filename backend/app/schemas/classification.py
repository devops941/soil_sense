from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ClassificationResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sample_id: int
    ph_class: Optional[str] = None
    n_class: Optional[str] = None
    p_class: Optional[str] = None
    k_class: Optional[str] = None
    fertility_class: Optional[str] = None
    overall_status: Optional[str] = None
    standard_used: Optional[str] = None
    classified_at: datetime
