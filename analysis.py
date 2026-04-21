

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings, os

warnings.filterwarnings("ignore")
sns.set_theme(style="darkgrid", palette="muted")
plt.rcParams.update({"figure.dpi": 130, "font.family": "DejaVu Sans"})

OUT = "/home/claude/outputs"
os.makedirs(OUT, exist_ok=True)

# ─── 1. LOAD ────────────────────────────────────────────────
print("=" * 60)
print("  STEP 1 — Loading Data")
print("=" * 60)

df = pd.read_csv("/mnt/user-data/uploads/Warehouse_and_Retail_Sales.csv")
print(f"  Rows   : {df.shape[0]:,}")
print(f"  Columns: {df.shape[1]}")
print(f"\n{df.head(3).to_string()}")

# ─── 2. CLEAN ───────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 2 — Cleaning")
print("=" * 60)

before = len(df)
df.dropna(subset=["ITEM TYPE"], inplace=True)
df["SUPPLIER"].fillna("UNKNOWN", inplace=True)
df.dropna(subset=["RETAIL SALES"], inplace=True)

# Remove extreme negatives (returns / adjustments)
df = df[df["WAREHOUSE SALES"] >= 0]
df = df[df["RETAIL SALES"] >= 0]

after = len(df)
print(f"  Removed {before - after:,} rows (nulls + negatives)")
print(f"  Clean rows: {after:,}")

# Derived columns
df["TOTAL SALES"]     = df["RETAIL SALES"] + df["WAREHOUSE SALES"]
df["DATE"]            = pd.to_datetime(
    df["YEAR"].astype(str) + "-" + df["MONTH"].astype(str).str.zfill(2) + "-01"
)
df["MONTH NAME"]      = df["DATE"].dt.strftime("%b")
df["YEAR_STR"]        = df["YEAR"].astype(str)

print(f"\n  Item Types: {sorted(df['ITEM TYPE'].unique())}")
print(f"  Year range: {df['YEAR'].min()} – {df['YEAR'].max()}")

# ─── 3. NUMPY STATISTICS ────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 3 — NumPy Descriptive Statistics")
print("=" * 60)

for col in ["RETAIL SALES", "WAREHOUSE SALES", "TOTAL SALES"]:
    vals = df[col].values
    print(f"\n  {col}")
    print(f"    Mean   : {np.mean(vals):>12,.2f}")
    print(f"    Median : {np.median(vals):>12,.2f}")
    print(f"    Std    : {np.std(vals):>12,.2f}")
    print(f"    Min    : {np.min(vals):>12,.2f}")
    print(f"    Max    : {np.max(vals):>12,.2f}")
    print(f"    P75    : {np.percentile(vals, 75):>12,.2f}")
    print(f"    P95    : {np.percentile(vals, 95):>12,.2f}")

# ─── 4. AGGREGATIONS ────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 4 — Pandas Aggregations")
print("=" * 60)

# 4a. By Item Type
by_type = (
    df.groupby("ITEM TYPE")[["RETAIL SALES", "WAREHOUSE SALES", "TOTAL SALES"]]
    .sum()
    .sort_values("TOTAL SALES", ascending=False)
)
print("\n  Sales by Item Type:")
print(by_type.to_string())

# 4b. By Year
by_year = (
    df.groupby("YEAR")[["RETAIL SALES", "WAREHOUSE SALES", "TOTAL SALES"]]
    .sum()
)
print("\n  Sales by Year:")
print(by_year.to_string())

# 4c. Monthly trend
monthly = (
    df.groupby(["YEAR", "MONTH"])[["RETAIL SALES", "WAREHOUSE SALES"]]
    .sum()
    .reset_index()
    .sort_values(["YEAR", "MONTH"])
)

