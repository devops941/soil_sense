from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path
from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Parameter definitions seed data
# ---------------------------------------------------------------------------

_PARAMETER_SEEDS = [
    {
        "code": "ph",
        "display_name": "Soil pH",
        "default_unit": "pH",
        "common_methods": json.dumps(["electrometric 1:2.5"]),
        "value_min": 0.0,
        "value_max": 14.0,
        "description": "Soil acidity/alkalinity measured in a 1:2.5 soil-to-water suspension.",
    },
    {
        "code": "nitrogen",
        "display_name": "Available Nitrogen",
        "default_unit": "kg/ha",
        "common_methods": json.dumps(["Alkaline KMnO4"]),
        "value_min": 0.0,
        "value_max": 5000.0,
        "description": "Available nitrogen content determined by the Alkaline KMnO4 method.",
    },
    {
        "code": "phosphorus",
        "display_name": "Available Phosphorus",
        "default_unit": "kg/ha",
        "common_methods": json.dumps(["Olsen", "Bray-1"]),
        "value_min": 0.0,
        "value_max": 2000.0,
        "description": "Available phosphorus content; Olsen method preferred for neutral/alkaline soils.",
    },
    {
        "code": "potassium",
        "display_name": "Available Potassium",
        "default_unit": "kg/ha",
        "common_methods": json.dumps(["Neutral Normal Ammonium Acetate"]),
        "value_min": 0.0,
        "value_max": 10000.0,
        "description": "Available potassium content determined by neutral normal ammonium acetate extraction.",
    },
]


def _seed_parameters(db: Session) -> Dict[str, int]:
    """Seed ParameterDefinition rows if absent. Returns code -> id mapping."""
    from app.models.parameter import ParameterDefinition

    code_to_id: Dict[str, int] = {}
    for seed in _PARAMETER_SEEDS:
        existing = db.query(ParameterDefinition).filter_by(code=seed["code"]).first()
        if existing is None:
            param = ParameterDefinition(**seed)
            db.add(param)
            db.flush()
            code_to_id[seed["code"]] = param.id
            logger.info("Seeded ParameterDefinition: %s", seed["code"])
        else:
            code_to_id[seed["code"]] = existing.id
    db.commit()
    return code_to_id


def _seed_thresholds(db: Session, code_to_id: Dict[str, int]) -> None:
    """Seed ClassificationThreshold rows from the JSON seed file for both standards."""
    from app.models.threshold import ClassificationThreshold

    # Check if thresholds are already seeded
    existing_count = db.query(ClassificationThreshold).count()
    if existing_count > 0:
        logger.info("Thresholds already seeded (%d rows). Skipping.", existing_count)
        return

    seed_file = Path(settings.THRESHOLDS_SEED_FILE)
    if not seed_file.exists():
        logger.warning("Thresholds seed file not found: %s", seed_file)
        return

    with seed_file.open(encoding="utf-8") as fh:
        data = json.load(fh)

    standards = data.get("standards", {})
    for standard_name, standard_data in standards.items():
        parameters = standard_data.get("parameters", {})
        for param_code, param_data in parameters.items():
            param_id = code_to_id.get(param_code)
            if param_id is None:
                logger.warning("Unknown parameter code '%s' in thresholds seed. Skipping.", param_code)
                continue

            unit = param_data.get("unit", "")
            classes = param_data.get("classes", [])
            for sort_idx, cls in enumerate(classes):
                threshold = ClassificationThreshold(
                    parameter_def_id=param_id,
                    standard=standard_name,
                    class_label=cls["label"],
                    lower_bound=cls.get("lower_bound"),
                    upper_bound=cls.get("upper_bound"),
                    lower_inclusive=cls.get("lower_inclusive", True),
                    upper_inclusive=cls.get("upper_inclusive", False),
                    unit=unit,
                    sort_order=sort_idx,
                    status="active",
                    version=1,
                )
                db.add(threshold)

    db.commit()
    logger.info("Thresholds seeded for standards: %s", list(standards.keys()))


