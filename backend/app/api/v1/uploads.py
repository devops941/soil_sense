from __future__ import annotations

import math
import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.schemas.common import PaginationMeta
from app.schemas.upload import UploadBatchRead, ValidationReport
from app.services import upload_service, validation_service

import pandas as pd

router = APIRouter(prefix="/uploads", tags=["uploads"])

_TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__),
    "../../../data/templates/soil_sample_upload_template.csv",
)


@router.get("/template", summary="Download the CSV upload template")
def get_template() -> FileResponse:
    path = os.path.abspath(_TEMPLATE_PATH)
    if not os.path.exists(path):
        raise NotFoundError("CSV template file not found.")
    return FileResponse(
        path=path,
        media_type="text/csv",
        filename="soil_sample_upload_template.csv",
    )


@router.post(
    "/validate",
    response_model=ValidationReport,
    summary="Validate a CSV file without persisting data",
)
async def validate_only(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ValidationReport:
    file_bytes = await file.read()
    try:
        import io
        df = pd.read_csv(io.BytesIO(file_bytes))
    except Exception as exc:
        from app.core.exceptions import ValidationError
        raise ValidationError(f"Could not parse CSV: {exc}") from exc

    from app.models.parameter import ParameterDefinition
    param_bounds = {
        p.code: (p.value_min, p.value_max)
        for p in db.query(ParameterDefinition).all()
    }
    return validation_service.validate_dataframe(df, param_bounds=param_bounds)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Upload and ingest a CSV file of soil samples",
)
async def upload_csv(
    file: UploadFile = File(...),
    data_source: str = Form("verified"),
    location_name: Optional[str] = Form(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    file_bytes = await file.read()
    batch, report, summary = upload_service.ingest_csv(
        db,
        file_bytes=file_bytes,
        filename=file.filename or "upload.csv",
        data_source=data_source,
        location_name=location_name,
    )
    return {
        "batch": UploadBatchRead.model_validate(batch).model_dump(),
        "validation_report": report.model_dump(),
        "summary": summary,
    }


@router.get("", summary="List all upload batches")
def list_batches(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    skip = (page - 1) * per_page
    items = upload_service.list_batches(db, skip=skip, limit=per_page)
    total = db.query(__import__("app.models.upload_batch", fromlist=["UploadBatch"]).UploadBatch).count()
    total_pages = max(1, math.ceil(total / per_page))
    return {
        "data": [UploadBatchRead.model_validate(b).model_dump() for b in items],
        "meta": PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
        ).model_dump(),
    }


@router.get("/{batch_uuid}", response_model=UploadBatchRead, summary="Get a single upload batch")
def get_batch(batch_uuid: str, db: Session = Depends(get_db)) -> UploadBatchRead:
    batch = upload_service.get_batch(db, batch_uuid)
    if batch is None:
        raise NotFoundError(f"Upload batch '{batch_uuid}' not found.")
    return UploadBatchRead.model_validate(batch)


@router.get("/{batch_uuid}/samples", summary="List samples belonging to a batch")
def get_batch_samples(
    batch_uuid: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    batch = upload_service.get_batch(db, batch_uuid)
    if batch is None:
        raise NotFoundError(f"Upload batch '{batch_uuid}' not found.")

    from app.models.sample import SoilSample
    from app.services.sample_service import to_read

    total = (
        db.query(SoilSample)
        .filter(SoilSample.batch_id == batch.id, SoilSample.is_deleted == False)  # noqa: E712
        .count()
    )
    skip = (page - 1) * per_page
    samples = (
        db.query(SoilSample)
        .filter(SoilSample.batch_id == batch.id, SoilSample.is_deleted == False)  # noqa: E712
        .offset(skip)
        .limit(per_page)
        .all()
    )
    total_pages = max(1, math.ceil(total / per_page))
    return {
        "data": [to_read(s).model_dump() for s in samples],
        "meta": PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
        ).model_dump(),
    }


@router.delete("/{batch_uuid}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a batch and its samples")
def delete_batch(batch_uuid: str, db: Session = Depends(get_db)) -> None:
    deleted = upload_service.delete_batch(db, batch_uuid)
    if not deleted:
        raise NotFoundError(f"Upload batch '{batch_uuid}' not found.")
