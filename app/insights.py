import pandas as pd

def bullets(df: pd.DataFrame) -> list[str]:
    pts = []
    if df["_metric"].notna().any():
        d = df["_metric"].dropna()
        pts.append(f"Count: {d.size:,} | Mean: {d.mean():.2f} | Median: {d.median():.2f} | Std: {d.std():.2f}")
        q1, q3 = d.quantile([0.25, 0.75])
        pts.append(f"IQR: {q1:.2f}–{q3:.2f} | Min–Max: {d.min():.2f}–{d.max():.2f}")
    if "_cat" in df.columns:
        top = df.groupby("_cat")["_metric"].sum().sort_values(ascending=False).head(3)
        if len(top):
            s = ", ".join([f"{k} ({v:.0f})" for k, v in top.items()])
            pts.append(f"Top categories by total metric: {s}")
    if "_time" in df.columns:
        by_y = (df.dropna(subset=["_time"])
                  .assign(_year=lambda x: x["_time"].dt.year)
                  .groupby("_year")["_metric"].sum().sort_index())
        if len(by_y) >= 2:
            delta = by_y.iloc[-1] - by_y.iloc[-2]
            pts.append(f"Last year vs previous year change: {delta:+.0f}")
    return pts
