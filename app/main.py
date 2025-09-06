import streamlit as st
import pandas as pd
import yaml

from roles import Roles, guess_roles
from pipeline import derive_standard_columns, topk_bucket, trim_outliers_iqr
from charts import hist, pie_or_bar, box_by_period
from insights import bullets

st.set_page_config(page_title="Data-Viz Kit", layout="wide")

st.title("Dataset-Agnostic Data-Viz Kit")
st.write("Upload any CSV, map columns to roles, and explore patterns.")

# --- SIDEBAR: data input ---
with st.sidebar:
    st.header("1) Data")
    src = st.radio("Choose data source", ["Upload CSV", "Use sample (YouTube-like)"])
    if src == "Upload CSV":
        f = st.file_uploader("CSV file", type=["csv"])
        if f:
            df = pd.read_csv(f)
        else:
            df = None
    else:
        st.info("Generating a small synthetic sample to try the app.")
        df = pd.DataFrame({
            "published_at": pd.date_range("2019-01-01", periods=300, freq="7D"),
            "subscriber_count": (pd.Series(range(300)).pow(1.05) * 120 + 5000).astype(int),
            "video_category": (["Tech","Music","Education","Comedy"] * 75)[:300],
            "channel_name": [f"Channel {i%30}" for i in range(300)]
        })

    if df is not None:
        st.caption(f"Loaded shape: {df.shape[0]} rows × {df.shape[1]} cols")

    st.header("2) Roles")
    if df is not None:
        guessed = guess_roles(df.columns.tolist())
        time_col = st.selectbox("Time (optional)", ["<none>"] + df.columns.tolist(),
                                index=(df.columns.get_loc(guessed.get("time","<none>"))+1 if guessed.get("time") in df.columns else 0))
        metric_col = st.selectbox("Metric (numeric)", df.columns.tolist(),
                                  index=(df.columns.get_loc(guessed.get("metric", df.columns[0]))))
        cat_col = st.selectbox("Category (optional)", ["<none>"] + df.columns.tolist(),
                               index=(df.columns.get_loc(guessed.get("category","<none>"))+1 if guessed.get("category") in df.columns else 0))
        id_col = st.selectbox("ID (optional)", ["<none>"] + df.columns.tolist(),
                              index=(df.columns.get_loc(guessed.get("id","<none>"))+1 if guessed.get("id") in df.columns else 0))

        roles = Roles(
            time=None if time_col=="<none>" else time_col,
            metric=metric_col,
            category=None if cat_col=="<none>" else cat_col,
            id=None if id_col=="<none>" else id_col
        ).model_dump()

    st.header("3) Options")
    topk = st.slider("Top-K categories", 3, 20, 10)
    outlier = st.checkbox("Trim outliers (IQR 1.5×)", value=False)
    period = st.selectbox("Time grain (for box plot)", ["Y","Q","M","W","D"])
    as_bar = st.checkbox("Use bar instead of pie", value=False)
    log_y = st.checkbox("Histogram: log Y axis", value=False)

# --- MAIN: processing & charts ---
if df is None:
    st.info("Upload a CSV or select the sample to proceed.")
    st.stop()

try:
    d = derive_standard_columns(df, roles)
except Exception as e:
    st.error(f"Role mapping error: {e}")
    st.stop()

if outlier:
    d = trim_outliers_iqr(d)

if "_cat" in d.columns:
    d = topk_bucket(d, k=topk)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Distribution")
    st.plotly_chart(hist(d, bins=30, log_y=log_y), use_container_width=True)
with col2:
    st.subheader("Category Mix")
    st.plotly_chart(pie_or_bar(d, as_bar=as_bar), use_container_width=True)

st.subheader("Box by Period")
bp = box_by_period(d, period=period, color_by="_cat" if "_cat" in d.columns else None)
if bp is not None:
    st.plotly_chart(bp, use_container_width=True)
else:
    st.info("No time column mapped; box-by-period needs a time role.")

st.subheader("Auto-insights")
for b in bullets(d):
    st.write("• " + b)
