# Data dictionary and source selection
Source: [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii), Daqing Chen, DOI 10.24432/C5CG6D, CC BY 4.0. The two sheets contain invoice-product lines for a UK non-store gift retailer, including wholesale customers. Executed dimensions: 1,067,371 rows × 8 columns; dates 2009-12-01 07:45:00 through 2011-12-09 12:50:00.

| Field | Meaning / rule |
|---|---|
| invoice | Purchase invoice identifier; C prefix is cancellation |
| stock | Product identifier; non-merchandise codes may remain, a limitation |
| description | Item text, unused by models |
| quantity | Units; require positive |
| date | Invoice timestamp, local timezone unspecified |
| price | Unit price GBP; require positive |
| customer | Customer identity, require observed identifier |
| country | Customer geography; not a protected-attribute fairness audit |
| revenue | quantity × price; gross positive purchase value |

Candidate evaluation: Online Retail provides only one year, making non-overlapping model and CLV windows restrictive. IBM Telco includes customer identity, tenure and charges but lacks invoice histories for genuine recency, cohorts, interpurchase gaps and transactional CLV. Online Retail II supports all those dimensions over two years, while sacrificing bank-specific products and confirmed churn. No public bank transaction source with comparable documented longitudinal value and churn histories was identified in this review. A bank-like presentation is a transfer discussion, not a bank-data claim.

Archive SHA256: `572e36277c2390fbfde10664750731e0a86f55e33470d91919085f0408e67bfb`. Invoice-level key is (customer, invoice). Models do not use identifiers. Clean rows: 779,425; orders: 36,969; observed customers: 5,878.
