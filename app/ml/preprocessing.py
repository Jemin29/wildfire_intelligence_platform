from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.ml.validation import RangeRule, SchemaSpec, validate_ranges, validate_schema
from app.utils.logging_config import setup_logging

LOGGER = setup_logging("preprocessing")

@dataclass(frozen=True)
class PreprocessConfig:
    numeric_features: List[str]
    categorical_features: List[str]
    target_column: str
    test_size: float = 0.2
    random_state: int = 42
    k_best: int = 10


def cap_outliers_iqr(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    capped = df.copy()
    for col in columns:
        if col not in capped.columns:
            continue
        q1 = capped[col].quantile(0.25)
        q3 = capped[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        capped[col] = capped[col].clip(lower=lower, upper=upper)
    return capped


def build_preprocessor(config: PreprocessConfig) -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, config.numeric_features),
            ("cat", categorical_pipeline, config.categorical_features),
        ]
    )


def build_pipeline(config: PreprocessConfig) -> Pipeline:
    preprocessor = build_preprocessor(config)
    selector = SelectKBest(score_func=mutual_info_classif, k=config.k_best)

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("selector", selector),
        ]
    )
    return pipeline


def split_data(
    df: pd.DataFrame, config: PreprocessConfig
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    X = df.drop(columns=[config.target_column])
    y = df[config.target_column]
    return train_test_split(
        X,
        y,
        test_size=config.test_size,
        random_state=config.random_state,
        stratify=y,
    )


def preprocess_dataset(
    df: pd.DataFrame,
    config: PreprocessConfig,
    schema_spec: SchemaSpec,
    range_rules: List[RangeRule],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Pipeline]:
    LOGGER.info("Validating schema")
    validate_schema(df, schema_spec)

    LOGGER.info("Validating feature ranges")
    validate_ranges(df, range_rules)

    LOGGER.info("Capping outliers")
    df = cap_outliers_iqr(df, config.numeric_features)

    LOGGER.info("Splitting data")
    X_train, X_test, y_train, y_test = split_data(df, config)

    LOGGER.info("Building preprocessing pipeline")
    pipeline = build_pipeline(config)

    LOGGER.info("Fitting pipeline")
    X_train_processed = pipeline.fit_transform(X_train, y_train)
    X_test_processed = pipeline.transform(X_test)

    return X_train_processed, X_test_processed, y_train.to_numpy(), y_test.to_numpy(), pipeline
