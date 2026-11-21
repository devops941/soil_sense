from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.sample import SoilSample


class ClassificationResult(Base):
    __tablename__ = "classification_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sample_id: Mapped[int] = mapped_column(
        ForeignKey("soil_samples.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    ph_class: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    n_class: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    p_class: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    k_class: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    fertility_class: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    overall_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    standard_used: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    classified_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), server_default=func.now(), nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    sample: Mapped["SoilSample"] = relationship(
        "SoilSample", back_populates="classification_result"
    )
