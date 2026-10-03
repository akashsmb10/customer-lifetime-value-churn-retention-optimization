# Retention policy comparison
Risk-only, value-only, risk × value and random targeting are compared at 5%, 10%, 20% contact capacity. Random results average 200 seeded without-replacement samples. Priority is p(inactivity) × estimated future gross revenue, a value-at-risk proxy, not expected treatment benefit. Under homogeneous treatment success and equal costs, selecting largest scores maximizes the scenario objective for a fixed contact count (exchange argument). With heterogeneous costs/uplift, estimate incremental benefit and solve a knapsack/constrained optimization instead. Capacity is a ceiling: a negative net scenario should recommend no contact rather than force spending.

Scenario retained revenue = sum(priority) × assumed_success. Scenario net contribution = retained revenue × assumed_margin − contacts × (contact_cost + incentive). Incentives are charged to every contact. Margin is 30%; success takes 2%, 5%, 10%; costs GBP 1/5/10; incentives GBP 0/10/25. None are observed. An illustrative 10%-capacity, GBP 5 contact, GBP 10 incentive and 5% effectiveness slice:
```
  strategy  capacity  contacts  contact_cost  assumed_success  incentive  assumed_margin  predicted_value_at_risk  scenario_retained_revenue  scenario_net_contribution
    random       0.1        36             5             0.05         10             0.3              5450.551841                 272.527592                -458.241722
      risk       0.1        36             5             0.05         10             0.3              6650.035339                 332.501767                -440.249470
     value       0.1        36             5             0.05         10             0.3              5995.340646                 299.767032                -450.069890
risk_value       0.1        36             5             0.05         10             0.3             10804.388539                 540.219427                -377.934172
```
Risk × value can win its own arithmetic objective by construction; this is not evidence of actual treatment superiority. Test heterogeneous response with a randomized pilot, intention-to-treat analysis, holdout controls, confidence intervals, incremental margin and customer experience guardrails. Churn risk is not persuadability. Conditional lost value may differ from unconditional BG/NBD forecasts; evaluate risk/value overlap before production.
