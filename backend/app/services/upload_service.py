from __future__ import annotations

import json
import os
import uuid as uuid_lib
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ValidationError as SoilValidationError
from app.models.parameter import ParameterDefinition
from app.models.sample import SoilParameterValue, SoilSample
from app.models.upload_batch import UploadBatch
from app.repositories.upload_repo import UploadRepository
from app.schemas.sample import ParameterValueIn, SampleCreate
from app.schemas.upload import UploadBatchRead, ValidationIssue, ValidationReport
from app.services import classification_service, validation_service
from app.services.sample_service import _build_parameter_values, create_sample
from app.services.validation_service import normalize_dataframe_columns, parse_depth

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
    "ph": "pH",
    "nitrogen": "kg/ha",
    "phosphorus": "kg/ha",
    "potassium": "kg/ha",
}


def _get_param_bounds(db: Session) -> dict:
    bounds = {}
    for param_def in db.query(ParameterDefinition).all():
        bounds[param_def.code] = (param_def.value_min, param_def.value_max)
    return bounds


def _row_to_sample_create(
    row: pd.Series,
    data_source: str,
    batch_id: int,
    location_name_override: Optional[str] = None,
) -> Optional[SampleCreate]:
    try:
        sample_code = str(row.get("sample_code", "")).strip()
        if not sample_code:
            return None

        # Resolve location details
        loc_name = location_name_override
        if not loc_name and "location_name" in row and pd.notna(row["location_name"]):
            loc_name = str(row["location_name"]).strip()

        taluk_block = str(row["taluk_block"]).strip() if "taluk_block" in row and pd.notna(row["taluk_block"]) else None
        village = str(row["village"]).strip() if "village" in row and pd.notna(row["village"]) else None
        district = str(row.get("district", "Madurai")).strip() or "Madurai"

        if not loc_name:
            loc_name = taluk_block or village or "Melur"

        # Resolve date
        sample_date_raw = row.get("sample_date")
        if pd.notna(sample_date_raw) and str(sample_date_raw).strip():
            try:
                sample_date = pd.to_datetime(str(sample_date_raw)).date()
            except Exception:
                sample_date = date.today()
        else:
            sample_date = date.today()

        depth_cm = parse_depth(row.get("depth_cm"))
        if depth_cm is None:
            depth_cm = 20.0

        land_use = str(row["land_use"]).strip() if "land_use" in row and pd.notna(row["land_use"]) else "Agricultural"
        collector_name = str(row["collector_name"]).strip() if "collector_name" in row and pd.notna(row["collector_name"]) else "Field Officer"
        notes = str(row["notes"]).strip() if "notes" in row and pd.notna(row["notes"]) else None

        parameters: List[ParameterValueIn] = []
        for csv_col, param_code in _CSV_COL_TO_PARAM.items():
            if csv_col not in row or pd.isna(row[csv_col]):
                continue
            try:
                val = float(row[csv_col])
            except (ValueError, TypeError):
                continue

            method_col = _CSV_COL_TO_METHOD.get(csv_col, "")
            method = "Standard Laboratory Method"
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
) -> Tuple[UploadBatch, ValidationReport, Dict[str, int]]:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    batch_uuid = str(uuid_lib.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{batch_uuid}.csv")

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    try:
        df = pd.read_csv(file_path)
    except Exception as exc:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise SoilValidationError(f"Could not parse CSV file: {exc}") from exc

    df = normalize_dataframe_columns(df)
    param_bounds = _get_param_bounds(db)
    report = validation_service.validate_dataframe(df, param_bounds=param_bounds)

    successful_count = 0
    duplicate_count = 0
    failed_count = 0

    batch = UploadBatch(
        uuid=batch_uuid,
        original_filename=filename,
        file_path=file_path,
        total_rows=len(df),
        valid_rows=0,
        error_rows=report.error_rows,
        status="processing",
        validation_report=report.model_dump_json(),
        data_source=data_source,
    )
    db.add(batch)
    db.flush()

    if report.valid_rows > 0:
        clean_df, _ = validation_service.clean_dataframe(df, param_bounds=param_bounds)
        seen_batch_codes: set[str] = set()

        for idx, row in clean_df.iterrows():
            sample_create = _row_to_sample_create(row, data_source, batch.id, location_name)
            if sample_create is None:
                failed_count += 1
                continue

            # Check duplicate in current batch
            if sample_create.sample_code in seen_batch_codes:
                duplicate_count += 1
                report.warnings.append(
                    ValidationIssue(
                        row=int(idx) + 2,
                        column="sample_code",
                        message=f"Duplicate sample code '{sample_create.sample_code}' repeated in upload; skipped.",
                        severity="warning",
                    )
                )
                continue
            seen_batch_codes.add(sample_create.sample_code)

            try:
                with db.begin_nested():
                    # Resolve location
                    loc_id = None
                    if sample_create.location_name:
                        from app.repositories.location_repo import LocationRepository
                        loc_repo = LocationRepository(db)
                        loc = loc_repo.get_or_create(
                            name=sample_create.location_name,
                            district=sample_create.district or "Madurai",
                            taluk_block=sample_create.taluk_block,
                            village=sample_create.village,
                        )
                        loc_id = loc.id

                    # Check if sample exists in database: update if exists (prevents duplicate error)
                    existing = (
                        db.query(SoilSample)
                        .filter(SoilSample.sample_code == sample_create.sample_code)
                        .first()
                    )

                    if existing:
                        sample = existing
                        sample.location_id = loc_id or sample.location_id
                        sample.sample_date = sample_create.sample_date
                        sample.depth_cm = sample_create.depth_cm
                        sample.land_use = sample_create.land_use
                        sample.collector_name = sample_create.collector_name
                        sample.notes = sample_create.notes
                        sample.data_source = data_source
                        sample.batch_id = batch.id
                        sample.is_deleted = False

                        # Clear and update parameters
                        db.query(SoilParameterValue).filter(SoilParameterValue.sample_id == sample.id).delete()
                        db.flush()
                        _build_parameter_values(db, sample, sample_create.parameters)
                        db.flush()
                        classification_service.classify_and_store(db, sample)
                        successful_count += 1
                    else:
                        sample = SoilSample(
                            sample_code=sample_create.sample_code,
                            location_id=loc_id,
                            sample_date=sample_create.sample_date,
                            depth_cm=sample_create.depth_cm,
                            land_use=sample_create.land_use,
                            collector_name=sample_create.collector_name,
                            notes=sample_create.notes,
                            data_source=data_source,
                            batch_id=batch.id,
                        )
                        db.add(sample)
                        db.flush()

                        _build_parameter_values(db, sample, sample_create.parameters)
                        db.flush()

                        classification_service.classify_and_store(db, sample)
                        successful_count += 1
            except Exception as exc:
                failed_count += 1
                report.errors.append(
                    ValidationIssue(
                        row=int(idx) + 2,
                        column="database",
                        message=f"Database error saving '{sample_create.sample_code}': {exc}",
                        severity="error",
                    )
                )

    total_failed = report.error_rows + failed_count
    batch.valid_rows = successful_count
    batch.error_rows = total_failed
    batch.status = "completed" if successful_count > 0 else ("failed" if total_failed > 0 or len(df) == 0 else "completed")
    batch.validation_report = report.model_dump_json()

    db.commit()
    db.refresh(batch)

    summary = {
        "total_rows": len(df),
        "successful_records": successful_count,
        "duplicate_records": duplicate_count,
        "failed_records": total_failed,
    }

    return batch, report, summary


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
    for sample in batch.samples:
        sample.is_deleted = True
    db.delete(batch)
    db.commit()
    return True
