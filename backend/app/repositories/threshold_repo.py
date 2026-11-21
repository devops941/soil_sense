from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.threshold import ClassificationThreshold
from app.repositories.base import BaseRepository


class ThresholdRepository(BaseRepository[ClassificationThreshold]):
    model = ClassificationThreshold

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list(  # type: ignore[override]
        self,
        standard: Optional[str] = None,
        status: Optional[str] = None,
        parameter_code: Optional[str] = None,
    ) -> List[ClassificationThreshold]:
        from app.models.parameter import ParameterDefinition

        query = self.db.query(ClassificationThreshold)

        if standard is not None:
            query = query.filter(ClassificationThreshold.standard == standard)
        if status is not None:
            query = query.filter(ClassificationThreshold.status == status)
        if parameter_code is not None:
            query = query.join(
                ParameterDefinition,
                ClassificationThreshold.parameter_def_id == ParameterDefinition.id,
            ).filter(ParameterDefinition.code == parameter_code)

        return query.order_by(
            ClassificationThreshold.standard,
            ClassificationThreshold.parameter_def_id,
            ClassificationThreshold.sort_order,
        ).all()

    def set_status(self, id: int, status: str) -> Optional[ClassificationThreshold]:
        threshold = self.get(id)
        if threshold is None:
            return None
        threshold.status = status
        self.db.flush()
        self.db.refresh(threshold)
        return threshold
