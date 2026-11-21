from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.statistics import LocationComparisonItem
from app.services import statistics_service

router = APIRouter(prefix="/statistics", tags=["statistics"])


class TTestRequest(BaseModel):
    parameter_code: str
    location_id_a: int
    location_id_b: int
    data_source: str = "verified"


@router.get(
    "/location-comparison",
    response_model=List[LocationComparisonItem],
    summary="Compare a parameter's mean/std across locations",
)
def location_comparison(
    parameter_code: str = Query("ph"),
    location_ids: Optional[str] = Query(None, description="Comma-separated location IDs"),
    data_source: str = Query("verified"),
    db: Session = Depends(get_db),
) -> List[LocationComparisonItem]:
    ids: Optional[List[int]] = None
    if location_ids:
        try:
            ids = [int(i.strip()) for i in location_ids.split(",") if i.strip()]
        except ValueError:
            ids = None
    return statistics_service.location_comparison(
        db,
        parameter_code=parameter_code,
        location_ids=ids,
        data_source=data_source,
    )


@router.post(
    "/ttest",
    summary="Welch's t-test between two locations for a parameter",
)
def ttest(body: TTestRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    return statistics_service.ttest_between_locations(
        db,
        parameter_code=body.parameter_code,
        location_id_a=body.location_id_a,
        location_id_b=body.location_id_b,
        data_source=body.data_source,
    )
