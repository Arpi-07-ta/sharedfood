"""Data cleaning routines for the FoodShare AI ML pipeline."""


def clean_dataset(raw_df):
    """Return a cleaned dataset placeholder for future feature preparation."""
    cleaned = raw_df.copy()
    cleaned = cleaned.dropna(subset=['date'])
    return cleaned
