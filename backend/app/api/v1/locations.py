from __future__ import annotations

import math
from typing import Any, Dict

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import PaginationMeta
from app.schemas.location import LocationCreate, LocationRead, LocationUpdate
from app.services import location_service

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", summary="List locations (paginated)")
def list_locations(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    skip = (page - 1) * per_page
    items, total = location_service.list_locations(db, skip=skip, limit=per_page)
    total_pages = max(1, math.ceil(total / per_page))
    return {
        "data": [LocationRead.model_validate(loc).model_dump() for loc in items],
        "meta": PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
        ).model_dump(),
    }


@router.post("", response_model=LocationRead, status_code=status.HTTP_201_CREATED, summary="Create a location")
def create_location(loc_in: LocationCreate, db: Session = Depends(get_db)) -> LocationRead:
    loc = location_service.create_location(db, loc_in)
    return LocationRead.model_validate(loc)


@router.get("/{location_id}", response_model=LocationRead, summary="Get a single location")
def get_location(location_id: int, db: Session = Depends(get_db)) -> LocationRead:
    loc = location_service.get_location(db, location_id)
    return LocationRead.model_validate(loc)


@router.put("/{location_id}", response_model=LocationRead, summary="Replace a location")
def replace_location(
    location_id: int,
    loc_in: LocationUpdate,
    db: Session = Depends(get_db),
) -> LocationRead:
    loc = location_service.update_location(db, location_id, loc_in)
    return LocationRead.model_validate(loc)


@router.patch("/{location_id}", response_model=LocationRead, summary="Partially update a location")
def patch_location(
    location_id: int,
    loc_in: LocationUpdate,
    db: Session = Depends(get_db),
) -> LocationRead:
    loc = location_service.update_location(db, location_id, loc_in)
    return LocationRead.model_validate(loc)


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a location")
def delete_location(location_id: int, db: Session = Depends(get_db)) -> None:
    location_service.delete_location(db, location_id)


@router.get("/{location_id}/stats", summary="Aggregate statistics for a location")
def location_stats(location_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    return location_service.location_stats(db, location_id)