def seed_database(db: Session) -> None:
    """Seed ParameterDefinitions and ClassificationThresholds. Idempotent."""
    code_to_id = _seed_parameters(db)
    _seed_thresholds(db, code_to_id)


def seed_demo_data(db: Session) -> None:
    """Seed demo SoilSample rows from the CSV. Idempotent."""
    import csv
    from datetime import datetime

    from app.models.location import Location
    from app.models.parameter import ParameterDefinition
    from app.models.sample import SoilParameterValue, SoilSample

    # Skip if demo samples or any samples already exist
    existing_count = db.query(SoilSample).count()
    if existing_count > 0:
        logger.info("Samples already seeded (%d rows). Skipping.", existing_count)
        return

    demo_file = Path(settings.DEMO_DATA_FILE)
    if not demo_file.exists():
        logger.warning("Demo data file not found: %s", demo_file)
        return

    # Build parameter code -> ParameterDefinition mapping
    param_defs = {p.code: p for p in db.query(ParameterDefinition).all()}

    with demo_file.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            sample_code = row["sample_code"].strip()
            location_name = row.get("location_name", "").strip()
            district = row.get("district", "").strip() or None

            # Resolve or create Location
            location: Optional[Location] = None
            if location_name:
                location = db.query(Location).filter_by(name=location_name).first()
                if location is None:
                    location = Location(name=location_name, district=district)
                    db.add(location)
                    db.flush()

            # Parse sample date
            sample_date_str = row.get("sample_date", "").strip()
            try:
                sample_date = date.fromisoformat(sample_date_str)
            except ValueError:
                logger.warning("Invalid sample_date '%s' for %s. Skipping.", sample_date_str, sample_code)
                continue

            # Parse depth
            depth_raw = row.get("depth_cm", "").strip()
            depth_cm: Optional[float] = None
            if depth_raw:
                # Handle ranges like "0-20"
                if "-" in depth_raw:
                    parts = depth_raw.split("-")
                    try:
                        depth_cm = (float(parts[0]) + float(parts[1])) / 2.0
                    except ValueError:
                        depth_cm = None
                else:
                    try:
                        depth_cm = float(depth_raw)
                    except ValueError:
                        depth_cm = None

            sample = SoilSample(
                sample_code=sample_code,
                location_id=location.id if location else None,
                sample_date=sample_date,
                depth_cm=depth_cm,
                land_use=row.get("land_use", "").strip() or None,
                collector_name=row.get("collector_name", "").strip() or None,
                notes=row.get("notes", "").strip() or None,
                data_source="demo",
            )
            db.add(sample)
            db.flush()

            # Parameter values
            param_map = {
                "ph": ("ph", row.get("ph"), row.get("ph_method", "electrometric 1:2.5"), "pH"),
                "nitrogen": ("nitrogen", row.get("nitrogen_kg_ha"), row.get("nitrogen_method", "Alkaline KMnO4"), "kg/ha"),
                "phosphorus": ("phosphorus", row.get("phosphorus_kg_ha"), row.get("phosphorus_method", "Olsen"), "kg/ha"),
                "potassium": ("potassium", row.get("potassium_kg_ha"), row.get("potassium_method", "Neutral Normal Ammonium Acetate"), "kg/ha"),
            }

            for code, (param_code, raw_value, method, unit) in param_map.items():
                if raw_value is None or str(raw_value).strip() == "":
                    continue
                try:
                    value = float(str(raw_value).strip())
                except ValueError:
                    logger.warning("Invalid value '%s' for %s/%s. Skipping.", raw_value, sample_code, param_code)
                    continue

                param_def = param_defs.get(param_code)
                if param_def is None:
                    logger.warning("ParameterDefinition not found for code '%s'. Skipping.", param_code)
                    continue

                pv = SoilParameterValue(
                    sample_id=sample.id,
                    parameter_def_id=param_def.id,
                    value=value,
                    unit=unit,
                    test_method=method.strip() if method else "",
                )
                db.add(pv)

            db.flush()
            from app.services import classification_service
            classification_service.classify_and_store(db, sample)

    db.commit()
    logger.info("Demo data seeded from %s.", demo_file)
