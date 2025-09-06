# app/main.py  — full updated file

import streamlit as st
import pandas as pd
import yaml

from roles import Roles, guess_roles
from pipeline import derive_standard_columns, topk_bucket, trim_outliers_iqr
from charts import hist, pie_or_bar, box_by_period
# Trend chart is optional; if your charts.py doesn't have it yet, we won't break.
try:
    from charts import line_over_time
except Exception:
    line_over_time = None

from insights import bullets

st.set_page_config(page_title="Data-Viz Kit", layout="wide")

# ---------------------------
# Helpers
# ---------------------------
@st.cache_data(show_spinner=False)
def read_csv_cached(binary: bytes) -> pd.DataFrame:
    from io import BytesIO
    return pd.read_csv(BytesIO(binary))

def _idx_or_none(cols, name):
    if not name or name not in cols:
        return 0  # for selects with "<none>"
    return cols.get_loc(name) + 1

# ---------------------------
# Header
# ---------------------------
st.title("Dataset-Agnostic Data-Viz Kit")
st.write("Upload any CSV, map columns to roles, and explore patterns.")

# ---------------------------
# SIDEBAR: data input & options
# ---------------------------
with st.sidebar:
    st.header("1) Data")
    source = st.radio("Choose data source", ["Upload CSV", "Use sample (YouTube-like)"], index=0)

    df = None
    if source == "Upload CSV":
        upload = st.file_uploader("CSV file (≤ 200MB)", type=["csv"])
        if upload is not None:
            try:
                df = read_csv_cached(upload.getvalue())
            except Exception as e:
                st.error(f"Couldn't read CSV: {e}")
    else:
        # small synthetic sample so the app always works
        df = pd.DataFrame({
            "published_at": pd.date_range("2019-01-01", periods=300, freq="7D"),
            "subscriber_count": (pd.Series(range(300)).pow(1.05) * 120 + 5000).astype(int),
            "video_category": (["Tech","Music","Education","Comedy"] * 75)[:300],
            "channel_name": [f"Channel {i%30}" for i in range(300)]
        })

    if df is not None:
        st.caption(f"Loaded shape: {df.shape[0]} rows × {df.shape[1]} cols")

        with st.expander("Preview data & column types", expanded=False):
            st.dataframe(df.head())
            st.write(df.dtypes.astype(str))

    st.header("2) Roles")
    roles = None
    if df is not None:
        guessed = guess_roles(df.columns.tolist())

        time_col = st.selectbox(
            "Time (optional)",
            ["<none>"] + df.columns.tolist(),
            index=_idx_or_none(df.columns, guessed.get("time"))
        )
        metric_col = st.selectbox(
            "Metric (numeric)",
            df.columns.tolist(),
            index=(df.columns.get_loc(guessed.get("metric", df.columns[0])))
        )
        cat_col = st.selectbox(
            "Category (optional)",
            ["<none>"] + df.columns.tolist(),
            index=_idx_or_none(df.columns, guessed.get("category"))
        )
        id_col = st.selectbox(
            "ID (optional)",
            ["<none>"] + df.columns.tolist(),
            index=_idx_or_none(df.columns, guessed.get("id"))
        )

        roles = Roles(
            time=None if time_col == "<none>" else time_col,
            metric=metric_col,
            category=None if cat_col == "<none>" else cat_col,
            id=None if id_col == "<none>" else id_col
        ).model_dump()

    st.header("3) Options")
    topk = st.slider("Top-K categories", 3, 20, 10)
    outlier = st.checkbox("Trim outliers (IQR 1.5×)", value=False)
    period = st.selectbox("Time grain (used by box & trend)", ["Y", "Q", "M", "W", "D"], index=0)
    as_bar = st.checkbox("Use bar instead of pie", value=False)
    agg = st.selectbox("Category aggregation", ["sum", "mean", "count"], index=0)
    log_x = st.checkbox("Histogram: log X axis", value=False)
    log_y = st.checkbox("Histogram: log Y axis", value=False)

