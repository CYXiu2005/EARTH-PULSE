"""Shared page frame and data availability handling."""

import streamlit as st

from components.filters import global_controls
from utils.constants import DATA_PATH, ROOT
from utils.data_loader import load_data


def frame(title: str, subtitle: str):
    st.set_page_config(page_title=f"{title} | EARTH PULSE", page_icon="🌐", layout="wide")
    css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    try:
        df = load_data()
    except Exception as exc:
        st.error(f"无法读取地震数据：{exc}")
        st.info(f"请确认 CSV 位于 `{DATA_PATH}`，并包含 Date、Time、Latitude、Longitude、Magnitude、Depth、ID 字段。")
        st.stop()
    if df is None:
        st.warning("尚未安装历史地震数据。")
        st.markdown(f"从 [Kaggle Earthquake Database](https://www.kaggle.com/datasets/usgs/earthquake-database) 下载 `database.csv`，放在 `{DATA_PATH}` 后刷新页面。")
        st.stop()
    if df.empty:
        st.warning("数据文件已读取，但清洗后没有可用的 Earthquake 记录。")
        st.stop()
    year_min, year_max = df["year"].min(), df["year"].max()
    st.markdown(f'''<div class="brand-header"><div><div class="brand-title">◉ &nbsp; EARTH PULSE</div>
    <div class="brand-subtitle">GLOBAL SEISMIC INTELLIGENCE</div></div>
    <div class="brand-dates">HISTORICAL DATA<br><strong>{year_min}–{year_max}</strong></div></div>''', unsafe_allow_html=True)
    st.markdown(f'<div class="page-kicker">SEISMIC INTELLIGENCE / {title}</div><h1>{title}</h1><p class="subtitle">{subtitle}</p>', unsafe_allow_html=True)
    filtered = global_controls(df, title)
    if filtered.empty:
        st.info("No Data · 当前筛选条件下没有地震记录，请调整全局筛选器。")
    return df, filtered


def footer():
    st.markdown('<div class="site-footer">DATA SOURCE: USGS / KAGGLE &nbsp; · &nbsp; HISTORICAL SEISMIC RECORDS &nbsp; · &nbsp; NOT REAL-TIME MONITORING</div>', unsafe_allow_html=True)
