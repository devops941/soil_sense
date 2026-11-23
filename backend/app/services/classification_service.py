from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import MissingParameterError
from app.models.classification_result import ClassificationResult
from app.models.sample import SoilSample, SoilParameterValue
from app.models.threshold import ClassificationThreshold
from app.models.parameter import ParameterDefinition
from app.schemas.statistics import NutrientIndex


@dataclass(frozen=True)
class ThresholdRule:
    parameter_code: str
    class_label: str
    lower_bound: Optional[float]
    upper_bound: Optional[float]
    lower_inclusive: bool
    upper_inclusive: bool
    unit: str


_PARAM_TO_CLASS_KEY: Dict[str, str] = {
    "ph": "ph_class",
    "nitrogen": "n_class",
    "phosphorus": "p_class",
    "potassium": "k_class",
}

_NUTRIENT_PARAMS: List[str] = ["nitrogen", "phosphorus", "potassium"]
_NUTRIENT_SYMBOLS: Dict[str, str] = {
    "nitrogen": "N",
    "phosphorus": "P",
    "potassium": "K",
}
_NUTRIENT_CLASS_KEYS: Dict[str, str] = {
    "nitrogen": "n_class",
    "phosphorus": "p_class",
    "potassium": "k_class",
}


def classify_value(value: float, rules: List[ThresholdRule]) -> Optional[str]:
    for rule in rules:
        lo = rule.lower_bound
        hi = rule.upper_bound

        if lo is None:
            lower_ok = True
        elif rule.lower_inclusive:
            lower_ok = value >= lo
        else:
            lower_ok = value > lo

        if hi is None:
            upper_ok = True
        elif rule.upper_inclusive:
            upper_ok = value <= hi
        else:
            upper_ok = value < hi

        if lower_ok and upper_ok:
            return rule.class_label
    return None


def determine_fertility_class(
    n_class: Optional[str],
    p_class: Optional[str],
    k_class: Optional[str],
) -> Optional[str]:
    """Determine overall sample fertility category (Low, Medium, High)
    using Rammoorthy & Bajaj (1969) / Parker scoring thresholds.
    """
    scores = []
    mapping = {"low": 1, "medium": 2, "high": 3}
    for c in [n_class, p_class, k_class]:
        if c and str(c).lower() in mapping:
            scores.append(mapping[str(c).lower()])
    if not scores:
        return None
    avg_score = sum(scores) / len(scores)
    score_rounded = round(avg_score, 2)
    if score_rounded < 1.67:
        return "Low"
    elif score_rounded <= 2.33:
        return "Medium"
    else:
        return "High"


def classify_sample(
    values: Dict[str, float],
    rules_by_param: Dict[str, List[ThresholdRule]],
) -> Dict[str, Optional[str]]:
    result: Dict[str, Optional[str]] = {
        "ph_class": None,
        "n_class": None,
        "p_class": None,
        "k_class": None,
        "fertility_class": None,
        "overall_status": None,
    }

    for param_code, class_key in _PARAM_TO_CLASS_KEY.items():
        rules = rules_by_param.get(param_code, [])
        val = values.get(param_code)
        if val is None:
            result[class_key] = None
        elif rules:
            result[class_key] = classify_value(val, rules)
        else:
            result[class_key] = None

    fertility_cls = determine_fertility_class(
        result.get("n_class"),
        result.get("p_class"),
        result.get("k_class"),
    )
    result["fertility_class"] = fertility_cls

    status_parts: List[str] = []
    for param_code in _NUTRIENT_PARAMS:
        class_key = _NUTRIENT_CLASS_KEYS[param_code]
        abbrev = _NUTRIENT_SYMBOLS.get(param_code, param_code[0].upper())
        label = result.get(class_key)
        if values.get(param_code) is None:
            status_parts.append(f"{abbrev}: pending")
        elif label is None:
            status_parts.append(f"{abbrev}: unclassified")
        else:
            status_parts.append(f"{abbrev}: {label.title()}")

    detail_str = " | ".join(status_parts)
    if fertility_cls:
        result["overall_status"] = f"{fertility_cls} Fertility ({detail_str})"
    else:
        result["overall_status"] = detail_str

    return result


