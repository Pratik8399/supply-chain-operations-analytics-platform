# BigQuery Cost Controls (how this stays at $0)

## The billing model in one line
On-demand BigQuery bills by **bytes scanned by queries** — not rows
returned, not compute time. `LIMIT 10` does NOT reduce cost: charges depend
on the columns and partitions scanned.

## Free things this project relies on
- **Batch load jobs are free** (the loader uses them; no streaming inserts,
  which are billed).
- **Free tier:** 1 TB of query bytes per month + 10 GB storage.
- **Sandbox mode:** BigQuery works without a credit card — honest caveat:
  sandbox tables/views **expire after 60 days**; re-run the loader to
  refresh, or attach billing (still effectively $0 at this scale).

## Rules encoded in this repo
1. Tables are **partitioned** by date and **clustered** by category/market
   (see 01_create_dataset_and_tables.sql) — partition pruning is the real
   cost lever, not LIMIT.
2. Views select **named columns only** — no SELECT * anywhere in
   bigquery_sql/ marts.
3. BI tools connect to **small aggregated views**, never base tables.
4. **No streaming inserts** — batch loads only.
5. Demo scale: this project's full scan is ~50 MB; even hundreds of runs
   stay orders of magnitude inside the free tier.

## Verify before running anything big
The BigQuery console shows "This query will process X MB" before execution
(top-right of the editor). Make checking it a habit; that number is the bill.
