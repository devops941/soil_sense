from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", summary="Dashboard summary statistics")
def dashboard_summary(
    data_source: Optional[str] = Query(None, description="Filter: 'verified', 'demo', or None for all"),
    location_id: Optional[int] = Query(None, description="Filter by location ID"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    return dashboard_service.summary(db, data_source=data_source, location_id=location_id)