# ---------------------------
# MAIN: processing & charts
# ---------------------------
if df is None:
    st.info("Upload a CSV or select the sample to proceed.")
    st.stop()

# Derive internal standard columns (_time, _metric, _cat, _id)
try:
    d = derive_standard_columns(df, roles)
except Exception as e:
    st.error(f"Role mapping error: {e}")
    st.stop()

# Optional trimming
if outlier and "_metric" in d.columns:
    d = trim_outliers_iqr(d)

# Top-K bucketing (only if a category is mapped)
if "_cat" in d.columns:
    d = topk_bucket(d, k=topk)

# ---- Filters (shown in sidebar so they feel like controls)
with st.sidebar:
    st.header("4) Filters")
    # Category filter
    if "_cat" in d.columns:
        unique_cats = sorted(d["_cat"].dropna().unique().tolist())[:200]
        chosen_cats = st.multiselect("Keep categories", unique_cats, default=unique_cats[:min(10, len(unique_cats))])
    else:
        chosen_cats = None

    # Metric range filter (robust even if metric has NaNs)
    if "_metric" in d.columns and d["_metric"].notna().any():
        mn, mx = float(d["_metric"].min()), float(d["_metric"].max())
        metric_range = st.slider("Metric range", mn, mx, (mn, mx))
    else:
        metric_range = None

# Apply filters
if chosen_cats is not None and "_cat" in d.columns and len(chosen_cats) > 0:
    d = d[d["_cat"].isin(chosen_cats)]
if metric_range is not None and "_metric" in d.columns:
    d = d[d["_metric"].between(metric_range[0], metric_range[1])]

st.caption(f"Rows after cleaning/filters: {len(d):,}")

# ---- Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribution")
    fig_hist = hist(d, bins=30, log_y=log_y)
    if log_x:
        fig_hist.update_xaxes(type="log")
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    st.subheader("Category Mix")
    if ("_cat" in d.columns) or ("_cat_topk" in d.columns):
        try:
            fig_cat = pie_or_bar(d, as_bar=as_bar, agg=agg)  # works with updated charts.py
        except TypeError:
            # fallback to original signature if your charts.py hasn't been updated
            fig_cat = pie_or_bar(d, as_bar=as_bar)
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("No category mapped; select a Category in Roles to see this chart.")
        fig_cat = None

st.subheader("Box by Period")
fig_box = box_by_period(d, period=period, color_by="_cat" if "_cat" in d.columns else None)
if fig_box is not None:
    st.plotly_chart(fig_box, use_container_width=True)
else:
    st.info("No time column mapped; box-by-period needs a Time role.")

st.subheader("Trend over time")
if line_over_time and "_time" in d.columns:
    # pick agg that matches the category chart unless it's 'count'
    series_agg = "mean" if agg == "mean" else "sum"
    fig_trend = line_over_time(d, grain=period, agg=series_agg)
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.info("No time column mapped (or trend function not installed).")

# ---- Auto-insights
st.subheader("Auto-insights")
ins = bullets(d)
if ins:
    for b in ins:
        st.write("• " + b)
else:
    st.write("No insights to show yet.")

# ---- Report export
from plotly.io import to_html

parts = []
# include Plotly JS once
parts.append(fig_hist.to_html(full_html=False, include_plotlyjs="cdn") if fig_hist else "")
for fig in [fig_cat, fig_box]:
    if fig:
        parts.append(fig.to_html(full_html=False, include_plotlyjs=False))
# trend may not exist
try:
    if line_over_time and "_time" in d.columns and 'fig_trend' in locals() and fig_trend:
        parts.append(fig_trend.to_html(full_html=False, include_plotlyjs=False))
except Exception:
    pass

ins_html = "<h2>Insights</h2><ul>" + "".join(f"<li>{x}</li>" for x in ins) + "</ul>"
report_html = f"<h1>Data-Viz Kit Report</h1>{ins_html}" + "".join(parts)

st.download_button(
    "Download HTML report",
    data=report_html,
    file_name="report.html",
    mime="text/html"
)
