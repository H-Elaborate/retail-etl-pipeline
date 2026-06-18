import pandas as pd
import sqlite3
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path

base_dir = Path(__file__).resolve().parent
table_name = "sales_summary"

divider  = "=" * 62
divider2 = "-" * 62

def header(title: str):
    print(f"\n{divider}")
    print(f"  {title}")
    print(divider)

header("PHASE 1 · EXTRACT")

customers = pd.read_csv(base_dir / "customers.csv")
products  = pd.read_csv(base_dir / "products.csv")
orders    = pd.read_csv(base_dir / "orders.csv")

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

header("PHASE 2 · TRANSFORM")

print("\n   Data Cleaning")
print(divider2) 

before = len(customers)
customers = customers.drop_duplicates(subset=["customer_id"])
customers = customers.dropna(subset=["customer_name"])
customers["signup_date"] = pd.to_datetime(
    customers["signup_date"],
    errors="coerce"
)
customers = customers.dropna(subset=["signup_date"])

print(f"  ✔  customers.csv  → {before:>6} rows → {len(customers):>6} rows after cleaning"
      f"(removed {before - len(customers)} duplicates/nulls)")

before = len(products)
products = products.drop_duplicates(subset=["product_id"])
products = products.dropna(subset=["product_name", "price"])
products["price"] = pd.to_numeric(
    products["price"],
    errors="coerce"
)
products = products.dropna(subset=["price"])

print(f"  ✔  products.csv   → {before:>6} rows → {len(products):>6} rows after cleaning"
      f"(removed {before - len(products)} duplicates/nulls)")

before = len(orders)
orders = orders.drop_duplicates(subset=["order_id"])
orders["quantity"] = pd.to_numeric(
    orders["quantity"],
    errors="coerce"
)
orders = orders.dropna(subset=["order_date", "quantity"])
invalid_qty = len(orders[orders["quantity"] <= 0])
orders = orders[orders["quantity"] > 0]

print(f"  ✔  orders.csv     → {before:>6} rows → {len(orders):>6} rows after cleaning"
      f"(removed {before - len(orders)} duplicates/nulls, "
      f"{invalid_qty} with qty ≤ 0)")

print("\n Merging Datasets")
print(divider2)

merged = (
    orders
    .merge(customers, how="left", on="customer_id")
    .merge(products, how="left", on="product_id")
)

missing_customers = merged["customer_name"].isna().sum()
missing_products = merged["product_name"].isna().sum()

print(f" After left join → {len(merged)} rows")
print(f" Missing customers → {missing_customers}")
print(f" Missing products → {missing_products}")

valid_rows = merged[is_valid].sum()
print(f" Valid orders → {valid_rows} / {len(merge)}")