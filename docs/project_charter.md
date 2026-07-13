# Project Charter — Enterprise Operations Analytics & Automation Suite

**Problem statement.** Operational data (orders, shipping, demand) is
reviewed manually and reactively: SLA breaches, billing anomalies, and
forecast misses are found late or not at all, and insight delivery depends
on analyst availability.

**Business objective.** Automate the path from raw operational data to
stakeholder action: validated data, forecasted demand, detected and routed
anomalies, and auto-generated narrative insights — refreshed by one
pipeline command.

**Stakeholders.** Logistics Operations, Finance Operations, Demand
Planning, Data Engineering, Executive sponsors (see
stakeholder_requirements.md).

**Scope.**
- Ingestion + standardization of the DataCo order-item dataset (~180k rows)
- Hybrid augmentation (planning columns) with manifest-logged anomaly
  injection for measurable detection validation
- Data quality gates with append-only audit logging
- Walk-forward weekly demand forecasting per category (WMAPE/bias)
- 7-detector anomaly ensemble with severity + team routing
- Automated narrative insight generation (template-based NLP-style)
- Role-based access simulation with full access audit trail
- BI-ready exports + dashboard specification for Tableau/Power BI

**Out of scope (this phase).** Live Snowflake deployment; real-time
streaming; write-back workflows (alert acknowledgment); ML-based reorder
optimization; production scheduler (documented as next steps).

**Deliverables.** Working pipeline (8 orchestrated stages), Snowflake DDL +
views, dashboard exports + wireframes + adoption guide, methodology and
governance documentation, executive summary artifact.


**Risks & mitigations.**
- Kaggle file licensing/size -> raw data git-ignored; download runbook
- Sparse category-weeks distort MAPE -> WMAPE headline metric
- Demand-detector precision vs organic volatility -> honest split reporting;
  analyst-labeling loop as next step
- Model dependency weight (Prophet) -> tiered fallback behind one harness

**Success metrics.** 100% recall of injected anomalies; transaction-level
precision measured against manifest; WMAPE reported per category with bias;
pipeline end-to-end in a single command with per-stage run logging; zero
sensitive data committed to the repository.
