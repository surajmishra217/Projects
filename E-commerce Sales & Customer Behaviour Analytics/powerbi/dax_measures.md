# Power BI DAX measures

Assume the fact table is named `ecommerce_transactions`.

```dax
Total Revenue = SUM(ecommerce_transactions[revenue])
Total Profit = SUM(ecommerce_transactions[profit])
Total Orders = DISTINCTCOUNT(ecommerce_transactions[order_id])
Total Customers = DISTINCTCOUNT(ecommerce_transactions[customer_id])
Units Sold = SUM(ecommerce_transactions[quantity])
Average Order Value = DIVIDE([Total Revenue], [Total Orders], 0)
Profit Margin % = DIVIDE([Total Profit], [Total Revenue], 0)
Discount Given = SUM(ecommerce_transactions[discount_amount])
Repeat Customers =
COUNTROWS(
    FILTER(VALUES(ecommerce_transactions[customer_id]),
        CALCULATE(DISTINCTCOUNT(ecommerce_transactions[order_id])) > 1)
)
Repeat Customer Rate % = DIVIDE([Repeat Customers], [Total Customers], 0)
```

Create a Calendar table, relate it to the transaction date, and add a one-to-many relationship from customers and products to the transaction fact table.

Recommended report pages:
1. Executive overview: KPI cards and monthly revenue/profit.
2. Product and region: category, top products and regional performance.
3. Customer insights: RFM segment counts and repeat customer rate.
4. Channels: channel and payment mix.

Add slicers for date, region, category and sales channel. Import `outputs/customer_rfm_segments.csv` to show customer segments.
