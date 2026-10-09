# FoodShare AI / ML documentation

## Overview
This ML layer provides two separate services:

1. Food wastage risk prediction using a scikit-learn pipeline and a prototype classification model.
2. Food donation urgency calculation using a transparent, deterministic scoring function.

The wastage model is intentionally separated from the urgency rule engine. The urgency service is not a trained ML model and is documented as such.

## Fraud and risk detection
The fraud detection module is a separate, deterministic **rule-based triage service**, not trained ML. No labeled fraud dataset is available, so it does not claim prediction accuracy or calibrated probabilities. It evaluates duplicate-like donation submissions, repeated cancellations, implausible quantities, repeated open complaints against a donor's donations, frequent submissions, and abnormal donation activity. Each alert stores a bounded 0–100 risk score, LOW/MEDIUM/HIGH/CRITICAL level, reason codes, rule version, and review status.

Thresholds, look-back windows, similarity limits, quantity limit, and rule point values are environment-configurable via Django settings. Score thresholds classify review priority; they do not decide guilt. Alerts are deduplicated while unresolved and shown only through admin-authorized review APIs. The service does not ban, suspend, or otherwise automatically penalize users. Human reviewers record an outcome and audit entry. False-positive risk remains, especially for legitimate bulk donors, repeated operational cancellations, and complaints; thresholds should be reviewed against operational data before production use.

See [FRAUD_DETECTION_DOCUMENTATION.md](FRAUD_DETECTION_DOCUMENTATION.md) for signal definitions, default point values and thresholds, configuration variables, review lifecycle, and operational limitations.

## Prototype status
The repository does not include a real production-labelled food waste dataset. Because of that, the current wastage prediction service is a prototype trained on a synthetic, rule-based dataset. It is suitable for demo and integration validation, but it is not a production-grade waste forecast model.

The implementation does not present the urgency score as a trained ML prediction. It is a transparent rule-based calculation based on observable donation characteristics.

## Service responsibilities
### 1) Food wastage risk prediction
Input features accepted by the API:
- food_category
- quantity
- preparation_time_hours
- remaining_shelf_life_hours
- storage_condition
- demand
- historical_wastage_rate

The model pipeline uses:
- a numeric preprocessing step with median imputation and standard scaling
- a categorical preprocessing step with most-frequent imputation and one-hot encoding
- a RandomForestClassifier trained on a synthetic rule-based prototype dataset

### 2) Food donation urgency calculation
Input features accepted by the API:
- food_category
- quantity
- remaining_shelf_life_hours
- storage_condition
- demand
- preparation_time_hours (optional)

Urgency is calculated as a deterministic score from 0 to 100 using factors such as:
- remaining shelf life
- category perishability
- storage condition
- demand level
- donation quantity
- preparation delay

The output is a label: LOW, MEDIUM, HIGH, or CRITICAL.

## Directory layout
- `ml/src/training/train_waste_model.py` — synthetic data generation, model training, persistence, and metadata export.
- `ml/src/inference/waste_predictor.py` — model loading and inference logic for wastage prediction.
- `ml/src/inference/urgency_service.py` — deterministic urgency scoring for donations.
- `ml/src/evaluation/evaluate_waste_model.py` — evaluation script that computes hold-out accuracy on the synthetic prototype data.
- `ml/models/` — saved model artifacts and metadata.

## Data and feature design
The prototype model intentionally uses a small, transparent feature set that matches the business needs of FoodShare AI.

| Feature | Type | Notes |
| --- | --- | --- |
| food_category | categorical | e.g. Produce, Bakery, Dairy, Prepared Meal |
| quantity | numeric | donation volume in kg or relevant unit |
| preparation_time_hours | numeric | time between prep and expected use |
| remaining_shelf_life_hours | numeric | critical for perishability |
| storage_condition | categorical | AMBIENT, REFRIGERATED, FROZEN, ROOM_TEMPERATURE |
| demand | numeric | demand signal from 0-100 |
| historical_wastage_rate | numeric | historical spoilage signal from 0-100 |

## Preprocessing and training pipeline
The training script builds a scikit-learn Pipeline with a `ColumnTransformer`:

- numeric columns receive median imputation and standard scaling
- categorical columns receive most-frequent imputation and one-hot encoding
- the classifier is a `RandomForestClassifier`

The model artifact is saved with `joblib` to `ml/models/food_waste_prototype.joblib`.

The metadata file stores:
- model name
- version
- dataset type
- hold-out accuracy
- notes about the prototype status

## Evaluation process
The evaluation script runs a proper train/test split with `train_test_split` and reports a measured hold-out accuracy. This is the only accuracy value used in documentation and output.

Important caveats:
- the accuracy is measured on synthetic prototype data only
- it should not be interpreted as a real-world deployment metric
- real-world validation will be required before claiming production readiness

## Inference and API usage
The Django API exposes:
- `POST /api/ai/predict-wastage/`
- `POST /api/ai/calculate-urgency/`

The wastage endpoint returns:
- risk_label
- risk_probability
- predicted_waste_kg
- model_status
- model_version
- generated_at

The urgency endpoint returns:
- urgency_score
- urgency_level
- explanation

## Database persistence
Prediction history is stored via the Django model in `apps.ai_engine.models`:
- `FoodWastePrediction` stores the generated risk prediction and feature summary.
- `AIRecommendation` stores urgency calculation output for donation records when a donation id is provided.

## Limitations
- No real food-waste labels were present in the repository, so the current model is trained on synthetic data.
- The model should be considered a prototype until a verified production dataset is obtained.
- The urgency calculation is rule-based and is intentionally separate from the trained wastage model.
- There is no claim that the model is calibrated for live operational decisions yet.

## Future improvements
- Replace synthetic labels with a real donation and waste dataset.
- Add richer historical features such as lead time, retailer demand, and weather effects.
- Monitor drift over time in production.
- Add calibration, threshold tuning, and a dedicated retraining pipeline.
- Move model training to a reproducible MLOps workflow with versioned datasets and experiments.