# 4d. Top 10 Suppliers
top_suppliers = (
    df.groupby("SUPPLIER")["TOTAL SALES"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
print("\n  Top 10 Suppliers by Total Sales:")
print(top_suppliers.to_string())

# 4e. Retail vs Warehouse share by type
share = by_type.copy()
share["RETAIL %"]    = (share["RETAIL SALES"]    / share["TOTAL SALES"] * 100).round(1)
share["WAREHOUSE %"] = (share["WAREHOUSE SALES"] / share["TOTAL SALES"] * 100).round(1)
print("\n  Retail vs Warehouse Share by Item Type:")
print(share[["RETAIL %", "WAREHOUSE %"]].to_string())

# ─── 5. VISUALISATIONS ──────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 5 — Generating Charts")
print("=" * 60)

COLORS   = ["#4C72B0","#DD8452","#55A868","#C44E52","#8172B3","#937860","#DA8BC3","#8C8C8C"]
BAR_CLR  = "#4C72B0"

# ── Fig 1: Sales Overview (2×2 grid) ────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle("Warehouse & Retail Sales — Overview", fontsize=16, fontweight="bold", y=1.01)

# 1a. Total Sales by Item Type (bar)
ax = axes[0, 0]
by_type["TOTAL SALES"].sort_values().plot(kind="barh", ax=ax, color=COLORS[:len(by_type)], edgecolor="white")
ax.set_title("Total Sales by Item Type", fontweight="bold")
ax.set_xlabel("Total Sales (units)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
ax.set_ylabel("")

# 1b. Retail vs Warehouse by Year (stacked bar)
ax = axes[0, 1]
by_year[["RETAIL SALES","WAREHOUSE SALES"]].plot(
    kind="bar", stacked=True, ax=ax, color=["#4C72B0","#DD8452"], edgecolor="white", width=0.6
)
ax.set_title("Retail vs Warehouse Sales by Year", fontweight="bold")
ax.set_xlabel("")
ax.set_ylabel("Sales (units)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
ax.tick_params(axis='x', rotation=0)
ax.legend(["Retail", "Warehouse"])

# 1c. Monthly Sales Trend (line)
ax = axes[1, 0]
for yr, grp in monthly.groupby("YEAR"):
    ax.plot(grp["MONTH"], grp["RETAIL SALES"] + grp["WAREHOUSE SALES"],
            marker="o", label=str(yr), linewidth=2, markersize=5)
ax.set_title("Monthly Total Sales Trend by Year", fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Sales (units)")
ax.set_xticks(range(1, 13))
ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], fontsize=8)
ax.legend(title="Year", fontsize=8)

# 1d. Top 10 Suppliers
ax = axes[1, 1]
top_suppliers.sort_values().plot(kind="barh", ax=ax, color="#55A868", edgecolor="white")
ax.set_title("Top 10 Suppliers by Total Sales", fontweight="bold")
ax.set_xlabel("Total Sales (units)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
ax.set_ylabel("")

plt.tight_layout()
fig.savefig(f"{OUT}/fig1_sales_overview.png", bbox_inches="tight")
plt.close()
print("  ✓ fig1_sales_overview.png")

# ── Fig 2: Item-Type Deep Dive ───────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("Item Type Deep Dive", fontsize=15, fontweight="bold")

# 2a. Donut — share of total sales
ax = axes[0]
vals = by_type["TOTAL SALES"]
wedges, texts, autotexts = ax.pie(
    vals, labels=vals.index, autopct="%1.1f%%",
    colors=COLORS[:len(vals)], startangle=140,
    wedgeprops=dict(width=0.55, edgecolor="white")
)
for t in autotexts: t.set_fontsize(8)
ax.set_title("Share of Total Sales", fontweight="bold")

# 2b. Grouped bar — retail vs warehouse per type
ax = axes[1]
x    = np.arange(len(by_type))
w    = 0.38
bars1 = ax.bar(x - w/2, by_type["RETAIL SALES"],    w, label="Retail",    color="#4C72B0", edgecolor="white")
bars2 = ax.bar(x + w/2, by_type["WAREHOUSE SALES"], w, label="Warehouse", color="#DD8452", edgecolor="white")
ax.set_xticks(x)
ax.set_xticklabels(by_type.index, rotation=30, ha="right", fontsize=8)
ax.set_title("Retail vs Warehouse per Type", fontweight="bold")
ax.set_ylabel("Sales (units)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
ax.legend()

# 2c. Box plot — distribution of retail sales per type (top 4)
ax = axes[2]
top4 = ["WINE","LIQUOR","BEER","KEGS"]
data_bp = [df[df["ITEM TYPE"]==t]["RETAIL SALES"].clip(upper=df["RETAIL SALES"].quantile(0.95)).values
           for t in top4]
bp = ax.boxplot(data_bp, patch_artist=True, notch=False,
                medianprops=dict(color="white", linewidth=2))
for patch, color in zip(bp["boxes"], COLORS[:4]):
    patch.set_facecolor(color)
ax.set_xticklabels(top4, fontsize=9)
ax.set_title("Retail Sales Distribution (top 4 types, 95th pct cap)", fontweight="bold")
ax.set_ylabel("Retail Sales (units)")

plt.tight_layout()
fig.savefig(f"{OUT}/fig2_item_type_deep_dive.png", bbox_inches="tight")
plt.close()
print("  ✓ fig2_item_type_deep_dive.png")

# ── Fig 3: Time Series & Seasonality ────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle("Time-Series & Seasonality Analysis", fontsize=15, fontweight="bold", y=1.01)

# 3a. Cumulative total sales over time
ax = axes[0, 0]
ts = df.groupby("DATE")["TOTAL SALES"].sum().sort_index().cumsum() / 1e6
ax.fill_between(ts.index, ts.values, alpha=0.25, color="#4C72B0")
ax.plot(ts.index, ts.values, color="#4C72B0", linewidth=2)
ax.set_title("Cumulative Total Sales Over Time", fontweight="bold")
ax.set_ylabel("Cumulative Sales (M units)")
ax.set_xlabel("")

# 3b. Heatmap: Year × Month total sales
ax = axes[0, 1]
pivot = df.pivot_table(values="TOTAL SALES", index="YEAR", columns="MONTH", aggfunc="sum")
pivot.columns = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
sns.heatmap(pivot / 1e3, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax, linewidths=0.5,
            cbar_kws={"label": "Sales (K units)"})
ax.set_title("Sales Heatmap — Year × Month (K units)", fontweight="bold")
ax.set_xlabel("")
ax.set_ylabel("")

# 3c. Average monthly seasonality
ax = axes[1, 0]
season = df.groupby("MONTH")["TOTAL SALES"].mean()
bars = ax.bar(range(1,13), season.values, color=sns.color_palette("muted", 12), edgecolor="white")
ax.set_xticks(range(1,13))
ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], fontsize=8)
ax.set_title("Average Monthly Sales (Seasonality)", fontweight="bold")
ax.set_ylabel("Avg Sales (units)")

# 3d. YoY growth
ax = axes[1, 1]
yoy = by_year["TOTAL SALES"].pct_change() * 100
yoy.dropna(inplace=True)
colors_yoy = ["#55A868" if v >= 0 else "#C44E52" for v in yoy]
ax.bar(yoy.index, yoy.values, color=colors_yoy, edgecolor="white", width=0.5)
ax.axhline(0, color="grey", linewidth=1, linestyle="--")
ax.set_title("Year-over-Year Growth (%)", fontweight="bold")
ax.set_xlabel("Year")
ax.set_ylabel("YoY Change (%)")
ax.set_xticks(yoy.index)

plt.tight_layout()
fig.savefig(f"{OUT}/fig3_timeseries_seasonality.png", bbox_inches="tight")
plt.close()
print("  ✓ fig3_timeseries_seasonality.png")

# ── Fig 4: Correlation & NumPy Insights ─────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Correlation & Statistical Insights", fontsize=14, fontweight="bold")

# 4a. Correlation heatmap
ax = axes[0]
corr = df[["RETAIL SALES","RETAIL TRANSFERS","WAREHOUSE SALES","TOTAL SALES"]].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
            ax=ax, vmin=-1, vmax=1, linewidths=1,
            cbar_kws={"shrink": 0.8})
ax.set_title("Correlation Matrix", fontweight="bold")

# 4b. Scatter: retail vs warehouse (wine only, sampled)
ax = axes[1]
wine = df[df["ITEM TYPE"] == "WINE"].sample(3000, random_state=42)
sc = ax.scatter(wine["RETAIL SALES"], wine["WAREHOUSE SALES"],
                alpha=0.35, s=12, c=wine["YEAR"], cmap="viridis")
plt.colorbar(sc, ax=ax, label="Year")
ax.set_title("Retail vs Warehouse Sales — WINE (sample)", fontweight="bold")
ax.set_xlabel("Retail Sales")
ax.set_ylabel("Warehouse Sales")
ax.set_xlim(0, wine["RETAIL SALES"].quantile(0.97))
ax.set_ylim(0, wine["WAREHOUSE SALES"].quantile(0.97))

plt.tight_layout()
fig.savefig(f"{OUT}/fig4_correlation.png", bbox_inches="tight")
plt.close()
print("  ✓ fig4_correlation.png")

# ─── 6. EXPORT CSVs FOR POWER BI ────────────────────────────
print("\n" + "=" * 60)
print("  STEP 6 — Exporting Cleaned Data for Power BI")
print("=" * 60)

# Main cleaned fact table
df.to_csv(f"{OUT}/fact_sales.csv", index=False)
print("  ✓ fact_sales.csv (full cleaned fact table)")

# Monthly summary
monthly_summary = (
    df.groupby(["YEAR","MONTH","ITEM TYPE"])
    .agg(RETAIL_SALES=("RETAIL SALES","sum"),
         WAREHOUSE_SALES=("WAREHOUSE SALES","sum"),
         RETAIL_TRANSFERS=("RETAIL TRANSFERS","sum"),
         TOTAL_SALES=("TOTAL SALES","sum"),
         TXN_COUNT=("TOTAL SALES","count"))
    .reset_index()
)
monthly_summary.to_csv(f"{OUT}/agg_monthly_by_type.csv", index=False)
print("  ✓ agg_monthly_by_type.csv")

# Supplier summary
supplier_summary = (
    df.groupby(["SUPPLIER","ITEM TYPE"])
    .agg(TOTAL_SALES=("TOTAL SALES","sum"),
         RETAIL_SALES=("RETAIL SALES","sum"),
         WAREHOUSE_SALES=("WAREHOUSE SALES","sum"))
    .reset_index()
    .sort_values("TOTAL_SALES", ascending=False)
)
supplier_summary.to_csv(f"{OUT}/agg_supplier_by_type.csv", index=False)
print("  ✓ agg_supplier_by_type.csv")

# ─── 7. SUMMARY REPORT ──────────────────────────────────────
print("\n" + "=" * 60)
print("  KEY INSIGHTS")
print("=" * 60)

total_rev = df["TOTAL SALES"].sum()
best_type = by_type["TOTAL SALES"].idxmax()
best_yr   = by_year["TOTAL SALES"].idxmax()
best_supp = top_suppliers.idxmax()
peak_mo   = season.idxmax()

MONTH_NAMES = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
               7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

print(f"  Total Units Sold   : {total_rev:>14,.0f}")
print(f"  Best Item Type     : {best_type}")
print(f"  Best Year          : {best_yr}")
print(f"  Best Supplier      : {best_supp}")
print(f"  Peak Month         : {MONTH_NAMES[peak_mo]}")
print(f"  Wine % of Total    : {by_type.loc['WINE','TOTAL SALES']/total_rev*100:.1f}%")

wh_share = df["WAREHOUSE SALES"].sum() / total_rev * 100
rt_share = df["RETAIL SALES"].sum()    / total_rev * 100
print(f"  Retail Share       : {rt_share:.1f}%")
print(f"  Warehouse Share    : {wh_share:.1f}%")

print("\n  Analysis complete — all files saved to /home/claude/outputs/\n")
