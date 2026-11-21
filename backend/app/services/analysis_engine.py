from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats

from app.schemas.statistics import ParameterStat


def summary_stats(df: pd.DataFrame, columns: List[str]) -> List[ParameterStat]:
    result: List[ParameterStat] = []
    for col in columns:
        if col not in df.columns:
            continue
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        n = len(series)
        if n == 0:
            result.append(
                ParameterStat(
                    parameter_code=col,
                    mean=0.0,
                    median=0.0,
                    std=0.0,
                    min=0.0,
                    max=0.0,
                    p25=0.0,
                    p75=0.0,
                    count=0,
                )
            )
            continue
        std_val = float(series.std(ddof=1)) if n > 1 else 0.0
        result.append(
            ParameterStat(
                parameter_code=col,
                mean=float(series.mean()),
                median=float(series.median()),
                std=std_val,
                min=float(series.min()),
                max=float(series.max()),
                p25=float(series.quantile(0.25)),
                p75=float(series.quantile(0.75)),
                count=n,
            )
        )
    return result


def correlation_matrix(df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
    valid_cols = [c for c in columns if c in df.columns]
    if not valid_cols:
        return {"labels": [], "matrix": []}

    n = len(valid_cols)
    matrix: List[List[float]] = [[0.0] * n for _ in range(n)]

    for i, col_a in enumerate(valid_cols):
        matrix[i][i] = 1.0
        for j, col_b in enumerate(valid_cols):
            if i == j:
                continue
            series_a = pd.to_numeric(df[col_a], errors="coerce")
            series_b = pd.to_numeric(df[col_b], errors="coerce")
            combined = pd.concat([series_a, series_b], axis=1).dropna()
            if len(combined) < 2:
                matrix[i][j] = float("nan")
                continue
            corr_val = combined.iloc[:, 0].corr(combined.iloc[:, 1])
            matrix[i][j] = round(float(corr_val) if not np.isnan(corr_val) else float("nan"), 6)

    return {"labels": valid_cols, "matrix": matrix}


def distribution(
    df: pd.DataFrame,
    column: str,
    bins: int = 20,
) -> Dict[str, Any]:
    if column not in df.columns:
        return {"bins": [], "counts": [], "parameter_code": column, "count": 0}

    series = pd.to_numeric(df[column], errors="coerce").dropna()
    if len(series) == 0:
        return {"bins": [], "counts": [], "parameter_code": column, "count": 0}

    counts, edges = np.histogram(series.values, bins=bins)
    return {
        "bins": [round(float(e), 6) for e in edges],
        "counts": [int(c) for c in counts],
        "parameter_code": column,
        "count": int(len(series)),
    }


def boxplot_by_group(
    df: pd.DataFrame,
    column: str,
    group_col: str = "location_name",
) -> List[Dict[str, Any]]:
    if column not in df.columns or group_col not in df.columns:
        return []

    result: List[Dict[str, Any]] = []
    for group_val, group_df in df.groupby(group_col):
        series = pd.to_numeric(group_df[column], errors="coerce").dropna()
        if len(series) == 0:
            continue
        q1 = float(series.quantile(0.25))
        median = float(series.median())
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1
        low_fence = q1 - 1.5 * iqr
        high_fence = q3 + 1.5 * iqr
        outliers = [float(v) for v in series if v < low_fence or v > high_fence]
        non_outliers = series[(series >= low_fence) & (series <= high_fence)]
        whisker_min = float(non_outliers.min()) if len(non_outliers) > 0 else q1
        whisker_max = float(non_outliers.max()) if len(non_outliers) > 0 else q3
        result.append(
            {
                "group": str(group_val),
                "q1": round(q1, 6),
                "median": round(median, 6),
                "q3": round(q3, 6),
                "min": round(whisker_min, 6),
                "max": round(whisker_max, 6),
                "outliers": [round(o, 6) for o in outliers],
            }
        )
    return result


def detect_outliers(
    df: pd.DataFrame,
    column: str,
    z_threshold: float = 3.0,
) -> List[Dict[str, Any]]:
    if column not in df.columns:
        return []

    series = pd.to_numeric(df[column], errors="coerce")
    valid_mask = series.notna()
    valid_series = series[valid_mask]

    if len(valid_series) < 2:
        return []

    z_scores = np.abs(stats.zscore(valid_series.values, nan_policy="omit"))

    result: List[Dict[str, Any]] = []
    for arr_idx, (orig_idx, val) in enumerate(valid_series.items()):
        z = float(z_scores[arr_idx])
        if z > z_threshold:
            result.append(
                {
                    "index": int(orig_idx),  # type: ignore[arg-type]
                    "value": float(val),
                    "z_score": round(z, 6),
                }
            )
    return result


def groupby_location(
    df: pd.DataFrame,
    columns: List[str],
    group_col: str = "location_name",
) -> List[Dict[str, Any]]:
    if group_col not in df.columns:
        return []

    valid_cols = [c for c in columns if c in df.columns]
    if not valid_cols:
        return []

    result: List[Dict[str, Any]] = []
    for group_val, group_df in df.groupby(group_col):
        entry: Dict[str, Any] = {"group": str(group_val)}
        for col in valid_cols:
            series = pd.to_numeric(group_df[col], errors="coerce").dropna()
            n = len(series)
            entry[col] = {
                "mean": round(float(series.mean()), 6) if n > 0 else None,
                "std": round(float(series.std(ddof=1)), 6) if n > 1 else 0.0,
                "count": n,
            }
        result.append(entry)
    return result
