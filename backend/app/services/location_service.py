from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateError, NotFoundError
from app.models.classification_result import ClassificationResult
from app.models.location import Location
from app.models.sample import SoilParameterValue, SoilSample
from app.models.parameter import ParameterDefinition
from app.repositories.location_repo import LocationRepository
from app.schemas.location import LocationCreate, LocationUpdate


def list_locations(db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[Location], int]:
    repo = LocationRepository(db)
    total = db.query(Location).count()
    items = repo.list(skip=skip, limit=limit)
    return items, total


def get_location(db: Session, location_id: int) -> Location:
    repo = LocationRepository(db)
    return repo.get_or_404(location_id)


def create_location(db: Session, loc_in: LocationCreate) -> Location:
    existing = db.query(Location).filter(Location.name == loc_in.name).first()
    if existing:
        raise DuplicateError(f"Location with name '{loc_in.name}' already exists.")
    loc = Location(**loc_in.model_dump())
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


def update_location(db: Session, location_id: int, loc_in: LocationUpdate) -> Location:
    repo = LocationRepository(db)
    loc = repo.get_or_404(location_id)
    update_data = loc_in.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] != loc.name:
        existing = db.query(Location).filter(Location.name == update_data["name"]).first()
        if existing:
            raise DuplicateError(f"Location with name '{update_data['name']}' already exists.")
    for field, value in update_data.items():
        setattr(loc, field, value)
    db.commit()
    db.refresh(loc)
    return loc


def delete_location(db: Session, location_id: int) -> None:
    repo = LocationRepository(db)
    loc = repo.get_or_404(location_id)
    db.delete(loc)
    db.commit()


def location_stats(db: Session, location_id: int) -> Dict[str, Any]:
    # Verify location exists
    repo = LocationRepository(db)
    repo.get_or_404(location_id)

    sample_count = (
        db.query(SoilSample)
        .filter(SoilSample.location_id == location_id, SoilSample.is_deleted == False)  # noqa: E712
        .count()
    )

    # Get parameter def ids
    def _param_avg(code: str) -> Optional[float]:
        param_def = db.query(ParameterDefinition).filter(ParameterDefinition.code == code).first()
        if param_def is None:
            return None
        result = (
            db.query(func.avg(SoilParameterValue.value))
            .join(SoilSample, SoilParameterValue.sample_id == SoilSample.id)
            .filter(
                SoilSample.location_id == location_id,
                SoilSample.is_deleted == False,  # noqa: E712
                SoilParameterValue.parameter_def_id == param_def.id,
            )
            .scalar()
        )
        return round(float(result), 4) if result is not None else None

    avg_ph = _param_avg("ph")
    avg_n = _param_avg("nitrogen")
    avg_p = _param_avg("phosphorus")
    avg_k = _param_avg("potassium")

    # Fertility distribution: count overall_status values
    classified_samples = (
        db.query(ClassificationResult.overall_status)
        .join(SoilSample, ClassificationResult.sample_id == SoilSample.id)
        .filter(
            SoilSample.location_id == location_id,
            SoilSample.is_deleted == False,  # noqa: E712
        )
        .all()
    )
    fertility_dist: Dict[str, int] = {}
    for (status,) in classified_samples:
        if status:
            fertility_dist[status] = fertility_dist.get(status, 0) + 1

    return {
        "location_id": location_id,
        "sample_count": sample_count,
        "avg_ph": avg_ph,
        "avg_n": avg_n,
        "avg_p": avg_p,
        "avg_k": avg_k,
        "fertility_distribution": fertility_dist,
    }
