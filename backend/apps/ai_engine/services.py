from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.src.inference.urgency_service import calculate_urgency
from ml.src.inference.waste_predictor import FoodWastePrototypePredictor


def predict_food_waste(payload):
    feature_input = {
        'food_category': payload.get('food_category', ''),
        'quantity': Decimal(str(payload.get('quantity', 0))),
        'preparation_time_hours': Decimal(str(payload.get('preparation_time_hours', 0) or 0)),
        'remaining_shelf_life_hours': Decimal(str(payload.get('remaining_shelf_life_hours', 0))),
        'storage_condition': payload.get('storage_condition', 'AMBIENT'),
        'demand': Decimal(str(payload.get('demand', 0))),
        'historical_wastage_rate': Decimal(str(payload.get('historical_wastage_rate', 0))),
    }
    predictor = FoodWastePrototypePredictor()
    return predictor.predict(feature_input)


def calculate_food_urgency(payload):
    feature_input = {
        'food_category': payload.get('food_category', ''),
        'quantity': Decimal(str(payload.get('quantity', 0))),
        'remaining_shelf_life_hours': Decimal(str(payload.get('remaining_shelf_life_hours', 0))),
        'storage_condition': payload.get('storage_condition', 'AMBIENT'),
        'demand': Decimal(str(payload.get('demand', 0))),
        'preparation_time_hours': Decimal(str(payload.get('preparation_time_hours', 0) or 0)),
    }
    return calculate_urgency(feature_input)
