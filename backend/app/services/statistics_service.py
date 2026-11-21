from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

import pandas as pd
from scipy import stats
from sqlalchemy.orm import Session

from app.models.location import Location
from app.models.parameter import ParameterDefinition
from app.models.sample import SoilSample, SoilParameterValue
from app.schemas.statistics import LocationComparisonItem
from app.services import analysis_engine

_PARAM_CODES: List[str] = ["ph", "nitrogen", "phosphorus", "potassium"]


def build_sample_dataframe(
    db: Session,
    data_source: Optional[str] = "verified",
    location_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> pd.DataFrame:
    query = (
        db.query(SoilSample)
        .filter(SoilSample.is_deleted == False)  # noqa: E712
    )

    if data_source is not None and data_source != "all":
        query = query.filter(SoilSample.data_source == data_source)
    if location_id is not None:
        query = query.filter(SoilSample.location_id == location_id)
    if date_from is not None:
        query = query.filter(SoilSample.sample_date >= date_from)
    if date_to is not None:
        query = query.filter(SoilSample.sample_date <= date_to)

    samples: List[SoilSample] = query.all()

    if not samples:
        cols = ["sample_id", "sample_code", "sample_date", "location_name"] + _PARAM_CODES
        return pd.DataFrame(columns=cols)

    param_def_map: Dict[int, str] = {
        row.id: row.code
        for row in db.query(ParameterDefinition).all()
    }

    location_map: Dict[int, str] = {
        row.id: row.name
        for row in db.query(Location).all()
    }

    rows: List[Dict[str, Any]] = []
    for sample in samples:
        row: Dict[str, Any] = {
            "sample_id": sample.id,
            "sample_code": sample.sample_code,
            "sample_date": sample.sample_date,
            "location_name": location_map.get(sample.location_id, "") if sample.location_id else "",
        }
        for code in _PARAM_CODES:
            row[code] = None

        param_vals: List[SoilParameterValue] = (
            db.query(SoilParameterValue)
            .filter(SoilParameterValue.sample_id == sample.id)
            .all()
        )
        for pv in param_vals:
            code = param_def_map.get(pv.parameter_def_id)
            if code and code in _PARAM_CODES:
                row[code] = pv.value

        rows.append(row)

    df = pd.DataFrame(rows)
    for code in _PARAM_CODES:
        if code in df.columns:
            df[code] = pd.to_numeric(df[code], errors="coerce")

    return df


def location_comparison(
    db: Session,
    parameter_code: str,
    location_ids: Optional[List[int]] = None,
    data_source: str = "verified",
) -> List[LocationComparisonItem]:
    df = build_sample_dataframe(db, data_source=data_source)

    if df.empty or parameter_code not in df.columns:
        return []

    location_map: Dict[int, str] = {
        row.id: row.name
        for row in db.query(Location).all()
    }
    location_name_map: Dict[str, int] = {v: k for k, v in location_map.items()}

    if location_ids is not None:
        allowed_names = {location_map[lid] for lid in location_ids if lid in location_map}
        df = df[df["location_name"].isin(allowed_names)]

    if df.empty:
        return []

    result: List[LocationComparisonItem] = []
    for group_name, group_df in df.groupby("location_name"):
        series = pd.to_numeric(group_df[parameter_code], errors="coerce").dropna()
        n = len(series)
        if n == 0:
            continue
        loc_id = location_name_map.get(str(group_name), -1)
        result.append(
            LocationComparisonItem(
                location_id=loc_id,
                location_name=str(group_name),
                mean=round(float(series.mean()), 6),
                std=round(float(series.std(ddof=1)), 6) if n > 1 else 0.0,
                count=n,
            )
        )
    return result


def ttest_between_locations(
    db: Session,
    parameter_code: str,
    location_id_a: int,
    location_id_b: int,
    data_source: str = "verified",
) -> Dict[str, Any]:
    ds = None if data_source == "all" else data_source
    df_a = build_sample_dataframe(db, data_source=ds, location_id=location_id_a)
    df_b = build_sample_dataframe(db, data_source=ds, location_id=location_id_b)

    series_a = pd.to_numeric(df_a.get(parameter_code, pd.Series(dtype=float)), errors="coerce").dropna()
    series_b = pd.to_numeric(df_b.get(parameter_code, pd.Series(dtype=float)), errors="coerce").dropna()

    n_a = len(series_a)
    n_b = len(series_b)
    mean_a = float(series_a.mean()) if n_a > 0 else 0.0
    mean_b = float(series_b.mean()) if n_b > 0 else 0.0

    if n_a < 2 or n_b < 2:
        reasons = []
        if n_a < 2:
            reasons.append(f"Location A has only {n_a} sample(s)")
        if n_b < 2:
            reasons.append(f"Location B has only {n_b} sample(s)")
        msg = f"Welch's t-test requires at least 2 samples per location to calculate sample variance. {', '.join(reasons)}."
        return {
            "statistic": None,
            "p_value": None,
            "significant": False,
            "mean_a": round(mean_a, 2),
            "mean_b": round(mean_b, 2),
            "n_a": n_a,
            "n_b": n_b,
            "message": msg,
        }

    tstat, pval = stats.ttest_ind(
        series_a.values,
        series_b.values,
        nan_policy="omit",
        equal_var=False,
    )

    import math
    stat_val = round(float(tstat), 4) if not math.isnan(tstat) else 0.0
    p_val = round(float(pval), 4) if not math.isnan(pval) else 1.0

    return {
        "statistic": stat_val,
        "p_value": p_val,
        "significant": bool(p_val < 0.05),
        "mean_a": round(mean_a, 2),
        "mean_b": round(mean_b, 2),
        "n_a": n_a,
        "n_b": n_b,
    }
