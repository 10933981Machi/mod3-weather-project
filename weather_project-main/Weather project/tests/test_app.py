"""
test_app.py

Tests for the Flask web application including authentication,
route protection, stats, and query history.
"""

import pytest
import sys
from pathlib import Path
from werkzeug.security import generate_password_hash

project_root = Path(__file__).resolve().parents[1]
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from app import app, db
from models import User


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        user = User(username="testuser", password_hash=generate_password_hash("testpass"))
        db.session.add(user)
        db.session.commit()
        yield app.test_client()
        db.drop_all()


@pytest.fixture
def logged_in_client(client):
    client.post("/login", data={"username": "testuser", "password": "testpass"})
    return client


class TestAuth:

    def test_login_page_loads(self, client):
        response = client.get("/login")
        assert response.status_code == 200
        assert b"Login" in response.data

    def test_login_valid_credentials(self, client):
        response = client.post("/login", data={"username": "testuser", "password": "testpass"})
        assert response.status_code == 302

    def test_login_invalid_credentials(self, client):
        response = client.post("/login", data={"username": "testuser", "password": "wrongpass"})
        assert response.status_code == 200
        assert b"Invalid" in response.data

    def test_logout_redirects_to_login(self, logged_in_client):
        response = logged_in_client.get("/logout")
        assert response.status_code == 302

    def test_home_requires_login(self, client):
        response = client.get("/")
        assert response.status_code == 302

    def test_history_requires_login(self, client):
        response = client.get("/history")
        assert response.status_code == 302

    def test_viz_requires_login(self, client):
        response = client.get("/viz")
        assert response.status_code == 302


class TestRoutes:

    def test_stats_page_loads(self, logged_in_client):
        response = logged_in_client.get("/stats")
        assert response.status_code == 200
        assert b"Stats" in response.data

    def test_stats_invalid_column(self, logged_in_client):
        response = logged_in_client.post("/stats", data={"column": "NotAColumn", "dataset": "training"})
        assert response.status_code == 200
        assert b"valid column" in response.data

    def test_stats_valid_column(self, logged_in_client):
        response = logged_in_client.post("/stats", data={"column": "MaxTemp", "dataset": "training"})
        assert response.status_code == 200
        assert b"MaxTemp" in response.data
        assert b"Mean" in response.data

    def test_history_page_loads(self, logged_in_client):
        response = logged_in_client.get("/history")
        assert response.status_code == 200
        assert b"Query History" in response.data

    def test_viz_page_loads(self, logged_in_client):
        response = logged_in_client.get("/viz")
        assert response.status_code == 200
        assert b"Visualizations" in response.data

    def test_history_records_query(self, logged_in_client):
        logged_in_client.post("/stats", data={"column": "Rainfall", "dataset": "training"})
        response = logged_in_client.get("/history")
        assert b"Rainfall" in response.data

    def test_stats_page_has_column_options(self, logged_in_client):
        response = logged_in_client.get("/stats")
        assert b"MinTemp" in response.data
        assert b"MaxTemp" in response.data
