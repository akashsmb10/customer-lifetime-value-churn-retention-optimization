SELECT customer, date_trunc('month', min(date)) AS first_observed_cohort,
sum(revenue) AS historical_gross_value FROM orders GROUP BY customer;
