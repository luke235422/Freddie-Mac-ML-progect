# Documentation

A walkthrough of `final_model.ipynb`, one file per section of the notebook.
Read in order for the full story, or jump to the part you care about.

![Power BI dashboard](../assets/img/dashboard-overview.png)

| # | Document | What it covers |
|---|---|---|
| 01 | [Data and target definition](01-data-and-target.md) | Source files, how the 90+ days delinquency target is built, and whether dropping loans biases it |
| 02 | [Cleaning and feature construction](02-cleaning-and-features.md) | Sentinel codes, the 26 modelling columns, derived columns |
| 03 | [Exploratory analysis](03-eda.md) | Class imbalance, risk ratios, missing-value signal, mutual information |
| 04 | [Validation framework](04-validation-framework.md) | Why the split is chronological and where the cut-offs fall |
| 05 | [Preprocessing pipeline](05-preprocessing-pipeline.md) | Feature engineering, imputation, one-hot vs target encoding |
| 06 | [Model selection](06-model-selection.md) | Four candidates compared on the validation quarter, plus calibration |
| 07 | [Feature selection and tuning](07-feature-selection-and-tuning.md) | RFE sweep and the hyperparameter search |
| 08 | [Final model and threshold](08-final-model-and-threshold.md) | Held-out test results and the F2-based cut-off |
| 09 | [Explainability](09-explainability.md) | Permutation importance, SHAP, and the exports that feed Power BI |
| 10 | [Power BI dashboard](10-dashboard.md) | What the dashboard shows and why the `.pbix` is not in the repo |
| 11 | [Limitations and next steps](11-limitations.md) | Honest read of what this model can and cannot do |

## The project in one paragraph

Using Freddie Mac's public loan-level data, the project predicts whether a
newly originated mortgage will be **90 or more days delinquent at loan age 20
months**, from origination-time information only. Roughly 1.02 million loans
from five quarterly vintages (2022 Q4 through 2024 Q1) carry that label, and
only **0.77%** of them are positive, so the whole design — chronological
validation, ranking metrics instead of accuracy, an F2-driven threshold —
follows from that imbalance. The chosen model is a gradient-boosted tree
(XGBoost) on 10 selected features, reaching **ROC-AUC 0.831** and **average
precision 0.032 (4.27x the base rate)** on a quarter of loans it never saw
during training.

## Figures

Every chart in these documents is the notebook's own output, and every
dashboard screenshot is the live Power BI report. They live in
[`../assets/img/`](../assets/img/) under descriptive names — `eda-risk-fico.png`,
`tuning-heatmap.png`, `dashboard-threshold.png` — so a figure can be found
without opening each file.

## Numbers in these documents

Every figure quoted here is taken from the stored outputs of
`final_model.ipynb` as committed, not re-computed. Re-running the notebook on
freshly downloaded data should reproduce them, with small movements possible
where the code depends on a random draw (the SHAP background sample, the
`IterativeImputer`).
