# Power BI Dashboard — Warehouse & Retail Sales
### Step-by-step Setup Guide

---

## FILES TO IMPORT
| File | Purpose |
|---|---|
| `fact_sales.csv` | Main fact table (306K rows, fully cleaned) |
| `agg_monthly_by_type.csv` | Pre-aggregated monthly + type summary |
| `agg_supplier_by_type.csv` | Supplier-level aggregations |

---

## STEP 1 — Import Data

1. Open Power BI Desktop → **Get Data → Text/CSV**
2. Import all three CSV files above
3. In Power Query Editor:
   - For `fact_sales`: set **YEAR** and **MONTH** as whole numbers, **RETAIL SALES / WAREHOUSE SALES / TOTAL SALES** as Decimal Number
   - Create a **Date column**: `= Date.From(Text.From([YEAR]) & "-" & Text.PadStart(Text.From([MONTH]),2,"0") & "-01")`

---

## STEP 2 — Data Model (Relationships)

```
fact_sales
  └── YEAR + MONTH + ITEM TYPE  →  agg_monthly_by_type (YEAR, MONTH, ITEM TYPE)
  └── SUPPLIER + ITEM TYPE      →  agg_supplier_by_type (SUPPLIER, ITEM TYPE)
```

Create a **Date Table** (recommended):
```dax
DateTable = CALENDAR(DATE(2017,1,1), DATE(2020,12,31))
```
Add columns: `Month Name`, `Quarter`, `Year` from this table.

---

## STEP 3 — DAX Measures

Paste these in **Modeling → New Measure**:

```dax
Total Sales = SUM(fact_sales[TOTAL SALES])

Retail Sales = SUM(fact_sales[RETAIL SALES])

Warehouse Sales = SUM(fact_sales[WAREHOUSE SALES])

Retail % = DIVIDE([Retail Sales], [Total Sales], 0) * 100

Warehouse % = DIVIDE([Warehouse Sales], [Total Sales], 0) * 100

YoY Growth % =
VAR current = [Total Sales]
VAR prior   = CALCULATE([Total Sales], DATEADD(DateTable[Date], -1, YEAR))
RETURN DIVIDE(current - prior, prior, 0) * 100

Top Supplier =
CALCULATE(
    SELECTEDVALUE(fact_sales[SUPPLIER]),
    TOPN(1, VALUES(fact_sales[SUPPLIER]), [Total Sales], DESC)
)
```

---

## STEP 4 — Dashboard Layout (4 Pages)

### PAGE 1 — Executive Summary
| Visual | Data | Notes |
|---|---|---|
| **KPI Card** | Total Sales | Show value + YoY arrow |
| **KPI Card** | Retail Sales | |
| **KPI Card** | Warehouse Sales | |
| **Donut Chart** | TOTAL SALES by ITEM TYPE | Legend: item type |
| **Stacked Bar** | RETAIL vs WAREHOUSE by YEAR | Color: blue/orange |
| **Slicer** | YEAR (single select) | Top of page |

### PAGE 2 — Time Series & Seasonality
| Visual | Data | Notes |
|---|---|---|
| **Line Chart** | TOTAL SALES by DATE | Legend: YEAR |
| **Matrix / Heatmap** | YEAR (rows) × MONTH (cols), value = TOTAL SALES | Conditional formatting: red-yellow |
| **Column Chart** | Avg TOTAL SALES by MONTH | Seasonality view |
| **Waterfall Chart** | YoY Growth % | Shows gains/losses |
| **Slicer** | ITEM TYPE (multi) | |

### PAGE 3 — Item Type Analysis
| Visual | Data | Notes |
|---|---|---|
| **Clustered Bar** | RETAIL vs WAREHOUSE by ITEM TYPE | |
| **100% Stacked Bar** | RETAIL % vs WAREHOUSE % by ITEM TYPE | Channel split |
| **Box & Whisker** | RETAIL SALES by ITEM TYPE (use R visual) | |
| **Line + Bar Combo** | Monthly trend per type | Dual Y-axis |
| **Slicer** | YEAR | |

### PAGE 4 — Supplier Deep Dive
| Visual | Data | Notes |
|---|---|---|
| **Bar Chart** | Top 20 Suppliers by TOTAL SALES | Sorted desc |
| **Treemap** | TOTAL SALES by SUPPLIER (top 50) | |
| **Table** | Supplier, Item Type, Retail, Warehouse, Total | Conditional bar |
| **Scatter Plot** | X=Retail Sales, Y=Warehouse Sales, size=Total | Color by Item Type |
| **Slicer** | ITEM TYPE, YEAR | |

---

## STEP 5 — Formatting Tips

- **Theme**: Use *Executive* or *Innovation* built-in theme (View → Themes)
- **Title font**: Segoe UI, 14pt, bold, dark navy `#1F3864`
- **Color palette**: Blue `#4472C4`, Orange `#ED7D31`, Green `#70AD47`, Red `#FF0000`
- **Canvas size**: 1280 × 720 px (16:9, standard)
- **Tooltips**: Enable "report page tooltips" for detail drill-through
- **Cross-filtering**: Enable on all charts (Format → Edit interactions)

---

## STEP 6 — Publish

1. **File → Publish → Publish to Power BI**
2. Sign in to your Power BI workspace
3. Enable **Scheduled Refresh** if you update the CSVs regularly
4. Set **Row-Level Security** if the report is shared across teams

---

## KEY INSIGHTS FROM THE DATA

| Insight | Value |
|---|---|
| Total Units Sold | 10,085,652 |
| #1 Item Type | Beer (70.4% of total) |
| #1 Supplier | Crown Imports |
| Best Year | 2019 |
| Peak Month | July |
| Warehouse dominance | 78.6% of all sales |
| Retail channel | Only 21.4% |
| Beer warehouse share | 91.9% via warehouse |
| Liquor retail share | 89.4% via retail |
