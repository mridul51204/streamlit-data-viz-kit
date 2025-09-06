import plotly.express as px
import pandas as pd

def hist(df: pd.DataFrame, bins: int = 30, log_y: bool = False):
    fig = px.histogram(df.dropna(subset=["_metric"]), x="_metric", nbins=bins, marginal="rug")
    if log_y: fig.update_yaxes(type="log")
    fig.update_layout(height=420, title="Distribution of Metric")
    return fig

def pie_or_bar(df: pd.DataFrame, as_bar: bool = False):
    if "_cat_topk" not in df.columns and "_cat" in df.columns:
        df = df.rename(columns={"_cat": "_cat_topk"})
    agg = df.groupby("_cat_topk", as_index=False)["_metric"].sum().sort_values("_metric", ascending=False)
    return (px.bar(agg, x="_cat_topk", y="_metric", title="Category Mix")
            if as_bar else
            px.pie(agg, names="_cat_topk", values="_metric", hole=0.35, title="Category Mix"))

def box_by_period(df: pd.DataFrame, period: str = "Y", color_by: str = None):
    if "_time" not in df.columns: return None
    d = df.dropna(subset=["_time"]).copy()
    d["_period"] = d["_time"].dt.to_period(period).dt.to_timestamp()
    fig = px.box(d, x="_period", y="_metric", color=(color_by if color_by in d.columns else None),
                 title=f"Metric by {period} Period")
    fig.update_layout(height=420)
    return fig
