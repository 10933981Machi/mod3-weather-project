"""
predictor.py

Trains a RandomForestClassifier on the weather training data to predict
whether it will rain tomorrow (RainTomorrow column).
Uses scikit-learn for model training, evaluation, and prediction.
"""

import pandas as pd
import logging
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)

# Features used for prediction
FEATURES = [
    "MinTemp", "MaxTemp", "Rainfall",
    "Humidity9am", "Humidity3pm",
    "Pressure9am", "Pressure3pm",
    "WindGustSpeed",
]

TARGET = "RainTomorrow"


def build_model(csv_path: str | Path):
    """
    Load the CSV, prepare data, train a RandomForestClassifier,
    and return the trained model along with train/test accuracy metrics.

    Returns a dict with:
        model       - the trained sklearn model
        accuracy    - test set accuracy (float)
        report      - classification report string
        le          - LabelEncoder fitted on the target column
    """
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)

    # Drop rows where target is missing
    df = df.dropna(subset=[TARGET])

    # RainTomorrow is stored as 0/1 in this dataset, map to No/Yes strings
    df[TARGET] = df[TARGET].astype(str).str.strip()
    df[TARGET] = df[TARGET].map({"0": "No", "1": "Yes"}).fillna(df[TARGET])

    # Encode target
    le = LabelEncoder()
    df["target"] = le.fit_transform(df[TARGET])

    # Convert feature columns to numeric and drop rows with missing values
    for col in FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=FEATURES)

    X = df[FEATURES]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=le.classes_)

    logger.info(f"Model trained. Test accuracy: {accuracy:.4f}")

    return {
        "model": model,
        "accuracy": accuracy,
        "report": report,
        "le": le,
    }


def predict_rain(model, le, feature_values: dict) -> dict:
    """
    Given a trained model and a dict of feature values, return a prediction.

    Args:
        model: trained RandomForestClassifier
        le: fitted LabelEncoder for the target
        feature_values: dict with keys matching FEATURES

    Returns:
        dict with prediction label and probability
    """
    row = [[float(feature_values.get(f, 0)) for f in FEATURES]]
    pred_encoded = model.predict(row)[0]
    pred_proba = model.predict_proba(row)[0]
    label = le.inverse_transform([pred_encoded])[0]
    # probability of "Yes"
    yes_idx = list(le.classes_).index("Yes")
    probability = round(float(pred_proba[yes_idx]) * 100, 1)
    return {
        "prediction": label,
        "probability": probability,
    }
