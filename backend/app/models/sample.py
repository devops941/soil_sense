from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.classification_result import ClassificationResult
    from app.models.location import Location
    from app.models.parameter import ParameterDefinition
    from app.models.upload_batch import UploadBatch


class SoilSample(Base):
    __tablename__ = "soil_samples"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sample_code: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    batch_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("upload_batches.id", ondelete="SET NULL"), nullable=True, index=True
    )
    sample_date: Mapped[date] = mapped_column(Date, nullable=False)
    depth_cm: Mapped[Optional[float]] = mapped_column(nullable=True)
    land_use: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    collector_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_source: Mapped[str] = mapped_column(String, default="verified", nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
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

    location: Mapped[Optional["Location"]] = relationship("Location", back_populates="samples")
    batch: Mapped[Optional["UploadBatch"]] = relationship("UploadBatch", back_populates="samples")
    parameter_values: Mapped[List["SoilParameterValue"]] = relationship(
        "SoilParameterValue", back_populates="sample", cascade="all, delete-orphan"
    )
    classification_result: Mapped[Optional["ClassificationResult"]] = relationship(
        "ClassificationResult",
        back_populates="sample",
        uselist=False,
        cascade="all, delete-orphan",
    )


class SoilParameterValue(Base):
    __tablename__ = "soil_parameter_values"

    __table_args__ = (UniqueConstraint("sample_id", "parameter_def_id", name="uq_sample_parameter"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sample_id: Mapped[int] = mapped_column(
        ForeignKey("soil_samples.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parameter_def_id: Mapped[int] = mapped_column(
        ForeignKey("parameter_definitions.id"), nullable=False, index=True
    )
    value: Mapped[float] = mapped_column(nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)
    test_method: Mapped[str] = mapped_column(String, nullable=False)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    flag_reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), server_default=func.now(), nullable=False
    )

    sample: Mapped["SoilSample"] = relationship("SoilSample", back_populates="parameter_values")
    parameter_def: Mapped["ParameterDefinition"] = relationship("ParameterDefinition")
