"""Model evaluation utilities for FoodShare AI."""


def summarize_metrics(y_true, y_pred):
    """A minimal placeholder metric summary for future validation."""
    return {
        'samples': len(y_true),
        'mae': None,
        'rmse': None,
    }
