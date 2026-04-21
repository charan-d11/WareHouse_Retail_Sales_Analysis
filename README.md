## 📦 Warehouse & Retail Sales — Data Analysis Project

A complete data analyst project on a real-world beverage distribution dataset 
with 307,000+ records spanning 4 years (2017–2020).

### 🔍 What's Inside
- **EDA & Cleaning** — null handling, outlier removal, feature engineering
- **NumPy Statistics** — descriptive stats, percentiles across all sales columns
- **Pandas Aggregations** — by item type, year, month, supplier & sales channel
- **4 Matplotlib/Seaborn Chart Panels** — overview, seasonality heatmap, 
  item deep-dive, correlation matrix
- **Power BI Dashboard** — 4-page interactive report with DAX measures, 
  slicers, and drill-through views

### 📊 Key Findings
| Metric | Value |
|---|---|
| Total Units Sold | 10.08 Million |
| #1 Item Type | Beer (70.4%) |
| #1 Supplier | Crown Imports |
| Best Year | 2019 |
| Peak Month | July |
| Warehouse vs Retail | 78.6% / 21.4% |

FILE STRUCTURE:
WareHouse_Retail_Sales_Analysis/
│
├── 📁 Dashboard_PNG/               # Power BI dashboard screenshots
│   ├── fig1_sales_overview.png
│   ├── fig2_item_type_deep_dive.png
│   ├── fig3_timeseries_seasonality.png
│   └── fig4_correlation.png
│
├── 📁 data/                        # Raw & processed datasets
│   ├── Warehouse_and_Retail_Sales.csv
│   ├── fact_sales.csv
│   ├── agg_monthly_by_type.csv
│   └── agg_supplier_by_type.csv
│
├── 📄 analysis.py                  # Main EDA script (NumPy + Pandas)
├── 📄 POWERBI_DASHBOARD_GUIDE.md   # Step-by-step Power BI setup guide
├── 📄 .gitignore                   # Excludes venv, pycache, etc.
├── 📄 LICENSE                      # Project license
└── 📄 README.md                    # Project documentation

Author:DURGA CH. MALLICK.
