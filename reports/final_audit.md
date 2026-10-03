# Final independent audit

- PASS: Metrics independently recomputed
- PASS: Classification metrics and confusion matrix
- PASS: Dataset dimensions and cleaning independently checked
- PASS: Value backtest independently checked
- PASS: Priority scores correct
- PASS: Input checksum
- PASS: Clean rebuild identical results
- PASS: Finite nonnegative CLV
- PASS: No future features
- PASS: Nonoverlapping prediction windows
- PASS: Customer identities disjoint
- PASS: SQL execution
- PASS: SQL RFM parity
- PASS: SQL concentration parity
- PASS: Nine executed notebooks
- PASS: All nine dashboard pages
- PASS: Critical pytest suite
- PASS: Serialized models load
- PASS: Dashboard HTTP health checked
- PASS: README metrics traceable
- PASS: Exactly three verified resume bullets
- PASS: No unfinished markers
- PASS: Censoring method reviewed
- PASS: CLV assumptions and holdout error disclosed
- PASS: Intervention economics explicitly assumed

Validation is executed by verify_project.py; conceptual method checks reflect a code/report review, not a causal or regulatory certification. Pipeline regenerated artifacts from raw data; input checksum is stable. Tests and dashboard page executions use the saved models/tables. The external Streamlit HTTP health check is recorded separately in reports/dashboard_health.txt.

...............                                                          [100%]
15 passed in 4.55s

Remaining analytical limitations: retail transfer, unknown true acquisition, gross positive revenue, seasonal censoring, finite-horizon CLV assumptions, small identity-disjoint validation blocks and homogeneous assumed treatment effects. No measured business uplift.
