from __future__ import annotations

import re
from datetime import date
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from app.core.madurai_geography import is_valid_madurai_district, TARGET_DISTRICT
from app.schemas.upload import ValidationIssue, ValidationReport

HEADER_ALIASES: Dict[str, str] = {
    "sample_code": "sample_code",
    "sample code": "sample_code",
    "samplecode": "sample_code",
    "sample_id": "sample_code",
    "sample id": "sample_code",
    "sampleid": "sample_code",
    "code": "sample_code",
    "id": "sample_code",
    "location_name": "location_name",
    "location name": "location_name",
    "location": "location_name",
    "place": "location_name",
    "taluk_block": "taluk_block",
    "taluk block": "taluk_block",
    "taluk": "taluk_block",
    "block": "taluk_block",
    "village": "village",
    "village_name": "village",
    "village name": "village",
    "district": "district",
    "district_name": "district",
    "sample_date": "sample_date",
    "sample date": "sample_date",
    "date": "sample_date",
    "sampling_date": "sample_date",
    "sampling date": "sample_date",
    "depth_cm": "depth_cm",
    "depth cm": "depth_cm",
    "depth": "depth_cm",
    "sampling_depth": "depth_cm",
    "land_use": "land_use",
    "land use": "land_use",
    "landuse": "land_use",
    "crop": "land_use",
    "crop_type": "land_use",
    "collector_name": "collector_name",
    "collector name": "collector_name",
    "collector": "collector_name",
    "officer": "collector_name",
    "notes": "notes",
    "note": "notes",
    "remarks": "notes",
    "ph": "ph",
    "soil_ph": "ph",
    "ph_val": "ph",
    "ph_value": "ph",
    "ph_method": "ph_method",
    "nitrogen_kg_ha": "nitrogen_kg_ha",
    "nitrogen (kg/ha)": "nitrogen_kg_ha",
    "nitrogen_kgha": "nitrogen_kg_ha",
    "nitrogen": "nitrogen_kg_ha",
    "available_nitrogen": "nitrogen_kg_ha",
    "available nitrogen": "nitrogen_kg_ha",
    "n_kg_ha": "nitrogen_kg_ha",
    "n (kg/ha)": "nitrogen_kg_ha",
    "n": "nitrogen_kg_ha",
    "nitrogen_method": "nitrogen_method",
    "phosphorus_kg_ha": "phosphorus_kg_ha",
    "phosphorus (kg/ha)": "phosphorus_kg_ha",
    "phosphorus_kgha": "phosphorus_kg_ha",
    "phosphorus": "phosphorus_kg_ha",
    "available_phosphorus": "phosphorus_kg_ha",
    "available phosphorus": "phosphorus_kg_ha",
    "p_kg_ha": "phosphorus_kg_ha",
    "p (kg/ha)": "phosphorus_kg_ha",
    "p": "phosphorus_kg_ha",
    "phosphorus_method": "phosphorus_method",
    "potassium_kg_ha": "potassium_kg_ha",
    "potassium (kg/ha)": "potassium_kg_ha",
    "potassium_kgha": "potassium_kg_ha",
    "potassium": "potassium_kg_ha",
    "available_potassium": "potassium_kg_ha",
    "available potassium": "potassium_kg_ha",
    "k_kg_ha": "potassium_kg_ha",
    "k (kg/ha)": "potassium_kg_ha",
    "k": "potassium_kg_ha",
    "potassium_method": "potassium_method",
}

_NUMERIC_PARAMS: Dict[str, Tuple[Optional[float], Optional[float]]] = {
    "ph": (0.0, 14.0),
    "nitrogen_kg_ha": (0.0, 5000.0),
    "phosphorus_kg_ha": (0.0, 2000.0),
    "potassium_kg_ha": (0.0, 10000.0),
}

_PARAM_BOUND_KEYS: Dict[str, str] = {
    "nitrogen_kg_ha": "nitrogen",
    "phosphorus_kg_ha": "phosphorus",
    "potassium_kg_ha": "potassium",
    "ph": "ph",
}


