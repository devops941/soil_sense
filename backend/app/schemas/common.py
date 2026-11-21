from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int


class ErrorDetail(BaseModel):
    row: Optional[int] = None
    column: Optional[str] = None
    message: str
