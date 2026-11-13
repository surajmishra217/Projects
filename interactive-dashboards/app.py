import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Suraj Mishra | Analytics Lab", page_icon="📊", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.6rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {background: #f4f7fb; padding: 14px 16px; border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

st.title("Analytics Lab")
st.caption("Interactive portfolio dashboards | E-commerce performance and telecom customer churn")
st.info("Data note: the e-commerce dataset is reproducibly simulated for portfolio demonstration. Telecom churn uses the CSV dataset stored in this repository.")

@st.cache_data
def make_ecommerce():
    rng = np.random.default_rng(42)
    n = 3600
    dates = pd.to_datetime(rng.choice(pd.date_range("2023-01-01", "2024-12-31", freq="D"), n))
    categories = rng.choice(["Electronics", "Fashion", "Home & Kitchen", "Beauty", "Sports"], n, p=[.25,.24,.22,.16,.13])
    regions = rng.choice(["North", "South", "East", "West", "Central"], n)
    channels = rng.choice(["Website", "Mobile App", "Marketplace"], n, p=[.35,.45,.20])
    customers = rng.integers(1001, 1842, n)
    qty = rng.integers(1, 5, n)
    base = pd.Series(categories).map({"Electronics":6500,"Fashion":1800,"Home & Kitchen":3200,"Beauty":950,"Sports":2200}).to_numpy()
    price = np.maximum(199, rng.normal(base, base*.28))
    discount = rng.choice([0,.05,.10,.15,.20], n, p=[.35,.20,.22,.15,.08])
    revenue = price * qty * (1-discount)
    cost = revenue * rng.uniform(.55,.78,n)
    return pd.DataFrame({"Order Date":dates,"Order ID":[f"ORD-{i:05d}" for i in range(n)],"Customer ID":customers,"Category":categories,"Region":regions,"Channel":channels,"Quantity":qty,"Sales":revenue.round(2),"Profit":(revenue-cost).round(2)})

@st.cache_data
def load_churn():
    url = "https://raw.githubusercontent.com/surajmishra217/Projects/main/python%20project/Customer%20Churn.csv"
    df = pd.read_csv(url)
    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    return df

def money(v):
    return f"₹{v:,.0f}"

def ecommerce_dashboard():
    df = make_ecommerce()
    st.subheader("E-commerce sales & customer behaviour")
    c1,c2,c3 = st.columns(3)
    with c1: start = st.date_input("Start date", df["Order Date"].min().date(), key="e_start")
    with c2: end = st.date_input("End date", df["Order Date"].max().date(), key="e_end")
    with c3: regions = st.multiselect("Region", sorted(df.Region.unique()), default=sorted(df.Region.unique()), key="e_region")
    categories = st.multiselect("Product category", sorted(df.Category.unique()), default=sorted(df.Category.unique()), key="e_category")
    f = df[(df["Order Date"].dt.date >= start) & (df["Order Date"].dt.date <= end) & df.Region.isin(regions) & df.Category.isin(categories)]
    if f.empty:
        st.warning("No rows match these filters. Expand the date range or select more regions/categories.")
        return
    revenue, profit, orders, buyers = f.Sales.sum(), f.Profit.sum(), f["Order ID"].nunique(), f["Customer ID"].nunique()
    a,b,c,d = st.columns(4)
    a.metric("Revenue", money(revenue))
    b.metric("Profit", money(profit))
    c.metric("Orders", f"{orders:,}")
    d.metric("Unique customers", f"{buyers:,}")
    x,y = st.columns(2)
    monthly = f.assign(Month=f["Order Date"].dt.to_period("M").astype(str)).groupby("Month",as_index=False).agg(Sales=("Sales","sum"),Profit=("Profit","sum"))
    x.plotly_chart(px.line(monthly,x="Month",y=["Sales","Profit"],markers=True,title="Monthly sales and profit"),use_container_width=True)
    cat = f.groupby("Category",as_index=False).agg(Sales=("Sales","sum")).sort_values("Sales",ascending=False)
    y.plotly_chart(px.bar(cat,x="Category",y="Sales",color="Category",title="Sales by category"),use_container_width=True)
    p,q = st.columns(2)
    region = f.groupby("Region",as_index=False).agg(Sales=("Sales","sum"),Profit=("Profit","sum"))
    p.plotly_chart(px.bar(region,x="Region",y="Sales",color="Region",title="Regional sales"),use_container_width=True)
    channel = f.groupby("Channel",as_index=False).agg(Orders=("Order ID","nunique"))
    q.plotly_chart(px.pie(channel,names="Channel",values="Orders",hole=.5,title="Orders by channel"),use_container_width=True)
    customer = f.groupby("Customer ID",as_index=False).agg(Orders=("Order ID","nunique"),Sales=("Sales","sum"))
    repeat = (customer.Orders.gt(1).mean()*100) if len(customer) else 0
    st.metric("Repeat-customer rate in filtered data",f"{repeat:.1f}%")
    st.dataframe(f.sort_values("Order Date",ascending=False),use_container_width=True,hide_index=True)
    st.download_button("Download filtered e-commerce data",f.to_csv(index=False).encode("utf-8"),"ecommerce_filtered.csv","text/csv")

