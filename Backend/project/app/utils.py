import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import timedelta
import matplotlib.pyplot as plt
import io
import base64

# === 1. Analyze Sales ===
def analyze_sales(csv_path):
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    first_date = df["date"].min()
    df["days"] = (df["date"] - first_date).dt.days

    X = df["days"].values.reshape(-1, 1)
    y = df["units_sold"].values

    model = LinearRegression()
    model.fit(X, y)

    slope = model.coef_[0]
    intercept = model.intercept_

    future_days = np.array(range(X[-1][0] + 1, X[-1][0] + 8)).reshape(-1, 1)
    future_dates = [df["date"].max() + timedelta(days=i) for i in range(1, 8)]
    predicted_future = model.predict(future_days)

    return {
        "slope": slope,
        "intercept": intercept,
        "r2": model.score(X, y),
        "df": df,
        "fitted_line": model.predict(X),
        "future_dates": future_dates,
        "predicted_future": predicted_future,
    }

# === 2. Suggest Price ===
def suggest_price(base_price, slope):
    if slope > 0.1:
        return round(base_price * 1.05, 2)  # increase 5%
    elif slope < -0.1:
        return round(base_price * 0.95, 2)  # decrease 5%
    else:
        return round(base_price, 2)  # stable → no change

# === 3. Plot Historical + Forecast ===
def plot_sales(df, fitted_line, future_dates, predicted_future):
    plt.figure(figsize=(10, 5))  # New figure

    # Past: Actual sales
    plt.plot(df["date"], df["units_sold"], label="Actual Sales", marker="o", color="blue")
    
    # Past: Fitted trend line
    plt.plot(df["date"], fitted_line, label="Trend Line", linestyle="--", color="orange")
    
    # Future: Predictions
    plt.plot(future_dates, predicted_future, label="Forecast", linestyle="-.", marker="x", color="red")

    plt.xlabel("Date")
    plt.ylabel("Units Sold")
    plt.title("Sales Trend & Forecast")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode("utf-8")

    # ✅ Cleanup
    buf.close()
    plt.close()  # Critical: close figure to avoid overlap

    return img_str

# === 4. Plot Predicted Week Only ===
def plot_predicted_week(future_dates, predicted_future):
    plt.figure(figsize=(8, 4))  # Fresh figure

    plt.plot(future_dates, predicted_future, color="green", marker="o", linestyle="-", linewidth=2)

    # Annotate values above points
    for i, val in enumerate(predicted_future):
        plt.text(future_dates[i], val + max(predicted_future)*0.01, f"{val:.1f}",
                 ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.xlabel("Date")
    plt.ylabel("Predicted Units Sold")
    plt.title("Predicted Sales: Next 7 Days")
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode("utf-8")

    # ✅ Cleanup
    buf.close()
    plt.close()  # Prevents second plot from affecting others

    return img_str