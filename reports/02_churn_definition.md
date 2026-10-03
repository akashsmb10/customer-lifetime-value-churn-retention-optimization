# Threshold and windows
Results are generated from `artifacts/tables/results.json`. Monetary amounts are GBP. Observed gross purchases exclude cancellations, returns, nonpositive prices and missing customer identifiers. No experimental intervention response, banking balances, margin or acquisition costs are available.

The prediction estimand is no valid purchase during the next 77 days among customers whose recency is below 77 days at the scoring cutoff. This is operational forward inactivity, not confirmed permanent churn. Survival measures time to the first completed 77-day gap; a customer can later revive. These related estimands are not identical.

The threshold is the ceiling to whole weeks of the 90th percentile of strictly positive consecutive-invoice purchase gaps observed before 2010-06-01. Executed quantiles: `{'0.5': 16.979861111111113, '0.75': 41.94166666666667, '0.9': 71.91270833333333, '0.95': 95.07392361111113}`. The chosen threshold is **77 days**. This captures a long typical repeat-purchase gap without claiming an optimal business rule. Completed gaps underrepresent long censored spells and repeat buyers; sensitivity, not this quantile alone, supports use. The 90th percentile is a transparent design assumption. See `churn_sensitivity.csv` for threshold ±28 days and resulting eligible population/rate changes; populations change as eligibility changes.

Observation history begins with the first dataset purchase and ends strictly before the cutoff. Prediction intervals are [cutoff, cutoff + horizon). The partial last calendar day is excluded from labels. The four windows have a seven-day embargo after each complete prediction interval.
```json
{
  "train": {
    "cutoff": "2010-06-01",
    "prediction_end": "2010-08-17",
    "customers": 1134,
    "inactive_rate": 0.47530864197530864
  },
  "validation": {
    "cutoff": "2010-08-24",
    "prediction_end": "2010-11-09",
    "customers": 181,
    "inactive_rate": 0.3756906077348066
  },
  "calibration": {
    "cutoff": "2010-11-16",
    "prediction_end": "2011-02-01",
    "customers": 262,
    "inactive_rate": 0.5648854961832062
  },
  "test": {
    "cutoff": "2011-02-08",
    "prediction_end": "2011-04-26",
    "customers": 363,
    "inactive_rate": 0.5179063360881543
  }
}
```
Identity partitions use SHA256 modulo 10 and are disjoint across all four windows. Calendar shift and customer mix both influence holdout differences. No customer ID, post-cutoff behavior, future cohort revenue, survival endpoint or target appears in features. Hyperparameter choices are fixed; model selection uses validation Brier score. Calibration is fitted on a separate later block; its in-sample acceptance rule can be optimistic and is disclosed. Final holdout is not used to choose models/calibration.
