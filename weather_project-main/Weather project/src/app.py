import sys
import io
import base64
from pathlib import Path
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from flask import Flask, render_template, request

sys.path.insert(0, str(Path(__file__).parent))
from weatherstats import load_weather_csv, WeatherDataStore, WeatherAnalyzer
from models import db, QueryHistory

app = Flask(__name__)

DB_PATH = Path(__file__).parent / "weather_app.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "weather-app-key"

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


@app.route("/")
def index():
    return render_template("index.html", columns=NUMERIC_COLUMNS)


@app.route("/stats", methods=["POST"])
def stats():
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


@app.route("/history")
def history():
    entries = QueryHistory.query.order_by(QueryHistory.queried_at.desc()).limit(50).all()
    return render_template("history.html", entries=entries)


if __name__ == "__main__":
    app.run(debug=True)
