"""
=============================================================
  YTG RETAIL — Streamlit Data Visualization Platform
  File: Viz.py
  Run: streamlit run Viz.py
=============================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path

# ─────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="YTG Retail Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fb; }
    .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    .section-title {
        font-size: 15px; font-weight: 600; color: #374151;
        margin-bottom: 12px; padding-bottom: 6px;
        border-bottom: 2px solid #e5e7eb;
    }
    div[data-testid="metric-container"] {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  INITIALIZE SESSION STATE — must happen before anything else
# ─────────────────────────────────────────────────────────────
if "sales_summary" not in st.session_state:
    st.session_state["sales_summary"] = None
if "quality" not in st.session_state:
    st.session_state["quality"] = None
if "filters" not in st.session_state:
    st.session_state["filters"] = None


# ─────────────────────────────────────────────────────────────
#  ETL FUNCTIONS  (same logic as etl_pipeline.py — untouched)
# ─────────────────────────────────────────────────────────────
def clean_customers(df):
    df = df.drop_duplicates(subset=["customer_id"])
    df = df.dropna(subset=["customer_name"])
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")
    df = df.dropna(subset=["signup_date"])
    return df

def clean_products(df):
    df = df.drop_duplicates(subset=["product_id"])
    df = df.dropna(subset=["product_name", "price"])
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])
    return df

def clean_orders(df):
    df = df.drop_duplicates(subset=["order_id"])
    df["quantity"]   = pd.to_numeric(df["quantity"],   errors="coerce")
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df = df.dropna(subset=["order_date", "quantity"])
    df = df[df["quantity"] > 0]
    return df

def run_etl(customers_raw, products_raw, orders_raw):
    customers = clean_customers(customers_raw.copy())
    products  = clean_products(products_raw.copy())
    orders    = clean_orders(orders_raw.copy())

    merged = (
        orders
        .merge(customers, on="customer_id", how="left")
        .merge(products,  on="product_id",  how="left")
    )
    merged["is_valid"]     = merged["customer_name"].notna() & merged["product_name"].notna()
    merged["total_amount"] = (merged["quantity"] * merged["price"]).round(2)
    merged["year_month"]   = merged["order_date"].dt.to_period("M").astype(str)

    sales_summary = merged[merged["is_valid"]][[
        "order_id", "order_date", "year_month",
        "customer_id", "customer_name", "city",
        "product_id", "product_name", "category",
        "quantity", "price", "total_amount"
    ]].copy()
    sales_summary = sales_summary.sort_values("order_date").reset_index(drop=True)

    quality = {
        "raw_customers":     len(customers_raw),
        "clean_customers":   len(customers),
        "raw_products":      len(products_raw),
        "clean_products":    len(products),
        "raw_orders":        len(orders_raw),
        "clean_orders":      len(orders),
        "missing_customers": int(merged["customer_name"].isna().sum()),
        "missing_products":  int(merged["product_name"].isna().sum()),
        "valid_orders":      int(merged["is_valid"].sum()),
    }
    return sales_summary, quality


# ─────────────────────────────────────────────────────────────
#  SIDEBAR — file upload
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛒 YTG Retail ETL")
    st.markdown("**Data Visualization Platform**")
    st.markdown("---")
    st.markdown("#### 📂 Upload Your CSV Files")
    st.caption("Upload all three files to run the ETL pipeline automatically.")

    cust_file = st.file_uploader("customers.csv", type="csv", key="cust")
    prod_file = st.file_uploader("products.csv",  type="csv", key="prod")
    ord_file  = st.file_uploader("orders.csv",    type="csv", key="ord")

    st.markdown("---")
    st.caption("YTG Retail · Data Engineering Capstone")


# ─────────────────────────────────────────────────────────────
#  MAIN HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("## 🛒 YTG Retail — Sales Dashboard")
st.caption("Upload your three CSV files in the sidebar to run the ETL pipeline and see live analytics.")
st.markdown("---")


# ─────────────────────────────────────────────────────────────
#  RUN ETL WHEN FILES ARE UPLOADED
# ─────────────────────────────────────────────────────────────
if cust_file and prod_file and ord_file:
    with st.spinner("⚙️ Running ETL pipeline — cleaning, merging, transforming..."):
        customers_raw = pd.read_csv(cust_file)
        products_raw  = pd.read_csv(prod_file)
        orders_raw    = pd.read_csv(ord_file)
        ss, quality   = run_etl(customers_raw, products_raw, orders_raw)
        st.session_state["sales_summary"] = ss
        st.session_state["quality"]       = quality
    st.success(f"✅ ETL complete — {len(ss):,} valid orders ready for analysis.")
else:
    st.info("👈 Upload **customers.csv**, **products.csv**, and **orders.csv** in the sidebar to begin.")
    st.stop()   # ← nothing below this runs until files are uploaded


# ─────────────────────────────────────────────────────────────
#  SAFELY READ FROM SESSION STATE
#  We only reach here if st.stop() was NOT triggered above
# ─────────────────────────────────────────────────────────────
ss = st.session_state["sales_summary"]
q  = st.session_state["quality"]

# Extra safety guard — should never be None here but just in case
if ss is None or q is None:
    st.warning("Something went wrong. Please re-upload your files.")
    st.stop()

# ─────────────────────────────────────────────────────────────
#  SIDEBAR FILTERS — only shown after data loads
# ─────────────────────────────────────────────────────────────
_months = sorted(ss["year_month"].dropna().unique().tolist())

with st.sidebar:
    st.markdown("#### 🔍 Filters")
    cats     = ["All"] + sorted(ss["category"].dropna().unique().tolist())
    sel_cat  = st.selectbox("Category", cats)
    cities   = ["All"] + sorted(ss["city"].dropna().unique().tolist())
    sel_city = st.selectbox("City", cities)
    sel_range = st.select_slider(
        "Month range", options=_months,
        value=(_months[0], _months[-1])
    )
    f = {"category": sel_cat, "city": sel_city, "range": sel_range}
    st.session_state["filters"] = f

# ─────────────────────────────────────────────────────────────
#  APPLY FILTERS
# ─────────────────────────────────────────────────────────────
filtered = ss.copy()
if f["category"] != "All":
    filtered = filtered[filtered["category"] == f["category"]]
if f["city"] != "All":
    filtered = filtered[filtered["city"] == f["city"]]
filtered = filtered[
    (filtered["year_month"] >= f["range"][0]) &
    (filtered["year_month"] <= f["range"][1])
]


# ─────────────────────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", "📈 Sales Trends", "🛍️ Products", "👥 Customers", "🔬 Data Quality"
])


# ══════════════════════════════════════════════════════════════
#  TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════
with tab1:
    total_rev = filtered["total_amount"].sum()
    total_ord = len(filtered)
    uniq_cust = filtered["customer_id"].nunique()
    avg_ord   = filtered["total_amount"].mean() if total_ord > 0 else 0
    uniq_prod = filtered["product_id"].nunique()
    max_order = filtered["total_amount"].max() if total_ord > 0 else 0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("💰 Total Revenue",    f"₦{total_rev:,.0f}")
    k2.metric("🧾 Total Orders",     f"{total_ord:,}")
    k3.metric("👤 Unique Customers", f"{uniq_cust:,}")
    k4.metric("📦 Unique Products",  f"{uniq_prod:,}")
    k5.metric("💡 Avg Order Value",  f"₦{avg_ord:,.0f}")
    k6.metric("🏆 Largest Order",    f"₦{max_order:,.0f}")

    st.markdown("---")
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<p class="section-title">📈 Monthly Revenue Trend</p>', unsafe_allow_html=True)
        monthly = (
            filtered.groupby("year_month")["total_amount"]
            .sum().reset_index().sort_values("year_month")
        )
        monthly.columns = ["Month", "Revenue"]
        fig_line = px.area(
            monthly, x="Month", y="Revenue",
            color_discrete_sequence=["#185FA5"], template="plotly_white"
        )
        fig_line.update_traces(fill="tozeroy", fillcolor="rgba(24,95,165,0.1)", line_width=2.5)
        fig_line.update_layout(margin=dict(t=10,b=10,l=10,r=10),
            yaxis_tickformat="₦,.0f", xaxis_tickangle=-45, height=300,
            yaxis_title="Revenue (₦)", xaxis_title="")
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">📦 Revenue by Category</p>', unsafe_allow_html=True)
        cat_rev = (
            filtered.groupby("category")["total_amount"]
            .sum().reset_index().sort_values("total_amount", ascending=False)
        )
        fig_pie = px.pie(cat_rev, values="total_amount", names="category",
            color_discrete_sequence=px.colors.qualitative.Bold,
            template="plotly_white", hole=0.45)
        fig_pie.update_traces(textposition="outside", textinfo="percent+label")
        fig_pie.update_layout(margin=dict(t=10,b=10,l=10,r=10),
            showlegend=False, height=300)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<p class="section-title">🏙️ Top 10 Cities by Revenue</p>', unsafe_allow_html=True)
        city_rev = (
            filtered.groupby("city")["total_amount"]
            .sum().reset_index()
            .sort_values("total_amount", ascending=True).tail(10)
        )
        fig_city = px.bar(city_rev, x="total_amount", y="city",
            orientation="h", template="plotly_white",
            color_discrete_sequence=["#0F6E56"])
        fig_city.update_layout(margin=dict(t=10,b=10,l=10,r=10),
            xaxis_tickformat="₦,.0f", height=320,
            xaxis_title="Revenue (₦)", yaxis_title="")
        st.plotly_chart(fig_city, use_container_width=True)

    with col4:
        st.markdown('<p class="section-title">📦 Category Revenue Bar</p>', unsafe_allow_html=True)
        cat_bar = (
            filtered.groupby("category")["total_amount"]
            .sum().reset_index().sort_values("total_amount", ascending=True)
        )
        fig_cat = px.bar(cat_bar, x="total_amount", y="category",
            orientation="h", template="plotly_white",
            color="total_amount", color_continuous_scale=["#bfdbfe","#185FA5"])
        fig_cat.update_layout(margin=dict(t=10,b=10,l=10,r=10),
            xaxis_tickformat="₦,.0f", height=320,
            xaxis_title="Revenue (₦)", yaxis_title="",
            coloraxis_showscale=False)
        st.plotly_chart(fig_cat, use_container_width=True)


# ══════════════════════════════════════════════════════════════
#  TAB 2 — SALES TRENDS
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-title">📅 Monthly Revenue — Full Trend</p>', unsafe_allow_html=True)
    monthly_full = (
        filtered.groupby("year_month")
        .agg(revenue=("total_amount","sum"), orders=("order_id","count"))
        .reset_index().sort_values("year_month")
    )
    fig_combo = go.Figure()
    fig_combo.add_trace(go.Bar(x=monthly_full["year_month"], y=monthly_full["revenue"],
        name="Revenue", marker_color="rgba(24,95,165,0.25)"))
    fig_combo.add_trace(go.Scatter(x=monthly_full["year_month"], y=monthly_full["revenue"],
        name="Trend", mode="lines+markers",
        line=dict(color="#185FA5", width=2.5), marker=dict(size=5)))
    fig_combo.update_layout(template="plotly_white", height=380,
        margin=dict(t=10,b=10,l=10,r=10),
        yaxis=dict(tickformat="₦,.0f", title="Revenue (₦)"),
        xaxis=dict(tickangle=-45, title=""),
        legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig_combo, use_container_width=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">📊 Orders per Month</p>', unsafe_allow_html=True)
        fig_ord = px.bar(monthly_full, x="year_month", y="orders",
            template="plotly_white", color_discrete_sequence=["#853C1A"])
        fig_ord.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=280,
            xaxis_tickangle=-45, xaxis_title="", yaxis_title="Orders")
        st.plotly_chart(fig_ord, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">💡 Avg Order Value per Month</p>', unsafe_allow_html=True)
        monthly_avg = (
            filtered.groupby("year_month")["total_amount"]
            .mean().reset_index().sort_values("year_month")
        )
        fig_avg = px.line(monthly_avg, x="year_month", y="total_amount",
            template="plotly_white", color_discrete_sequence=["#0F6E56"], markers=True)
        fig_avg.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=280,
            xaxis_tickangle=-45, xaxis_title="",
            yaxis_tickformat="₦,.0f", yaxis_title="Avg Order (₦)")
        st.plotly_chart(fig_avg, use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-title">🗓️ Revenue Heatmap (Category × Month)</p>', unsafe_allow_html=True)
    heat = filtered.groupby(["year_month","category"])["total_amount"].sum().reset_index()
    heat_pivot = heat.pivot(index="category", columns="year_month", values="total_amount").fillna(0)
    fig_heat = px.imshow(heat_pivot, color_continuous_scale=["#eff6ff","#185FA5"],
        template="plotly_white", aspect="auto")
    fig_heat.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=300, xaxis_tickangle=-45)
    st.plotly_chart(fig_heat, use_container_width=True)


# ══════════════════════════════════════════════════════════════
#  TAB 3 — PRODUCTS
# ══════════════════════════════════════════════════════════════
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">🛒 Top 10 Products by Units Sold</p>', unsafe_allow_html=True)
        top_units = (
            filtered.groupby(["product_name","category"])
            .agg(units=("quantity","sum")).reset_index()
            .sort_values("units", ascending=True).tail(10)
        )
        fig_units = px.bar(top_units, x="units", y="product_name",
            orientation="h", color="category", template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Bold)
        fig_units.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=360,
            xaxis_title="Units Sold", yaxis_title="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, title=""))
        st.plotly_chart(fig_units, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">💰 Top 10 Products by Revenue</p>', unsafe_allow_html=True)
        top_rev = (
            filtered.groupby(["product_name","category"])
            .agg(revenue=("total_amount","sum")).reset_index()
            .sort_values("revenue", ascending=True).tail(10)
        )
        fig_rev = px.bar(top_rev, x="revenue", y="product_name",
            orientation="h", color="category", template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Bold)
        fig_rev.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=360,
            xaxis_tickformat="₦,.0f", xaxis_title="Revenue (₦)", yaxis_title="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, title=""))
        st.plotly_chart(fig_rev, use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-title">📊 Units Sold vs Revenue (Bubble Chart)</p>', unsafe_allow_html=True)
    bubble = (
        filtered.groupby(["category","product_name"])
        .agg(units=("quantity","sum"), revenue=("total_amount","sum"), orders=("order_id","count"))
        .reset_index()
    )
    fig_bubble = px.scatter(bubble, x="units", y="revenue", size="orders",
        color="category", hover_name="product_name", template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Bold, size_max=30)
    fig_bubble.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=380,
        xaxis_title="Units Sold", yaxis_tickformat="₦,.0f", yaxis_title="Revenue (₦)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, title=""))
    st.plotly_chart(fig_bubble, use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-title">📋 Full Product Summary Table</p>', unsafe_allow_html=True)
    prod_table = (
        filtered.groupby(["product_id","product_name","category"])
        .agg(units_sold=("quantity","sum"), orders=("order_id","count"), revenue=("total_amount","sum"))
        .reset_index().sort_values("revenue", ascending=False)
    )
    prod_table["revenue"] = prod_table["revenue"].apply(lambda x: f"₦{x:,.2f}")
    st.dataframe(prod_table, use_container_width=True, height=300)


# ══════════════════════════════════════════════════════════════
#  TAB 4 — CUSTOMERS
# ══════════════════════════════════════════════════════════════
with tab4:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">🏆 Top 10 Customers by Spending</p>', unsafe_allow_html=True)
        top_cust = (
            filtered.groupby(["customer_id","customer_name","city"])["total_amount"]
            .sum().reset_index()
            .sort_values("total_amount", ascending=True).tail(10)
        )
        fig_cust = px.bar(top_cust, x="total_amount", y="customer_name",
            orientation="h", template="plotly_white",
            color_discrete_sequence=["#185FA5"], hover_data=["city"])
        fig_cust.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=360,
            xaxis_tickformat="₦,.0f", xaxis_title="Total Spent (₦)", yaxis_title="")
        st.plotly_chart(fig_cust, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">🛍️ Orders per Customer (Distribution)</p>', unsafe_allow_html=True)
        cust_orders = filtered.groupby("customer_id")["order_id"].count().reset_index()
        cust_orders.columns = ["customer_id","order_count"]
        fig_dist = px.histogram(cust_orders, x="order_count", nbins=20,
            template="plotly_white", color_discrete_sequence=["#0F6E56"])
        fig_dist.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=360,
            xaxis_title="Number of Orders", yaxis_title="Number of Customers", bargap=0.1)
        st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown("---")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<p class="section-title">🗺️ Customers by City</p>', unsafe_allow_html=True)
        cust_city = (
            filtered.groupby("city")["customer_id"].nunique().reset_index()
            .sort_values("customer_id", ascending=True).tail(12)
        )
        cust_city.columns = ["city","customers"]
        fig_cc = px.bar(cust_city, x="customers", y="city",
            orientation="h", template="plotly_white",
            color_discrete_sequence=["#854F0B"])
        fig_cc.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=360,
            xaxis_title="Unique Customers", yaxis_title="")
        st.plotly_chart(fig_cc, use_container_width=True)

    with col4:
        st.markdown('<p class="section-title">💳 Avg Spend per Order by City</p>', unsafe_allow_html=True)
        avg_spend = (
            filtered.groupby("city")
            .agg(avg_spend=("total_amount","mean"))
            .reset_index().sort_values("avg_spend", ascending=True).tail(12)
        )
        fig_as = px.bar(avg_spend, x="avg_spend", y="city",
            orientation="h", template="plotly_white",
            color_discrete_sequence=["#639922"])
        fig_as.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=360,
            xaxis_tickformat="₦,.0f", xaxis_title="Avg Spend (₦)", yaxis_title="")
        st.plotly_chart(fig_as, use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-title">📋 Top 50 Customers Table</p>', unsafe_allow_html=True)
    cust_table = (
        filtered.groupby(["customer_id","customer_name","city"])
        .agg(orders=("order_id","count"), total_spent=("total_amount","sum"),
             avg_order=("total_amount","mean"))
        .reset_index().sort_values("total_spent", ascending=False).head(50)
    )
    cust_table.index = range(1, len(cust_table)+1)
    cust_table["total_spent"] = cust_table["total_spent"].apply(lambda x: f"₦{x:,.2f}")
    cust_table["avg_order"]   = cust_table["avg_order"].apply(lambda x: f"₦{x:,.2f}")
    st.dataframe(cust_table.rename(columns={
        "customer_id":"ID","customer_name":"Name","city":"City",
        "orders":"Orders","total_spent":"Total Spent","avg_order":"Avg Order"
    }), use_container_width=True, height=350)


# ══════════════════════════════════════════════════════════════
#  TAB 5 — DATA QUALITY
# ══════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<p class="section-title">🔬 ETL Pipeline Quality Report</p>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Raw Customers",  f"{q['raw_customers']:,}",
              delta=f"-{q['raw_customers']-q['clean_customers']:,} removed")
    c2.metric("Raw Products",   f"{q['raw_products']:,}",
              delta=f"-{q['raw_products']-q['clean_products']:,} removed")
    c3.metric("Raw Orders",     f"{q['raw_orders']:,}",
              delta=f"-{q['raw_orders']-q['clean_orders']:,} removed")

    st.markdown("---")
    c4, c5, c6 = st.columns(3)
    c4.metric("Missing Customers in Orders", f"{q['missing_customers']:,}")
    c5.metric("Missing Products in Orders",  f"{q['missing_products']:,}")
    c6.metric("Valid Orders (is_valid=True)", f"{q['valid_orders']:,}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">📊 Cleaning Funnel</p>', unsafe_allow_html=True)
        funnel_df = pd.DataFrame({
            "Stage": ["Raw Customers","Clean Customers","Raw Products",
                      "Clean Products","Raw Orders","Clean Orders","Valid Orders"],
            "Count": [q["raw_customers"], q["clean_customers"],
                      q["raw_products"],  q["clean_products"],
                      q["raw_orders"],    q["clean_orders"], q["valid_orders"]]
        })
        fig_funnel = px.bar(funnel_df, x="Stage", y="Count",
            color="Stage", template="plotly_white",
            color_discrete_sequence=["#185FA5","#185FA5","#0F6E56","#0F6E56",
                                     "#853C1A","#853C1A","#639922"])
        fig_funnel.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=320,
            showlegend=False, xaxis_tickangle=-30,
            xaxis_title="", yaxis_title="Row Count")
        st.plotly_chart(fig_funnel, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">📋 Cleaned Data Preview</p>', unsafe_allow_html=True)
        st.dataframe(ss.head(20), use_container_width=True, height=320)

    st.markdown("---")
    st.markdown('<p class="section-title">⬇️ Download Cleaned Data</p>', unsafe_allow_html=True)
    csv_data = ss.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download sales_summary.csv",
        data=csv_data,
        file_name="sales_summary.csv",
        mime="text/csv"
    )
