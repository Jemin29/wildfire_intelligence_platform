from __future__ import annotations

import time
from typing import Any, Dict, Optional
from uuid import uuid4

from app.core.errors import ModelNotReadyError, ValidationError
from app.core.extensions import db
from app.db.models import InferenceLog, RiskPrediction
from app.ml.inference import (
    REQUIRED_FEATURES,
    build_feature_frame,
    build_feature_importance,
    validate_payload,
)
from app.ml.model_loader import load_model_package


class PredictionService:
    def __init__(self, model_path: str) -> None:
        self.model_path = model_path
        self._package = None

    def _get_package(self):
        if self._package is None:
            try:
                self._package = load_model_package(self.model_path)
            except FileNotFoundError as exc:
                raise ModelNotReadyError(
                    "Model not found. Train and save a pipeline before predicting.",
                ) from exc
        return self._package

    def predict(self, payload: Dict[str, Any], include_explainability: bool = False) -> Dict[str, Any]:
        start_time = time.perf_counter()
        request_id = payload.get("request_id") or uuid4().hex

        try:
            features = validate_payload(payload, REQUIRED_FEATURES)
        except ValueError as exc:
            self._log_inference(request_id, "invalid_payload", 0)
            raise ValidationError(str(exc)) from exc

        package = self._get_package()
        model = package.model
        frame = build_feature_frame(features)

        prediction = model.predict(frame)[0]
        confidence = _compute_confidence(model, frame)
        latency_ms = int((time.perf_counter() - start_time) * 1000)

        response = {
            "prediction": int(prediction),
            "confidence": confidence,
            "model": package.metadata,
            "request_id": request_id,
        }

        if include_explainability:
            response["explainability"] = build_feature_importance(model, frame)

        self._log_inference(request_id, "success", latency_ms, model_version=package.metadata.get("version"))
        self._log_prediction(payload, prediction, confidence, package.metadata.get("version"))

        return response

    def _log_inference(
        self,
        request_id: str,
        status: str,
        latency_ms: int,
        model_version: Optional[str] = None,
    ) -> None:
        try:
            log = InferenceLog(
                request_id=request_id,
                status=status,
                latency_ms=latency_ms,
                model_version=model_version,
            )
            db.session.add(log)
            db.session.commit()
        except Exception:
            db.session.rollback()

    def _log_prediction(
        self,
        payload: Dict[str, Any],
        prediction: int,
        confidence: float,
        model_version: Optional[str],
    ) -> None:
        lat = payload.get("lat")
        lon = payload.get("lon")
        if lat is None or lon is None:
            return

        try:
            record = RiskPrediction(
                lat=float(lat),
                lon=float(lon),
                prediction=int(prediction),
                probability=float(confidence),
                model_version=model_version,
            )
            db.session.add(record)
            db.session.commit()
        except Exception:
            db.session.rollback()


def _compute_confidence(model: Any, frame) -> float:
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(frame)[0]
        if hasattr(model, "classes_") and len(model.classes_) == 2:
            classes = list(model.classes_)
            index = classes.index(1) if 1 in classes else 1
        else:
            index = int(proba.argmax())
        return float(proba[index])

    if hasattr(model, "decision_function"):
        score = model.decision_function(frame)[0]
        return float(1 / (1 + pow(2.718281828459045, -score)))

    return 0.5
