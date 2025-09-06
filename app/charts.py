import pandas as pd
import plotly.express as px

# ---------- Core charts ----------

def hist(df: pd.DataFrame, bins: int = 30, log_y: bool = False):
    """
    Histogram of _metric with optional log Y.
    (Log X is toggled in main.py to avoid extra param churn.)
    """
    d = df.dropna(subset=["_metric"]) if "_metric" in df.columns else df.copy()
    fig = px.histogram(d, x="_metric", nbins=bins, marginal="rug", title="Distribution of Metric")
    if log_y:
        fig.update_yaxes(type="log")
    fig.update_layout(height=420)
    return fig


def pie_or_bar(df: pd.DataFrame, as_bar: bool = False, agg: str = "sum"):
    """
    Category mix chart.
    - Uses _cat_topk if present; else _cat.
    - If _metric is unusable or agg == 'count', falls back to row counts.
    - Returns a simple empty fig with a message if no category is mapped.
    """
    if "_cat_topk" not in df.columns and "_cat" not in df.columns:
        return px.bar(title="No category mapped")

    d = df.copy()
    if "_cat_topk" not in d.columns:
        d = d.rename(columns={"_cat": "_cat_topk"})

    # Decide whether to use metric or counts
    metric_ok = ("_metric" in d.columns) and d["_metric"].notna().any()
    if (not metric_ok) or (agg == "count"):
        agg_df = (
            d.groupby("_cat_topk", as_index=False)
             .size()
             .rename(columns={"size": "value"})
             .sort_values("value", ascending=False)
        )
        title = "Category Mix (row counts)"
    else:
        func = {"sum": "sum", "mean": "mean"}.get(agg, "sum")
        agg_df = (
            d.groupby("_cat_topk", as_index=False)["_metric"]
             .agg(func)
             .rename(columns={"_metric": "value"})
             .sort_values("value", ascending=False)
        )
        title = f"Category Mix ({agg})"

    if as_bar:
        fig = px.bar(agg_df, x="_cat_topk", y="value", title=title)
    else:
        fig = px.pie(agg_df, names="_cat_topk", values="value", hole=0.35, title=title)
    fig.update_layout(height=420)
    return fig


def box_by_period(df: pd.DataFrame, period: str = "Y", color_by: str = None):
    """
    Box plot of _metric by time period (Y/Q/M/W/D).
    Returns None if _time is missing.
    """
    if "_time" not in df.columns:
        return None
    d = df.dropna(subset=["_time"]).copy()
    d["_period"] = d["_time"].dt.to_period(period).dt.to_timestamp()
    # Only color if the column exists (e.g., _cat)
    color = color_by if (color_by and color_by in d.columns) else None
    fig = px.box(d, x="_period", y="_metric", color=color, title=f"Metric by {period} Period")
    fig.update_layout(height=420)
    return fig


def line_over_time(df: pd.DataFrame, time: str = "_time", metric: str = "_metric",
                   grain: str = "M", agg: str = "sum"):
    """
    Resampled time series line chart.
    - grain: "D","W","M","Q","Y"
    - agg: "sum" or "mean"
    Returns None if time is missing.
    """
    if time not in df.columns:
        return None
    d = df.dropna(subset=[time]).copy()
    if d.empty:
        return None
    # Ensure datetime index
    d = d.set_index(time)
    # Safe metric: if missing, bail gracefully
    if metric not in d.columns or not d[metric].notna().any():
        return None

    series = d[metric].resample(grain).agg({"sum": "sum", "mean": "mean"}.get(agg, "sum"))
    series = series.reset_index()
    fig = px.line(series, x=time, y=metric, markers=True,
                  title=f"{agg.title()} over time ({grain})")
    fig.update_layout(height=420)
    return fig
