from pathlib import Path
import numpy as np
import pandas as pd
import json

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT = ROOT / "data", ROOT / "outputs"
DATA.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(42)

# Reproducible synthetic Indian e-commerce dataset (not real customer data).
regions = {"North":["Delhi","Jaipur","Lucknow"],"South":["Bengaluru","Chennai","Hyderabad"],
           "East":["Kolkata","Patna","Guwahati"],"West":["Mumbai","Pune","Ahmedabad"],
           "Central":["Bhopal","Indore","Nagpur"]}
categories = ["Electronics","Home & Kitchen","Fashion","Beauty","Sports","Books"]
customers = pd.DataFrame({
    "customer_id":[f"C{i:04d}" for i in range(1,501)],
    "region":rng.choice(list(regions),500),
})
customers["city"] = customers["region"].map(lambda r:rng.choice(regions[r]))
customers["signup_date"] = pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0,650,500),unit="D")
products = pd.DataFrame({"product_id":[f"P{i:03d}" for i in range(1,61)]})
products["category"] = [categories[(i-1)%len(categories)] for i in range(1,61)]
products["product_name"] = products["category"].str.split().str[0] + " Item " + products["product_id"]
products["list_price"] = np.round(rng.uniform(250,12000,60),2)

rows=[]
for i in range(1,2201):
    c=customers.iloc[int(rng.integers(0,len(customers)))]
    date=pd.Timestamp("2024-01-01")+pd.Timedelta(days=int(rng.integers(0,366)))
    for pidx in rng.choice(len(products),size=int(rng.choice([1,1,1,2,3])),replace=False):
        p=products.iloc[int(pidx)]
        qty=int(rng.choice([1,1,1,2,3]))
        unit=round(float(p.list_price*rng.uniform(.9,1.1)),2)
        disc=float(rng.choice([0,.05,.10,.15,.20]))
        revenue=round(unit*qty*(1-disc),2)
        cost=round(unit*qty*rng.uniform(.5,.78),2)
        rows.append((f"O{i:06d}",date,c.customer_id,c.region,c.city,p.product_id,p.product_name,
                     p.category,qty,unit,disc,round(unit*qty*disc,2),revenue,cost,
                     rng.choice(["Website","Mobile App","Marketplace"]),
                     rng.choice(["UPI","Credit Card","Debit Card","Cash on Delivery"])))
df=pd.DataFrame(rows,columns=["order_id","order_date","customer_id","region","city","product_id",
 "product_name","category","quantity","unit_price","discount_pct","discount_amount","revenue",
 "cost","sales_channel","payment_method"])
df["order_date"]=pd.to_datetime(df.order_date)
df["profit"]=(df.revenue-df.cost).round(2)
customers.to_csv(DATA/"customers.csv",index=False)
products.to_csv(DATA/"products.csv",index=False)
df.to_csv(DATA/"ecommerce_transactions.csv",index=False)

df["month"]=df.order_date.dt.to_period("M").astype(str)
df.groupby("month").agg(revenue=("revenue","sum"),profit=("profit","sum"),
 orders=("order_id","nunique"),units=("quantity","sum")).reset_index().to_csv(OUT/"monthly_sales.csv",index=False)
df.groupby("category").agg(revenue=("revenue","sum"),profit=("profit","sum"),
 units=("quantity","sum")).reset_index().sort_values("revenue",ascending=False).to_csv(OUT/"category_performance.csv",index=False)
df.groupby("region").agg(revenue=("revenue","sum"),profit=("profit","sum"),
 orders=("order_id","nunique")).reset_index().sort_values("revenue",ascending=False).to_csv(OUT/"regional_performance.csv",index=False)

snapshot=df.order_date.max()+pd.Timedelta(days=1)
rfm=df.groupby("customer_id").agg(
 recency_days=("order_date",lambda s:(snapshot-s.max()).days),
 frequency=("order_id","nunique"),monetary=("revenue","sum")).reset_index()
for col,ascending,labels in [("r_score",False,[4,3,2,1]),("f_score",True,[1,2,3,4]),("m_score",True,[1,2,3,4])]:
    source={"r_score":"recency_days","f_score":"frequency","m_score":"monetary"}[col]
    rfm[col]=pd.qcut(rfm[source].rank(method="first",ascending=ascending),4,labels=labels).astype(int)
def segment(x):
    if x.r_score>=3 and x.f_score>=3 and x.m_score>=3:return "Champions"
    if x.r_score>=3 and x.f_score>=2:return "Loyal Customers"
    if x.r_score>=3:return "Recent Customers"
    if x.f_score>=3:return "At Risk"
    return "Needs Attention"
rfm["segment"]=rfm.apply(segment,axis=1)
rfm.to_csv(OUT/"customer_rfm_segments.csv",index=False)
orders=df.groupby("order_id").revenue.sum()
summary={"revenue":round(float(df.revenue.sum()),2),"profit":round(float(df.profit.sum()),2),
 "orders":int(df.order_id.nunique()),"customers":int(df.customer_id.nunique()),
 "average_order_value":round(float(orders.mean()),2),
 "profit_margin_pct":round(float(df.profit.sum()/df.revenue.sum()*100),2)}
(OUT/"kpi_summary.json").write_text(json.dumps(summary,indent=2))
print("Generated synthetic dataset and analysis outputs.")
print(json.dumps(summary,indent=2))
