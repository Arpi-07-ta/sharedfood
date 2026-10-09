"""Feature engineering for inventory and donation forecasting."""


def engineer_features(dataset):
    """Placeholder feature engineering function."""
    dataset = dataset.copy()
    dataset['day_of_week'] = dataset['date'].dt.dayofweek
    return dataset
