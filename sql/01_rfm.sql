SELECT customer, date_diff('day', max(date), DATE '2011-12-09') AS recency_days,
count(*) AS frequency, sum(revenue) AS monetary, avg(revenue) AS average_order_value
FROM orders GROUP BY customer;