def normalize_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize dataframe column headers using known aliases and strip whitespace."""
    new_cols = {}
    for col in df.columns:
        cleaned = str(col).strip().lower().replace("-", "_")
        canonical = HEADER_ALIASES.get(cleaned, cleaned)
        new_cols[col] = canonical
    return df.rename(columns=new_cols)


def parse_depth(raw_val: object) -> Optional[float]:
    """Parse depth values like '20', '0-20', '0 - 15 cm'."""
    if pd.isna(raw_val):
        return None
    s = str(raw_val).strip()
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:cm)?$", s)
    if match:
        try:
            return float(match.group(1))
        except (ValueError, TypeError):
            pass
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def validate_dataframe(
    df: pd.DataFrame,
    param_bounds: Optional[Dict[str, Tuple[float, float]]] = None,
) -> ValidationReport:
    errors: List[ValidationIssue] = []
    warnings: List[ValidationIssue] = []

    df = normalize_dataframe_columns(df)

    if len(df) == 0:
        errors.append(
            ValidationIssue(
                row=None,
                column=None,
                message="Uploaded CSV file is completely empty.",
                severity="error",
            )
        )
        return ValidationReport(
            total_rows=0,
            valid_rows=0,
            error_rows=0,
            errors=errors,
            warnings=warnings,
        )

    # Required column check: sample_code is essential
    if "sample_code" not in df.columns:
        errors.append(
            ValidationIssue(
                row=None,
                column="sample_code",
                message="Required column 'sample_code' is missing from CSV header.",
                severity="error",
            )
        )
        return ValidationReport(
            total_rows=len(df),
            valid_rows=0,
            error_rows=len(df),
            errors=errors,
            warnings=warnings,
        )

    # Check for at least one soil parameter column
    param_cols = [c for c in ("ph", "nitrogen_kg_ha", "phosphorus_kg_ha", "potassium_kg_ha") if c in df.columns]
    if not param_cols:
        errors.append(
            ValidationIssue(
                row=None,
                column="parameters",
                message="CSV must contain at least one soil nutrient or pH column (e.g. ph, nitrogen_kg_ha, phosphorus_kg_ha, potassium_kg_ha).",
                severity="error",
            )
        )
        return ValidationReport(
            total_rows=len(df),
            valid_rows=0,
            error_rows=len(df),
            errors=errors,
            warnings=warnings,
        )

    # Strip text columns
    df = df.copy()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)

    error_rows: set[int] = set()
    seen_codes: Dict[str, int] = {}

    for idx, row in df.iterrows():
        excel_row = int(idx) + 2  # type: ignore[arg-type]

        # Validate sample_code
        code_val = row.get("sample_code", None)
        if pd.isna(code_val) or str(code_val).strip() == "":
            errors.append(
                ValidationIssue(
                    row=excel_row,
                    column="sample_code",
                    message="sample_code is missing or empty.",
                    severity="error",
                )
            )
            error_rows.add(int(idx))  # type: ignore[arg-type]
        else:
            code_str = str(code_val).strip()
            if code_str in seen_codes:
                warnings.append(
                    ValidationIssue(
                        row=excel_row,
                        column="sample_code",
                        message=f"Duplicate sample_code '{code_str}' in file (first seen at row {seen_codes[code_str]}).",
                        severity="warning",
                    )
                )
            else:
                seen_codes[code_str] = excel_row

        # Validate district if provided
        if "district" in row:
            district_val = row.get("district")
            if pd.notna(district_val) and str(district_val).strip() != "":
                if not is_valid_madurai_district(str(district_val)):
                    errors.append(
                        ValidationIssue(
                            row=excel_row,
                            column="district",
                            message=(
                                f"Invalid district '{district_val}'. SoilSense is strictly scoped to "
                                f"{TARGET_DISTRICT} District, Tamil Nadu only. Records from outside {TARGET_DISTRICT} "
                                "cannot be accepted."
                            ),
                            severity="error",
                        )
                    )
                    error_rows.add(int(idx))  # type: ignore[arg-type]

        # Validate sample_date if provided
        if "sample_date" in row:
            date_val = row.get("sample_date")
            if pd.notna(date_val) and str(date_val).strip() != "":
                try:
                    pd.to_datetime(str(date_val))
                except (ValueError, TypeError):
                    errors.append(
                        ValidationIssue(
                            row=excel_row,
                            column="sample_date",
                            message=f"Invalid sample_date format: '{date_val}'.",
                            severity="error",
                        )
                    )
                    error_rows.add(int(idx))  # type: ignore[arg-type]

        # Validate parameters in this row
        row_has_valid_num = False
        for col, (lo, hi) in _NUMERIC_PARAMS.items():
            if col not in df.columns:
                continue
            raw_val = row.get(col)
            if pd.isna(raw_val) or str(raw_val).strip() == "":
                continue

            try:
                num = float(raw_val)  # type: ignore[arg-type]
            except (ValueError, TypeError):
                errors.append(
                    ValidationIssue(
                        row=excel_row,
                        column=col,
                        message=f"Parameter '{col}' value '{raw_val}' is not a valid number.",
                        severity="error",
                    )
                )
                error_rows.add(int(idx))  # type: ignore[arg-type]
                continue

            if lo is not None and num < lo:
                errors.append(
                    ValidationIssue(
                        row=excel_row,
                        column=col,
                        message=f"Parameter '{col}' value {num} is below minimum ({lo}).",
                        severity="error",
                    )
                )
                error_rows.add(int(idx))  # type: ignore[arg-type]
                continue

            if hi is not None and num > hi:
                errors.append(
                    ValidationIssue(
                        row=excel_row,
                        column=col,
                        message=f"Parameter '{col}' value {num} exceeds maximum ({hi}).",
                        severity="error",
                    )
                )
                error_rows.add(int(idx))  # type: ignore[arg-type]
                continue

            row_has_valid_num = True

        if not row_has_valid_num and int(idx) not in error_rows:
            warnings.append(
                ValidationIssue(
                    row=excel_row,
                    column="parameters",
                    message="Row has no valid nutrient parameter values.",
                    severity="warning",
                )
            )

    total = len(df)
    n_error = len(error_rows)
    n_valid = total - n_error

    return ValidationReport(
        total_rows=total,
        valid_rows=n_valid,
        error_rows=n_error,
        errors=errors,
        warnings=warnings,
    )


def clean_dataframe(
    df: pd.DataFrame,
    param_bounds: Optional[Dict[str, Tuple[float, float]]] = None,
) -> Tuple[pd.DataFrame, List[int]]:
    """Clean and normalize the dataframe, retaining only rows that pass validation."""
    df = normalize_dataframe_columns(df)
    report = validate_dataframe(df, param_bounds=param_bounds)

    error_indices: set[int] = set()
    for issue in report.errors:
        if issue.row is not None:
            error_indices.add(issue.row - 2)

    valid_indices = [i for i in df.index if i not in error_indices]
    clean_df = df.loc[valid_indices].reset_index(drop=True)
    return clean_df, valid_indices
