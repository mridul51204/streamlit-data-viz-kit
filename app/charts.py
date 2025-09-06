import plotly.express as px
import pandas as pd

def hist(df: pd.DataFrame, bins: int = 30, log_y: bool = False):
    fig = px.histogram(df.dropna(subset=["_metric"]), x="_metric", nbins=bins, marginal="rug")
    if log_y: fig.update_yaxes(type="log")
    fig.update_layout(height=420, title="Distribution of Metric")
    return fig

def pie_or_bar(df: pd.DataFrame, as_bar: bool = False, agg: str = "sum"):
    if "_cat_topk" not in df.columns and "_cat" not in df.columns:
        return px.bar(title="No category mapped")

    d = df.copy()
    if "_cat_topk" not in d.columns:
        d = d.rename(columns={"_cat": "_cat_topk"})

    # if metric unusable → fall back to row counts
    metric_ok = "_metric" in d.columns and d["_metric"].notna().any()
    if not metric_ok or agg == "count":
        agg_df = d.groupby("_cat_topk", as_index=False).size().rename(columns={"size": "value"})
        title = "Category Mix (row counts)"
    else:
        func = {"sum": "sum", "mean": "mean"}.get(agg, "sum")
        agg_df = d.groupby("_cat_topk", as_index=False)["_metric"].agg(func).rename(columns={"_metric": "value"})
        title = f"Category Mix ({agg})"

    return (px.bar(agg_df, x="_cat_topk", y="value", title=title)
            if as_bar else
            px.pie(agg_df, names="_cat_topk", values="value", hole=0.35, title=title))

def box_by_period(df: pd.DataFrame, period: str = "Y", color_by: str = None):
    if "_time" not in df.columns: return None
    d = df.dropna(subset=["_time"]).copy()
    d["_period"] = d["_time"].dt.to_period(period).dt.to_timestamp()
    fig = px.box(d, x="_period", y="_metric", color=(color_by if color_by in d.columns else None),
                 title=f"Metric by {period} Period")
    fig.update_layout(height=420)
    return fig
