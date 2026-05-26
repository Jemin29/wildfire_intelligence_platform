from __future__ import annotations

from typing import Any, Dict, Iterable

import pandas as pd

REQUIRED_FEATURES = [
    "temperature",
    "humidity",
    "rainfall",
    "wind_speed",
    "vegetation",
    "soil_moisture",
]

FEATURE_RANGES = {
    "temperature": (-50.0, 70.0),
    "humidity": (0.0, 100.0),
    "rainfall": (0.0, 500.0),
    "wind_speed": (0.0, 120.0),
    "vegetation": (0.0, 1.0),
    "soil_moisture": (0.0, 1.0),
}


def validate_payload(payload: Dict[str, Any], required: Iterable[str]) -> Dict[str, float]:
    missing = [feature for feature in required if feature not in payload]
    if missing:
        raise ValueError(f"Missing required features: {missing}")

    cleaned: Dict[str, float] = {}
    for feature in required:
        value = payload.get(feature)
        if value is None:
            raise ValueError(f"Feature '{feature}' must be provided")
        try:
            cleaned[feature] = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Feature '{feature}' must be numeric") from exc

        if feature in FEATURE_RANGES:
            min_value, max_value = FEATURE_RANGES[feature]
            if cleaned[feature] < min_value or cleaned[feature] > max_value:
                raise ValueError(
                    f"Feature '{feature}' must be between {min_value} and {max_value}"
                )

    return cleaned


def build_feature_frame(features: Dict[str, float]) -> pd.DataFrame:
    return pd.DataFrame([features])


def build_feature_importance(model: Any, frame: pd.DataFrame) -> Dict[str, Any]:
    if hasattr(model, "named_steps"):
        model_step = model.named_steps.get("model")
        preprocessor = model.named_steps.get("preprocessor")
    else:
        model_step = model
        preprocessor = None

    if model_step is None or not hasattr(model_step, "feature_importances_"):
        return {"available": False}

    importances = getattr(model_step, "feature_importances_", [])
    if not importances:
        return {"available": False}

    if preprocessor is not None and hasattr(preprocessor, "get_feature_names_out"):
        names = list(preprocessor.get_feature_names_out())
    else:
        names = list(frame.columns)

    pairs = sorted(
        zip(names, importances),
        key=lambda item: item[1],
        reverse=True,
    )

    top = [{"feature": name, "importance": float(score)} for name, score in pairs[:10]]
    return {"available": True, "top_features": top}
