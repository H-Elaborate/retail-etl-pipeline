"""
=============================================================
  YTG RETAIL — Customer Orders ETL Pipeline
  Data Engineer: ETL Assignment
=============================================================
"""
 
import pandas as pd #imports pandas library for data manipulation and analysis.
import sqlite3 #imports sqlite3, an  RDBMs, library for database operations.
import warnings #Suppress warnings completely
warnings.filterwarnings("ignore")
from pathlib import Path

# ─────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent #No matter where I run this from, always use the script’s folder.
TABLE_NAME = "sales_summary"

DIVIDER  = "=" * 62
DIVIDER2 = "-" * 62
 
def header(title: str):
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)
 
# ══════════════════════════════════════════════════════════════
#  PHASE 1 — EXTRACT
# ══════════════════════════════════════════════════════════════
header("PHASE 1 · EXTRACT")
 
customers = pd.read_csv(BASE_DIR / "customers.csv") #DataFrame\
products  = pd.read_csv(BASE_DIR / "products.csv") #DataFrame\
orders    = pd.read_csv(BASE_DIR / "orders.csv") #DataFrame\
 
print(f"  ✔  customers.csv  → {len(customers):>6} rows, {customers.shape[1]} cols")
print(f"  ✔  products.csv   → {len(products):>6} rows, {products.shape[1]} cols")
print(f"  ✔  orders.csv     → {len(orders):>6} rows, {orders.shape[1]} cols")
 
print("\n  — Raw previews —")
for name, df in [
    ("Customers", customers), 
    ("Products", products), 
    ("Orders", orders)
    ]:
    print(f"\n  [{name}]")
    print(df.head(3).to_string(index=False))
 
 
# ══════════════════════════════════════════════════════════════
#  PHASE 2 — TRANSFORM
# ══════════════════════════════════════════════════════════════

header("PHASE 2 · TRANSFORM")

# ── 2a. Data Cleaning ────────────────────────────────────────
print("\n   Data Cleaning")
print(DIVIDER2)

# --- customers ---
before = len(customers)
customers = customers.drop_duplicates(subset=["customer_id"])
customers = customers.dropna(subset=["customer_name"])
customers["signup_date"] = pd.to_datetime(
    customers["signup_date"],
    errors="coerce"
)
customers = customers.dropna(subset=["signup_date"])

print(f"  Customers : {before} → {len(customers)} rows  "
      f"(removed {before - len(customers)} duplicates/nulls)")

# --- products ---
before = len(products)
products = products.drop_duplicates(subset=["product_id"])
products = products.dropna(subset=["product_name", "price"])
products["price"] = pd.to_numeric(
    products["price"],
    errors="coerce"
)
products = products.dropna(subset=["price"])

print(f"  Products  : {before} → {len(products)} rows  "
      f"(removed {before - len(products)} duplicates/nulls)")

# --- orders ---
before = len(orders)
orders = orders.drop_duplicates(subset=["order_id"])

orders["quantity"] = pd.to_numeric(
    orders["quantity"],
    errors="coerce"
)

orders["order_date"] = pd.to_datetime(
    orders["order_date"],
    errors="coerce"
)

orders = orders.dropna(subset=["order_date", "quantity"])

invalid_qty = len(orders[orders["quantity"] <= 0])
orders = orders[orders["quantity"] > 0]

print(f"  Orders    : {before} → {len(orders)} rows  "
      f"(removed {before - len(orders)} duplicates/invalid rows, "
      f"{invalid_qty} with qty ≤ 0)")

# ── 2b. Merge Datasets (LEFT JOIN VERSION) ───────────────────
print("\n   Merging Datasets")
print(DIVIDER2)

merged = (
    orders
    .merge(customers, on="customer_id", how="left")
    .merge(products,  on="product_id",  how="left")
)

# Data quality tracking (NEW)
missing_customers = merged["customer_name"].isna().sum()
missing_products  = merged["product_name"].isna().sum()

print(f"  After left-join  → {len(merged)} rows")
print(f"  Missing customers → {missing_customers}")
print(f"  Missing products  → {missing_products}")

# Optional but recommended flag
merged["is_valid"] = (
    merged["customer_name"].notna() &
    merged["product_name"].notna()
)

valid_rows = merged["is_valid"].sum()
print(f"  Valid orders → {valid_rows} / {len(merged)}")

# ── 2c. Calculated Fields ────────────────────────────────────
print("\n   Calculated Fields")
print(DIVIDER2)

merged["total_amount"] = (merged["quantity"] * merged["price"]).round(2)
merged["year_month"]   = merged["order_date"].dt.to_period("M").astype(str)

print(f"  ✔  total_amount  = quantity × price")
print(f"  ✔  year_month    extracted from order_date")
print(f"  ✔  Dates cast to datetime")

# ── 2d. Final column selection ───────────────────────────────
sales_summary = merged[[
    "order_id", "order_date", "year_month",
    "customer_id", "customer_name", "city",
    "product_id", "product_name", "category",
    "quantity", "price", "total_amount"
]].copy()

sales_summary = sales_summary.sort_values("order_date")
sales_summary = sales_summary.reset_index(drop=True)

print(f"\n  Final dataset  → {len(sales_summary)} rows × {sales_summary.shape[1]} cols")

