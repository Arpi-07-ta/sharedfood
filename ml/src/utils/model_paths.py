from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = PROJECT_ROOT / 'models'
WASTE_MODEL_PATH = MODEL_DIR / 'food_waste_prototype.joblib'
WASTE_METADATA_PATH = MODEL_DIR / 'food_waste_model_metadata.json'
