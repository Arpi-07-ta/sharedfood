from __future__ import annotations

import json
from pathlib import Path

import joblib

from ml.src.training.train_waste_model import train_and_evaluate

MODEL_PATH = Path(__file__).resolve().parents[2] / 'models' / 'food_waste_prototype.joblib'


if __name__ == '__main__':
    metadata = train_and_evaluate()
    model = joblib.load(MODEL_PATH)
    print(json.dumps({
        'model_name': metadata['model_name'],
        'model_version': metadata['model_version'],
        'dataset_type': metadata['dataset_type'],
        'holdout_accuracy': round(metadata['accuracy'], 4),
        'notes': metadata['notes'],
    }, indent=2))
