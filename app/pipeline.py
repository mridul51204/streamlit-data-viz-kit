import pandas as pd

def coerce_time(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, errors="coerce")

def derive_standard_columns(df: pd.DataFrame, roles: dict) -> pd.DataFrame:
    d = df.copy()
    mapping = {}
    if roles.get("time"): mapping[roles["time"]] = "_time"
    mapping[roles["metric"]] = "_metric"
    if roles.get("category"): mapping[roles["category"]] = "_cat"
    if roles.get("id"): mapping[roles["id"]] = "_id"
    d = d.rename(columns=mapping)

    if "_time" in d.columns:
        d["_time"] = coerce_time(d["_time"])
    d["_metric"] = pd.to_numeric(d["_metric"], errors="coerce")

    return d

def topk_bucket(df: pd.DataFrame, k: int = 10) -> pd.DataFrame:
    if "_cat" not in df.columns: return df
    totals = df.groupby("_cat", as_index=False)["_metric"].sum()
    keep = set(totals.nlargest(k, "_metric")["_cat"])
    d = df.copy()
    d["_cat_topk"] = d["_cat"].where(d["_cat"].isin(keep), "Other")
    return d

def trim_outliers_iqr(df: pd.DataFrame, k: float = 1.5) -> pd.DataFrame:
    q1, q3 = df["_metric"].quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - k*iqr, q3 + k*iqr
    return df[df["_metric"].between(lo, hi)]
