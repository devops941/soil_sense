from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.upload_batch import UploadBatch
from app.repositories.base import BaseRepository


class UploadRepository(BaseRepository[UploadBatch]):
    model = UploadBatch

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_uuid(self, uuid: str) -> Optional[UploadBatch]:
        return self.db.query(UploadBatch).filter(UploadBatch.uuid == uuid).first()
