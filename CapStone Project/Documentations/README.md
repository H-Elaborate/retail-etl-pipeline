# 🛒 retail-etl-pipeline

> **YTG Retail — Customer Orders ETL Pipeline**  
> A end-to-end data engineering project that extracts, transforms, loads, and analyses retail sales data using Python, Pandas, and SQLite.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Dataset Summary](#dataset-summary)
- [Repository Structure](#repository-structure)
- [Pipeline Architecture](#pipeline-architecture)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [How to Run](#how-to-run)
- [ETL Phases Explained](#etl-phases-explained)
  - [Phase 1 — Extract](#phase-1--extract)
  - [Phase 2 — Transform](#phase-2--transform)
  - [Phase 3 — Load](#phase-3--load)
  - [Phase 4 — Reporting & Analysis](#phase-4--reporting--analysis)
- [Data Cleaning Rules](#data-cleaning-rules)
- [Output Files](#output-files)
- [Sample Output](#sample-output)
- [Visualization Dashboard](#visualization-dashboard)
  - [Running the Dashboard](#running-the-dashboard)
  - [Dashboard Features](#dashboard-features)
- [Known Limitations & Future Improvements](#known-limitations--future-improvements)
- [Author](#author)

---

## Project Overview

This project simulates a real-world retail data pipeline for **YTG Retail**, a Nigerian-based retail business. The pipeline ingests raw transactional data from three CSV source files, cleans and validates it, merges it into a unified sales dataset, loads it into a SQLite database, and produces business intelligence reports covering revenue, top customers, best-selling products, category breakdowns, and monthly sales trends.

The project was built as a Data Engineering capstone assignment, demonstrating core ETL concepts including data extraction, transformation, quality validation, relational merging, and analytical reporting.

---

## Dataset Summary

| File | Records | Columns | Description |
|---|---|---|---|
| `customers.csv` | 12,002 | 4 | Customer profiles across Nigerian cities |
| `products.csv` | 10,045 | 4 | Product catalogue across 6 categories |
| `orders.csv` | 20,000 | 5 | Transactional orders linking customers to products |

**Date Range:** January 2023 → August 2026  
**Cities Covered:** 40+ Nigerian cities including Lagos, Abuja, Port Harcourt, Kano, Ibadan, Enugu, and more  
**Product Categories:** Electronics, Accessories, Groceries, Stationery, Fashion, Home  
**Order Quantity Range:** 1 – 10 units per order

---

## Repository Structure

```
retail-etl-pipeline/
│
├── data/
│   ├── customers.csv          # Raw customer data
│   ├── products.csv           # Raw product catalogue
│   └── orders.csv             # Raw orders/transactions
│
├── Python/
│   └── Data Pipelines/
│       └── Data_pipeline/
│           └── Visuals/
│               └── Viz.py     # Streamlit visualization dashboard
│
├── etl_pipeline.py            # Main ETL script
├── retail_sales.db            # SQLite output database (generated on run)
│
├── README.md                  # Project documentation (this file)
└── requirements.txt           # Python dependencies
```

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    RAW DATA SOURCES                     │
│   customers.csv    products.csv    orders.csv           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                 PHASE 1 — EXTRACT                       │
│         pd.read_csv() → 3 DataFrames                   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                PHASE 2 — TRANSFORM                      │
│  2a. Data Cleaning  (dedup, nulls, type casting)        │
│  2b. Left Join Merge (orders + customers + products)    │
│  2c. Calculated Fields (total_amount, year_month)       │
│  2d. Final Column Selection & Sorting                   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  PHASE 3 — LOAD                         │
│         SQLite Database → sales_summary table           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│            PHASE 4 — REPORTING & ANALYSIS               │
│  • Total Revenue        • Top 5 Customers               │
│  • Best-Selling Products• Revenue by Category           │
│  • Monthly Sales Trend  • Average Order Value           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│         PHASE 5 — VISUALIZATION DASHBOARD (Viz.py)      │
│  • Streamlit web app with 5 interactive tabs            │
│  • Plotly charts: area, bar, pie, scatter, heatmap      │
│  • Sidebar filters: Category, City, Month Range         │
│  • Data Quality audit + CSV export                      │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| **Python 3.x** | Core programming language |
| **Pandas** | Data manipulation, cleaning, merging, and analysis |
| **SQLite3** | Lightweight relational database for loading output |
| **Streamlit** | Interactive web dashboard for data visualization |
| **Plotly** | Interactive charts (area, bar, pie, scatter, heatmap) |
| **Pathlib** | Cross-platform file path handling |
| **Warnings** | Suppressing non-critical runtime warnings |

---

## Setup & Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/retail-etl-pipeline.git
cd retail-etl-pipeline
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### `requirements.txt`

```
pandas>=1.5.0
streamlit>=1.25.0
plotly>=5.0.0
```

> SQLite3 and Pathlib are part of Python's standard library — no separate installation needed.

---

## How to Run

Make sure all three CSV files (`customers.csv`, `products.csv`, `orders.csv`) are in the **same folder** as `etl_pipeline.py`, then run:

```bash
python etl_pipeline.py
```

The script will:
1. Extract data from the three CSV files
2. Clean and transform the data
3. Create `retail_sales.db` in the same directory
4. Print a full analysis report to the console

---

## ETL Phases Explained

### Phase 1 — Extract

Reads all three raw CSV files into pandas DataFrames using `pathlib.Path` for cross-platform compatibility. Prints row counts, column counts, and a 3-row preview of each file to the console.

```python
customers = pd.read_csv(BASE_DIR / "customers.csv")
products  = pd.read_csv(BASE_DIR / "products.csv")
orders    = pd.read_csv(BASE_DIR / "orders.csv")
```

---

### Phase 2 — Transform

#### 2a. Data Cleaning

Each dataset is cleaned independently before merging:

**Customers:**
- Remove duplicate `customer_id` rows
- Drop rows with missing `customer_name`
- Parse `signup_date` to datetime, drop unparseable dates

**Products:**
- Remove duplicate `product_id` rows
- Drop rows with missing `product_name` or `price`
- Convert `price` to numeric, drop non-numeric values

**Orders:**
- Remove duplicate `order_id` rows
- Convert `quantity` to numeric (coerce errors to NaN)
- Parse `order_date` to datetime (coerce errors to NaT)
- Drop rows with null `order_date` or `quantity`
- Drop rows where `quantity <= 0` (business rule: no zero or negative sales)

#### 2b. Merge Datasets

Uses a **left join** strategy to preserve all orders while detecting data quality issues:

```python
merged = (
    orders
    .merge(customers, on="customer_id", how="left")
    .merge(products,  on="product_id",  how="left")
)
```

An `is_valid` flag is added to track orders that have matching customer and product records. Missing customer/product counts are logged to the console for audit purposes.

#### 2c. Calculated Fields

| Field | Calculation |
|---|---|
| `total_amount` | `quantity × price`, rounded to 2 decimal places |
| `year_month` | Extracted from `order_date` as `YYYY-MM` string |

#### 2d. Final Column Selection

The output dataset `sales_summary` contains exactly 12 columns:

```
order_id | order_date | year_month | customer_id | customer_name | city |
product_id | product_name | category | quantity | price | total_amount
```

Sorted by `order_date` ascending.

---

### Phase 3 — Load

The cleaned `sales_summary` DataFrame is written to a SQLite database:

```python
conn = sqlite3.connect(BASE_DIR / "retail_sales.db")
sales_summary.to_sql("sales_summary", conn, if_exists="replace", index=False)
```

`if_exists="replace"` drops and recreates the table on every run to ensure fresh, consistent data. The schema is printed to console after loading for verification.

---

### Phase 4 — Reporting & Analysis

Six business reports are generated directly from `sales_summary`:

| Report | Method |
|---|---|
| Total Revenue | `.sum()` on `total_amount` |
| Top 5 Customers by Spending | `.groupby()` + `.sum()` + `.sort_values()` |
| Best-Selling Products (units) | `.groupby()` + `.agg()` with named aggregation |
| Revenue by Category | `.groupby()` + `% share` calculation |
| Monthly Sales Trend | `.groupby("year_month")` + ASCII bar chart |
| Average Order Value | `.mean()` on `total_amount` |

---

## Data Cleaning Rules

| Rule | Dataset | Action |
|---|---|---|
| Duplicate primary key | All | Drop duplicate, keep first |
| Missing `customer_name` | Customers | Drop row |
| Invalid `signup_date` format | Customers | Coerce to NaT, then drop |
| Missing `product_name` or `price` | Products | Drop row |
| Non-numeric `price` | Products | Coerce to NaN, then drop |
| Missing `order_date` or `quantity` | Orders | Drop row |
| `quantity <= 0` | Orders | Drop row (business rule) |
| Unmatched customer/product ID | Merged | Flagged via `is_valid` column |

---

## Output Files

| File | Type | Description |
|---|---|---|
| `retail_sales.db` | SQLite Database | Contains the `sales_summary` table |
| Console output | Terminal | Full ETL log + analysis reports |

### Database Schema — `sales_summary`

| Column | Type | Description |
|---|---|---|
| `order_id` | TEXT | Unique order identifier |
| `order_date` | TEXT | Date of the order |
| `year_month` | TEXT | Month period (YYYY-MM) |
| `customer_id` | TEXT | Customer identifier |
| `customer_name` | TEXT | Full name of customer |
| `city` | TEXT | Customer's city |
| `product_id` | TEXT | Product identifier |
| `product_name` | TEXT | Name of product |
| `category` | TEXT | Product category |
| `quantity` | REAL | Units ordered |
| `price` | REAL | Unit price in Naira (₦) |
| `total_amount` | REAL | quantity × price |

---

## Sample Output

```
==============================================================
  PHASE 1 · EXTRACT
==============================================================
  ✔  customers.csv  →  12,002 rows, 4 cols
  ✔  products.csv   →  10,045 rows, 4 cols
  ✔  orders.csv     →  20,000 rows, 5 cols

==============================================================
  PHASE 4 · REPORTING & ANALYSIS
==============================================================

  📊 Total Revenue Generated
  --------------------------------------------------------------
  ₦    XXX,XXX,XXX.XX

  🏆 Top 5 Customers by Spending
  --------------------------------------------------------------
     ID        Name              City       Total Spent
  1  C00045    Emeka Okafor      Lagos      ₦X,XXX,XXX.XX
  ...

  📈 Monthly Sales Trend
  --------------------------------------------------------------
  2023-01  ██████████████████████          ₦  X,XXX,XXX.XX
  2023-02  ████████████████████████████    ₦  X,XXX,XXX.XX
  ...
```

---

## Visualization Dashboard

The project includes **`Viz.py`**, a full-featured interactive web dashboard built with Streamlit and Plotly. It runs the ETL pipeline live in the browser — upload your three CSV files and explore the cleaned data through five analytical tabs.

### Running the Dashboard

Make sure dependencies are installed:

```bash
pip install streamlit plotly pandas
```

Then navigate to the dashboard directory and launch it:

```bash
cd "Python/Data Pipelines/Data_pipeline/Visuals"
streamlit run Viz.py
```

The dashboard opens automatically at `http://localhost:8501`. Upload `customers.csv`, `products.csv`, and `orders.csv` in the sidebar to trigger the ETL pipeline and load all visualizations.

> ⚠️ **Important:** Always run with `streamlit run Viz.py`, not `python Viz.py`. Running with plain Python bypasses Streamlit's execution model and will cause errors.

### Dashboard Features

The dashboard is organized into five tabs:

#### 📊 Overview
High-level KPI cards followed by four charts giving a full business snapshot at a glance.

| KPI | Chart |
|---|---|
| Total Revenue (₦) | Monthly Revenue Area Trend |
| Total Orders | Revenue by Category (Donut) |
| Unique Customers | Top 10 Cities by Revenue (Bar) |
| Unique Products | Category Revenue Comparison (Bar) |
| Avg Order Value | |
| Largest Single Order | |

#### 📈 Sales Trends
Deep-dive into time-series performance:
- Combined bar + line chart of monthly revenue
- Orders per month (bar)
- Average order value per month (line)
- Revenue heatmap — **Category × Month** (shows which categories peak in which months)

#### 🛍️ Products
Product-level performance analysis:
- Top 10 products by units sold (colour-coded by category)
- Top 10 products by revenue (colour-coded by category)
- Bubble chart — Units Sold vs Revenue, bubble size = order count
- Full product summary table (sortable, downloadable)

#### 👥 Customers
Customer behaviour and geography:
- Top 10 customers by total spending
- Order count distribution histogram
- Unique customers by city
- Average spend per order by city
- Top 50 customers table with total spent and avg order value

#### 🔬 Data Quality
ETL audit report for pipeline transparency:
- Before/after record counts for each dataset (customers, products, orders)
- Missing customer and product counts in the merged dataset
- Valid order count after `is_valid` filtering
- Cleaning funnel bar chart
- Preview of the first 20 rows of cleaned `sales_summary`
- **Download button** to export `sales_summary.csv`

#### Sidebar Filters
All five tabs respond to three global filters in the sidebar:
- **Category** — filter by product category
- **City** — filter by customer city
- **Month Range** — slide to narrow the date window

---

## Known Limitations & Future Improvements

| Limitation | Suggested Improvement |
|---|---|
| No error handling on file read | Add `try/except FileNotFoundError` |
| `if_exists="replace"` risks data loss | Use staging table + atomic swap |
| No logging to file | Replace `print()` with Python `logging` module |
| No schema validation on input | Add column presence check before processing |
| Pipeline runs manually | Schedule with Apache Airflow or cron job |
| SQLite not scalable | Migrate to PostgreSQL for production use |
| No unit tests | Add `pytest` test suite for cleaning functions |
| Dashboard has no authentication | Add Streamlit authentication for multi-user deployments |
| Dashboard re-runs ETL on every upload | Cache results with `@st.cache_data` for large datasets |
| No map visualisation | Add choropleth map of Nigerian cities using Plotly Geo |

---

## Author

**Emmanuel Akinloye**  
Capstone Project — Data Engineer ETL Assignment  
Pipeline: `etl_pipeline.py` | Database: `retail_sales.db` | Repo: `retail-etl-pipeline`
