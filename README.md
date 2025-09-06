# Data-Viz Kit — Dataset-Agnostic Streamlit App

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://app-data-viz-kit-opgib23cnocdbbopamvmwm.streamlit.app/)
[![Made with Streamlit](https://img.shields.io/badge/Made%20with-Streamlit-red)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)

Upload any CSV, map columns to semantic roles (Time / Metric / Category / ID) in the sidebar, and instantly explore your data with reusable Plotly charts and quick insights — no code changes needed.

**Live demo:** https://app-data-viz-kit-opgib23cnocdbbopamvmwm.streamlit.app/  
**Repo:** https://github.com/mridul51204/streamlit-data-viz-kit

---

## ✨ Features

- Dataset-agnostic via role mapping (no hard-coded column names)
- Charts: Histogram, Category Mix (Pie/Bar with sum / mean / count), Box by Period, Trend over Time
- Top-K bucketing with “Other”
- Outlier trimming (IQR 1.5×) and log axes (X/Y) for skewed data
- Filters: category multi-select + numeric metric range
- Auto-insights bullets (summary stats, IQR, top categories, simple YoY delta)
- One-click HTML report export
- Handles Year-only time columns (e.g., 2019 → 2019-01-01)
- Privacy-friendly: files processed in memory during your session

---

## 🧰 Tech Stack

- Streamlit, Pandas, Plotly Express
- Pydantic (role schema), PyYAML
- Python 3.10+

---

## 🚀 Quick Start (Local)

    git clone https://github.com/mridul51204/streamlit-data-viz-kit
    cd streamlit-data-viz-kit

    python -m venv .venv
    # Windows: .venv\Scripts\activate
    # macOS/Linux:
    source .venv/bin/activate

    pip install -r requirements.txt
    streamlit run app/main.py

Open http://localhost:8501

---

## 🖱️ How to Use

1. Upload CSV (or use the built-in sample).
2. In Roles, map your columns:
   - Time (optional): a date column (or a Year column like 2019).
   - Metric (required): a numeric column (e.g., revenue, subscribers).
   - Category (optional): grouping column (e.g., product category, region).
   - ID (optional): identifier (e.g., order_id, channel_name).
3. In Options, choose: Top-K, outlier trim, time grain (Y/Q/M/W/D), bar vs pie, aggregation (sum/mean/count), log axes.
4. Use Filters to narrow the view.
5. Review Auto-insights and click Download HTML report to export.

Tip: If charts look empty, make sure Metric is numeric (not text like "12,345").  
Note: If you select Year as Time, it’s auto-converted to YYYY-01-01 for time-based charts.

---

## 🗂️ Project Structure

    streamlit-data-viz-kit/
    ├─ app/
    │  ├─ main.py           # Streamlit UI + wiring
    │  ├─ pipeline.py       # standardize/clean helpers (time parsing, outliers, top-K)
    │  ├─ charts.py         # plot recipes (hist, pie/bar, box, trend)
    │  ├─ insights.py       # quick auto-insights bullets
    │  └─ roles.py          # role schema + guessing helpers
    ├─ assets/              # (optional) screenshots or sample CSVs
    ├─ requirements.txt
    └─ README.md

---

## ☁️ Deployment

The app is live on Streamlit Community Cloud:  
https://app-data-viz-kit-opgib23cnocdbbopamvmwm.streamlit.app/

Deploy your own copy:

1. Go to https://share.streamlit.io → New app.
2. Repository: mridul51204/streamlit-data-viz-kit  
   Branch: main  
   Main file path: app/main.py
3. Deploy. Dependencies are auto-installed from requirements.txt.

(Optional) Mirror to Hugging Face Spaces (Streamlit template) for a backup host.

---

## 🧪 Troubleshooting

- Blank charts → pick a numeric Metric; map Time for time-based charts.
- Module not found (on deploy) → ensure requirements.txt exists at repo root.
- Large CSV → start with a smaller sample; the app processes in-memory.
- Same column used for multiple roles → supported (columns are copied, not renamed).

---

## 📸 Screenshots

<img width="2240" height="1400" alt="Screenshot (70)" src="https://github.com/user-attachments/assets/c5b17bc9-a738-43e7-a6d0-2d9a179c6360" />


---

## 📝 License

MIT. If you plan to distribute, add a LICENSE file with the MIT text.
