from dataclasses import dataclass
from typing import Iterable, List

import pandas as pd

@dataclass(frozen=True)
class SchemaSpec:
    required_columns: List[str]
    target_column: str

@dataclass(frozen=True)
class RangeRule:
    column: str
    min_value: float | None = None
    max_value: float | None = None


def validate_schema(df: pd.DataFrame, spec: SchemaSpec) -> None:
    missing = [col for col in spec.required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if spec.target_column not in df.columns:
        raise ValueError(f"Missing target column: {spec.target_column}")


def validate_ranges(df: pd.DataFrame, rules: Iterable[RangeRule]) -> None:
    for rule in rules:
        if rule.column not in df.columns:
            continue
        series = df[rule.column]
        if rule.min_value is not None and (series < rule.min_value).any():
            raise ValueError(f"{rule.column} has values below {rule.min_value}")
        if rule.max_value is not None and (series > rule.max_value).any():
            raise ValueError(f"{rule.column} has values above {rule.max_value}")
