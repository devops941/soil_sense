from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateError, NotFoundError
from app.models.parameter import ParameterDefinition
from app.models.sample import SoilParameterValue, SoilSample
from app.repositories.location_repo import LocationRepository
from app.repositories.sample_repo import SampleRepository
from app.schemas.classification import ClassificationResultRead
from app.schemas.sample import ParameterValueRead, SampleCreate, SampleRead, SampleUpdate
from app.services import classification_service


def _resolve_or_create_location(
    db: Session,
    location_id: Optional[int],
    location_name: Optional[str],
    district: str = "Madurai",
    taluk_block: Optional[str] = None,
    village: Optional[str] = None,
) -> Optional[int]:
    if location_id is not None:
        return location_id
    if location_name:
        loc_repo = LocationRepository(db)
        loc = loc_repo.get_or_create(
            name=location_name,
            district=district,
            taluk_block=taluk_block,
            village=village,
        )
        return loc.id
    return None


def _build_parameter_values(
    db: Session,
    sample: SoilSample,
    parameters: List[Any],
) -> None:
    for param_in in parameters:
        param_def = (
            db.query(ParameterDefinition)
            .filter(ParameterDefinition.code == param_in.parameter_code)
            .first()
        )
        if param_def is None:
            continue
        pv = SoilParameterValue(
            sample_id=sample.id,
            parameter_def_id=param_def.id,
            value=param_in.value,
            unit=param_in.unit,
            test_method=param_in.test_method,
        )
        db.add(pv)


def to_read(sample: SoilSample) -> SampleRead:
    """Convert ORM SoilSample to SampleRead schema."""
    param_values: List[ParameterValueRead] = []
    for pv in sample.parameter_values or []:
        param_def = pv.parameter_def
        param_values.append(
            ParameterValueRead(
                parameter_code=param_def.code if param_def else "",
                display_name=param_def.display_name if param_def else "",
                value=pv.value,
                unit=pv.unit,
                test_method=pv.test_method,
                is_flagged=pv.is_flagged,
                flag_reason=pv.flag_reason,
            )
        )

    classification = None
    if sample.classification_result is not None:
        classification = ClassificationResultRead.model_validate(sample.classification_result)

    return SampleRead(
        id=sample.id,
        sample_code=sample.sample_code,
        location=sample.location,
        sample_date=sample.sample_date,
        depth_cm=sample.depth_cm,
        land_use=sample.land_use,
        collector_name=sample.collector_name,
        notes=sample.notes,
        data_source=sample.data_source,
        parameter_values=param_values,
        classification=classification,
        created_at=sample.created_at,
        updated_at=sample.updated_at,
    )


def create_sample(db: Session, sample_in: SampleCreate) -> SoilSample:
    repo = SampleRepository(db)

    # Check uniqueness
    existing = db.query(SoilSample).filter(SoilSample.sample_code == sample_in.sample_code).first()
    if existing:
        raise DuplicateError(f"Sample with code '{sample_in.sample_code}' already exists.")

    location_id = _resolve_or_create_location(
        db,
        sample_in.location_id,
        sample_in.location_name,
        district=sample_in.district,
        taluk_block=sample_in.taluk_block,
        village=sample_in.village,
    )

    sample = SoilSample(
        sample_code=sample_in.sample_code,
        location_id=location_id,
        sample_date=sample_in.sample_date,
        depth_cm=sample_in.depth_cm,
        land_use=sample_in.land_use,
        collector_name=sample_in.collector_name,
        notes=sample_in.notes,
        data_source=sample_in.data_source,
    )
    db.add(sample)
    db.flush()

    _build_parameter_values(db, sample, sample_in.parameters)
    db.flush()

    classification_service.classify_and_store(db, sample)
    db.commit()
    db.refresh(sample)
    return sample


def get_sample(db: Session, sample_id: int) -> SoilSample:
    repo = SampleRepository(db)
    sample = repo.get_with_values(sample_id)
    if sample is None:
        raise NotFoundError(f"SoilSample with id={sample_id} not found.")
    return sample


def update_sample(db: Session, sample_id: int, sample_in: SampleUpdate) -> SoilSample:
    repo = SampleRepository(db)
    sample = repo.get_or_404(sample_id)

    update_data = sample_in.model_dump(exclude_unset=True)

    if "sample_code" in update_data and update_data["sample_code"] != sample.sample_code:
        existing = (
            db.query(SoilSample)
            .filter(SoilSample.sample_code == update_data["sample_code"])
            .first()
        )
        if existing:
            raise DuplicateError(f"Sample with code '{update_data['sample_code']}' already exists.")

    for field, value in update_data.items():
        setattr(sample, field, value)

    db.commit()
    db.refresh(sample)
    return sample


def delete_sample(db: Session, sample_id: int) -> None:
    repo = SampleRepository(db)
    sample = repo.get_or_404(sample_id)
    sample.is_deleted = True
    db.commit()


def list_samples(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    location_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    data_source: Optional[str] = None,
    fertility_class: Optional[str] = None,
    search: Optional[str] = None,
) -> Tuple[List[SoilSample], int]:
    repo = SampleRepository(db)
    return repo.list_filtered(
        page=page,
        per_page=per_page,
        location_id=location_id,
        date_from=date_from,
        date_to=date_to,
        data_source=data_source,
        fertility_class=fertility_class,
        search=search,
    )
