# Learn and defend this project

Begin with the business question: prioritize valuable customers at risk, then test whether intervention actually helps. Trace the chain from invoice audit → pre-cutoff RFM → inactivity labels → cohorts and survival → risk probabilities → finite-horizon value → explicit retention scenarios.

## 1. What is churn here?

No valid purchase within 77 days after cutoff among eligible customers; it is inactivity, not permanent exit.

## 2. How was the threshold chosen?

Pre-training positive interpurchase-gap 90th percentile, rounded to weeks, with ±28-day sensitivity; repeat-buyer and censoring bias are disclosed.

## 3. What is retention?

Continued activity in an observed period; cohort monthly retention differs from avoiding the first inactivity spell.

## 4. What is a cohort?

Customers grouped by first observed purchase month; actual acquisition is unknown.

## 5. What is RFM?

Recency since last invoice, frequency of invoices, monetary gross purchase total, all before cutoff.

## 6. How do recency definitions differ?

Churn features use cutoff minus last purchase; BG/NBD uses last minus first purchase occasion.

## 7. What is tenure?

Days from first observed purchase to cutoff, not confirmed relationship age.

## 8. Why exclude returns?

Unmatched negative lines cannot give reliable net customer economics; gross value limitations must remain explicit.

## 9. What is CLV?

Here it is a 77-day expected future gross-revenue estimate, not perpetual lifetime profit.

## 10. Why BG/NBD?

Noncontractual repeat transactions permit a probabilistic purchase/dropout model; stationary-rate assumptions can fail.

## 11. What does frequency mean in BG/NBD?

Repeat purchase days excluding the first; daily orders are aggregated.

## 12. What is T?

Days from first purchase to calibration end.

## 13. What is Gamma-Gamma?

A positive monetary-value model with customer heterogeneity and an independence assumption relative to purchase propensity.

## 14. How did you test monetary independence?

Spearman rank correlation among repeat purchasers; it diagnoses association but cannot establish independence.

## 15. Why might CLV estimates be wrong?

Seasonality, wholesalers, heavy tails, dropout misspecification, limited histories, returns and monetary dependence.

## 16. What is survival analysis?

It models time to the first completed inactivity spell while retaining right-censored customers.

## 17. What is censoring?

No event is observed by the administrative end; duration is known only to exceed that follow-up.

## 18. Why survival if you have a classifier?

Survival describes event timing and incomplete follow-up; classification predicts a fixed future window.

## 19. What is Kaplan-Meier?

Product of conditional survival proportions at event times; intervals use Greenwood uncertainty.

## 20. What is hazard?

Instantaneous event rate conditional on remaining event-free, not event probability by itself.

## 21. What is Cox PH?

A proportional baseline hazard model; hazard ratios are associative and require PH diagnostics.

## 22. Why no Cox model here?

First-gap events, short seasonal panel and left truncation weaken justified interpretation; KM is sufficient for the stated descriptive question.

## 23. Can a customer revive?

Yes. The first inactivity-spell endpoint persists; monthly cohort activity can rise again.

## 24. What is logistic regression?

A linear model of log odds; log1p and scaling accommodate skewed pre-cutoff features.

## 25. Why a tree model?

Histogram gradient boosting captures nonlinear thresholds/interactions as a justified XGBoost alternative.

## 26. What is XGBoost?

Regularized boosted decision trees; adding it would require the same temporal and identity safeguards, not guarantee improvement.

## 27. What is ROC-AUC?

Probability a randomly selected inactive customer has a higher score than a purchasing customer.

## 28. What is PR-AUC here?

Average precision, emphasizing positive-class retrieval and dependent on base rate.

## 29. Why not accuracy?

Accuracy hides positive-class errors and does not measure probability reliability or economic exposure.

## 30. What is calibration?

Customers scored near p should show about p inactivity; reliability bins and Brier assess this.

## 31. What is Brier score?

Mean squared error of probability against binary outcome; lower is better, with both discrimination and calibration components.

## 32. What is target leakage?

Features derived from future activity, the label window, survival events or future customer value contaminate prediction.

## 33. What is temporal validation?

Training precedes validation, calibration and test; non-overlapping outcomes and a seven-day embargo limit contamination.

## 34. How is customer leakage prevented?

Stable SHA256 partitions keep identities disjoint across supervised splits; IDs are not features.

## 35. Why not random splitting?

It mixes historical regimes and can share customer histories; temporal transfer is the real use case.

## 36. Can the model prove why customers churn?

No. Permutation importance and perturbations are predictive associations, not causal effects.

## 37. What is SHAP?

Additive attribution relative to a reference distribution; it is not causal and is not used in this project.

## 38. Why does high churn probability not automatically justify contact?

Value, costs, persuadability, consent and incremental treatment benefit determine whether contact pays.

## 39. Why combine churn with CLV?

It introduces economic exposure, but multiplying correlated dropout-aware forecasts can understate lost value; it is a scenario proxy.

## 40. How are capacity decisions optimized?

Under equal costs and homogeneous assumed effectiveness, choose the highest score; negative net cases justify no contact.

## 41. What is uplift?

Incremental outcome difference due to treatment, requiring a randomized or justified causal design; unavailable here.

## 42. What happens when behavior changes?

Monitor feature/score PSI, delayed calibration, cohort activity, value residuals and segment sizes; diagnose before retraining.

## 43. What does statistical significance mean?

Evidence against the test null conditional on assumptions; it does not demonstrate large economic impact.

## 44. Why bootstrap customers rather than invoices?

Invoices within a customer are dependent; the customer is the decision and inference unit.

## 45. How would a real bank differ?

Use balances, fee/interest contribution, multi-product relationships, operational dormant-account definitions, consent and regulatory controls, then test incremental retention.

## 46. What must you never claim?

Saved revenue, uplift, measured ROI, causal drivers, permanent churn, profit or live production banking effectiveness.

## 47. Why can risk × value win the simulator?

The simulator objective is defined from that same score; the win is arithmetic, not empirical proof of campaign effectiveness.

## 48. How would unequal costs change optimization?

Estimate incremental net benefit per action and solve constrained selection or a knapsack with budget/fairness constraints.

## 49. How are unobserved cohort cells treated?

NaN, not zero; final incomplete month excluded.

## 50. What are the verified model results?

logistic: ROC-AUC 0.7603, average precision 0.7543, Brier 0.2020; inspect full confusion matrix and calibration in the model card.
