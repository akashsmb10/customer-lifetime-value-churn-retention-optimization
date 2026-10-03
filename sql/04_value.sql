SELECT customer, monetary AS historical_value, future_revenue AS estimated_future_revenue,
observed_future_revenue FROM scores ORDER BY future_revenue DESC;
