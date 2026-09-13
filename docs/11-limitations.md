# 11 — Limitations and next steps

What this model does and does not support, and the changes most likely to
improve it.

## What the model does not do

- **It is not a loss model.** It predicts the *probability* of 90+ day
  delinquency at month 20, not loss given default or expected loss. No dollar
  amount should be read off it.
- **It sees origination data only.** No macroeconomic path, no house-price
  index, no employment data, and no payment behaviour after origination. A
  model allowed to see the first six months of payments would beat this one
  easily — and would answer a different, easier question.
- **It is trained on one rate environment.** Loans originated 2022 Q4 through
  2024 Q1 all come from a high-rate, low-refinance period. Applied to a 2021
  vintage, or to whatever follows the next rate cut, performance should be
  expected to drop until the model is refit.
- **It is trained on conforming loans only.** Freddie Mac's Standard dataset
  excludes non-conforming, subprime and jumbo lending, which is the population
  where credit risk is most interesting. The 0.77% base rate reflects that
  selection.
- **The 20-month horizon is a modelling choice.** Defaults arriving in year
  three are invisible to this target.

## Known issues in the current code

Small, real, and worth fixing before anyone builds on this:

1. **The missingness indicators never reach the model.**
   `dti_was_missing` and `fico_score_was_missing` are created in
   `new_features()` but appear in none of the `ColumnTransformer` column lists,
   so they are dropped. Given that [03](03-eda.md) showed missing DTI carries
   2.2x and missing FICO 1.7x the average risk, adding them to the numerical
   list is the single cheapest improvement available.
2. **`target_90plus` is still inside the `X` frames.** Harmless — the
   transformers select columns by name and never pick it up — but it should be
   dropped, if only so it stops appearing in importance tables.
3. **Confusion-matrix print labels are swapped** in the final evaluation cell.
   scikit-learn returns `[[TN, FP], [FN, TP]]`. The values are right; the
   labels above them are not. [08](08-final-model-and-threshold.md) reports the
   corrected assignment.
4. **Permutation importance is computed in-sample**, on a pipeline fit to the
   test set and without the RFE step. It maps where signal lives, but it is not
   a statement about the deployed model's generalisation.
5. **`property_value` is fed through two branches at once** (numerical and
   target-encoded), an accident of the column lists rather than a decision.
6. **The threshold is tuned on the test set.** The 0.0285 cut-off maximising F2
   was selected using test labels, which makes the reported F2 mildly
   optimistic. The ranking metrics (ROC-AUC, AP) are unaffected — they need no
   threshold — but a fully clean protocol would pick the cut-off on validation
   and only then apply it to test.

## Next steps, roughly by value per hour spent

1. **Fix the missingness indicators** (issue 1) and re-measure.
2. **Move threshold selection to the validation set**, and report the test F2 at
   that pre-committed cut-off.
3. **Add vintage-aware cross-validation.** A single train/validation/test split
   gives one estimate with no error bar. Rolling-origin validation across the
   five quarters would show how stable the 0.831 AUC actually is.
4. **Add macro context.** A regional house-price index and unemployment rate
   joined on state or MSA would give the model the one thing it most obviously
   lacks, and would likely reduce its reliance on target-encoded geography
   standing in for those variables.
5. **Compare against `scale_pos_weight` or focal loss.** The current design
   handles imbalance through metrics and thresholding, which preserves
   calibration. Reweighting might buy recall; the question is how much
   calibration it costs, and it is a measurable trade-off rather than a
   judgement call.
6. **Try LightGBM with native categorical handling**, which would sidestep the
   encoding layer entirely and offers a clean benchmark for whether the
   target-encoding work is pulling its weight.
7. **Make the pipeline a module.** The notebook is the right medium for the
   analysis, but `cleaning()`, `new_features()` and the `ColumnTransformer`
   belong in an importable `src/` so that a scoring script and the notebook
   cannot drift apart.
