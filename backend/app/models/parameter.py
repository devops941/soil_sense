from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.threshold import ClassificationThreshold


class ParameterDefinition(Base):
    __tablename__ = "parameter_definitions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    default_unit: Mapped[str] = mapped_column(String, nullable=False)
    common_methods: Mapped[str] = mapped_column(String, nullable=False)  # JSON array as text
    value_min: Mapped[Optional[float]] = mapped_column(nullable=True)
    value_max: Mapped[Optional[float]] = mapped_column(nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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

    thresholds: Mapped[List["ClassificationThreshold"]] = relationship(
        "ClassificationThreshold", back_populates="parameter_def"
    )
