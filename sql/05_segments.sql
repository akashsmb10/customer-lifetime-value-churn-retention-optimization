SELECT segment,count(*) AS customers,avg(risk) AS mean_risk,sum(future_revenue) AS estimated_value
FROM scores GROUP BY segment;