def nutrient_index(class_counts: Dict[str, int]) -> tuple[float, str]:
    low = class_counts.get("low", 0)
    medium = class_counts.get("medium", 0)
    high = class_counts.get("high", 0)
    total = low + medium + high
    if total == 0:
        return (0.0, "N/A")
    ni = (1 * low + 2 * medium + 3 * high) / total
    if ni < 1.67:
        label = "Low"
    elif ni <= 2.33:
        label = "Medium"
    else:
        label = "High"
    return (round(ni, 3), label)


def compute_nutrient_indices(
    samples_classes: List[Dict],
    standard: str,
) -> List[NutrientIndex]:
    tallies: Dict[str, Dict[str, int]] = {
        p: {"low": 0, "medium": 0, "high": 0} for p in _NUTRIENT_PARAMS
    }

    for sample_cls in samples_classes:
        for param_code, class_key in _NUTRIENT_CLASS_KEYS.items():
            label = sample_cls.get(class_key)
            if label is None:
                continue
            label_lower = str(label).lower()
            if label_lower in tallies[param_code]:
                tallies[param_code][label_lower] += 1

    indices: List[NutrientIndex] = []
    for param_code in _NUTRIENT_PARAMS:
        ni_val, ni_label = nutrient_index(tallies[param_code])
        indices.append(
            NutrientIndex(
                parameter_code=param_code,
                index_value=ni_val,
                class_label=ni_label,
            )
        )
    return indices


def load_rules(
    db: Session,
    standard: str,
    status: str = "active",
) -> Dict[str, List[ThresholdRule]]:
    rows = (
        db.query(ClassificationThreshold, ParameterDefinition)
        .join(ParameterDefinition, ClassificationThreshold.parameter_def_id == ParameterDefinition.id)
        .filter(
            ClassificationThreshold.standard == standard,
            ClassificationThreshold.status == status,
        )
        .all()
    )

    rules_by_param: Dict[str, List[ThresholdRule]] = {}
    for threshold, param_def in rows:
        code = param_def.code
        rule = ThresholdRule(
            parameter_code=code,
            class_label=threshold.class_label,
            lower_bound=threshold.lower_bound,
            upper_bound=threshold.upper_bound,
            lower_inclusive=threshold.lower_inclusive,
            upper_inclusive=threshold.upper_inclusive,
            unit=threshold.unit,
        )
        rules_by_param.setdefault(code, []).append(rule)

    for code in rules_by_param:
        rules_by_param[code].sort(
            key=lambda r: (r.lower_bound is None, r.lower_bound or 0.0)
        )

    return rules_by_param


def classify_and_store(
    db: Session,
    sample: SoilSample,
    standard: Optional[str] = None,
) -> ClassificationResult:
    effective_standard = standard or settings.ACTIVE_STANDARD

    param_values: List[SoilParameterValue] = (
        db.query(SoilParameterValue)
        .join(ParameterDefinition, SoilParameterValue.parameter_def_id == ParameterDefinition.id)
        .filter(SoilParameterValue.sample_id == sample.id)
        .all()
    )

    if not param_values:
        raise MissingParameterError(
            f"Sample '{sample.sample_code}' has no parameter values to classify."
        )

    code_to_value: Dict[str, float] = {}
    for pv in param_values:
        param_def = db.get(ParameterDefinition, pv.parameter_def_id)
        if param_def:
            code_to_value[param_def.code] = pv.value

    rules_by_param = load_rules(db, effective_standard)

    classification = classify_sample(code_to_value, rules_by_param)

    existing = (
        db.query(ClassificationResult)
        .filter(ClassificationResult.sample_id == sample.id)
        .first()
    )

    if existing:
        existing.ph_class = classification.get("ph_class")
        existing.n_class = classification.get("n_class")
        existing.p_class = classification.get("p_class")
        existing.k_class = classification.get("k_class")
        existing.fertility_class = classification.get("fertility_class")
        existing.overall_status = classification.get("overall_status")
        existing.standard_used = effective_standard
        result_row = existing
    else:
        result_row = ClassificationResult(
            sample_id=sample.id,
            ph_class=classification.get("ph_class"),
            n_class=classification.get("n_class"),
            p_class=classification.get("p_class"),
            k_class=classification.get("k_class"),
            fertility_class=classification.get("fertility_class"),
            overall_status=classification.get("overall_status"),
            standard_used=effective_standard,
        )
        db.add(result_row)

    db.flush()
    if not db.in_nested_transaction():
        db.commit()
        db.refresh(result_row)
    return result_row
