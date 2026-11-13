# Interactive dashboards

This folder contains a runnable Streamlit application with two interactive portfolio dashboards:

1. **E-commerce Sales & Customer Behaviour** — generated, reproducible synthetic retail data; date, region and category filters; revenue, profit, order and customer KPIs; monthly trends; category/region/channel breakdowns; filtered CSV export.
2. **Telecom Customer Churn** — the repository's Telco churn CSV; contract and tenure filters; customer/churn KPIs; churn breakdowns; charge distribution; filtered CSV export.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser at the local URL printed by Streamlit.

## Deploy for a public portfolio link

Deploy this repository using Streamlit Community Cloud and set the app file path to `interactive-dashboards/app.py`. The dashboard is interactive after deployment; GitHub Pages itself cannot execute Streamlit apps.

## Data and tool transparency

- E-commerce values are simulated with a fixed random seed. They are not real company transactions or verified business outcomes.
- Telecom churn uses the CSV in `python project/Customer Churn.csv`.
- The repository already contains two native Power BI report files at its root: `SALES DASHBOARD.pbix` and `HR ANALYTICS DASHBOARD.pbix`. Open them in Power BI Desktop to inspect and interact with those reports.
- The Streamlit dashboards are browser-based interactive applications, not native Tableau workbooks. Tableau authoring requires Tableau Desktop/Public to create and validate a genuine `.twb`/`.twbx` workbook. The churn CSV can be connected directly in Tableau.
