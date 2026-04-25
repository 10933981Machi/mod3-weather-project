"""
test_dashboard.py

Tests for the login, upload, dashboard, and API routes
added in the Phase 11 final project.
"""

import pytest
import sys
import io
from pathlib import Path
from werkzeug.security import generate_password_hash

project_root = Path(__file__).resolve().parents[1]
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from app import app, db, UPLOAD_FOLDER
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


@pytest.fixture
def client_with_csv(logged_in_client):
    # Upload the real training CSV via the upload route
    csv_path = project_root / "Data" / "Weather Training Data.csv"
    with open(csv_path, "rb") as f:
        data = {"csv_file": (f, "Weather Training Data.csv")}
        logged_in_client.post("/upload", data=data, content_type="multipart/form-data")
    return logged_in_client


class TestLoginUploadRoutes:

    def test_login_page_loads(self, client):
        response = client.get("/login")
        assert response.status_code == 200
        assert b"Australian Weather Analytics Dashboard" in response.data

    def test_login_success_redirects(self, client):
        response = client.post("/login", data={"username": "testuser", "password": "testpass"})
        assert response.status_code == 302

    def test_login_fails_bad_password(self, client):
        response = client.post("/login", data={"username": "testuser", "password": "wrong"})
        assert b"Invalid" in response.data

    def test_upload_page_requires_login(self, client):
        response = client.get("/upload")
        assert response.status_code == 302

    def test_upload_page_loads_when_logged_in(self, logged_in_client):
        response = logged_in_client.get("/upload")
        assert response.status_code == 200
        assert b"Upload CSV" in response.data

    def test_upload_rejects_non_csv(self, logged_in_client):
        data = {"csv_file": (io.BytesIO(b"not a csv"), "file.txt")}
        response = logged_in_client.post("/upload", data=data, content_type="multipart/form-data")
        assert b"valid CSV" in response.data or response.status_code == 200


class TestDashboardRoutes:

    def test_dashboard_requires_login(self, client):
        response = client.get("/dashboard")
        assert response.status_code == 302

    def test_dashboard_without_csv_redirects_to_upload(self, logged_in_client):
        response = logged_in_client.get("/dashboard")
        assert response.status_code == 302

    def test_dashboard_loads_with_csv(self, client_with_csv):
        response = client_with_csv.get("/dashboard")
        assert response.status_code == 200
        assert b"Weather Analytics Dashboard" in response.data

    def test_dashboard_has_buttons(self, client_with_csv):
        response = client_with_csv.get("/dashboard")
        assert b"Temperature Trends" in response.data
        assert b"Rainfall Patterns" in response.data
        assert b"Extreme Weather" in response.data


class TestAPIRoutes:

    def test_api_cities_requires_login(self, client):
        response = client.get("/api/cities")
        assert response.status_code == 302

    def test_api_cities_returns_list(self, client_with_csv):
        response = client_with_csv.get("/api/cities")
        assert response.status_code == 200
        data = response.get_json()
        assert "cities" in data
        assert len(data["cities"]) > 0

    def test_api_cities_sorted(self, client_with_csv):
        response = client_with_csv.get("/api/cities")
        data = response.get_json()
        cities = data["cities"]
        assert cities == sorted(cities)

    def test_api_chart_temperature(self, client_with_csv):
        response = client_with_csv.get("/api/chart?category=temperature&city=Albury")
        assert response.status_code == 200
        data = response.get_json()
        assert "chart" in data
        assert "summary" in data

    def test_api_chart_rainfall(self, client_with_csv):
        response = client_with_csv.get("/api/chart?category=rainfall&city=Albury")
        assert response.status_code == 200
        data = response.get_json()
        assert "chart" in data

    def test_api_chart_extreme(self, client_with_csv):
        response = client_with_csv.get("/api/chart?category=extreme&city=Albury")
        assert response.status_code == 200
        data = response.get_json()
        assert "chart" in data
        assert "summary" in data

    def test_api_chart_bad_category(self, client_with_csv):
        response = client_with_csv.get("/api/chart?category=fake&city=Albury")
        assert response.status_code == 400

    def test_api_chart_bad_city(self, client_with_csv):
        response = client_with_csv.get("/api/chart?category=temperature&city=FakeCity")
        assert response.status_code == 400
