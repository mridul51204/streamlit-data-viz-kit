# Data-Viz Kit — Dataset-Agnostic Streamlit App

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](<YOUR_APP_URL>)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](#license)
[![Made with: Streamlit](https://img.shields.io/badge/Made%20with-Streamlit-red)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)

Upload **any CSV**, map columns to semantic **roles** (Time / Metric / Category / ID), and get instant, reusable data visualizations + quick insights. The app is **schema-agnostic**: switch from YouTube subscribers to ecommerce sales or hospital wait times by just remapping columns—no code changes.

> Live demo: <YOUR_APP_URL>  
> Repo: <YOUR_REPO_URL>

---

## ✨ Features

- **Dataset-agnostic** via role mapping (no hard-coded column names)
- Charts: **Histogram**, **Category Mix** (Pie/Bar with sum/mean/count), **Box by Period**, **Trend over Time**
- **Top-K** bucketing with “Other” category
- **Outlier trimming** (IQR) and **log axes** for skewed data
- **Filters** (category multi-select, numeric range)
- **Auto-insights** bullets (summary stats, IQR, top categories, simple YoY change)
- **HTML report export** (one-click)
- Handles **Year-only** time columns (e.g., `2019` → `2019-01-01`)
- Works fully in browser; CSVs are processed in memory by Streamlit

---

## 🧰 Tech Stack

- **Streamlit**, **Pandas**, **Plotly Express**
- **Pydantic** (role schema), **PyYAML**
- Python **3.10+**

---

## 🚀 Quick Start (local)

```bash
git clone <YOUR_REPO_URL>
cd streamlit-data-viz-kit
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/main.py
