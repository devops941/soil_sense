from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.location import Location
from app.repositories.base import BaseRepository


class LocationRepository(BaseRepository[Location]):
    model = Location

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_name(self, name: str, district: Optional[str] = None) -> Optional[Location]:
        query = self.db.query(Location).filter(Location.name == name)
        if district is not None:
            query = query.filter(Location.district == district)
        return query.first()

    def get_or_create(
        self,
        name: str,
        district: Optional[str] = "Madurai",
        taluk_block: Optional[str] = None,
        village: Optional[str] = None,
    ) -> Location:
        effective_district = district or "Madurai"
        existing = self.get_by_name(name, effective_district)
        if existing:
            if taluk_block and not existing.taluk_block:
                existing.taluk_block = taluk_block
            if village and not existing.village:
                existing.village = village
            return existing
        new_loc = Location(
            name=name,
            district=effective_district,
            taluk_block=taluk_block,
            village=village,
        )
        self.db.add(new_loc)
        self.db.flush()
        self.db.refresh(new_loc)
        return new_loc
