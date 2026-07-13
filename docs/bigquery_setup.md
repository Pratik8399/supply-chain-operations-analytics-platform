"""
BigQuery Setup Guide (Free Tier)

Why BigQuery instead of Snowflake for this portfolio project?
Both are cloud SQL data warehouses sharing the same core concepts:
staging, curated facts, dimensions, SQL views, governance, and cost-aware
access. BigQuery offers a generous free tier (1 TB of processed query data
per month and 10 GB active storage) making it portfolio-friendly. In a
Snowflake-based enterprise environment, the same warehouse design could be
ported using Snowflake tables, views, clustering, and RBAC patterns, with
dialect and operational differences adjusted.

This guide assumes you've never used GCP before.
"""

# ===== STEP 1: Create a GCP Account =====
1. Go to https://cloud.google.com/free
2. Sign up with your Google / Gmail account
3. Accept the free-tier terms
4. You get $300 free credit + perpetual free tier
   (1 TB processed query data/month, 10 GB active storage).
   Sandbox mode works without a credit card; note sandbox tables
   expire after 60 days.

# ===== STEP 2: Create a GCP Project =====
1. Go to https://console.cloud.google.com
2. Click the project dropdown (top-left, next to "Google Cloud")
3. Click "NEW PROJECT"
4. Name it: "Supply Chain Analytics" (or whatever)
5. Click "CREATE"
6. Wait ~30 seconds for the project to initialize
7. Once created, click the project name to enter it
8. Copy your PROJECT_ID from the dashboard (gray text under the title)
   Example: "my-project-12345"

# ===== STEP 3: Enable BigQuery API =====
1. In the GCP console, search for "BigQuery API" (top search bar)
2. Click on it, then "ENABLE"
3. Wait for it to enable (~10 seconds)

# ===== STEP 4: Create a BigQuery Dataset =====
1. Go to https://console.cloud.google.com/bigquery
2. In the left panel under your project, click "CREATE DATASET"
3. Name: "supply_chain"
4. Location: "us (multiple regions in US)"
5. Click "CREATE DATASET"

# ===== STEP 5: Set Up Local Authentication =====

Option A: Use the gcloud CLI (simpler)
  1. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install
  2. Run: gcloud auth application-default login
  3. A browser window opens; sign in with your GCP account
  4. Approve the request
  5. Done — credentials are saved locally

Option B: Create a service account + JSON key (more control, not needed for dev)
  1. In GCP console, go to Service Accounts (search top bar)
  2. Click "CREATE SERVICE ACCOUNT"
  3. Name: "supply-chain-analytics"
  4. Grant it "BigQuery Admin" role (step 2 of the wizard)
  5. In "Keys" tab, click "ADD KEY" > "Create new key" > JSON
  6. Save the JSON file to ~/.google/credentials.json
  7. Set env var: export GOOGLE_APPLICATION_CREDENTIALS=~/.google/credentials.json

# ===== STEP 6: Install the Python Client =====
pip install google-cloud-bigquery

# ===== STEP 7: Test =====
Run this Python script:

```python
from google.cloud import bigquery
import os

os.environ['GCP_PROJECT_ID'] = 'YOUR_PROJECT_ID_HERE'
client = bigquery.Client(project=os.environ['GCP_PROJECT_ID'])
print(f"Connected to {os.environ['GCP_PROJECT_ID']}")
datasets = list(client.list_datasets())
print(f"Datasets: {[d.dataset_id for d in datasets]}")
```

If you see your "supply_chain" dataset listed, you're good.

# ===== STEP 8: Run the Pipeline =====
Set your project ID in the environment:
  export GCP_PROJECT_ID='your-project-id'

Then run the full pipeline:
  python etl/pipeline_orchestration.py

The orchestration will detect the env var, wire in the BigQuery stage,
and load your data.

# ===== Monitoring Costs (you won't hit the free tier) =====
https://console.cloud.google.com/billing
Shows all costs in real-time. The pipeline runs ~100k rows through maybe
10-20 queries; that's ~50 MB scanned = negligible cost even without the
free tier. You'll never exceed the $1.25/TB threshold.

# ===== Troubleshooting =====

"google-cloud-bigquery not installed"
  -> pip install google-cloud-bigquery

"GCP_PROJECT_ID not set"
  -> export GCP_PROJECT_ID='your-project-id-12345'
  -> (get it from the GCP console dashboard)

"401 Unauthorized"
  -> You haven't authenticated. Run: gcloud auth application-default login

"Dataset not found"
  -> Create it in the BigQuery console (see STEP 4 above)
  -> Or the pipeline will try to create it automatically (less reliable)

# ===== Interview Defense =====

"Why BigQuery instead of Snowflake?"
"BigQuery serves as the cloud warehouse layer and demonstrates the concepts
a Snowflake environment relies on: staging, curated facts and dimensions,
SQL views, governance, and cost-aware access. Its free tier (1 TB processed
query data/month, 10 GB active storage) makes it accessible for a portfolio
project without a corporate account. In a Snowflake-based enterprise
environment, this same warehouse design could be ported using Snowflake
tables, views, clustering, and RBAC patterns — dialects and operational
details differ, but the design thinking transfers directly."

"Show me your BigQuery console"
(Pull up https://console.cloud.google.com/bigquery?project=YOUR_PROJECT)
"Here's the dataset, the fact tables, and the views. Query run history shows
every load and analytical query. Cost tracking [show billing] shows total
spend under $1 for the entire project."
