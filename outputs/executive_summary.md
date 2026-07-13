# Executive Summary — Operations Analytics
*Generated 12 Jul 2026 by the automated insight module (template-based narrative generation).*

## Business at a glance
Revenue of $3,844,144 across 4,800 orders and 9 categories, with overall on-time-in-full at 39.0%.

OTIF improved in the latest month (46.8% vs 34.5% prior), with average shipping delay of 4.6 days.

## Alert posture
321 open alerts (30 critical, 108 high). The largest queue routes to **Demand Planning**, driven primarily by actual demand diverging >15% from plan.
Recommended first action: Review planner assumptions for the flagged category-weeks; re-baseline if drift persists.

## Forecast health
Demand forecast WMAPE ranges from 43.6% (Men's Footwear) to 79.7% (Women's Apparel). Categories above 30% WMAPE should be prioritized for planner review; persistent positive bias indicates systematic over-forecasting and excess inventory risk.

## Where to act
Detailed, team-routed items with review SLAs: `outputs/stakeholder_action_items.csv` (also surfaced on the Anomaly Detection Center dashboard page).