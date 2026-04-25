import sys
import io
import base64
from pathlib import Path
from datetime import datetime
from functools import wraps

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

sys.path.insert(0, str(Path(__file__).parent))
from weatherstats import load_weather_csv, WeatherDataStore, WeatherAnalyzer
from weatherstats.predictor import build_model, predict_rain, FEATURES
from models import db, User, QueryHistory, PredictionLog

app = Flask(__name__)

DB_PATH = Path(__file__).parent / "weather_app.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "weather-app-secret-key-2024"

UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

db.init_app(app)

DATA_DIR = Path(__file__).parent.parent / "Data"
DATASETS = {
    "training": DATA_DIR / "Weather Training Data.csv",
    "test": DATA_DIR / "Weather Test Data.csv",
}

NUMERIC_COLUMNS = [
    "MinTemp", "MaxTemp", "Rainfall", "Evaporation", "Sunshine",
    "WindGustSpeed", "WindSpeed9am", "WindSpeed3pm",
    "Humidity9am", "Humidity3pm", "Pressure9am", "Pressure3pm",
    "Cloud9am", "Cloud3pm", "Temp9am", "Temp3pm",
]

with app.app_context():
    db.create_all()
    if User.query.count() == 0:
        default_user = User(
            username="admin",
            password_hash=generate_password_hash("password")
        )
        db.session.add(default_user)
        db.session.commit()


@app.context_processor
def inject_user():
    return {"username": session.get("username")}


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# --- Auth routes ---

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("upload"))
        error = "Invalid username or password."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# --- Upload route ---

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    error = None
    if request.method == "POST":
        f = request.files.get("csv_file")
        if not f or not f.filename.endswith(".csv"):
            error = "Please upload a valid CSV file."
        else:
            filename = secure_filename(f.filename)
            save_path = UPLOAD_FOLDER / filename
            f.save(str(save_path))
            session["csv_path"] = str(save_path)
            return redirect(url_for("dashboard"))
    return render_template("upload.html", error=error)


# --- Dashboard routes ---

@app.route("/")
@login_required
def index():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@login_required
def dashboard():
    if "csv_path" not in session:
        return redirect(url_for("upload"))
    return render_template("dashboard.html")


@app.route("/api/cities")
@login_required
def api_cities():
    csv_path = session.get("csv_path")
    if not csv_path:
        return jsonify({"error": "No CSV uploaded"}), 400
    csv_path_obj = Path(csv_path).resolve()
    upload_dir = UPLOAD_FOLDER.resolve()
    if not str(csv_path_obj).startswith(str(upload_dir)):
        return jsonify({"error": "Invalid file path"}), 400
    if not csv_path_obj.exists():
        return jsonify({"error": "Uploaded file not found"}), 400
    df = pd.read_csv(csv_path_obj)
    if "Location" not in df.columns:
        return jsonify({"error": "No Location column in this CSV"}), 400
    cities = sorted(df["Location"].dropna().unique().tolist())
    return jsonify({"cities": cities})


