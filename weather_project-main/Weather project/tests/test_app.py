"""
test_app.py

Basic tests for the Flask web application.
Tests that routes load correctly, stats are returned,
and invalid inputs are handled.
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from app import app, db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


class TestRoutes:

    def test_home_page_loads(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert b"Weather Data Explorer" in response.data

    def test_history_page_loads(self, client):
        response = client.get("/history")
        assert response.status_code == 200
        assert b"Query History" in response.data

    def test_viz_page_loads(self, client):
        response = client.get("/viz")
        assert response.status_code == 200
        assert b"Visualizations" in response.data

    def test_stats_invalid_column(self, client):
        response = client.post("/stats", data={"column": "NotAColumn", "dataset": "training"})
        assert response.status_code == 200
        assert b"valid column" in response.data

    def test_stats_valid_column(self, client):
        response = client.post("/stats", data={"column": "MaxTemp", "dataset": "training"})
        assert response.status_code == 200
        assert b"MaxTemp" in response.data
        assert b"Mean" in response.data

    def test_history_records_query(self, client):
        # Run a stats query first
        client.post("/stats", data={"column": "Rainfall", "dataset": "training"})
        response = client.get("/history")
        assert b"Rainfall" in response.data

    def test_home_page_has_column_options(self, client):
        response = client.get("/")
        assert b"MinTemp" in response.data
        assert b"MaxTemp" in response.data
        assert b"Rainfall" in response.data
