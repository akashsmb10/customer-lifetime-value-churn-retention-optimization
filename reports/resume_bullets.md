# Customer Lifetime Value, Churn & Retention Optimization
Python | SQL/DuckDB | scikit-learn | Kaplan-Meier | BG/NBD | Gamma-Gamma | Streamlit | pytest

- Analyzed 1,067,371 public transaction lines across 5,878 identified customers, deriving leakage-controlled inactivity labels and cohort retention analyses.
- Evaluated customer-disjoint temporal churn models, achieving holdout ROC-AUC 0.760 and Brier score 0.202, with separate probability calibration and finite-horizon value backtesting.
- Built a retention decision dashboard and executed 8 DuckDB queries comparing risk, value and combined targeting under explicitly assumed intervention economics.

Traceability: all counts and metrics originate in artifacts/tables/results.json; this describes analysis and simulated decisions, not realized business uplift.
