from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from app.ml.persistence import load_model


@dataclass(frozen=True)
class ModelPackage:
    model: Any
    metadata: Dict[str, Any]


def load_model_package(model_path: str) -> ModelPackage:
    model = load_model(model_path)
    metadata = _load_metadata(model_path)
    return ModelPackage(model=model, metadata=metadata)


def _load_metadata(model_path: str) -> Dict[str, Any]:
    path = Path(model_path)
    meta_path = path.with_suffix(path.suffix + ".meta.json")
    if not meta_path.exists():
        return {
            "name": path.stem,
            "version": "unknown",
            "algorithm": "random_forest",
        }

    with meta_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if "name" not in data:
        data["name"] = path.stem
    if "version" not in data:
        data["version"] = "unknown"
    if "algorithm" not in data:
        data["algorithm"] = "random_forest"

    return data
