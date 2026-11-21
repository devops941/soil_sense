from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.sample import SoilSample
from app.services import report_service
from app.services.sample_service import get_sample

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get(
    "/samples/{sample_id}/pdf",
    summary="Download Individual Soil Health Card PDF Report",
    response_class=Response,
)
def download_sample_pdf(
    sample_id: int,
    db: Session = Depends(get_db),
) -> Response:
    sample = get_sample(db, sample_id)
    pdf_bytes = report_service.generate_sample_pdf(db, sample)
    filename = f"soilsense_sample_{sample.sample_code}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/dataset/pdf",
    summary="Download Madurai District Soil Analytics Summary PDF Report",
    response_class=Response,
)
def download_dataset_pdf(
    data_source: Optional[str] = Query(None, description="Filter: 'verified', 'demo', or None for all"),
    location_id: Optional[int] = Query(None, description="Filter by location ID"),
    db: Session = Depends(get_db),
) -> Response:
    pdf_bytes = report_service.generate_dataset_pdf(
        db, data_source=data_source, location_id=location_id
    )
    filename = "soilsense_madurai_dataset_report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/pdf",
    summary="Generate PDF report (Compatible endpoint)",
    response_class=Response,
)
def generate_pdf_report(
    sample_id: Optional[int] = Query(None),
    data_source: Optional[str] = Query(None),
    location_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
) -> Response:
    if sample_id is not None:
        sample = get_sample(db, sample_id)
        pdf_bytes = report_service.generate_sample_pdf(db, sample)
        filename = f"soilsense_sample_{sample.sample_code}.pdf"
    else:
        pdf_bytes = report_service.generate_dataset_pdf(
            db, data_source=data_source, location_id=location_id
        )
        filename = "soilsense_madurai_dataset_report.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
