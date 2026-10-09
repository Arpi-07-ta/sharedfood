from __future__ import annotations

from decimal import Decimal


def calculate_urgency(payload: dict) -> dict:
    food_category = str(payload.get('food_category', '')).title()
    quantity = float(payload.get('quantity', 0.0) or 0.0)
    remaining_shelf_life = float(payload.get('remaining_shelf_life_hours', 0.0) or 0.0)
    storage_condition = str(payload.get('storage_condition', 'AMBIENT')).upper()
    demand = float(payload.get('demand', 0.0) or 0.0)
    preparation_time_hours = float(payload.get('preparation_time_hours', 0.0) or 0.0)

    score = 0.0
    reasons = []

    category_weights = {
        'Produce': 18,
        'Bakery': 14,
        'Dairy': 17,
        'Prepared Meal': 22,
        'Pantry': 8,
    }
    score += category_weights.get(food_category, 12)
    reasons.append(f'{food_category} category is perishable enough to require priority handling.')

    if remaining_shelf_life <= 12:
        score += 35
        reasons.append('Only a very short shelf life remains.')
    elif remaining_shelf_life <= 24:
        score += 20
        reasons.append('Shelf life is limited but still workable.')

    if storage_condition in {'AMBIENT', 'ROOM_TEMPERATURE'}:
        score += 15
        reasons.append('Ambient storage increases the likelihood of quality loss.')
    elif storage_condition == 'REFRIGERATED':
        score += 8
        reasons.append('Refrigerated storage helps but still needs attention.')

    if demand >= 70:
        score += 12
        reasons.append('Current demand is strong, so this donation can move quickly.')
    elif demand >= 40:
        score += 6
        reasons.append('There is moderate market demand for this donation.')

    if quantity >= 10:
        score += 10
        reasons.append('A larger donation volume raises urgency for timely pickup.')
    elif quantity >= 5:
        score += 5
        reasons.append('Quantity is material enough to warrant a quick response.')

    if preparation_time_hours and preparation_time_hours >= 4:
        score += 8
        reasons.append('The preparation window is longer, which increases the need for prompt action.')

    score = min(100.0, max(0.0, score))

    if score >= 75:
        urgency_level = 'CRITICAL'
    elif score >= 50:
        urgency_level = 'HIGH'
    elif score >= 25:
        urgency_level = 'MEDIUM'
    else:
        urgency_level = 'LOW'

    explanation = ' '.join(reasons)

    return {
        'urgency_score': round(score, 2),
        'urgency_level': urgency_level,
        'explanation': explanation,
    }
