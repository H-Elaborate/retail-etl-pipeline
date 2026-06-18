# Data Dictionary — YTG Retail ETL Pipeline

This document describes every field in the three source CSV files and the
final `sales_summary` output table.

---

## Source Files

### customers.csv

| Column | Type | Example | Description |
|---|---|---|---|
| `customer_id` | String | `C00001` | Unique customer identifier. Format: `C` + 5-digit number |
| `customer_name` | String | `Emeka Okafor` | Full name of the customer |
| `city` | String | `Lagos` | Nigerian city where the customer is located |
| `signup_date` | Date (YYYY-MM-DD) | `2024-03-15` | Date the customer registered on the platform |

**Total records:** 12,002  
**Cities covered:** 40+ Nigerian cities  
**Date range:** January 2023 – August 2026

---

### products.csv

| Column | Type | Example | Description |
|---|---|---|---|
| `product_id` | String | `P00003` | Unique product identifier. Format: `P` + 5-digit number |
| `product_name` | String | `iPhone 13` | Full name of the product |
| `category` | String | `Electronics` | Product category (see categories below) |
| `price` | Float | `780000` | Unit price in Nigerian Naira (₦) |

**Total records:** 10,045  
**Categories:**

| Category | Description |
|---|---|
| Electronics | Phones, laptops, TVs, cameras, accessories |
| Accessories | Cables, chargers, bags, cases, peripherals |
| Groceries | Food items, beverages, cooking ingredients |
| Stationery | Books, pens, notebooks, office supplies |
| Fashion | Clothing, shoes, bags, watches, jewellery |
| Home | Appliances, furniture, kitchen, decor |

---

### orders.csv

| Column | Type | Example | Description |
|---|---|---|---|
| `order_id` | String | `O000001` | Unique order identifier. Format: `O` + 6-digit number |
| `customer_id` | String | `C00001` | Foreign key → `customers.customer_id` |
| `product_id` | String | `P00003` | Foreign key → `products.product_id` |
| `quantity` | Integer | `2` | Number of units ordered. Must be ≥ 1 |
| `order_date` | Date (YYYY-MM-DD) | `2024-06-20` | Date the order was placed |

**Total records:** 20,000  
**Quantity range:** 1 – 10 units  
**Date range:** January 2023 – August 2026

---

## Output Table

### sales_summary (SQLite — retail_sales.db)

This is the final cleaned and enriched dataset produced by the ETL pipeline.

| Column | Type | Source | Description |
|---|---|---|---|
| `order_id` | TEXT | orders.csv | Unique order identifier |
| `order_date` | TEXT | orders.csv | Date the order was placed |
| `year_month` | TEXT | Calculated | Month period extracted from order_date (YYYY-MM) |
| `customer_id` | TEXT | orders.csv | Customer identifier |
| `customer_name` | TEXT | customers.csv | Full name of the customer |
| `city` | TEXT | customers.csv | Customer's city |
| `product_id` | TEXT | orders.csv | Product identifier |
| `product_name` | TEXT | products.csv | Name of the product |
| `category` | TEXT | products.csv | Product category |
| `quantity` | REAL | orders.csv | Units ordered |
| `price` | REAL | products.csv | Unit price in Naira (₦) |
| `total_amount` | REAL | Calculated | quantity × price, rounded to 2 decimal places |

---

## Business Rules Applied During Cleaning

| Rule | Field | Action |
|---|---|---|
| No duplicate customer records | `customer_id` | Keep first, drop rest |
| Customer name must exist | `customer_name` | Drop row if null |
| Signup date must be valid | `signup_date` | Drop row if unparseable |
| No duplicate product records | `product_id` | Keep first, drop rest |
| Product name and price must exist | `product_name`, `price` | Drop row if null |
| Price must be a number | `price` | Drop row if non-numeric |
| No duplicate orders | `order_id` | Keep first, drop rest |
| Order date must be valid | `order_date` | Drop row if unparseable |
| Quantity must be a number | `quantity` | Drop row if non-numeric |
| Quantity must be greater than zero | `quantity` | Drop row if ≤ 0 |
| Order must have matching customer | `customer_id` | Flagged via `is_valid` |
| Order must have matching product | `product_id` | Flagged via `is_valid` |