@app.route("/api/chart")
@login_required
def api_chart():
    category = request.args.get("category")
    city = request.args.get("city")
    csv_path = session.get("csv_path")

    if not csv_path:
        return jsonify({"error": "No CSV uploaded"}), 400
    csv_path_obj = Path(csv_path).resolve()
    upload_dir = UPLOAD_FOLDER.resolve()
    if not str(csv_path_obj).startswith(str(upload_dir)):
        return jsonify({"error": "Invalid file path"}), 400
    if not csv_path_obj.exists():
        return jsonify({"error": "Uploaded file not found"}), 400

    df = pd.read_csv(csv_path_obj)
    df = df[df["Location"] == city]
    if df.empty:
        return jsonify({"error": f"No data found for {city}"}), 400

    fig, ax = plt.subplots(figsize=(9, 4))
    summary = ""

    if category == "temperature":
        df["MinTemp"] = pd.to_numeric(df["MinTemp"], errors="coerce")
        df["MaxTemp"] = pd.to_numeric(df["MaxTemp"], errors="coerce")
        ax.plot(range(len(df)), df["MinTemp"].values, label="MinTemp", color="steelblue", alpha=0.7)
        ax.plot(range(len(df)), df["MaxTemp"].values, label="MaxTemp", color="tomato", alpha=0.7)
        ax.set_title(f"Temperature Trends - {city}")
        ax.set_xlabel("Record #")
        ax.set_ylabel("Temperature (°C)")
        ax.legend()
        avg_min = round(df["MinTemp"].mean(), 2)
        avg_max = round(df["MaxTemp"].mean(), 2)
        summary = (
            f"{city} has an average minimum temperature of {avg_min}°C "
            f"and an average maximum temperature of {avg_max}°C. "
            f"The highest recorded temperature was {round(df['MaxTemp'].max(), 1)}°C "
            f"and the lowest was {round(df['MinTemp'].min(), 1)}°C."
        )

    elif category == "rainfall":
        df["Rainfall"] = pd.to_numeric(df["Rainfall"], errors="coerce")
        rainy = df[df["Rainfall"] > 0]["Rainfall"].dropna()
        if rainy.empty:
            plt.close(fig)
            return jsonify({"error": "No rainfall data for this city"}), 400
        ax.hist(rainy, bins=20, color="steelblue", edgecolor="white")
        ax.set_title(f"Rainfall Distribution - {city}")
        ax.set_xlabel("Rainfall (mm)")
        ax.set_ylabel("Frequency")
        total = round(df["Rainfall"].sum(), 1)
        rainy_days = int((df["Rainfall"] > 0).sum())
        avg_rain = round(rainy.mean(), 2)
        summary = (
            f"{city} recorded {rainy_days} rainy days in the dataset. "
            f"Total rainfall: {total} mm. "
            f"On days when it rained, the average rainfall was {avg_rain} mm."
        )

    elif category == "extreme":
        df["MaxTemp"] = pd.to_numeric(df["MaxTemp"], errors="coerce")
        df["Humidity3pm"] = pd.to_numeric(df["Humidity3pm"], errors="coerce")
        hot_days = int((df["MaxTemp"] >= 35).sum())
        humid_days = int((df["Humidity3pm"] >= 80).sum())
        labels = ["Hot Days\n(MaxTemp >= 35C)", "Humid Afternoons\n(Humidity3pm >= 80%)"]
        values = [hot_days, humid_days]
        ax.bar(labels, values, color=["tomato", "steelblue"])
        ax.set_title(f"Extreme Weather Indicators - {city}")
        ax.set_ylabel("Number of Days")
        note = "Significant heat stress recorded." if hot_days > 30 else (
            "Some extreme heat events." if hot_days > 10 else "Rare extreme heat events."
        )
        summary = (
            f"{city} had {hot_days} hot days (max temp >= 35°C) "
            f"and {humid_days} humid afternoons (humidity >= 80% at 3pm). {note}"
        )

    else:
        plt.close(fig)
        return jsonify({"error": "Unknown category"}), 400

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    chart_data = base64.b64encode(buf.read()).decode("utf-8")
    return jsonify({"chart": chart_data, "summary": summary})


# --- Legacy routes (still accessible) ---

@app.route("/stats", methods=["GET", "POST"])
@login_required
def stats():
    if request.method == "GET":
        return render_template("index.html", columns=NUMERIC_COLUMNS)

    column = request.form.get("column")
    dataset = request.form.get("dataset", "training")

    if column not in NUMERIC_COLUMNS:
        return render_template("index.html", columns=NUMERIC_COLUMNS, error="Please select a valid column.")

    csv_path = DATASETS.get(dataset)
    if not csv_path or not csv_path.exists():
        return render_template("index.html", columns=NUMERIC_COLUMNS, error="Dataset file not found.")

    df = load_weather_csv(csv_path)
    store = WeatherDataStore(df)
    analyzer = WeatherAnalyzer(store)
    result = analyzer.descriptive_stats(column)

    if "error" in result:
        return render_template("index.html", columns=NUMERIC_COLUMNS, error=result["error"])

    entry = QueryHistory(column=column, dataset=dataset, queried_at=datetime.utcnow())
    db.session.add(entry)
    db.session.commit()

    return render_template("stats.html", result=result, column=column, dataset=dataset)


