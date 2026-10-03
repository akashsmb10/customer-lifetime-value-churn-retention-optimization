WITH customer_value AS (SELECT customer,sum(revenue) AS revenue FROM orders GROUP BY customer),
ranked AS (SELECT *,row_number() OVER(ORDER BY revenue DESC) AS rank,
count(*) OVER() AS n,sum(revenue) OVER() AS total FROM customer_value)
SELECT sum(CASE WHEN rank<=ceil(n*.2) THEN revenue ELSE 0 END)/max(total) AS top20_revenue_share FROM ranked;
