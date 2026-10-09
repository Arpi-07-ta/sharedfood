from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = PROJECT_ROOT / 'models'
MODEL_DIR.mkdir(exist_ok=True, parents=True)

NUMERIC_FEATURES = [
    'quantity',
    'preparation_time_hours',
    'remaining_shelf_life_hours',
    'demand',
    'historical_wastage_rate',
]
CATEGORICAL_FEATURES = ['food_category', 'storage_condition']
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def generate_synthetic_dataset(n_samples: int = 1200, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    categories = ['Produce', 'Bakery', 'Dairy', 'Prepared Meal', 'Pantry']
    storage_conditions = ['AMBIENT', 'REFRIGERATED', 'FROZEN', 'ROOM_TEMPERATURE']
    rows = []

    for _ in range(n_samples):
        category = rng.choice(categories)
        quantity = float(rng.uniform(0.5, 30.0))
        prep_hours = float(rng.uniform(0.5, 24.0))
        shelf_life = float(rng.uniform(2.0, 72.0))
        storage = rng.choice(storage_conditions)
        demand = float(rng.uniform(5.0, 100.0))
        historical_wastage = float(rng.uniform(0.0, 40.0))

        category_multiplier = {'Produce': 1.2, 'Bakery': 1.1, 'Dairy': 1.4, 'Prepared Meal': 1.6, 'Pantry': 0.7}[category]
        storage_multiplier = {'AMBIENT': 1.4, 'REFRIGERATED': 0.8, 'FROZEN': 0.3, 'ROOM_TEMPERATURE': 1.2}[storage]
        risk_score = (
            (quantity / 12.0) * 0.9
            + (max(0, 24 - shelf_life) / 24.0) * 1.5
            + (prep_hours / 24.0) * 0.8
            + (max(0, 100 - demand) / 100.0) * 0.9
            + (historical_wastage / 100.0) * 1.5
            + category_multiplier
            + storage_multiplier
        )
        label = 1 if risk_score > 4.8 else 0

        rows.append({
            'food_category': category,
            'quantity': quantity,
            'preparation_time_hours': prep_hours,
            'remaining_shelf_life_hours': shelf_life,
            'storage_condition': storage,
            'demand': demand,
            'historical_wastage_rate': historical_wastage,
            'risk_label': label,
        })

    return pd.DataFrame(rows, columns=FEATURE_COLUMNS + ['risk_label'])


def build_pipeline() -> Pipeline:
    numeric_transformer = Pipeline(
        steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler()),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('encoder', OneHotEncoder(handle_unknown='ignore')),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ('numeric', numeric_transformer, NUMERIC_FEATURES),
            ('categorical', categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )
    model = RandomForestClassifier(
        n_estimators=250,
        max_depth=None,
        random_state=42,
        class_weight='balanced',
    )
    return Pipeline(steps=[('preprocessor', preprocessor), ('classifier', model)])


def train_and_evaluate() -> dict:
    dataset = generate_synthetic_dataset()
    X = dataset[FEATURE_COLUMNS]
    y = dataset['risk_label']
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions, output_dict=True)

    model_path = MODEL_DIR / 'food_waste_prototype.joblib'
    metadata_path = MODEL_DIR / 'food_waste_model_metadata.json'
    joblib.dump(pipeline, model_path)

    metadata = {
        'model_name': 'food_waste_prototype',
        'model_version': 'prototype-random-forest-v1',
        'dataset_type': 'synthetic-prototype',
        'accuracy': float(accuracy),
        'classification_report': report,
        'features': FEATURE_COLUMNS,
        'notes': 'This is a prototype model trained on a synthetic rule-based dataset because no real historical food waste labels were available in the repository.',
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')

    return metadata


if __name__ == '__main__':
    metadata = train_and_evaluate()
    print(json.dumps({
        'model_name': metadata['model_name'],
        'accuracy': metadata['accuracy'],
        'dataset_type': metadata['dataset_type'],
        'model_path': str(MODEL_DIR / 'food_waste_prototype.joblib'),
    }, indent=2))
