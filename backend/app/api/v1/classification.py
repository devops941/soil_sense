from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.classification_result import ClassificationResult
from app.models.sample import SoilSample
from app.schemas.classification import ClassificationResultRead
from app.schemas.statistics import NutrientIndex
from app.services import classification_service
from app.services.sample_service import get_sample

router = APIRouter(prefix="/classification", tags=["classification"])


@router.post(
    "/samples/{sample_id}",
    response_model=ClassificationResultRead,
    summary="Classify or reclassify a sample",
)
def classify_sample(
    sample_id: int,
    standard: Optional[str] = Query(None, description="Override classification standard"),
    db: Session = Depends(get_db),
) -> ClassificationResultRead:
    sample = get_sample(db, sample_id)
    result = classification_service.classify_and_store(db, sample, standard=standard)
    return ClassificationResultRead.model_validate(result)


@router.get(
    "/samples/{sample_id}",
    response_model=ClassificationResultRead,
    summary="Get classification result for a sample",
)
def get_classification(sample_id: int, db: Session = Depends(get_db)) -> ClassificationResultRead:
    result = (
        db.query(ClassificationResult)
        .filter(ClassificationResult.sample_id == sample_id)
        .first()
    )
    if result is None:
        raise NotFoundError(f"No classification result found for sample id={sample_id}.")
    return ClassificationResultRead.model_validate(result)


@router.post(
    "/batch",
    summary="Classify all unclassified samples (or by filter)",
)
def classify_batch(
    data_source: Optional[str] = Query(None),
    standard: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    effective_standard = standard or settings.ACTIVE_STANDARD

    query = db.query(SoilSample).filter(SoilSample.is_deleted == False)  # noqa: E712
    if data_source:
        query = query.filter(SoilSample.data_source == data_source)

    # Only samples without a classification result
    already_classified_ids = {
        row.sample_id for row in db.query(ClassificationResult.sample_id).all()
    }

    samples = [s for s in query.all() if s.id not in already_classified_ids]
    classified = 0
    errors = 0
    for sample in samples:
        try:
            classification_service.classify_and_store(db, sample, standard=effective_standard)
            classified += 1
        except Exception:
            errors += 1

    return {
        "classified": classified,
        "errors": errors,
        "standard": effective_standard,
    }


@router.get(
    "/summary",
    response_model=List[NutrientIndex],
    summary="Nutrient indices for N/P/K under the active standard",
)
def classification_summary(
    data_source: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> List[NutrientIndex]:
    query = (
        db.query(ClassificationResult)
        .join(SoilSample, ClassificationResult.sample_id == SoilSample.id)
        .filter(SoilSample.is_deleted == False)  # noqa: E712
    )
    if data_source:
        query = query.filter(SoilSample.data_source == data_source)

    results = query.all()
    samples_classes = [
        {"n_class": r.n_class, "p_class": r.p_class, "k_class": r.k_class}
        for r in results
    ]
    return classification_service.compute_nutrient_indices(samples_classes, settings.ACTIVE_STANDARD)
