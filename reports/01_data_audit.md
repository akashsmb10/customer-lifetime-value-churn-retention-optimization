# Executed audit
```json
{
  "raw_rows": 1067371,
  "raw_columns": 8,
  "duplicates": 34335,
  "missing_customer_rows": 243007,
  "negative_quantity_rows": 22950,
  "nonpositive_price_rows": 6207,
  "cancellation_rows": 19494,
  "clean_rows": 779425,
  "orders": 36969,
  "customers": 5878,
  "start": "2009-12-01 07:45:00",
  "end": "2011-12-09 12:50:00",
  "archive_sha256": "572e36277c2390fbfde10664750731e0a86f55e33470d91919085f0408e67bfb",
  "missingness": {
    "invoice": 0,
    "stock": 0,
    "description": 4382,
    "quantity": 0,
    "date": 0,
    "price": 0,
    "customer": 243007,
    "country": 0
  },
  "gross_positive_revenue": 17374804.268,
  "outside_documented_date_rows": 0,
  "invoice_ids_multiple_customers": 0,
  "positive_revenue_p99_invoice": 3610.5
}
```
Counts of exclusions overlap and must not be added. Exact duplicate lines are removed; identical legitimate repeated item lines may also be removed. Negative quantities/cancellations are audited rather than netted. Dates are parsed from the workbook; there are no null-date rows after cleaning. Dataset timestamps are historical, not impossible relative to extraction. Same invoice/customer lines are aggregated. Outliers are retained; the decision score must be checked for concentration. See schema, missingness, geography and monthly-health tables.
