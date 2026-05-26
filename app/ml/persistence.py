from pathlib import Path
from typing import Any

import joblib


def save_model(model: Any, path: str) -> None:
    model_path = Path(path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)


def load_model(path: str) -> Any:
    return joblib.load(path)