def churn_dashboard():
    try:
        df = load_churn()
    except Exception as e:
        st.error(f"Could not load the churn CSV: {e}")
        st.markdown("[Open the dataset on GitHub](https://github.com/surajmishra217/Projects/blob/main/python%20project/Customer%20Churn.csv)")
        return
    st.subheader("Telecom customer churn")
    if "Churn" not in df.columns:
        st.error("The uploaded dataset must contain a 'Churn' column.")
        return
    numeric = [c for c in ["tenure","MonthlyCharges","TotalCharges"] if c in df.columns]
    categorical = [c for c in ["Contract","InternetService","PaymentMethod"," gender","gender"] if c in df.columns]
    left,right = st.columns(2)
    with left:
        contract = st.multiselect("Contract type",sorted(df.Contract.dropna().unique()),default=sorted(df.Contract.dropna().unique())) if "Contract" in df else []
    with right:
        tenure_max = int(df.tenure.max()) if "tenure" in df else 100
        tenure_range = st.slider("Customer tenure (months)",0,tenure_max,(0,tenure_max)) if "tenure" in df else (0,tenure_max)
    f = df.copy()
    if "Contract" in f and contract: f=f[f.Contract.isin(contract)]
    if "tenure" in f: f=f[f.tenure.between(*tenure_range)]
    if f.empty:
        st.warning("No customers match the selected filters.")
        return
    churned = f.Churn.astype(str).str.lower().isin(["yes","1","true"]).sum()
    rate = churned/len(f)*100
    a,b,c,d=st.columns(4)
    a.metric("Customers",f"{len(f):,}")
    b.metric("Churned customers",f"{churned:,}")
    c.metric("Churn rate",f"{rate:.1f}%")
    d.metric("Average monthly charge",money(f.MonthlyCharges.mean()) if "MonthlyCharges" in f else "N/A")
    x,y=st.columns(2)
    if "Contract" in f:
        cr=f.groupby("Contract",as_index=False).Churn.apply(lambda s:(s.astype(str).str.lower().eq("yes").mean()*100)).rename(columns={"Churn":"Churn rate"})
        x.plotly_chart(px.bar(cr,x="Contract",y="Churn rate",color="Contract",title="Churn rate by contract"),use_container_width=True)
    if "tenure" in f:
        f2=f.assign(TenureBand=pd.cut(f.tenure,bins=[-1,12,24,48,72],labels=["0–12","13–24","25–48","49–72"]))
        tr=f2.groupby("TenureBand",observed=False).Churn.apply(lambda s:s.astype(str).str.lower().eq("yes").mean()*100).reset_index(name="Churn rate")
        y.plotly_chart(px.bar(tr,x="TenureBand",y="Churn rate",title="Churn rate by tenure band"),use_container_width=True)
    p,q=st.columns(2)
    if "InternetService" in f:
        ir=f.groupby("InternetService",as_index=False).Churn.apply(lambda s:s.astype(str).str.lower().eq("yes").mean()*100).rename(columns={"Churn":"Churn rate"})
        p.plotly_chart(px.bar(ir,x="InternetService",y="Churn rate",title="Churn rate by internet service"),use_container_width=True)
    if "MonthlyCharges" in f:
        q.plotly_chart(px.histogram(f,x="MonthlyCharges",color="Churn",nbins=25,barmode="overlay",title="Monthly charges by churn status"),use_container_width=True)
    st.dataframe(f,use_container_width=True,hide_index=True)
    st.download_button("Download filtered churn data",f.to_csv(index=False).encode("utf-8"),"churn_filtered.csv","text/csv")

tab1,tab2=st.tabs(["E-commerce dashboard","Customer churn dashboard"])
with tab1: ecommerce_dashboard()
with tab2: churn_dashboard()
