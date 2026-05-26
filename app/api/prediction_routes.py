from typing import Dict

from flask import Blueprint, current_app, render_template, request

from app.api.schemas import PredictionRequestSchema
from app.core.api_utils import ok, validate_json
from app.services.prediction_service import PredictionService

prediction_bp = Blueprint("prediction", __name__)
prediction_page_bp = Blueprint("prediction_page", __name__)


@prediction_bp.post("/api/predict")
def predict():
    payload = request.get_json(silent=True)
    data = validate_json(PredictionRequestSchema(), payload)
    include_explainability = bool(data.get("include_explainability", False))

    service = PredictionService(model_path=current_app.config["MODEL_PATH"])
    result = service.predict(data, include_explainability=include_explainability)

    return ok(result)


@prediction_page_bp.get("/predictions")
def predictions_page():
    return render_template("predictions.html", active_page="predictions")
