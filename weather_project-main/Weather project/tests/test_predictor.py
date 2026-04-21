"""
test_predictor.py

Tests for the scikit-learn rain prediction model in weatherstats/predictor.py.
Tests model training, prediction output, and accuracy thresholds.
"""

import pytest
import sys
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parents[1]
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from weatherstats.predictor import build_model, predict_rain, FEATURES, TARGET


@pytest.fixture(scope="module")
def model_data():
    csv_path = project_root / "Data" / "Weather Training Data.csv"
    return build_model(csv_path)


class TestBuildModel:

    def test_model_data_has_model(self, model_data):
        assert "model" in model_data

    def test_model_data_has_accuracy(self, model_data):
        assert "accuracy" in model_data

    def test_model_data_has_report(self, model_data):
        assert "report" in model_data

    def test_accuracy_is_reasonable(self, model_data):
        # Random forest on this dataset should be above 80%
        assert model_data["accuracy"] > 0.80

    def test_report_is_string(self, model_data):
        assert isinstance(model_data["report"], str)

    def test_report_contains_yes_no(self, model_data):
        assert "Yes" in model_data["report"]
        assert "No" in model_data["report"]

    def test_features_list_not_empty(self):
        assert len(FEATURES) > 0

    def test_target_column_name(self):
        assert TARGET == "RainTomorrow"


class TestPredictRain:

    def test_predict_returns_dict(self, model_data):
        values = {f: 15.0 for f in FEATURES}
        result = predict_rain(model_data["model"], model_data["le"], values)
        assert isinstance(result, dict)

    def test_predict_has_prediction_key(self, model_data):
        values = {f: 15.0 for f in FEATURES}
        result = predict_rain(model_data["model"], model_data["le"], values)
        assert "prediction" in result

    def test_predict_has_probability_key(self, model_data):
        values = {f: 15.0 for f in FEATURES}
        result = predict_rain(model_data["model"], model_data["le"], values)
        assert "probability" in result

    def test_prediction_is_yes_or_no(self, model_data):
        values = {f: 15.0 for f in FEATURES}
        result = predict_rain(model_data["model"], model_data["le"], values)
        assert result["prediction"] in ("Yes", "No")

    def test_probability_is_between_0_and_100(self, model_data):
        values = {f: 15.0 for f in FEATURES}
        result = predict_rain(model_data["model"], model_data["le"], values)
        assert 0.0 <= result["probability"] <= 100.0

    def test_high_humidity_leans_toward_rain(self, model_data):
        # Very high humidity and rainfall should predict rain
        values = {
            "MinTemp": 18.0, "MaxTemp": 22.0, "Rainfall": 20.0,
            "Humidity9am": 99.0, "Humidity3pm": 99.0,
            "Pressure9am": 1005.0, "Pressure3pm": 1002.0,
            "WindGustSpeed": 60.0,
        }
        result = predict_rain(model_data["model"], model_data["le"], values)
        # High humidity / high rainfall should have a meaningful rain probability
        assert result["probability"] > 50.0

    def test_low_humidity_leans_away_from_rain(self, model_data):
        values = {
            "MinTemp": 10.0, "MaxTemp": 30.0, "Rainfall": 0.0,
            "Humidity9am": 20.0, "Humidity3pm": 15.0,
            "Pressure9am": 1025.0, "Pressure3pm": 1022.0,
            "WindGustSpeed": 10.0,
        }
        result = predict_rain(model_data["model"], model_data["le"], values)
        assert result["probability"] < 50.0
