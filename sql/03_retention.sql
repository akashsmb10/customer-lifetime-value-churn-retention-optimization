WITH cohorts AS (SELECT customer,date_trunc('month',min(date)) AS cohort FROM orders GROUP BY customer),
activity AS (SELECT DISTINCT customer,date_trunc('month',date) AS month FROM orders),
sizes AS (SELECT cohort,count(*) AS cohort_size FROM cohorts GROUP BY cohort)
SELECT c.cohort,a.month,date_diff('month',c.cohort,a.month) AS cohort_age,
count(*) AS active_customers,s.cohort_size,count(*)*1.0/s.cohort_size AS retention
FROM cohorts c JOIN activity a USING(customer) JOIN sizes s USING(cohort)
WHERE a.month < DATE '2011-12-01'
GROUP BY c.cohort,a.month,s.cohort_size ORDER BY c.cohort,a.month;
