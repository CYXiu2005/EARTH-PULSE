"""Reusable metric cards."""

import math

import streamlit as st

from utils.analytics import summary


def render_kpis(df, prefix: str = ""):
    stats = summary(df)
    items = [
        ("TOTAL EVENTS", f"{stats['events']:,}"),
        ("MAXIMUM MAGNITUDE", f"M {stats['max_magnitude']:.1f}" if math.isfinite(stats["max_magnitude"]) else "—"),
        ("AVERAGE DEPTH", f"{stats['avg_depth']:.1f} km" if math.isfinite(stats["avg_depth"]) else "—"),
        ("MAJOR EARTHQUAKES · M≥7", f"{stats['major']:,}"),
    ]
    for col, (label, value) in zip(st.columns(4), items):
        col.markdown(f'<div class="kpi-card"><div class="kpi-label">{prefix}{label}</div><div class="kpi-value">{value}</div></div>', unsafe_allow_html=True)
