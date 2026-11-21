from __future__ import annotations

from typing import Any, Dict, List, Optional
from collections import Counter

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.core.config import settings
from app.models.classification_result import ClassificationResult
from app.models.location import Location
from app.models.parameter import ParameterDefinition
from app.models.sample import SoilParameterValue, SoilSample
from app.services import classification_service
from app.services.sample_service import to_read


def summary(
    db: Session,
    data_source: Optional[str] = None,
    location_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Compute comprehensive dashboard summary for Madurai soil samples."""
    # Base sample query
    query = db.query(SoilSample).filter(SoilSample.is_deleted == False)  # noqa: E712

    # Global counts across DB
    total_db_samples = query.count()
    verified_total = query.filter(SoilSample.data_source == "verified").count()
    demo_total = query.filter(SoilSample.data_source == "demo").count()
    locations_count = db.query(Location).count()

    # Filtered query for current view
    if data_source and data_source.lower() not in ("all", ""):
        query = query.filter(SoilSample.data_source == data_source)
    if location_id is not None:
        query = query.filter(SoilSample.location_id == location_id)

    filtered_samples = query.options(
        joinedload(SoilSample.location),
        joinedload(SoilSample.parameter_values).joinedload(SoilParameterValue.parameter_def),
        joinedload(SoilSample.classification_result),
    ).all()

    filtered_total = len(filtered_samples)

    # Classifications breakdown
    high_count = 0
    medium_count = 0
    low_count = 0
    unclassified_count = 0

    n_dist = {"low": 0, "medium": 0, "high": 0}
    p_dist = {"low": 0, "medium": 0, "high": 0}
    k_dist = {"low": 0, "medium": 0, "high": 0}
    ph_dist: Dict[str, int] = {}

    samples_classes = []
    sample_ids = [s.id for s in filtered_samples]

    for s in filtered_samples:
        cr = s.classification_result
        if cr:
            fc = (cr.fertility_class or "").capitalize()
            if fc == "High":
                high_count += 1
            elif fc == "Medium":
                medium_count += 1
            elif fc == "Low":
                low_count += 1
            else:
                unclassified_count += 1

            if cr.n_class and cr.n_class.lower() in n_dist:
                n_dist[cr.n_class.lower()] += 1
            if cr.p_class and cr.p_class.lower() in p_dist:
                p_dist[cr.p_class.lower()] += 1
            if cr.k_class and cr.k_class.lower() in k_dist:
                k_dist[cr.k_class.lower()] += 1

            if cr.ph_class:
                ph_dist[cr.ph_class] = ph_dist.get(cr.ph_class, 0) + 1

            samples_classes.append({
                "n_class": cr.n_class,
                "p_class": cr.p_class,
                "k_class": cr.k_class,
            })
        else:
            unclassified_count += 1

    # Nutrient indices
    nutrient_indices = classification_service.compute_nutrient_indices(
        samples_classes, settings.ACTIVE_STANDARD
    )

    # Location-wise breakdown
    location_map: Dict[str, Dict[str, Any]] = {}
    for s in filtered_samples:
        loc_name = s.location.name if s.location else "Unknown"
        taluk = (s.location.taluk_block if s.location else None) or loc_name
        if loc_name not in location_map:
            location_map[loc_name] = {
                "location_name": loc_name,
                "taluk_block": taluk,
                "sample_count": 0,
                "ph_values": [],
                "n_values": [],
                "p_values": [],
                "k_values": [],
                "fertility_classes": [],
            }
        loc_entry = location_map[loc_name]
        loc_entry["sample_count"] += 1
        if s.classification_result and s.classification_result.fertility_class:
            loc_entry["fertility_classes"].append(s.classification_result.fertility_class)

        for pv in s.parameter_values:
            code = pv.parameter_def.code if pv.parameter_def else ""
            if code == "ph":
                loc_entry["ph_values"].append(pv.value)
            elif code == "nitrogen":
                loc_entry["n_values"].append(pv.value)
            elif code == "phosphorus":
                loc_entry["p_values"].append(pv.value)
            elif code == "potassium":
                loc_entry["k_values"].append(pv.value)

    location_wise_stats = []
    for loc_name, data in sorted(location_map.items()):
        fc_counts = Counter(data["fertility_classes"])
        dominant_fertility = fc_counts.most_common(1)[0][0] if fc_counts else "N/A"
        location_wise_stats.append({
            "location_name": loc_name,
            "taluk_block": data["taluk_block"],
            "sample_count": data["sample_count"],
            "avg_ph": round(sum(data["ph_values"]) / len(data["ph_values"]), 2) if data["ph_values"] else None,
            "avg_nitrogen": round(sum(data["n_values"]) / len(data["n_values"]), 1) if data["n_values"] else None,
            "avg_phosphorus": round(sum(data["p_values"]) / len(data["p_values"]), 1) if data["p_values"] else None,
            "avg_potassium": round(sum(data["k_values"]) / len(data["k_values"]), 1) if data["k_values"] else None,
            "dominant_fertility": dominant_fertility,
        })

    # Recent samples (last 6)
    recent_samples = [
        to_read(s) for s in sorted(filtered_samples, key=lambda x: x.created_at, reverse=True)[:6]
    ]

    return {
        "total_samples": filtered_total,
        "total_db_samples": total_db_samples,
        "verified_count": verified_total,
        "demo_count": demo_total,
        "locations_count": locations_count,
        "high_fertility_count": high_count,
        "medium_fertility_count": medium_count,
        "low_fertility_count": low_count,
        "unclassified_count": unclassified_count,
        "fertility_distribution": {
            "High": high_count,
            "Medium": medium_count,
            "Low": low_count,
            "Unclassified": unclassified_count,
        },
        "nutrient_distribution": {
            "nitrogen": n_dist,
            "phosphorus": p_dist,
            "potassium": k_dist,
        },
        "ph_distribution": ph_dist,
        "location_wise_stats": location_wise_stats,
        "nutrient_indices": [ni.model_dump() for ni in nutrient_indices],
        "recent_samples": [s.model_dump() for s in recent_samples],
        "active_standard": settings.ACTIVE_STANDARD,
        "geographical_scope": "Madurai District, Tamil Nadu",
    }