@app.route("/viz", methods=["GET", "POST"])
@login_required
def viz():
    plot_data = None
    plot_type = None
    dataset = "training"
    error = None

    if request.method == "POST":
        plot_type = request.form.get("plot_type")
        dataset = request.form.get("dataset", "training")

        csv_path = DATASETS.get(dataset)
        if not csv_path or not csv_path.exists():
            error = "Dataset file not found."
        else:
            df = load_weather_csv(csv_path)
            fig, ax = plt.subplots(figsize=(10, 5))

            if plot_type == "rainfall_hist":
                rainfall = pd.to_numeric(df["Rainfall"], errors="coerce").dropna()
                ax.hist(rainfall[rainfall > 0], bins=30, color="steelblue", edgecolor="white")
                ax.set_title("Rainfall Distribution (days with rainfall > 0)")
                ax.set_xlabel("Rainfall (mm)")
                ax.set_ylabel("Frequency")

            elif plot_type == "avg_temp_location":
                df["MaxTemp"] = pd.to_numeric(df["MaxTemp"], errors="coerce")
                avg = df.groupby("Location")["MaxTemp"].mean().sort_values(ascending=False).head(15)
                avg.plot(kind="bar", ax=ax, color="tomato", edgecolor="white")
                ax.set_title("Average Max Temp by Location (Top 15)")
                ax.set_xlabel("Location")
                ax.set_ylabel("Avg MaxTemp (°C)")
                plt.xticks(rotation=45, ha="right")

            elif plot_type == "humidity_box":
                df["Humidity9am"] = pd.to_numeric(df["Humidity9am"], errors="coerce")
                df["Humidity3pm"] = pd.to_numeric(df["Humidity3pm"], errors="coerce")
                data = [
                    df["Humidity9am"].dropna().values,
                    df["Humidity3pm"].dropna().values,
                ]
                ax.boxplot(data, labels=["9am", "3pm"])
                ax.set_title("Humidity at 9am vs 3pm")
                ax.set_ylabel("Humidity (%)")

            else:
                error = "Unknown plot type."
                plt.close(fig)

            if not error:
                plt.tight_layout()
                buf = io.BytesIO()
                plt.savefig(buf, format="png")
                plt.close(fig)
                buf.seek(0)
                plot_data = base64.b64encode(buf.read()).decode("utf-8")

    return render_template("viz.html", plot_data=plot_data, plot_type=plot_type, dataset=dataset, error=error)


@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    result = None
    error = None
    accuracy = None
    report = None

    csv_path = DATASETS["training"]

    try:
        model_data = build_model(csv_path)
    except Exception as e:
        error = f"Could not train model: {e}"
        return render_template("predict.html", features=FEATURES, result=result, error=error)

    accuracy = round(model_data["accuracy"] * 100, 2)
    report = model_data["report"]

    if request.method == "POST":
        try:
            feature_values = {f: request.form.get(f, 0) for f in FEATURES}
            result = predict_rain(model_data["model"], model_data["le"], feature_values)

            log = PredictionLog(
                prediction=result["prediction"],
                probability=result["probability"],
                min_temp=float(feature_values.get("MinTemp", 0)),
                max_temp=float(feature_values.get("MaxTemp", 0)),
                humidity_3pm=float(feature_values.get("Humidity3pm", 0)),
            )
            db.session.add(log)
            db.session.commit()

        except Exception as e:
            error = f"Prediction failed: {e}"

    return render_template(
        "predict.html",
        features=FEATURES,
        result=result,
        error=error,
        accuracy=accuracy,
        report=report,
    )


@app.route("/history")
@login_required
def history():
    entries = QueryHistory.query.order_by(QueryHistory.queried_at.desc()).limit(50).all()
    return render_template("history.html", entries=entries)


if __name__ == "__main__":
    app.run(debug=True)
