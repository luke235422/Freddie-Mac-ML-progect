# 05 — Preprocessing pipeline

Everything below lives inside a single scikit-learn `Pipeline`. That matters
more than it sounds: imputation and target encoding both learn from the data, so
if they ran as loose notebook cells before the split they would absorb
information from the validation and test rows. Inside a pipeline, every
`fit` sees only the training fold.

```
Pipeline
├── "new features"        FunctionTransformer(new_features)
├── "impute and encode"   ColumnTransformer
│   ├── numerical            IterativeImputer
│   ├── categorical one hot  SimpleImputer(constant) -> OneHotEncoder
│   └── categorical target   SimpleImputer(constant) -> TargetEncoder
├── "selector"            RFE
└── "model"               XGBClassifier
```

## Step 1 — Feature engineering

`new_features()` adds five columns:

| Column | Definition | Purpose |
|---|---|---|
| `property_value` | `original_ltv / original_upb` | Implied property value |
| `All_known_morgage` | `original_cltv * property_value` | Total secured debt including junior liens |
| `dti_was_missing` | `original_dti.isnull()` | Preserve the missingness signal found in [03](03-eda.md) |
| `fico_score_was_missing` | `classic_fico.isnull()` | Same, for credit score |
| `position_combined` | `postal_code + "-" + msa + "-" + property_state` | One high-resolution location key |

`position_combined` is the interesting one. ZIP, MSA and state each carry
geographic risk, but individually they are coarse or noisy. Concatenating them
creates a single very high-cardinality key which target encoding can then turn
into one well-estimated risk number — a cleaner way to exploit geography than
three overlapping columns.

The final loop normalises every column to `object` dtype with real `np.nan`
markers, so that the imputers behave consistently regardless of whether pandas
handed over a nullable or a numpy dtype.

## Step 2a — Numerical features: iterative imputation

`IterativeImputer(max_iter=10, random_state=1)` fills the numerical columns by
modelling each one against the others, rather than substituting a mean.

This is the right call for this dataset because the numerical features are
strongly interrelated (LTV, CLTV and MI percentage move together — see
[03](03-eda.md)), so a missing CLTV can be predicted well from LTV and MI. A
mean would flatten exactly the leverage structure the model needs. The cost is
compute: iterative imputation is the slowest step in the pipeline.

## Step 2b — Low-cardinality categoricals: one-hot

Constant imputation with the literal value `"missing"`, then
`OneHotEncoder(handle_unknown="ignore")`.

- `"missing"` as its own level, rather than a filled-in mode, keeps the
  missingness signal visible to the model.
- `handle_unknown="ignore"` is what makes the pipeline safe under a
  chronological split: a category that only appears in a later quarter
  (a new seller, a new program code) becomes all-zeros instead of raising.

Columns: first-time buyer, number of units, occupancy, channel, amortization
type, prepayment penalty, property type, loan purpose, number of borrowers,
super-conforming flag, special eligibility program, valuation method, first
payment month. **13 fields.**

## Step 2c — High-cardinality categoricals: target encoding

`TargetEncoder(cv=StratifiedKFold(5, shuffle=True, random_state=42), target_type="binary", smooth="auto")`

Columns: `msa_or_metropolitan_division`, `property_state`, `postal_code`,
`original_loan_term`, `seller_name`, `effective_loan_duration`, plus the three
engineered columns including `position_combined`.

One-hot encoding ZIP codes would add tens of thousands of nearly empty columns.
Target encoding replaces each level with its own default rate instead, giving
one dense, informative feature per field. Two safeguards make it usable:

- **Internal cross-fitting.** Each row's encoded value is computed from folds
  that exclude it, so a loan's own target never feeds its own feature. Without
  this, target encoding leaks and overfits badly.
- **`smooth="auto"`.** Rare levels are shrunk toward the global mean, in
  proportion to how little data supports them. With a 0.774% base rate, a ZIP
  with 3 loans and 1 default would otherwise read as 33% risk; smoothing pulls
  that back to something defensible.

After the `ColumnTransformer`, the design matrix has **61 columns**.

## Note on the two engineered numerics

`property_value` is passed to the numerical branch **and**, together with
`All_known_morgage`, to the target-encoding branch, so those two are represented
twice in different forms. Redundancy a tree model absorbs without difficulty,
and RFE then picks whichever representation earns its place — but it is an
accident of the column lists rather than a deliberate choice.

The `dti_was_missing` and `fico_score_was_missing` indicators are created but
appear in none of the three column lists, so the `ColumnTransformer` drops them
(its default is `remainder="drop"`). The missingness signal therefore survives
only through the `"missing"` one-hot level, not as the dedicated flags intended.
Adding them to the numerical list is a one-line improvement — see
[11](11-limitations.md).
