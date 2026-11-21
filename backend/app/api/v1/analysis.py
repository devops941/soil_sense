from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import analysis_engine, dashboard_service
from app.services.statistics_service import build_sample_dataframe

_PARAM_CODES = ["ph", "nitrogen", "phosphorus", "potassium"]

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/fertility-distribution", summary="Overall and per-nutrient fertility distributions")
def fertility_distribution(
    data_source: Optional[str] = Query(None),
    location_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    summary_data = dashboard_service.summary(db, data_source=data_source, location_id=location_id)
    return {
        "total_samples": summary_data["total_samples"],
        "fertility_distribution": summary_data["fertility_distribution"],
        "nutrient_distribution": summary_data["nutrient_distribution"],
        "ph_distribution": summary_data["ph_distribution"],
        "nutrient_indices": summary_data["nutrient_indices"],
    }


@router.get("/summary-stats", summary="Descriptive statistics for soil parameters")
def summary_stats(
    data_source: Optional[str] = Query("verified"),
    location_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    df = build_sample_dataframe(
        db,
        data_source=data_source,
        location_id=location_id,
        date_from=date_from,
        date_to=date_to,
    )
    stats = analysis_engine.summary_stats(df, _PARAM_CODES)
    return {"data": [s.model_dump() for s in stats]}


@router.get("/distribution", summary="Histogram distribution for a parameter")
def distribution(
    parameter: str = Query("ph", description="Parameter code"),
    bins: int = Query(20, ge=2, le=100),
    data_source: Optional[str] = Query("verified"),
    location_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    df = build_sample_dataframe(
        db,
        data_source=data_source,
        location_id=location_id,
        date_from=date_from,
        date_to=date_to,
    )
    return analysis_engine.distribution(df, parameter, bins=bins)


@router.get("/correlation", summary="Pearson correlation matrix for parameters")
def correlation(
    data_source: Optional[str] = Query("verified"),
    location_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    df = build_sample_dataframe(
        db,
        data_source=data_source,
        location_id=location_id,
        date_from=date_from,
        date_to=date_to,
    )
    return analysis_engine.correlation_matrix(df, _PARAM_CODES)


@router.get("/boxplot", summary="Box-plot statistics grouped by location")
def boxplot(
    parameter: str = Query("ph", description="Parameter code"),
    data_source: Optional[str] = Query("verified"),
    location_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    df = build_sample_dataframe(db, data_source=data_source, location_id=location_id)
    return analysis_engine.boxplot_by_group(df, parameter)


@router.get("/outliers", summary="Z-score outlier detection for a parameter")
def outliers(
    parameter: str = Query("ph", description="Parameter code"),
    z_threshold: float = Query(3.0, ge=1.0, le=5.0),
    data_source: Optional[str] = Query("verified"),
    location_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    df = build_sample_dataframe(db, data_source=data_source, location_id=location_id)
    return analysis_engine.detect_outliers(df, parameter, z_threshold=z_threshold)
