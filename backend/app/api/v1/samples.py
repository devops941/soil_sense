from __future__ import annotations

import math
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import PaginationMeta
from app.schemas.sample import SampleCreate, SampleRead, SampleUpdate
from app.services import sample_service

router = APIRouter(prefix="/samples", tags=["samples"])


@router.get("", summary="List soil samples (paginated, filterable)")
def list_samples(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    location_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    data_source: Optional[str] = Query(None),
    fertility_class: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Search by sample code, location, or collector"),
    db: Session = Depends(get_db),
) -> dict:
    items, total = sample_service.list_samples(
        db,
        page=page,
        per_page=per_page,
        location_id=location_id,
        date_from=date_from,
        date_to=date_to,
        data_source=data_source,
        fertility_class=fertility_class,
        search=search,
    )
    total_pages = max(1, math.ceil(total / per_page))
    return {
        "data": [sample_service.to_read(s).model_dump() for s in items],
        "meta": PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
        ).model_dump(),
    }


@router.post("", response_model=SampleRead, status_code=status.HTTP_201_CREATED, summary="Create a soil sample")
def create_sample(
    sample_in: SampleCreate,
    db: Session = Depends(get_db),
) -> SampleRead:
    sample = sample_service.create_sample(db, sample_in)
    return sample_service.to_read(sample)


@router.get("/{sample_id}", response_model=SampleRead, summary="Get a single soil sample")
def get_sample(sample_id: int, db: Session = Depends(get_db)) -> SampleRead:
    sample = sample_service.get_sample(db, sample_id)
    return sample_service.to_read(sample)


@router.put("/{sample_id}", response_model=SampleRead, summary="Replace sample metadata")
def replace_sample(
    sample_id: int,
    sample_in: SampleUpdate,
    db: Session = Depends(get_db),
) -> SampleRead:
    sample = sample_service.update_sample(db, sample_id, sample_in)
    return sample_service.to_read(sample)


@router.patch("/{sample_id}", response_model=SampleRead, summary="Partially update sample metadata")
def patch_sample(
    sample_id: int,
    sample_in: SampleUpdate,
    db: Session = Depends(get_db),
) -> SampleRead:
    sample = sample_service.update_sample(db, sample_id, sample_in)
    return sample_service.to_read(sample)


@router.delete("/{sample_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Soft-delete a sample")
def delete_sample(sample_id: int, db: Session = Depends(get_db)) -> None:
    sample_service.delete_sample(db, sample_id)
