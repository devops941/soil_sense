from __future__ import annotations

import json
import os
import uuid as uuid_lib
from datetime import date
from typing import List, Optional, Tuple

import pandas as pd
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ValidationError as SoilValidationError
from app.models.parameter import ParameterDefinition
from app.models.sample import SoilSample
from app.models.upload_batch import UploadBatch
from app.repositories.upload_repo import UploadRepository
from app.schemas.sample import ParameterValueIn, SampleCreate
from app.schemas.upload import UploadBatchRead, ValidationReport
from app.services import classification_service, validation_service
from app.services.sample_service import create_sample

_CSV_COL_TO_PARAM: dict = {
    "ph": "ph",
    "nitrogen_kg_ha": "nitrogen",
    "phosphorus_kg_ha": "phosphorus",
    "potassium_kg_ha": "potassium",
}

_CSV_COL_TO_METHOD: dict = {
    "ph": "ph_method",
    "nitrogen_kg_ha": "nitrogen_method",
    "phosphorus_kg_ha": "phosphorus_method",
    "potassium_kg_ha": "potassium_method",
}

_PARAM_DEFAULT_UNIT: dict = {
    "ph": "pH units",
    "nitrogen": "kg/ha",
    "phosphorus": "kg/ha",
    "potassium": "kg/ha",
}


def _get_param_bounds(db: Session) -> dict:
    bounds = {}
    for param_def in db.query(ParameterDefinition).all():
        bounds[param_def.code] = (param_def.value_min, param_def.value_max)
    return bounds


def _row_to_sample_create(row: pd.Series, data_source: str, batch_id: int, location_name_override: Optional[str] = None) -> Optional[SampleCreate]:
    try:
        sample_code = str(row["sample_code"]).strip()
        loc_name = location_name_override or (str(row["location_name"]).strip() if "location_name" in row and pd.notna(row["location_name"]) else None)
        sample_date_raw = row.get("sample_date")
        sample_date = pd.to_datetime(str(sample_date_raw)).date()

        depth_cm = None
        if "depth_cm" in row and pd.notna(row["depth_cm"]):
            try:
                depth_cm = float(row["depth_cm"])
            except (ValueError, TypeError):
                depth_cm = None

        land_use = str(row["land_use"]).strip() if "land_use" in row and pd.notna(row["land_use"]) else None
        collector_name = str(row["collector_name"]).strip() if "collector_name" in row and pd.notna(row["collector_name"]) else None
        notes = str(row["notes"]).strip() if "notes" in row and pd.notna(row["notes"]) else None

        district = str(row.get("district", "Madurai")).strip()
        taluk_block = str(row["taluk_block"]).strip() if "taluk_block" in row and pd.notna(row["taluk_block"]) else None
        village = str(row["village"]).strip() if "village" in row and pd.notna(row["village"]) else None

        parameters: List[ParameterValueIn] = []
        for csv_col, param_code in _CSV_COL_TO_PARAM.items():
            if csv_col not in row or pd.isna(row[csv_col]):
                continue
            try:
                val = float(row[csv_col])
            except (ValueError, TypeError):
                continue

            method_col = _CSV_COL_TO_METHOD.get(csv_col, "")
            method = "standard"
            if method_col and method_col in row and pd.notna(row[method_col]):
                method = str(row[method_col]).strip()

            unit = _PARAM_DEFAULT_UNIT.get(param_code, "kg/ha")
            parameters.append(
                ParameterValueIn(
                    parameter_code=param_code,
                    value=val,
                    unit=unit,
                    test_method=method,
                )
            )

        if not parameters:
            return None

        return SampleCreate(
            sample_code=sample_code,
            location_name=loc_name,
            district=district,
            taluk_block=taluk_block,
            village=village,
            sample_date=sample_date,
            depth_cm=depth_cm,
            land_use=land_use,
            collector_name=collector_name,
            notes=notes,
            data_source=data_source,
            parameters=parameters,
        )
    except Exception:
        return None


def ingest_csv(
    db: Session,
    file_bytes: bytes,
    filename: str,
    data_source: str = "verified",
    location_name: Optional[str] = None,
) -> Tuple[UploadBatch, ValidationReport]:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    batch_uuid = str(uuid_lib.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{batch_uuid}.csv")

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    try:
        df = pd.read_csv(file_path)
    except Exception as exc:
        # Unreadable CSV — clean up and raise
        os.remove(file_path)
        raise SoilValidationError(f"Could not parse CSV file: {exc}") from exc

    param_bounds = _get_param_bounds(db)
    report = validation_service.validate_dataframe(df, param_bounds=param_bounds)

    all_invalid = report.valid_rows == 0

    batch = UploadBatch(
        uuid=batch_uuid,
        original_filename=filename,
        file_path=file_path,
        total_rows=report.total_rows,
        valid_rows=report.valid_rows,
        error_rows=report.error_rows,
        status="failed" if all_invalid else "completed",
        validation_report=report.model_dump_json(),
        data_source=data_source,
    )
    db.add(batch)
    db.flush()

    if not all_invalid:
        clean_df, _ = validation_service.clean_dataframe(df)
        for _, row in clean_df.iterrows():
            sample_create = _row_to_sample_create(row, data_source, batch.id, location_name)
            if sample_create is None:
                continue
            try:
                with db.begin_nested():
                    # Check duplicate sample_code
                    existing = db.query(SoilSample).filter(
                        SoilSample.sample_code == sample_create.sample_code
                    ).first()
                    if existing:
                        continue

                    sample = SoilSample(
                        sample_code=sample_create.sample_code,
                        location_id=None,
                        sample_date=sample_create.sample_date,
                        depth_cm=sample_create.depth_cm,
                        land_use=sample_create.land_use,
                        collector_name=sample_create.collector_name,
                        notes=sample_create.notes,
                        data_source=data_source,
                        batch_id=batch.id,
                    )
                    # Resolve location
                    if sample_create.location_name:
                        from app.repositories.location_repo import LocationRepository
                        loc_repo = LocationRepository(db)
                        loc = loc_repo.get_or_create(
                            name=sample_create.location_name,
                            district=sample_create.district or "Madurai",
                            taluk_block=sample_create.taluk_block,
                            village=sample_create.village,
                        )
                        sample.location_id = loc.id

                    db.add(sample)
                    db.flush()

                    from app.services.sample_service import _build_parameter_values
                    _build_parameter_values(db, sample, sample_create.parameters)
                    db.flush()

                    classification_service.classify_and_store(db, sample)
            except Exception:
                continue

    db.commit()
    db.refresh(batch)
    return batch, report


def list_batches(
    db: Session,
    skip: int = 0,
    limit: int = 50,
) -> List[UploadBatch]:
    return db.query(UploadBatch).order_by(UploadBatch.created_at.desc()).offset(skip).limit(limit).all()


def get_batch(db: Session, batch_uuid: str) -> Optional[UploadBatch]:
    repo = UploadRepository(db)
    return repo.get_by_uuid(batch_uuid)


def delete_batch(db: Session, batch_uuid: str) -> bool:
    repo = UploadRepository(db)
    batch = repo.get_by_uuid(batch_uuid)
    if batch is None:
        return False
    # Cascade: soft-delete associated samples
    for sample in batch.samples:
        sample.is_deleted = True
    db.delete(batch)
    db.commit()
    return True
