from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Invoice Performance",
    page_icon="I",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container { max-width: 1440px; padding-top: 2rem; }
    [data-testid="stMetricValue"] { color: #1d3557; }
    h1, h2, h3 { color: #1d3557; }
    </style>
    """,
    unsafe_allow_html=True,
)

CSV_FILE = Path(__file__).with_name("invoices_clean.csv")


def format_currency(value):
    return f"Rp {value / 1_000_000:,.1f}M"


@st.cache_data
def load_data(path):
    data = pd.read_csv(path, parse_dates=["date", "due_date"])
    data["line_total"] = pd.to_numeric(data["line_total"], errors="coerce").fillna(0)
    data["month_start"] = data["date"].dt.to_period("M").dt.to_timestamp()
    return data


if not CSV_FILE.exists():
    st.error(f"CSV file not found: {CSV_FILE}")
    st.stop()


df = load_data(CSV_FILE)

st.title("Invoice Performance")
st.caption("Local BI dashboard powered by invoices_clean.csv")

with st.sidebar:
    st.header("Filters")
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    selected_dates = st.date_input("Invoice date", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    selected_statuses = st.multiselect("Payment status", sorted(df["status"].unique()), default=sorted(df["status"].unique()))
    selected_clients = st.multiselect("Client", sorted(df["client"].unique()), default=sorted(df["client"].unique()))

if len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date = end_date = selected_dates[0]

filtered = df[
    df["date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date))
    & df["status"].isin(selected_statuses)
    & df["client"].isin(selected_clients)
].copy()

invoice_level = (
    filtered.groupby("invoice_no", as_index=False)
    .agg(
        invoice_date=("date", "min"),
        status=("status", "first"),
        client=("client", "first"),
        due_date=("due_date", "min"),
        invoice_total=("line_total", "sum"),
    )
)

revenue = invoice_level["invoice_total"].sum()
invoice_count = invoice_level["invoice_no"].nunique()
paid_revenue = invoice_level.loc[invoice_level["status"].eq("PAID"), "invoice_total"].sum()
overdue_revenue = invoice_level.loc[invoice_level["status"].eq("OVERDUE"), "invoice_total"].sum()

kpi_columns = st.columns(4)
kpi_columns[0].metric("Total invoiced", format_currency(revenue))
kpi_columns[1].metric("Invoices", f"{invoice_count:,}")
kpi_columns[2].metric("Paid revenue", format_currency(paid_revenue))
kpi_columns[3].metric("Overdue revenue", format_currency(overdue_revenue))

if invoice_level.empty:
    st.info("No invoices match the selected filters.")
    st.stop()

monthly = filtered.groupby("month_start", as_index=False)["line_total"].sum()
status_revenue = invoice_level.groupby("status", as_index=False)["invoice_total"].sum()
client_revenue = invoice_level.groupby("client", as_index=False)["invoice_total"].sum().sort_values("invoice_total")
overdue = invoice_level[invoice_level["status"].eq("OVERDUE")].sort_values("invoice_total", ascending=False)

chart_columns = st.columns(2)
with chart_columns[0]:
    monthly_chart = px.area(monthly, x="month_start", y="line_total", markers=True, title="Monthly invoiced revenue")
    monthly_chart.update_traces(line_color="#1d3557", fillcolor="rgba(168, 218, 220, 0.45)")
    monthly_chart.update_layout(yaxis_title="Revenue", xaxis_title=None)
    st.plotly_chart(monthly_chart, use_container_width=True)

with chart_columns[1]:
    status_chart = px.bar(status_revenue, x="status", y="invoice_total", color="status", title="Revenue by payment status")
    status_chart.update_layout(showlegend=False, yaxis_title="Revenue", xaxis_title=None)
    st.plotly_chart(status_chart, use_container_width=True)

chart_columns = st.columns(2)
with chart_columns[0]:
    client_chart = px.bar(client_revenue, x="invoice_total", y="client", orientation="h", title="Revenue by client")
    client_chart.update_layout(yaxis_title=None, xaxis_title="Revenue")
    st.plotly_chart(client_chart, use_container_width=True)

with chart_columns[1]:
    st.subheader("Top overdue invoices")
    if overdue.empty:
        st.success("No overdue invoices match the selected filters.")
    else:
        overdue_display = overdue.head(10).copy()
        overdue_display["invoice_total"] = overdue_display["invoice_total"].map(format_currency)
        overdue_display["invoice_date"] = overdue_display["invoice_date"].dt.strftime("%Y-%m-%d")
        overdue_display["due_date"] = overdue_display["due_date"].dt.strftime("%Y-%m-%d")
        st.dataframe(
            overdue_display[["invoice_no", "client", "invoice_date", "due_date", "invoice_total"]],
            hide_index=True,
            use_container_width=True,
        )

st.subheader("Invoice detail")
detail_columns = ["invoice_no", "date", "due_date", "status", "client", "description", "qty", "unit_price", "line_total"]
st.dataframe(filtered[detail_columns].sort_values("date", ascending=False), hide_index=True, use_container_width=True)
