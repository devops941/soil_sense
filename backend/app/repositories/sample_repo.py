from __future__ import annotations

from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from app.models.sample import SoilSample
from app.repositories.base import BaseRepository


class SampleRepository(BaseRepository[SoilSample]):
    model = SoilSample

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_filtered(
        self,
        page: int = 1,
        per_page: int = 20,
        location_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        data_source: Optional[str] = None,
        fertility_class: Optional[str] = None,
        search: Optional[str] = None,
        include_deleted: bool = False,
    ) -> Tuple[List[SoilSample], int]:
        from app.models.classification_result import ClassificationResult
        from app.models.location import Location
        from sqlalchemy import or_

        query = self.db.query(SoilSample)

        if not include_deleted:
            query = query.filter(SoilSample.is_deleted == False)  # noqa: E712

        if location_id is not None:
            query = query.filter(SoilSample.location_id == location_id)
        if date_from is not None:
            query = query.filter(SoilSample.sample_date >= date_from)
        if date_to is not None:
            query = query.filter(SoilSample.sample_date <= date_to)
        if data_source is not None:
            query = query.filter(SoilSample.data_source == data_source)
        if fertility_class is not None:
            query = query.join(
                ClassificationResult,
                ClassificationResult.sample_id == SoilSample.id,
            ).filter(
                or_(
                    ClassificationResult.fertility_class.ilike(fertility_class),
                    ClassificationResult.overall_status.ilike(f"%{fertility_class}%"),
                )
            )
        if search:
            search_term = f"%{search.strip()}%"
            query = query.outerjoin(Location, SoilSample.location_id == Location.id).filter(
                or_(
                    SoilSample.sample_code.ilike(search_term),
                    SoilSample.collector_name.ilike(search_term),
                    SoilSample.notes.ilike(search_term),
                    SoilSample.land_use.ilike(search_term),
                    Location.name.ilike(search_term),
                    Location.taluk_block.ilike(search_term),
                    Location.village.ilike(search_term),
                )
            )

        total = query.count()
        skip = (page - 1) * per_page
        items = (
            query.options(
                joinedload(SoilSample.location),
                joinedload(SoilSample.parameter_values),
                joinedload(SoilSample.classification_result),
            )
            .order_by(SoilSample.created_at.desc())
            .offset(skip)
            .limit(per_page)
            .all()
        )
        return items, total

    def get_with_values(self, id: int) -> Optional[SoilSample]:
        return (
            self.db.query(SoilSample)
            .options(
                joinedload(SoilSample.location),
                joinedload(SoilSample.parameter_values),
                joinedload(SoilSample.classification_result),
            )
            .filter(SoilSample.id == id, SoilSample.is_deleted == False)  # noqa: E712
            .first()
        )

    def soft_delete(self, id: int) -> Optional[SoilSample]:
        sample = self.get(id)
        if sample is None:
            return None
        sample.is_deleted = True
        self.db.flush()
        return sample
