from __future__ import annotations

from datetime import date
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.models.classification_result import ClassificationResult
from app.models.parameter import ParameterDefinition
from app.models.sample import SoilParameterValue, SoilSample


def _get_param_value(sample: SoilSample, code: str, param_def_map: dict) -> Optional[float]:
    for pv in sample.parameter_values:
        if param_def_map.get(pv.parameter_def_id) == code:
            return pv.value
    return None


def samples_to_csv(
    db: Session,
    data_source: Optional[str] = None,
    location_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> bytes:
    from sqlalchemy.orm import joinedload

    query = (
        db.query(SoilSample)
        .options(
            joinedload(SoilSample.location),
            joinedload(SoilSample.parameter_values),
            joinedload(SoilSample.classification_result),
        )
        .filter(SoilSample.is_deleted == False)  # noqa: E712
    )
    if data_source is not None:
        query = query.filter(SoilSample.data_source == data_source)
    if location_id is not None:
        query = query.filter(SoilSample.location_id == location_id)
    if date_from is not None:
        query = query.filter(SoilSample.sample_date >= date_from)
    if date_to is not None:
        query = query.filter(SoilSample.sample_date <= date_to)

    samples = query.order_by(SoilSample.created_at.desc()).all()

    param_def_map = {row.id: row.code for row in db.query(ParameterDefinition).all()}

    rows = []
    for s in samples:
        location_name = s.location.name if s.location else ""
        district = s.location.district if s.location else "Madurai"
        taluk_block = s.location.taluk_block if s.location else ""
        village = s.location.village if s.location else ""
        ph_val = _get_param_value(s, "ph", param_def_map)
        n_val = _get_param_value(s, "nitrogen", param_def_map)
        p_val = _get_param_value(s, "phosphorus", param_def_map)
        k_val = _get_param_value(s, "potassium", param_def_map)
        cr = s.classification_result
        rows.append({
            "id": s.id,
            "sample_code": s.sample_code,
            "location_name": location_name,
            "taluk_block": taluk_block,
            "village": village,
            "district": district,
            "sample_date": s.sample_date.isoformat() if s.sample_date else "",
            "depth_cm": s.depth_cm,
            "land_use": s.land_use,
            "collector_name": s.collector_name,
            "data_source": s.data_source,
            "ph": ph_val,
            "nitrogen_kg_ha": n_val,
            "phosphorus_kg_ha": p_val,
            "potassium_kg_ha": k_val,
            "measurement_units": "pH / kg/ha",
            "ph_class": cr.ph_class if cr else "",
            "n_class": cr.n_class if cr else "",
            "p_class": cr.p_class if cr else "",
            "k_class": cr.k_class if cr else "",
            "fertility_class": cr.fertility_class if cr else "",
            "overall_status": cr.overall_status if cr else "",
            "notes": s.notes,
            "created_at": s.created_at.isoformat() if s.created_at else "",
        })

    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode("utf-8")


def classification_to_csv(
    db: Session,
    data_source: Optional[str] = None,
    location_id: Optional[int] = None,
) -> bytes:
    from sqlalchemy.orm import joinedload

    query = (
        db.query(ClassificationResult)
        .join(SoilSample, ClassificationResult.sample_id == SoilSample.id)
        .options(joinedload(ClassificationResult.sample))
        .filter(SoilSample.is_deleted == False)  # noqa: E712
    )
    if data_source is not None:
        query = query.filter(SoilSample.data_source == data_source)
    if location_id is not None:
        query = query.filter(SoilSample.location_id == location_id)

    results = query.all()

    rows = []
    for cr in results:
        s = cr.sample
        rows.append({
            "sample_id": cr.sample_id,
            "sample_code": s.sample_code if s else "",
            "ph_class": cr.ph_class,
            "n_class": cr.n_class,
            "p_class": cr.p_class,
            "k_class": cr.k_class,
            "fertility_class": cr.fertility_class,
            "overall_status": cr.overall_status,
            "standard_used": cr.standard_used,
            "classified_at": cr.classified_at.isoformat() if cr.classified_at else "",
        })

    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode("utf-8")
