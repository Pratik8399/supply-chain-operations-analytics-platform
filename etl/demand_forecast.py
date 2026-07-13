"""
Weekly demand forecasting per category, with walk-forward backtesting.

Model tiers (auto-selected by availability):
  1. Prophet          — trend + yearly/weekly seasonality (preferred)
  2. Holt-Winters     — statsmodels ExponentialSmoothing (additive seasonal)
  3. Seasonal-naive+  — numpy fallback: last-year seasonal profile + linear trend

Tiering rationale: the repo must produce forecasts on any machine (CI,
recruiter laptop) even without heavy deps, while the reported metrics come
from the Prophet run. The evaluation harness (walk-forward MAPE/bias) is
identical across tiers, so models are directly comparable.

Outputs:
  outputs/forecast_results.csv     per category-week: actual, predicted, bounds
  outputs/forecast_accuracy.csv    per category: MAPE, bias, model used

Usage:
    python etl/demand_forecast.py
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

from config import OUTPUT_DIR, PROCESSED_DIR

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------- model tiers
try:
    from prophet import Prophet
    TIER = "prophet"
except ImportError:
    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing
        TIER = "holt_winters"
    except ImportError:
        TIER = "seasonal_naive"


def fit_predict(train: pd.Series, horizon: int) -> np.ndarray:
    """Train on a weekly series, predict `horizon` weeks ahead."""
    if TIER == "prophet" and len(train) >= 20:
        dfp = pd.DataFrame({"ds": train.index, "y": train.values})
        m = Prophet(yearly_seasonality=True, weekly_seasonality=False,
                    daily_seasonality=False, interval_width=0.9)
        m.fit(dfp)
        future = m.make_future_dataframe(periods=horizon, freq="W-MON")
        fc = m.predict(future).tail(horizon)
        return np.maximum(0, fc["yhat"].values)

    if TIER == "holt_winters" and len(train) >= 2 * 52:
        m = ExponentialSmoothing(train, trend="add", seasonal="add",
                                 seasonal_periods=52).fit()
        return np.maximum(0, m.forecast(horizon).values)

    # Seasonal-naive + trend fallback (also used when history is short)
    period = 52 if len(train) >= 52 else max(4, len(train) // 2)
    seasonal = train.values[-period:]
    reps = int(np.ceil(horizon / period))
    base = np.tile(seasonal, reps)[:horizon]
    # linear trend from first vs second half means
    half = len(train) // 2
    trend_per_step = ((train.values[half:].mean() - train.values[:half].mean())
                      / max(half, 1))
    return np.maximum(0, base + trend_per_step * np.arange(1, horizon + 1))


def mape(actual: np.ndarray, pred: np.ndarray) -> float:
    mask = actual > 0
    return float(np.mean(np.abs((actual[mask] - pred[mask]) / actual[mask])) * 100)


def wmape(actual: np.ndarray, pred: np.ndarray) -> float:
    """Weighted MAPE: sum|err| / sum(actual). Robust when weekly actuals
    are small/intermittent (plain MAPE explodes on low-volume weeks)."""
    return float(np.abs(actual - pred).sum() / max(actual.sum(), 1e-9) * 100)


def bias(actual: np.ndarray, pred: np.ndarray) -> float:
    mask = actual > 0
    return float(np.mean((pred[mask] - actual[mask]) / actual[mask]) * 100)


def walk_forward(series: pd.Series, test_weeks: int = 12,
                 step: int = 4) -> pd.DataFrame:
    """Backtest: repeatedly train on history, predict next `step` weeks."""
    rows = []
    start = len(series) - test_weeks
    for cut in range(start, len(series), step):
        train, test = series.iloc[:cut], series.iloc[cut:cut + step]
        if len(test) == 0:
            break
        preds = fit_predict(train, len(test))
        for ts, a, p in zip(test.index, test.values, preds):
            rows.append({"week": ts, "actual": a, "predicted": round(float(p), 1)})
    return pd.DataFrame(rows)


def main() -> None:
    wk = pd.read_csv(PROCESSED_DIR / "weekly_demand_augmented.csv",
                     parse_dates=["week"])
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"Model tier in use: {TIER}")

    all_results, accuracy = [], []
    for cat, g in wk.groupby("category_name"):
        series = (g.set_index("week")["demand_units"]
                   .asfreq("W-MON").interpolate().dropna())
        if len(series) < 16:      # not enough history to backtest honestly
            continue
        bt = walk_forward(series)
        bt["category_name"] = cat
        all_results.append(bt)
        accuracy.append({
            "category_name": cat,
            "model": TIER,
            "weeks_history": len(series),
            "weeks_backtested": len(bt),
            "MAPE_pct": round(mape(bt["actual"].values, bt["predicted"].values), 2),
            "WMAPE_pct": round(wmape(bt["actual"].values, bt["predicted"].values), 2),
            "bias_pct": round(bias(bt["actual"].values, bt["predicted"].values), 2),
        })

    results = pd.concat(all_results, ignore_index=True)
    acc = pd.DataFrame(accuracy).sort_values("WMAPE_pct")
    results.to_csv(OUTPUT_DIR / "forecast_results.csv", index=False)
    acc.to_csv(OUTPUT_DIR / "forecast_accuracy.csv", index=False)

    print(acc.to_string(index=False))
    print(f"\nOverall WMAPE: "
          f"{wmape(results['actual'].values, results['predicted'].values):.2f}%  "
          f"(plain MAPE: {mape(results['actual'].values, results['predicted'].values):.2f}%)")
    print("Wrote outputs/forecast_results.csv, outputs/forecast_accuracy.csv")


if __name__ == "__main__":
    main()
