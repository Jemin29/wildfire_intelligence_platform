from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.compose import ColumnTransformer
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

from app.ml.preprocessing import PreprocessConfig, build_preprocessor

@dataclass(frozen=True)
class ModelSpec:
    name: str
    estimator: BaseEstimator
    param_grid: Dict[str, List]


def build_model_specs(random_state: int) -> List[ModelSpec]:
    return [
        ModelSpec(
            name="random_forest",
            estimator=RandomForestClassifier(
                n_estimators=200,
                random_state=random_state,
                class_weight="balanced",
                n_jobs=-1,
            ),
            param_grid={
                "model__n_estimators": [200, 400],
                "model__max_depth": [None, 10, 20],
                "model__min_samples_split": [2, 5],
            },
        ),
        ModelSpec(
            name="xgboost",
            estimator=XGBClassifier(
                n_estimators=300,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.9,
                colsample_bytree=0.9,
                eval_metric="logloss",
                random_state=random_state,
                n_jobs=-1,
                tree_method="hist",
            ),
            param_grid={
                "model__n_estimators": [200, 400],
                "model__max_depth": [4, 6, 8],
                "model__learning_rate": [0.05, 0.1],
            },
        ),
        ModelSpec(
            name="decision_tree",
            estimator=DecisionTreeClassifier(
                random_state=random_state,
                class_weight="balanced",
            ),
            param_grid={
                "model__max_depth": [None, 5, 10, 20],
                "model__min_samples_split": [2, 5, 10],
            },
        ),
    ]


def build_model_pipeline(config: PreprocessConfig, estimator: BaseEstimator) -> Pipeline:
    preprocessor = build_preprocessor(config)
    selector = SelectKBest(score_func=mutual_info_classif, k=config.k_best)
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("selector", selector),
            ("model", estimator),
        ]
    )


def get_feature_names(
    preprocessor: ColumnTransformer,
    config: PreprocessConfig,
) -> List[str]:
    numeric_names = list(config.numeric_features)
    categorical_names: List[str] = []

    if config.categorical_features:
        encoder = preprocessor.named_transformers_["cat"].named_steps["encoder"]
        if isinstance(encoder, OneHotEncoder):
            categorical_names = list(
                encoder.get_feature_names_out(config.categorical_features)
            )

    return numeric_names + categorical_names


def build_feature_importance_frame(
    pipeline: Pipeline,
    config: PreprocessConfig,
) -> pd.DataFrame:
    preprocessor = pipeline.named_steps["preprocessor"]
    selector = pipeline.named_steps["selector"]
    model = pipeline.named_steps["model"]

    if not hasattr(model, "feature_importances_"):
        return pd.DataFrame(columns=["feature", "importance"])

    names = get_feature_names(preprocessor, config)
    support = selector.get_support()
    selected_names = [name for name, keep in zip(names, support) if keep]

    importances = model.feature_importances_
    if len(importances) != len(selected_names):
        return pd.DataFrame(columns=["feature", "importance"])

    frame = pd.DataFrame(
        {
            "feature": selected_names,
            "importance": importances,
        }
    )
    frame = frame.sort_values("importance", ascending=False).reset_index(drop=True)
    return frame


def format_metrics_table(metrics: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    rows: List[Tuple[str, float, float, float, float]] = []
    for name, values in metrics.items():
        rows.append(
            (
                name,
                values["accuracy"],
                values["precision"],
                values["recall"],
                values["f1"],
            )
        )
    return pd.DataFrame(
        rows,
        columns=["model", "accuracy", "precision", "recall", "f1"],
    ).sort_values("f1", ascending=False)
