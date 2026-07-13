# Raw Data — Download Instructions

This project uses the **DataCo Smart Supply Chain** dataset from Kaggle.

1. Go to Kaggle and search: "DataCo Smart Supply Chain For Big Data Analysis"
   (dataset by shashwatwork / DataCo Global).
2. Download `DataCoSupplyChainDataset.csv` (~180k rows, ~91 MB).
3. Place it in this folder: `data/raw/DataCoSupplyChainDataset.csv`

The raw file is deliberately git-ignored:
- GitHub discourages files this large in source repos.
- Kaggle dataset licenses generally do not permit redistribution;
  linking + ingestion instructions is the compliant pattern.

`data/sample/sample_dataco_5k.csv` is a small schema-compatible DEV SAMPLE
(synthetically constructed to mirror the DataCo column layout) so the
pipeline can be smoke-tested before the real download. All reported project
metrics come from runs against the real dataset.
