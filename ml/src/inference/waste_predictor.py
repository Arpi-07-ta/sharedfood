from __future__ import annotations

import json
import sys
from decimal import Decimal
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

MODEL_DIR = PROJECT_ROOT / 'models'
MODEL_PATH = MODEL_DIR / 'food_waste_prototype.joblib'
METADATA_PATH = MODEL_DIR / 'food_waste_model_metadata.json'

FEATURE_COLUMNS = [
    'quantity',
    'preparation_time_hours',
    'remaining_shelf_life_hours',
    'demand',
    'historical_wastage_rate',
    'food_category',
    'storage_condition',
]


class FoodWastePrototypePredictor:
    def __init__(self, model_path: str | Path | None = None):
        self.model_path = Path(model_path) if model_path else MODEL_PATH
        if not self.model_path.exists():
            raise FileNotFoundError(
                'The prototype wastage model was not found. Run the training script in ml/src/training/train_waste_model.py to generate it.'
            )
        self.model = joblib.load(self.model_path)
        self.metadata = self._load_metadata()

    def _load_metadata(self):
        if METADATA_PATH.exists():
            return json.loads(METADATA_PATH.read_text(encoding='utf-8'))
        return {'model_version': 'prototype-random-forest-v1', 'dataset_type': 'synthetic-prototype'}

    def _prepare_input(self, payload: dict) -> pd.DataFrame:
        normalized = {
            'quantity': float(payload.get('quantity', 0.0)),
            'preparation_time_hours': float(payload.get('preparation_time_hours', 0.0) or 0.0),
            'remaining_shelf_life_hours': float(payload.get('remaining_shelf_life_hours', 0.0) or 0.0),
            'demand': float(payload.get('demand', 0.0) or 0.0),
            'historical_wastage_rate': float(payload.get('historical_wastage_rate', 0.0) or 0.0),
            'food_category': str(payload.get('food_category', '')).title(),
            'storage_condition': str(payload.get('storage_condition', 'AMBIENT')).upper(),
        }
        feature_row = pd.DataFrame([normalized], columns=FEATURE_COLUMNS)
        return feature_row

    def predict(self, payload: dict) -> dict:
        feature_frame = self._prepare_input(payload)
        prediction = int(self.model.predict(feature_frame)[0])
        probabilities = self.model.predict_proba(feature_frame)[0]
        risk_probability = float(probabilities[prediction])
        risk_label = 'HIGH' if prediction == 1 else 'LOW'

        quantity = float(feature_frame.iloc[0]['quantity'])
        historical_wastage = float(feature_frame.iloc[0]['historical_wastage_rate'])
        shelf_life = float(feature_frame.iloc[0]['remaining_shelf_life_hours'])
        predicted_waste_kg = max(0.0, round(quantity * (0.08 + (historical_wastage / 100) * 0.8 + max(0.0, 24 - shelf_life) / 72.0), 2))

        urgency_signal = 'high' if prediction == 1 else 'moderate' if risk_probability > 0.4 else 'low'
        return {
            'risk_label': risk_label,
            'risk_probability': round(risk_probability, 4),
            'predicted_waste_kg': predicted_waste_kg,
            'model_status': 'prototype',
            'model_version': self.metadata.get('model_version', 'prototype-random-forest-v1'),
            'feature_summary': {
                'food_category': feature_frame.iloc[0]['food_category'],
                'quantity': quantity,
                'remaining_shelf_life_hours': shelf_life,
                'storage_condition': feature_frame.iloc[0]['storage_condition'],
                'demand': float(feature_frame.iloc[0]['demand']),
            },
            'urgency_signal': urgency_signal,
        }
