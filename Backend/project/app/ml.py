# analyze_sales.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

# === 1. Load Data ===
df = pd.read_csv(r'F:\projects\Bookkeeping\Backend\project\app\sales_data.csv')

# Convert date column to datetime
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')  # Ensure chronological order

print(f"Loaded {len(df)} days of data from {df['date'].min().date()} to {df['date'].max().date()}")

# === 2. Prepare Features for Linear Regression ===
# X = days since start
first_date = df['date'].min()
df['days'] = (df['date'] - first_date).dt.days

X = df['days'].values.reshape(-1, 1)  # Shape: (n_samples, 1)
y = df['units_sold'].values           # Shape: (n_samples,)

# === 3. Train Linear Regression Model ===
model = LinearRegression()
model.fit(X, y)

slope = model.coef_[0]      # Units sold per day change
intercept = model.intercept_
r2 = model.score(X, y)

print(f"\n📈 Trend Analysis:")
print(f"Slope: {slope:.4f} units/day")
print(f"Y-intercept: {intercept:.2f}")
print(f"R² Score: {r2:.4f}")

# Interpret slope
if slope > 0.1:
    trend = "📈 Upward trend – sales are increasing"
elif slope < -0.1:
    trend = "📉 Downward trend – sales are decreasing"
else:
    trend = "➡️ Stable – no significant trend"

print(f"Trend: {trend}")

# === 4. Generate Predictions (Next 7 Days) ===
future_days = np.array(range(X[-1][0] + 1, X[-1][0] + 8)).reshape(-1, 1)
future_dates = [df['date'].max() + timedelta(days=i) for i in range(1, 8)]
predicted_future = model.predict(future_days)

# === 5. Plot Everything ===
plt.figure(figsize=(12, 6))

# Historical data (actual)
plt.plot(df['date'], df['units_sold'], label='Actual Sales', color='blue', marker='o', markersize=4, linewidth=1)

# Fitted trend line
fitted_line = model.predict(X)
plt.plot(df['date'], fitted_line, label=f'Trend Line (Slope={slope:.3f})', color='red', linestyle='--')

# Forecast (next week)
plt.plot(future_dates, predicted_future, label='Forecast (Next 7 Days)', color='green', linestyle='-.', marker='x')

# Styling
plt.title('Sales Trend & Linear Regression Forecast')
plt.xlabel('Date')
plt.ylabel('Units Sold')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Show plot
plt.show()

# === 6. Optional: Save results to DataFrame and CSV ===
forecast_df = pd.DataFrame({
    'date': future_dates,
    'predicted_units_sold': predicted_future.round(2)
})
print("\n🔮 Next Week Forecast:")
print(forecast_df)

# Save prediction
forecast_df.to_csv('forecast_next_week.csv', index=False)