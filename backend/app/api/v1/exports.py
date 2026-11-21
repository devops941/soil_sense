from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import export_service

router = APIRouter(prefix="/exports", tags=["exports"])


@router.get(
    "/samples.csv",
    summary="Export soil samples as CSV",
    response_class=Response,
)
def export_samples_csv(
    data_source: Optional[str] = Query(None),
    location_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
) -> Response:
    csv_bytes = export_service.samples_to_csv(
        db,
        data_source=data_source,
        location_id=location_id,
        date_from=date_from,
        date_to=date_to,
    )
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=soil_samples.csv"},
    )


@router.get(
    "/classification-results.csv",
    summary="Export classification results as CSV",
    response_class=Response,
)
def export_classification_csv(
    data_source: Optional[str] = Query(None),
    location_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
) -> Response:
    csv_bytes = export_service.classification_to_csv(
        db,
        data_source=data_source,
        location_id=location_id,
    )
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=classification_results.csv"},
    )
