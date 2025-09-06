import pandas as pd

def coerce_time_any(s: pd.Series) -> pd.Series:
    t = pd.to_datetime(s, errors="coerce")
    if t.notna().sum() >= 0.5 * len(s):
        return t
    y = pd.to_numeric(s, errors="coerce")
    if y.notna().sum() >= 0.8 * len(s):
        return pd.to_datetime(y.astype("Int64").astype(str) + "-01-01", errors="coerce")
    return t

def derive_standard_columns(df: pd.DataFrame, roles: dict) -> pd.DataFrame:
    d = df.copy()
    if roles.get("time") in d.columns:
        d["_time"] = coerce_time_any(d[roles["time"]])
    d["_metric"] = pd.to_numeric(d[roles["metric"]], errors="coerce")
    if roles.get("category") in d.columns:
        d["_cat"] = d[roles["category"]].astype(str)
    if roles.get("id") in d.columns:
        d["_id"] = d[roles["id"]].astype(str)
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
