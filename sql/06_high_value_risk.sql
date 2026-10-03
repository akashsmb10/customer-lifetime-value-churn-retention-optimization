SELECT customer,risk,future_revenue,priority FROM scores
WHERE segment = 'High value / High risk' ORDER BY priority DESC;
