# 04 — Validation framework

## Split by time, not at random

A random split would be wrong here. Loans from the same quarter share an
interest-rate environment, house-price trend and underwriting standard, so
scattering them across train and test lets the model see the future of its own
test set — the score would look good and would not survive deployment.

The split is chronological on `first_payment_date`:

| Set | Window (first payment date) | Role |
|---|---|---|
| **Train** | 2022-10-01 → 2023-09-30 | Fit candidate models |
| **Validation** | 2023-10-01 → 2023-12-31 | Compare models, select features, tune hyperparameters |
| **Test** | 2024-01-01 → 2024-03-31 | Touched once, for the final number |
| **Full train** | train + validation | Refit the chosen configuration before testing |

This mirrors how the model would be used: train on what has been observed,
score loans originated afterwards.

## Why refit on train + validation

Once the architecture, feature count and hyperparameters are settled on the
validation quarter, keeping validation data out of the final fit would waste a
quarter of labelled data for no benefit. The final model is therefore refit on
`X_full_train` and evaluated once on the test quarter. Because the test window
sits chronologically after everything used in fitting, the evaluation stays
honest.

Note that the test quarter's own base rate (**0.756%**) differs slightly from
the overall 0.774% — vintage-to-vintage variation, and a reminder that a
threshold tuned on one quarter is not automatically right for the next.

## One caveat carried forward

The target column is still present inside the `X_train` / `X_val` / `X_test`
frames (the notebook flags this in a comment). It is harmless in practice: the
`ColumnTransformer` selects features by explicit name lists and
`target_90plus` is in none of them, so the model never sees it. It does show up
as a zero-importance row in the permutation-importance table
([09](09-explainability.md)). Dropping it from `X` would be the tidier fix.
