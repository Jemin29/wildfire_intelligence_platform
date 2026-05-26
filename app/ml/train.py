import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
from sklearn.model_selection import GridSearchCV, StratifiedKFold

from app.ml.evaluation import build_confusion_matrix, evaluate_predictions
from app.ml.modeling import (
    ModelSpec,
    build_feature_importance_frame,
    build_model_pipeline,
    build_model_specs,
    format_metrics_table,
)
from app.ml.preprocessing import PreprocessConfig, cap_outliers_iqr, split_data
from app.ml.validation import RangeRule, SchemaSpec, validate_ranges, validate_schema
from app.ml.persistence import save_model
from app.utils.logging_config import setup_logging

LOGGER = setup_logging("training")

@dataclass(frozen=True)
class TrainingArtifacts:
    metrics: Dict[str, Dict[str, float]]
    confusion_matrices: Dict[str, List[List[int]]]
    best_model_name: str
    best_model_path: str


def train_models(
    df: pd.DataFrame,
    preprocess_config: PreprocessConfig,
    schema_spec: SchemaSpec,
    range_rules: List[RangeRule],
    model_dir: str = "models",
) -> TrainingArtifacts:
    LOGGER.info("Validating schema")
    validate_schema(df, schema_spec)

    LOGGER.info("Validating feature ranges")
    validate_ranges(df, range_rules)

    LOGGER.info("Capping outliers")
    df = cap_outliers_iqr(df, preprocess_config.numeric_features)

    LOGGER.info("Splitting data")
    X_train, X_test, y_train, y_test = split_data(df, preprocess_config)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=preprocess_config.random_state)
    metrics: Dict[str, Dict[str, float]] = {}
    confusion_matrices: Dict[str, List[List[int]]] = {}
    best_model_name = ""
    best_model_score = -1.0
    best_model_path = ""

    for spec in build_model_specs(preprocess_config.random_state):
        LOGGER.info("Training %s", spec.name)
        pipeline = build_model_pipeline(preprocess_config, spec.estimator)

        search = GridSearchCV(
            pipeline,
            spec.param_grid,
            scoring="f1",
            cv=cv,
            n_jobs=-1,
        )
        search.fit(X_train, y_train)

        LOGGER.info("Best params for %s: %s", spec.name, search.best_params_)
        best_pipeline = search.best_estimator_

        y_pred = best_pipeline.predict(X_test)
        metrics[spec.name] = evaluate_predictions(y_test, y_pred)
        confusion_matrices[spec.name] = build_confusion_matrix(y_test, y_pred).tolist()

        if metrics[spec.name]["f1"] > best_model_score:
            best_model_score = metrics[spec.name]["f1"]
            best_model_name = spec.name
            best_model_path = str(Path(model_dir) / f"{spec.name}_pipeline.joblib")
            save_model(best_pipeline, best_model_path)

        feature_frame = build_feature_importance_frame(best_pipeline, preprocess_config)
        if not feature_frame.empty:
            LOGGER.info("Top features for %s:\n%s", spec.name, feature_frame.head(10))

    metrics_table = format_metrics_table(metrics)
    LOGGER.info("Model comparison:\n%s", metrics_table)

    return TrainingArtifacts(
        metrics=metrics,
        confusion_matrices=confusion_matrices,
        best_model_name=best_model_name,
        best_model_path=best_model_path,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train wildfire prediction models")
    parser.add_argument("--data", required=True, help="Path to CSV dataset")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.data)

    preprocess_config = PreprocessConfig(
        numeric_features=[
            "temperature",
            "humidity",
            "rainfall",
            "wind_speed",
            "vegetation",
            "soil_moisture",
        ],
        categorical_features=[],
        target_column="fire_occurrence",
        test_size=0.2,
        random_state=42,
        k_best=6,
    )

    schema_spec = SchemaSpec(
        required_columns=[
            "temperature",
            "humidity",
            "rainfall",
            "wind_speed",
            "vegetation",
            "soil_moisture",
            "fire_occurrence",
        ],
        target_column="fire_occurrence",
    )

    range_rules = [
        RangeRule(column="temperature", min_value=-60, max_value=60),
        RangeRule(column="humidity", min_value=0, max_value=100),
        RangeRule(column="rainfall", min_value=0),
        RangeRule(column="wind_speed", min_value=0),
        RangeRule(column="vegetation", min_value=0, max_value=1),
        RangeRule(column="soil_moisture", min_value=0, max_value=1),
    ]

    artifacts = train_models(
        df,
        preprocess_config,
        schema_spec,
        range_rules,
    )

    LOGGER.info("Best model: %s", artifacts.best_model_name)
    LOGGER.info("Saved at: %s", artifacts.best_model_path)


if __name__ == "__main__":
    main()