print("\n  Sample (first 5 rows):")
print(sales_summary.head(5).to_string(index=False))
 
# ══════════════════════════════════════════════════════════════
#  PHASE 3 — LOAD
# ══════════════════════════════════════════════════════════════
header("PHASE 3 · LOAD → SQLite")
 
conn = sqlite3.connect(BASE_DIR / "retails_sales.db")
sales_summary.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
 
# Verify
row_count = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
print(f"  ✔  Database  : retail_sales.db")
print(f"  ✔  Table     : {TABLE_NAME}")
print(f"  ✔  Rows loaded : {row_count}")
print(f"\n  Schema:") #Shows the structure of this table.
for row in conn.execute(f"PRAGMA table_info({TABLE_NAME})").fetchall():
    print(f"    {row[1]:<20} {row[2]}")
 
 
# ══════════════════════════════════════════════════════════════
#  PHASE 4 — REPORTING & ANALYSIS
# ══════════════════════════════════════════════════════════════
header("PHASE 4 · REPORTING & ANALYSIS")
 
# ── 4.1 Total Revenue ────────────────────────────────────────
total_revenue = sales_summary["total_amount"].sum()
print(f"\n  📊 Total Revenue Generated")
print(DIVIDER2)
print(f"  ₦{total_revenue:>15,.2f}")
 
# ── 4.2 Top 5 Customers by Spending ─────────────────────────
print(f"\n  🏆 Top 5 Customers by Spending")
print(DIVIDER2)
top_customers = (
    sales_summary.groupby(["customer_id", "customer_name", "city"])["total_amount"]
    .sum()
    .reset_index()
    .sort_values("total_amount", ascending=False)
    .head(5)
    .reset_index(drop=True)
)
top_customers.index += 1
top_customers["total_amount"] = top_customers["total_amount"].apply(lambda x: f"₦{x:,.2f}")
print(top_customers.rename(columns={
    "customer_id": "ID", 
    "customer_name": "Name",
    "city": "City", 
    "total_amount": "Total Spent"
}).to_string())
 
# ── 4.3 Best-Selling Products ────────────────────────────────
print(f"\n  🛒 Best-Selling Products (by units sold)")
print(DIVIDER2)

best_products = (
    sales_summary.groupby(["product_id", "product_name", "category"])
    .agg(units_sold=("quantity", "sum"), revenue=("total_amount", "sum"))
    .reset_index()
    .sort_values("units_sold", ascending=False)
    .head(5)
    .reset_index(drop=True)
)
best_products.index += 1
best_products["revenue"] = best_products["revenue"].apply(lambda x: f"₦{x:,.2f}")
print(best_products.rename(columns={
    "product_id": "ID", "product_name": "Product",
    "category": "Category", "units_sold": "Units", "revenue": "Revenue"
}).to_string())
 
# ── 4.4 Revenue by Category ──────────────────────────────────
print(f"\n  📦 Revenue by Product Category")
print(DIVIDER2)
cat_revenue = (
    sales_summary.groupby("category")["total_amount"]
    .sum()
    .reset_index()
    .sort_values("total_amount", ascending=False)
)
cat_revenue["% share"] = (cat_revenue["total_amount"] / total_revenue * 100).round(1)
cat_revenue["total_amount"] = cat_revenue["total_amount"].apply(lambda x: f"₦{x:,.2f}")
cat_revenue.columns = ["Category", "Revenue", "% Share"]
print(cat_revenue.to_string(index=False))
 
# ── 4.5 Monthly Sales Trend ──────────────────────────────────
print(f"\n  📈 Monthly Sales Trend")
print(DIVIDER2)
monthly = (
    sales_summary.groupby("year_month")["total_amount"]
    .sum()
    .reset_index()
    .sort_values("year_month")
)
monthly.columns = ["Month", "Revenue"]
monthly["Bar"] = monthly["Revenue"].apply(
    lambda v: "█" * int(v / monthly["Revenue"].max() * 30)
)
for _, row in monthly.iterrows():
    print(f"  {row['Month']}  {row['Bar']:<32}  ₦{row['Revenue']:>14,.2f}")
 
# ── 4.6 Average Order Value ──────────────────────────────────
print(f"\n  💡 Average Order Value")
print(DIVIDER2)
avg_order = sales_summary["total_amount"].mean()
print(f"  ₦{avg_order:>15,.2f}  per order")
 
# ── Summary ─────────────────────────────────────────────────
print(f"\n{DIVIDER}")
print(f"  ETL PIPELINE COMPLETE")
print(DIVIDER)
print(f"  Total orders processed  : {len(sales_summary)}")
print(f"  Total revenue           : ₦{total_revenue:,.2f}")
print(f"  Average order value     : ₦{avg_order:,.2f}")
print(f"  Unique customers        : {sales_summary['customer_id'].nunique()}")
print(f"  Unique products         : {sales_summary['product_id'].nunique()}")
print(f"  Date range              : {sales_summary['order_date'].min().date()} "
      f"→ {sales_summary['order_date'].max().date()}")
print(DIVIDER)
print(f"\n  Output files:")
print(f"    • retail_sales.db   (SQLite database)")
print(f"    • etl_pipeline.py   (this script)\n")
 
conn.close()