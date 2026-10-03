# Customer-level statistical findings
H0: pre-cutoff monetary-value distributions are identical for future inactive and purchasing holdout customers. H1: the distributions differ (two-sided Mann-Whitney). Independent customers, ordinal/continuous measurement and exchangeability under H0 are assumed; this is not a causal design. A median interpretation needs similar distribution shapes. Rank-biserial effect is 2U/(n_inactive n_retained)−1, positive for higher inactive values.
```json
{
  "test": "Mann-Whitney U",
  "statistic": 8100.0,
  "p_value": 6.378956777275112e-17,
  "rank_biserial": -0.5075987841945289,
  "inactive_median": 834.26,
  "retained_median": 2586.21,
  "median_difference_ci95": [
    -2160.38525,
    -1105.9627500000008
  ],
  "inactive_n": 188,
  "retained_n": 175,
  "inactive_rate_wilson_ci95": [
    0.46658560760766227,
    0.568852044509936
  ]
}
```
Median-difference percentile interval uses 2,000 independent within-group customer bootstrap samples, seed 42. Wilson interval describes the holdout inactivity proportion conditional on this sample, not future stationarity. Statistical evidence does not establish practical profitability: inspect GBP median differences and the effect size. The group label is future behavior; the test is descriptive and never becomes a feature. One prespecified test avoids a fishing expedition; no causal attribution is made.
