# Survival analysis
S(t)=P(T>t), where T is days from first observed purchase until the first completed 77-day purchase gap. The hazard h(t)=lim[Δt→0] P(t≤T<t+Δt | T≥t)/Δt. Kaplan-Meier is the product over event times of (1−d_j/n_j). A subsequent revival does not erase the first event. If no qualifying gap completes by the end of observation, duration ends at the administrative cutoff and event=0.
```json
{
  "First observed Jan-Jun": {
    "customers": 2717,
    "events": 2613,
    "survival_180_days": 0.15393792898397185,
    "median_days": 77.0
  },
  "First observed Jul-Dec": {
    "customers": 3161,
    "events": 2388,
    "survival_180_days": 0.19117101560927535,
    "median_days": 77.0
  }
}
```
Curves include Greenwood confidence intervals. Jan-Jun versus Jul-Dec first-observed season is a baseline segment; eventual lifetime spend would introduce post-event information. First-observed customers are not verified new customers. There is a structural event-free interval before the threshold. Cohort length and seasonality limit group comparisons. Cox PH is deliberately omitted: stationarity, left truncation and first-gap events make an explanatory PH fit insufficiently justified here. In a longer bank panel, fit baseline covariates, inspect Schoenfeld residuals, time interactions and PH assumptions, and interpret hazard ratios associationally.
