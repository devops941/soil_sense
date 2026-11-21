from __future__ import annotations

import json
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator


class ParameterDefinitionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    display_name: str
    default_unit: str
    common_methods: List[str]
    value_min: Optional[float] = None
    value_max: Optional[float] = None
    description: Optional[str] = None

    @field_validator("common_methods", mode="before")
    @classmethod
    def parse_methods(cls, v: object) -> object:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, ValueError):
                return [v]
        return v
