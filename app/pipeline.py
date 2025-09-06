import pandas as pd

# ---------- Time parsing helpers ----------

def coerce_time_any(s: pd.Series) -> pd.Series:
    """
    Try to parse a column into pandas datetime.
    1) Standard datetime parsing
    2) Fallback: plain year (e.g., 2019) -> "2019-01-01"
    """
    # Attempt normal datetime
    t = pd.to_datetime(s, errors="coerce", utc=False, infer_datetime_format=True)
    if t.notna().sum() >= 0.5 * len(s):
        return t

    # Fallback: treat mostly-numeric column as years
    y = pd.to_numeric(s, errors="coerce")
    if y.notna().sum() >= 0.8 * len(s):
        # use Int64 to keep NaN; then build YYYY-01-01 strings
        return pd.to_datetime(y.astype("Int64").astype(str) + "-01-01", errors="coerce")

    # If all else fails, return whatever best-effort datetime produced
    return t


# ---------- Standardization / cleaning ----------

def derive_standard_columns(df: pd.DataFrame, roles: dict) -> pd.DataFrame:
    """
    Create internal, dataset-agnostic columns without renaming originals:
      _time   -> datetime-like (optional)
      _metric -> numeric (required)
      _cat    -> category/grouping (optional, as string)
      _id     -> identifier (optional, as string)
    Copies instead of renaming so the same source column can be used for multiple roles.
    """
    if roles is None or "metric" not in roles:
        raise ValueError("Roles must at least include a 'metric' column.")

    d = df.copy()

    # Time (optional)
    if roles.get("time") and roles["time"] in d.columns:
        d["_time"] = coerce_time_any(d[roles["time"]])

    # Metric (required)
    if roles["metric"] not in d.columns:
        raise ValueError(f"Metric column '{roles['metric']}' not found in data.")
    d["_metric"] = pd.to_numeric(d[roles["metric"]], errors="coerce")

    # Category (optional)
    if roles.get("category") and roles["category"] in d.columns:
        d["_cat"] = d[roles["category"]].astype(str)

    # ID (optional)
    if roles.get("id") and roles["id"] in d.columns:
        d["_id"] = d[roles["id"]].astype(str)

    return d


def topk_bucket(df: pd.DataFrame, k: int = 10) -> pd.DataFrame:
    """
    Keep the top-k categories by total _metric; bucket the rest as 'Other'.
    No-op if _cat is missing.
    """
    if "_cat" not in df.columns:
        return df
    d = df.copy()
    totals = d.groupby("_cat", as_index=False)["_metric"].sum()
    keep = set(totals.nlargest(k, "_metric")["_cat"])
    d["_cat_topk"] = d["_cat"].where(d["_cat"].isin(keep), "Other")
    return d


def trim_outliers_iqr(df: pd.DataFrame, k: float = 1.5) -> pd.DataFrame:
    """
    Remove rows outside [Q1 - k*IQR, Q3 + k*IQR] for _metric.
    Safe if metric has NaNs.
    """
    if "_metric" not in df.columns:
        return df
    d = df.copy()
    q1, q3 = d["_metric"].quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - k * iqr, q3 + k * iqr
    return d[d["_metric"].between(lo, hi)]
