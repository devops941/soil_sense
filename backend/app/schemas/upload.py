from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ValidationIssue(BaseModel):
    row: Optional[int] = None
    column: Optional[str] = None
    message: str
    severity: str  # 'error' or 'warning'


class ValidationReport(BaseModel):
    total_rows: int
    valid_rows: int
    error_rows: int
    errors: List[ValidationIssue] = []
    warnings: List[ValidationIssue] = []


class UploadBatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    original_filename: str
    total_rows: Optional[int] = None
    valid_rows: Optional[int] = None
    error_rows: Optional[int] = None
    status: str
    data_source: str
    created_at: datetime
