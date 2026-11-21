from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.parameter import ParameterDefinition


class ClassificationThreshold(Base):
    __tablename__ = "classification_thresholds"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    parameter_def_id: Mapped[int] = mapped_column(
        ForeignKey("parameter_definitions.id"), nullable=False, index=True
    )
    standard: Mapped[str] = mapped_column(String, nullable=False, index=True)  # 'TNAU' or 'SHC'
    class_label: Mapped[str] = mapped_column(String, nullable=False)
    lower_bound: Mapped[Optional[float]] = mapped_column(nullable=True)
    upper_bound: Mapped[Optional[float]] = mapped_column(nullable=True)
    lower_inclusive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    upper_inclusive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)
    recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String, default="active", nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    parameter_def: Mapped["ParameterDefinition"] = relationship(
        "ParameterDefinition", back_populates="thresholds"
    )
