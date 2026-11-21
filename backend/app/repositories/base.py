from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar

from sqlalchemy.orm import Session

from app.core.database import Base
from app.core.exceptions import NotFoundError

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic SQLAlchemy repository providing common CRUD operations."""

    model: Type[ModelT]

    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, id: int) -> Optional[ModelT]:
        return self.db.get(self.model, id)

    def get_or_404(self, id: int) -> ModelT:
        obj = self.get(id)
        if obj is None:
            raise NotFoundError(f"{self.model.__name__} with id={id} not found.")
        return obj

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters: Any,
    ) -> List[ModelT]:
        query = self.db.query(self.model)
        for attr, value in filters.items():
            if value is not None and hasattr(self.model, attr):
                query = query.filter(getattr(self.model, attr) == value)
        return query.offset(skip).limit(limit).all()

    def create(self, obj_in: Dict[str, Any]) -> ModelT:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.flush()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelT, data: Dict[str, Any]) -> ModelT:
        for field, value in data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        self.db.flush()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: ModelT) -> None:
        self.db.delete(db_obj)
        self.db.flush()

    def count(self, **filters: Any) -> int:
        query = self.db.query(self.model)
        for attr, value in filters.items():
            if value is not None and hasattr(self.model, attr):
                query = query.filter(getattr(self.model, attr) == value)
        return query.count()
