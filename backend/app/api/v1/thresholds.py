from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.parameter import ParameterDefinition
from app.repositories.threshold_repo import ThresholdRepository
from app.schemas.threshold import ThresholdCreate, ThresholdRead, ThresholdUpdate

router = APIRouter(prefix="/thresholds", tags=["thresholds"])


def _to_read(threshold, db: Session) -> ThresholdRead:
    param_def = db.get(ParameterDefinition, threshold.parameter_def_id)
    param_code = param_def.code if param_def else ""
    data = {
        "id": threshold.id,
        "parameter_def_id": threshold.parameter_def_id,
        "parameter_code": param_code,
        "standard": threshold.standard,
        "class_label": threshold.class_label,
        "lower_bound": threshold.lower_bound,
        "upper_bound": threshold.upper_bound,
        "lower_inclusive": threshold.lower_inclusive,
        "upper_inclusive": threshold.upper_inclusive,
        "unit": threshold.unit,
        "recommendation": threshold.recommendation,
        "sort_order": threshold.sort_order,
        "status": threshold.status,
        "version": threshold.version,
        "effective_from": threshold.effective_from,
        "effective_to": threshold.effective_to,
        "notes": threshold.notes,
        "created_at": threshold.created_at,
        "updated_at": threshold.updated_at,
    }
    return ThresholdRead(**data)


@router.get("/active", response_model=List[ThresholdRead], summary="List active thresholds for the active standard")
def list_active(
    db: Session = Depends(get_db),
) -> List[ThresholdRead]:
    repo = ThresholdRepository(db)
    items = repo.list(standard=settings.ACTIVE_STANDARD, status="active")
    return [_to_read(t, db) for t in items]


@router.get("", response_model=List[ThresholdRead], summary="List thresholds with optional filters")
def list_thresholds(
    standard: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    parameter_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> List[ThresholdRead]:
    repo = ThresholdRepository(db)
    items = repo.list(standard=standard, status=status, parameter_code=parameter_code)
    return [_to_read(t, db) for t in items]


@router.post("", response_model=ThresholdRead, status_code=201, summary="Create a threshold")
def create_threshold(
    threshold_in: ThresholdCreate,
    db: Session = Depends(get_db),
) -> ThresholdRead:
    from app.models.threshold import ClassificationThreshold

    threshold = ClassificationThreshold(**threshold_in.model_dump())
    db.add(threshold)
    db.commit()
    db.refresh(threshold)
    return _to_read(threshold, db)


@router.put("/{threshold_id}", response_model=ThresholdRead, summary="Replace a threshold")
def replace_threshold(
    threshold_id: int,
    threshold_in: ThresholdUpdate,
    db: Session = Depends(get_db),
) -> ThresholdRead:
    repo = ThresholdRepository(db)
    threshold = repo.get_or_404(threshold_id)
    update_data = threshold_in.model_dump(exclude_unset=False)
    for field, value in update_data.items():
        if hasattr(threshold, field) and value is not None:
            setattr(threshold, field, value)
    db.commit()
    db.refresh(threshold)
    return _to_read(threshold, db)


@router.patch("/{threshold_id}/status", response_model=ThresholdRead, summary="Update threshold status")
def patch_threshold_status(
    threshold_id: int,
    new_status: str = Query(..., description="New status (active/inactive/archived)"),
    db: Session = Depends(get_db),
) -> ThresholdRead:
    repo = ThresholdRepository(db)
    threshold = repo.set_status(threshold_id, new_status)
    if threshold is None:
        raise NotFoundError(f"Threshold with id={threshold_id} not found.")
    db.commit()
    db.refresh(threshold)
    return _to_read(threshold, db)


@router.delete("/{threshold_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a threshold")
def delete_threshold(threshold_id: int, db: Session = Depends(get_db)) -> None:
    repo = ThresholdRepository(db)
    threshold = repo.get_or_404(threshold_id)
    db.delete(threshold)
    db.commit()
