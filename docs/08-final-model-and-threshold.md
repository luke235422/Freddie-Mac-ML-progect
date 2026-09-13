# 08 — Final model and threshold

The chosen configuration — engineered features, imputation, mixed encoding, RFE
to 10 features, tuned XGBoost — is refit on **train + validation**
(2022-10 → 2023-12) and scored **once** on the test quarter (loans with first
payment in 2024 Q1).

## Test-set results

| Metric | Value |
|---|---|
| Positive prevalence | 0.7564% |
| **ROC-AUC** | **0.8311** |
| **Average Precision** | **0.03233** |
| **AP lift over base rate** | **4.27x** |
| Brier Score | 0.007568 |

How to read these:

- **ROC-AUC 0.831** — given two loans, one that went 90+ delinquent and one
  that did not, the model ranks them correctly 83% of the time. Consistent with
  the 0.827 seen on validation, so the model generalises across quarters rather
  than having been fitted to one.
- **Average precision 0.0323 against a 0.0076 base rate** is the number that
  matters: the model concentrates defaults **4.27x** better than random. In
  absolute terms it is still low, and it should be — predicting rare credit
  events from origination data alone is hard, and a paper reporting 0.9 here
  would be reporting leakage.
- **Brier 0.007568 against a prevalence of 0.007564** — the mean predicted
  probability lands on the true default rate almost exactly. The model is not
  systematically over- or under-predicting risk.

## Choosing an operating threshold

A probability has to become a decision. The default 0.5 cut-off is useless here:
almost no loan is ever predicted above 50%, so every loan would be passed.

101 thresholds between 0 and 0.19 are evaluated on precision, recall, F1, F2 and
specificity. **F2** is the selection criterion — it weights recall twice as
heavily as precision:

> Approving a loan that defaults costs tens of thousands. Flagging a good loan
> for extra review costs an underwriter's time. Missing a default is the
> expensive error, so recall is worth more than precision.

Best F2 = **0.1353** at threshold **0.0285** — flag any loan with a predicted
default probability above ~2.9%.

![Threshold selection](../assets/img/threshold-selection.png)

*The trade-off in one picture. Recall (orange) falls away steeply as the
threshold rises while precision (blue) barely improves — it never clears 7%
anywhere on the grid. F2 (red) peaks early, at 0.0285, and the curve is broad
enough that anything between roughly 0.02 and 0.04 performs about the same.
Specificity (purple) is already above 90% at the chosen point, which is what
keeps the review queue to a manageable size.*

## Performance at the chosen threshold

|  | Predicted good | Predicted at risk |
|---|---|---|
| **Actually good** | 133,089 (TN) | 12,944 (FP) |
| **Actually defaulted** | 629 (FN) | 484 (TP) |

| Metric | Value |
|---|---|
| Recall (sensitivity) | **43.49%** |
| Precision | **3.60%** |
| Specificity | 91.14% |
| F1 | 0.0666 |
| F2 | 0.1353 |
| Accuracy | 90.78% |

In plain terms: the model flags **9.1% of loans** (13,428 of 147,146) and that
flagged pool contains **43.5% of all loans that will go 90+ days delinquent**.
Within the flagged pool, 1 loan in 28 actually defaults, against 1 in 132 across
the whole book — a **4.8x concentration**.

Precision of 3.6% is not a flaw in the model, it is arithmetic: when only 0.76%
of cases are positive, any screen with meaningful recall will be mostly false
positives. The question is whether a 4.8x-enriched review queue covering 9% of
volume is worth an underwriter's time, and for a triage tool it plainly is. The
accuracy figure of 90.78% is reported for completeness and should be ignored —
it is *worse* than the 99.24% a do-nothing model scores, which is precisely why
accuracy was never the target.

Note that the notebook's printed labels for the confusion matrix are swapped;
scikit-learn returns `[[TN, FP], [FN, TP]]`, and the table above uses the
correct assignment (confirmed by the precision and recall values).

## Threshold is a business dial, not a constant

The F2 choice encodes one particular view of relative costs. The full
threshold-by-metric table is in the notebook, and the curve is smooth, so the
cut-off can be moved to match an actual review budget: raising it shrinks the
queue and raises precision, lowering it catches more defaults. It should also be
re-tuned per vintage — each quarter's base rate differs.
