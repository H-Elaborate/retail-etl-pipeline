"""
=============================================================
  YTG RETAIL — ETL Pipeline Unit Tests
  File: tests/test_etl.py
  Run: python -m pytest tests/ -v
=============================================================
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# ── Helpers (inline transforms matching etl_pipeline.py logic) ──

def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["customer_id"])
    df = df.dropna(subset=["customer_name"])
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")
    df = df.dropna(subset=["signup_date"])
    return df.reset_index(drop=True)


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["product_id"])
    df = df.dropna(subset=["product_name", "price"])
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])
    return df.reset_index(drop=True)


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["order_id"])
    df["quantity"]   = pd.to_numeric(df["quantity"],   errors="coerce")
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df = df.dropna(subset=["order_date", "quantity"])
    df = df[df["quantity"] > 0]
    return df.reset_index(drop=True)


# ════════════════════════════════════════════════════════
#  CUSTOMER CLEANING TESTS
# ════════════════════════════════════════════════════════

class TestCustomerCleaning:

    def test_removes_duplicate_customer_ids(self):
        df = pd.DataFrame({
            "customer_id":   ["C001", "C001", "C002"],
            "customer_name": ["Alice", "Alice Dup", "Bob"],
            "city":          ["Lagos", "Abuja", "Kano"],
            "signup_date":   ["2024-01-01", "2024-01-02", "2024-01-03"]
        })
        result = clean_customers(df)
        assert len(result) == 2
        assert result["customer_id"].nunique() == 2

    def test_drops_null_customer_name(self):
        df = pd.DataFrame({
            "customer_id":   ["C001", "C002"],
            "customer_name": [None, "Bob"],
            "city":          ["Lagos", "Abuja"],
            "signup_date":   ["2024-01-01", "2024-01-02"]
        })
        result = clean_customers(df)
        assert len(result) == 1
        assert result.iloc[0]["customer_name"] == "Bob"

    def test_drops_invalid_signup_date(self):
        df = pd.DataFrame({
            "customer_id":   ["C001", "C002"],
            "customer_name": ["Alice", "Bob"],
            "city":          ["Lagos", "Abuja"],
            "signup_date":   ["not-a-date", "2024-01-02"]
        })
        result = clean_customers(df)
        assert len(result) == 1

    def test_signup_date_is_datetime(self):
        df = pd.DataFrame({
            "customer_id":   ["C001"],
            "customer_name": ["Alice"],
            "city":          ["Lagos"],
            "signup_date":   ["2024-03-15"]
        })
        result = clean_customers(df)
        assert pd.api.types.is_datetime64_any_dtype(result["signup_date"])

    def test_all_valid_customers_retained(self):
        df = pd.DataFrame({
            "customer_id":   ["C001", "C002", "C003"],
            "customer_name": ["Alice", "Bob", "Carol"],
            "city":          ["Lagos", "Abuja", "Kano"],
            "signup_date":   ["2024-01-01", "2024-02-01", "2024-03-01"]
        })
        result = clean_customers(df)
        assert len(result) == 3


# ════════════════════════════════════════════════════════
#  PRODUCT CLEANING TESTS
# ════════════════════════════════════════════════════════

class TestProductCleaning:

    def test_removes_duplicate_product_ids(self):
        df = pd.DataFrame({
            "product_id":   ["P001", "P001", "P002"],
            "product_name": ["Laptop", "Laptop Dup", "Phone"],
            "category":     ["Electronics", "Electronics", "Electronics"],
            "price":        [450000, 450000, 320000]
        })
        result = clean_products(df)
        assert len(result) == 2

    def test_drops_null_price(self):
        df = pd.DataFrame({
            "product_id":   ["P001", "P002"],
            "product_name": ["Laptop", "Phone"],
            "category":     ["Electronics", "Electronics"],
            "price":        [None, 320000]
        })
        result = clean_products(df)
        assert len(result) == 1

    def test_drops_non_numeric_price(self):
        df = pd.DataFrame({
            "product_id":   ["P001", "P002"],
            "product_name": ["Laptop", "Phone"],
            "category":     ["Electronics", "Electronics"],
            "price":        ["N/A", "320000"]
        })
        result = clean_products(df)
        assert len(result) == 1
        assert result.iloc[0]["price"] == 320000.0

    def test_price_is_numeric(self):
        df = pd.DataFrame({
            "product_id":   ["P001"],
            "product_name": ["Laptop"],
            "category":     ["Electronics"],
            "price":        ["450000"]
        })
        result = clean_products(df)
        assert pd.api.types.is_numeric_dtype(result["price"])

    def test_drops_null_product_name(self):
        df = pd.DataFrame({
            "product_id":   ["P001", "P002"],
            "product_name": [None, "Phone"],
            "category":     ["Electronics", "Electronics"],
            "price":        [450000, 320000]
        })
        result = clean_products(df)
        assert len(result) == 1


# ════════════════════════════════════════════════════════
#  ORDER CLEANING TESTS
# ════════════════════════════════════════════════════════

class TestOrderCleaning:

    def test_removes_duplicate_order_ids(self):
        df = pd.DataFrame({
            "order_id":    ["O001", "O001", "O002"],
            "customer_id": ["C001", "C001", "C002"],
            "product_id":  ["P001", "P001", "P002"],
            "quantity":    [1, 1, 2],
            "order_date":  ["2024-01-01", "2024-01-01", "2024-01-02"]
        })
        result = clean_orders(df)
        assert len(result) == 2

    def test_drops_zero_quantity(self):
        df = pd.DataFrame({
            "order_id":    ["O001", "O002"],
            "customer_id": ["C001", "C002"],
            "product_id":  ["P001", "P002"],
            "quantity":    [0, 3],
            "order_date":  ["2024-01-01", "2024-01-02"]
        })
        result = clean_orders(df)
        assert len(result) == 1
        assert result.iloc[0]["quantity"] == 3

    def test_drops_negative_quantity(self):
        df = pd.DataFrame({
            "order_id":    ["O001", "O002"],
            "customer_id": ["C001", "C002"],
            "product_id":  ["P001", "P002"],
            "quantity":    [-1, 2],
            "order_date":  ["2024-01-01", "2024-01-02"]
        })
        result = clean_orders(df)
        assert len(result) == 1

    def test_drops_null_order_date(self):
        df = pd.DataFrame({
            "order_id":    ["O001", "O002"],
            "customer_id": ["C001", "C002"],
            "product_id":  ["P001", "P002"],
            "quantity":    [1, 2],
            "order_date":  [None, "2024-01-02"]
        })
        result = clean_orders(df)
        assert len(result) == 1

    def test_drops_invalid_order_date(self):
        df = pd.DataFrame({
            "order_id":    ["O001", "O002"],
            "customer_id": ["C001", "C002"],
            "product_id":  ["P001", "P002"],
            "quantity":    [1, 2],
            "order_date":  ["bad-date", "2024-01-02"]
        })
        result = clean_orders(df)
        assert len(result) == 1

    def test_order_date_is_datetime(self):
        df = pd.DataFrame({
            "order_id":    ["O001"],
            "customer_id": ["C001"],
            "product_id":  ["P001"],
            "quantity":    [1],
            "order_date":  ["2024-06-15"]
        })
        result = clean_orders(df)
        assert pd.api.types.is_datetime64_any_dtype(result["order_date"])


# ════════════════════════════════════════════════════════
#  CALCULATED FIELDS TESTS
# ════════════════════════════════════════════════════════

class TestCalculatedFields:

    def setup_method(self):
        self.df = pd.DataFrame({
            "order_id":    ["O001", "O002"],
            "order_date":  pd.to_datetime(["2024-01-15", "2024-03-20"]),
            "customer_id": ["C001", "C002"],
            "quantity":    [2, 3],
            "price":       [50000.0, 12000.0]
        })

    def test_total_amount_calculation(self):
        self.df["total_amount"] = (self.df["quantity"] * self.df["price"]).round(2)
        assert self.df.iloc[0]["total_amount"] == 100000.0
        assert self.df.iloc[1]["total_amount"] == 36000.0

    def test_total_amount_rounded_to_2dp(self):
        df = pd.DataFrame({"quantity": [3], "price": [10000.333]})
        df["total_amount"] = (df["quantity"] * df["price"]).round(2)
        assert df.iloc[0]["total_amount"] == 30001.0

    def test_year_month_extraction(self):
        self.df["year_month"] = self.df["order_date"].dt.to_period("M").astype(str)
        assert self.df.iloc[0]["year_month"] == "2024-01"
        assert self.df.iloc[1]["year_month"] == "2024-03"

    def test_year_month_is_string(self):
        self.df["year_month"] = self.df["order_date"].dt.to_period("M").astype(str)
        assert self.df["year_month"].dtype == object
