-- Import data/ecommerce_transactions.csv as ecommerce_transactions in SQLite.
-- Use DISTINCT order_id because each row is an order line, not a whole order.

-- Executive KPIs
SELECT ROUND(SUM(revenue),2) AS revenue, ROUND(SUM(profit),2) AS profit,
 COUNT(DISTINCT order_id) AS orders, COUNT(DISTINCT customer_id) AS customers,
 ROUND(SUM(revenue)/COUNT(DISTINCT order_id),2) AS average_order_value
FROM ecommerce_transactions;

-- Monthly trends
SELECT strftime('%Y-%m',order_date) AS month, ROUND(SUM(revenue),2) revenue,
 ROUND(SUM(profit),2) profit, COUNT(DISTINCT order_id) orders
FROM ecommerce_transactions GROUP BY month ORDER BY month;

-- Category and regional performance
SELECT category, ROUND(SUM(revenue),2) revenue, ROUND(SUM(profit),2) profit
FROM ecommerce_transactions GROUP BY category ORDER BY revenue DESC;
SELECT region, ROUND(SUM(revenue),2) revenue, COUNT(DISTINCT order_id) orders
FROM ecommerce_transactions GROUP BY region ORDER BY revenue DESC;

-- Repeat purchase rate
WITH customer_orders AS (
 SELECT customer_id,COUNT(DISTINCT order_id) order_count
 FROM ecommerce_transactions GROUP BY customer_id
)
SELECT COUNT(*) customers,
 SUM(CASE WHEN order_count>1 THEN 1 ELSE 0 END) repeat_customers,
 ROUND(100.0*SUM(CASE WHEN order_count>1 THEN 1 ELSE 0 END)/COUNT(*),2) repeat_rate_pct
FROM customer_orders;

-- Top products within each category (window function)
WITH product_sales AS (
 SELECT product_id,product_name,category,SUM(revenue) revenue
 FROM ecommerce_transactions GROUP BY product_id,product_name,category
), ranked AS (
 SELECT *,DENSE_RANK() OVER(PARTITION BY category ORDER BY revenue DESC) category_rank
 FROM product_sales
)
SELECT * FROM ranked WHERE category_rank<=5 ORDER BY category,category_rank;

-- Month-over-month revenue growth (CTE + LAG)
WITH monthly AS (
 SELECT strftime('%Y-%m',order_date) month,SUM(revenue) revenue
 FROM ecommerce_transactions GROUP BY month
), prior AS (
 SELECT month,revenue,LAG(revenue) OVER(ORDER BY month) previous_revenue FROM monthly
)
SELECT month,ROUND(revenue,2) revenue,
 ROUND(100.0*(revenue-previous_revenue)/NULLIF(previous_revenue,0),2) mom_growth_pct
FROM prior ORDER BY month;
