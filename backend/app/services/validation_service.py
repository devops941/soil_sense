from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from app.core.madurai_geography import is_valid_madurai_district, TARGET_DISTRICT
from app.schemas.upload import ValidationIssue, ValidationReport

REQUIRED_COLUMNS: List[str] = [
    "sample_code",
    "location_name",
    "district",
    "sample_date",
    "depth_cm",
    "land_use",
    "collector_name",
    "ph",
    "ph_method",
    "nitrogen_kg_ha",
    "nitrogen_method",
    "phosphorus_kg_ha",
    "phosphorus_method",
    "potassium_kg_ha",
    "potassium_method",
]

OPTIONAL_COLUMNS: List[str] = ["notes"]

_NUMERIC_PARAMS: Dict[str, Tuple[Optional[float], Optional[float]]] = {
    "ph": (0.0, 14.0),
    "nitrogen_kg_ha": (0.0, None),
    "phosphorus_kg_ha": (0.0, None),
    "potassium_kg_ha": (0.0, None),
}

_PARAM_BOUND_KEYS: Dict[str, str] = {
    "nitrogen_kg_ha": "nitrogen",
    "phosphorus_kg_ha": "phosphorus",
    "potassium_kg_ha": "potassium",
    "ph": "ph",
}


def validate_dataframe(
    df: pd.DataFrame,
    param_bounds: Optional[Dict[str, Tuple[float, float]]] = None,
) -> ValidationReport:
    errors: List[ValidationIssue] = []
    warnings: List[ValidationIssue] = []

    missing_required = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_required:
        for col in missing_required:
            errors.append(
                ValidationIssue(
                    row=None,
                    column=col,
                    message=f"Required column '{col}' is missing.",
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

    for col in OPTIONAL_COLUMNS:
        if col not in df.columns:
            warnings.append(
                ValidationIssue(
                    row=None,
                    column=col,
                    message=f"Optional column '{col}' is absent; it will be treated as empty.",
                    severity="warning",
                )
            )

    df = df.copy()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)

    error_rows: set[int] = set()

    seen_codes: Dict[str, int] = {}
    for idx, row in df.iterrows():
        excel_row = int(idx) + 2  # type: ignore[arg-type]
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
                        message=f"Duplicate sample_code '{code_str}' (first seen at row {seen_codes[code_str]}).",
                        severity="warning",
                    )
                )
            else:
                seen_codes[code_str] = excel_row

        # Madurai District Strict Geographical Verification
        district_val = row.get("district", None)
        if pd.isna(district_val) or str(district_val).strip() == "":
            errors.append(
                ValidationIssue(
                    row=excel_row,
                    column="district",
                    message="district is missing or empty. Madurai District is required.",
                    severity="error",
                )
            )
            error_rows.add(int(idx))  # type: ignore[arg-type]
        elif not is_valid_madurai_district(str(district_val)):
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

    for idx, row in df.iterrows():
        excel_row = int(idx) + 2  # type: ignore[arg-type]
        date_val = row.get("sample_date", None)
        if pd.isna(date_val) or str(date_val).strip() == "":
            errors.append(
                ValidationIssue(
                    row=excel_row,
                    column="sample_date",
                    message="sample_date is missing.",
                    severity="error",
                )
            )
            error_rows.add(int(idx))  # type: ignore[arg-type]
        else:
            try:
                pd.to_datetime(str(date_val))
            except (ValueError, TypeError):
                errors.append(
                    ValidationIssue(
                        row=excel_row,
                        column="sample_date",
                        message=f"sample_date '{date_val}' is not a recognisable date.",
                        severity="error",
                    )
                )
                error_rows.add(int(idx))  # type: ignore[arg-type]

    for col, (lo, hi) in _NUMERIC_PARAMS.items():
        if col not in df.columns:
            continue
        param_key = _PARAM_BOUND_KEYS.get(col)
        effective_max: Optional[float] = hi
        if param_bounds and param_key and param_key in param_bounds:
            _, bound_max = param_bounds[param_key]
            if bound_max is not None:
                effective_max = bound_max

        for idx, raw_val in df[col].items():
            excel_row = int(idx) + 2  # type: ignore[arg-type]
            if pd.isna(raw_val) or str(raw_val).strip() == "":
                warnings.append(
                    ValidationIssue(
                        row=excel_row,
                        column=col,
                        message=f"'{col}' is empty; row will be skipped for analysis.",
                        severity="warning",
                    )
                )
                continue
            try:
                num = float(raw_val)  # type: ignore[arg-type]
            except (ValueError, TypeError):
                errors.append(
                    ValidationIssue(
                        row=excel_row,
                        column=col,
                        message=f"'{col}' value '{raw_val}' is not numeric.",
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
                        message=f"'{col}' value {num} is negative (minimum {lo}).",
                        severity="error",
                    )
                )
                error_rows.add(int(idx))  # type: ignore[arg-type]
            elif hi is not None and num > hi:
                errors.append(
                    ValidationIssue(
                        row=excel_row,
                        column=col,
                        message=f"'{col}' value {num} exceeds maximum {hi}.",
                        severity="error",
                    )
                )
                error_rows.add(int(idx))  # type: ignore[arg-type]

            if effective_max is not None and num > effective_max and not (hi is not None and num > hi):
                errors.append(
                    ValidationIssue(
                        row=excel_row,
                        column=col,
                        message=f"'{col}' value {num} exceeds allowed maximum {effective_max}.",
                        severity="error",
                    )
                )
                error_rows.add(int(idx))  # type: ignore[arg-type]

    for col in OPTIONAL_COLUMNS:
        if col in df.columns:
            for idx, val in df[col].items():
                if pd.isna(val) or str(val).strip() == "":
                    excel_row = int(idx) + 2  # type: ignore[arg-type]
                    warnings.append(
                        ValidationIssue(
                            row=excel_row,
                            column=col,
                            message=f"Optional field '{col}' is empty.",
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
) -> Tuple[pd.DataFrame, List[int]]:
    df = df.copy()

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)

    for col in _NUMERIC_PARAMS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "sample_date" in df.columns:
        df["sample_date"] = pd.to_datetime(df["sample_date"], errors="coerce")

    report = validate_dataframe(df)
    error_excel_rows: set[int] = set()
    for issue in report.errors:
        if issue.row is not None:
            error_excel_rows.add(issue.row - 2)

    valid_indices = [i for i in df.index if i not in error_excel_rows]  # type: ignore[operator]
    clean_df = df.loc[valid_indices].reset_index(drop=True)
    return clean_df, valid_indices
