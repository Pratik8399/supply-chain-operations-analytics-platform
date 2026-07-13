# Stakeholder Requirements

Requirements gathered per stakeholder group (structured as an enterprise
analytics engagement across regions — Americas / EMEA / APAC operations all
consume the same views filtered by Market).

## Logistics Operations
- **Need:** monitor SLA breaches and delayed shipments by lane and carrier.
- **Dashboard view:** OTIF trend, late-shipment alerts with severity,
  route-to-owner field, Market/Region filter.
- **Decision supported:** prioritize vendor and region investigation;
  escalate repeat-offender lanes.
- **Cadence:** daily alert review (high severity within 3 business days).

## Finance Operations
- **Need:** identify cost spikes and billing anomalies before month-end close.
- **Dashboard view:** critical cost-spike alerts with billed-vs-expected
  ratio; drill-through to order line.
- **Decision supported:** reconcile abnormal order totals; recover
  overbilling; correct catalog mismatches.
- **Cadence:** critical alerts within 24 hours; weekly reconciliation digest.

## Demand Planning
- **Need:** detect demand shocks and forecast drift early enough to act.
- **Dashboard view:** forecast vs actual by category, WMAPE and bias tiles,
  demand-shock alert list.
- **Decision supported:** adjust replenishment plans; re-baseline forecasts
  where drift persists; flag promo/stockout drivers.
- **Cadence:** weekly S&OP review input.

## Data Engineering / Platform
- **Need:** trust signals on every dataset consumed downstream.
- **Dashboard view:** quality-gate pass/fail by dimension, audit-log volume,
  pipeline run history.
- **Decision supported:** block promotion of failing loads; prioritize
  source-system fixes.

## Executive Sponsors
- **Need:** one-page narrative, not tables.
- **Deliverable:** `outputs/executive_summary.md`, auto-generated each run
  by the insight module; headline KPIs + alert posture + forecast health.

## Cross-cutting requirements
- All views filterable by Market (LATAM / Europe / Pacific Asia / USCA /
  Africa) to serve regional stakeholders from one model.
- Every alert carries `route_to` so ownership is unambiguous.
- Access is least-privilege: transaction-level detail restricted to
  Finance Ops / admin roles (see governance policy).
