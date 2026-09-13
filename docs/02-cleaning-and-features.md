# 02 — Cleaning and feature construction

All of this happens in one `cleaning()` function applied to the joined frame, so
the same treatment is guaranteed for every quarter.

## Sentinel codes become missing values

Freddie Mac encodes "not available" as out-of-range numbers rather than blanks.
Left untouched, a FICO of `9999` would be read as a genuine score and would
wreck any model. Each one is mapped to `NaN`:

| Field | Sentinel | Meaning |
|---|---|---|
| `classic_fico` | `9999` | Score not available |
| `mi_percentage` | `999` | MI percentage unknown |
| `number_of_units` | `99` | Unknown |
| `original_cltv`, `original_dti`, `original_ltv` | `999` | Unknown |
| `occupancy_status`, `channel`, `loan_purpose`, `first_time_homebuyer_indicator` | `"9"` | Unknown |
| `property_type` | `"99"` | Unknown |
| `postal_code` | `000` | Unknown |
| `number_of_borrowers` | `99` | Unknown |
| `property_valuation_method` | `7` | Not applicable |

Missingness is not discarded, though — section [03](03-eda.md) tests whether a
missing value is itself a risk signal, and it is.

## Recoding

- **Y/N flags to 0/1**: `first_time_homebuyer_indicator`,
  `prepayment_penalty_indicator`, `super_conforming_flag`.
- **`number_of_borrowers` capped at 2.** Values 3 through 10 collapse to 2.
  Three-plus-borrower loans are rare enough that they would only add sparse,
  noisy categories; the meaningful distinction is single versus joint borrower.
- **`property_valuation_method` given readable labels**: appraisal waiver
  (ACE), appraisal, other, ACE_PDR.
- **`special_eligibility_program`**: missing becomes the explicit category
  `NONE_OR_NA`, since "no program" is information, not absence of it.

## Derived columns

| New column | How | Why |
|---|---|---|
| `first_payment_date` | `YYYYMM` parsed to a real date | Needed as the sort key for the chronological split |
| `first_payment_month` | Calendar month, 1–12 | Captures seasonality in origination |
| `effective_loan_duration` | Months between `first_payment_date` and `maturity_date` | The actual term of the contract, more trustworthy than the stated `original_loan_term` |

## Columns dropped

Removed because they are empty, near-constant, or inapplicable to recent
vintages:

- `pre_harp_loan_sequence_number`, `harp_indicator` — HARP ended in 2018.
- `interest_only_indicator` — effectively absent from post-crisis conforming
  originations.
- `vantagescore_4_0` — too sparsely populated in these quarters to use.
- `maturity_date` — its information is already in `effective_loan_duration`.

`loan_identifier` is deliberately kept, not as a feature but as the join key
that later lets SHAP values be attributed to individual loans for the dashboard.

## The modelling column set

**26 features + target.** Split by type, because the two groups are treated
differently downstream:

**Numerical (7)** — cast to `float64`:
`classic_fico`, `mi_percentage`, `original_cltv`, `original_dti`,
`original_upb`, `original_ltv`, `original_interest_rate`

**Categorical (19)** — cast to `string`:
`first_time_homebuyer_indicator`, `msa_or_metropolitan_division`,
`number_of_units`, `occupancy_status`, `channel`,
`prepayment_penalty_indicator`, `amortization_type`, `property_state`,
`property_type`, `postal_code`, `loan_purpose`, `original_loan_term`,
`number_of_borrowers`, `seller_name`, `super_conforming_flag`,
`special_eligibility_program`, `property_valuation_method`,
`first_payment_month`, `effective_loan_duration`

Two choices worth flagging. `original_loan_term` and
`effective_loan_duration` are treated as **categorical** even though they are
numbers: mortgage terms cluster on a handful of values (360, 180, 240 months),
so their levels behave like categories rather than a continuum. And the
encoding strategy is decided here too — low-cardinality fields go to one-hot,
high-cardinality ones (ZIP, MSA, state, seller) to target encoding. See
[05](05-preprocessing-pipeline.md).
