# Business decision
Which currently active customers should receive scarce retention attention when risk and economic exposure differ? Use a reproducible ranking as input to a randomized pilot, not an automatic marketing decision.

Results are generated from `artifacts/tables/results.json`. Monetary amounts are GBP. Observed gross purchases exclude cancellations, returns, nonpositive prices and missing customer identifiers. No experimental intervention response, banking balances, margin or acquisition costs are available.

The prediction estimand is no valid purchase during the next 77 days among customers whose recency is below 77 days at the scoring cutoff. This is operational forward inactivity, not confirmed permanent churn. Survival measures time to the first completed 77-day gap; a customer can later revive. These related estimands are not identical.


Features use all valid history strictly before each cutoff: recency, invoice frequency, historical monetary total, average invoice value, observed tenure and orders in the preceding 90 days. Retention actions are candidate experiments: high value/high risk receives tailored outreach; high value/low risk receives proactive service; low value/high risk receives low-cost channels; low value/low risk receives routine nurture. Median risk/value split defines descriptive segments, not a decision threshold.
