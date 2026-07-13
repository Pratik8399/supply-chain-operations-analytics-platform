# Executive Summary — Operations Analytics
*Generated 13 Jul 2026 by the automated insight module (template-based narrative generation).*

## Business at a glance
Revenue of $36,785,077 across 65,752 orders and 50 categories, with overall on-time-in-full at 42.3%.

OTIF declined in the latest month (40.8% vs 41.3% prior), with average shipping delay of 3.6 days.

## Alert posture
13,607 open alerts (1085 critical, 9598 high). The largest queue routes to **Logistics**, driven primarily by shipments delivered 4+ days past the scheduled window.
Recommended first action: Review carrier and route performance for the flagged orders; escalate repeat lanes.

## Forecast health
Demand forecast WMAPE ranges from 14.6% (Camping & Hiking) to 320.9% (Baseball & Softball). Categories above 30% WMAPE should be prioritized for planner review; persistent positive bias indicates systematic over-forecasting and excess inventory risk.

## Where to act
Detailed, team-routed items with review SLAs: `outputs/stakeholder_action_items.csv` (also surfaced on the Anomaly Detection Center dashboard page).