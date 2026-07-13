# Statistical Methodology

## Hybrid data strategy
Base layer is the real **DataCo Smart Supply Chain** dataset (~180k order
items). Real operational datasets lack (a) planning columns and (b) labeled
anomalies, so two augmentations are applied on top of the real transactions:

1. **Planning columns** — weekly demand forecasts per category are simulated
   as `actual x (1 + bias + noise)` with bias +2% and noise sigma 8%
   (typical planner error), and inventory positions as 12–35 days of cover.
2. **Controlled anomaly injection** — five issue classes (SLA breaches, cost
   spikes, duplicate transactions, missing values, demand shocks) injected at
   configured rates, every key logged to `injection_manifest.csv`.

Rationale: real data gives business credibility; the manifest turns
"my charts look anomalous" into measured precision/recall.

## Forecasting
Weekly demand per category, walk-forward backtest (train on history, predict
4 weeks, roll forward across the final 12 weeks). Model tiers: Prophet
(preferred), Holt-Winters, seasonal-naive+trend fallback — one evaluation
harness across all tiers so they are directly comparable.

**Headline metric: WMAPE** = sum|error| / sum(actual). Plain MAPE explodes on
low-volume weeks (divide by small actuals); WMAPE is the industry standard
for intermittent demand. Bias% is reported alongside to expose systematic
over/under-forecasting.

## Anomaly detection
| detector | method | why this method |
|---|---|---|
| sla_breach | rule: actual - scheduled >= 4 days | SLA is a contract; a rule is the correct detector |
| cost_spike | billed / catalog-expected > 1.5x | each line judged vs ITS OWN expected amount; global z-scores fail when unit prices span 50x |
| duplicates | exact key repeat | deterministic |
| missing_values | critical-field nulls | deterministic |
| multivariate | IsolationForest (contamination 1%) | catches combinations no single rule sees |
| demand_shock | robust z vs 9-week rolling median (MAD), \|z\|>3.5 | level shocks stand out vs local baseline even when neighbors are noisy |
| forecast_drift | \|actual-forecast\|/forecast > 15% | operational planner alert |

## Validation & honest caveats
- Recall is measured against **injected** anomalies (ground truth known).
- Transaction-level precision is exact (injected keys known): 1.0 across all
  four classes in the reference run.
- Demand-level "precision vs injected" **undercounts true precision**: the
  detector also fires on organic volatility that is genuinely anomalous but
  wasn't injected. On the noisy 5k dev sample this is severe; on the real
  180k-row dataset weekly demand is far smoother. Report your real-run
  numbers and say exactly this in review.
- forecast_drift is excluded from precision scoring by design — it is an
  operational alert on planner error, not an injected-issue detector.
