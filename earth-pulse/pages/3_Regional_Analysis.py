"""Approximate geographic region views and comparison."""

import streamlit as st

from components.charts import annual_frequency, depth_distribution, magnitude_depth_scatter
from components.kpi_cards import render_kpis
from components.maps import render_regional_map
from components.sidebar import footer, frame
from utils.analytics import region_events, summary
from utils.constants import REGIONS


_, events = frame("REGIONAL SEISMIC ANALYSIS", "Investigate seismic characteristics across geographic regions.")
region = st.selectbox("Region", list(REGIONS))
regional = region_events(events, region)
st.caption("Regional boxes are approximate geographic filters, not tectonic boundaries.")
render_kpis(regional)
st.subheader("Regional Epicenter Map")
render_regional_map(regional, region)
left, right = st.columns(2, gap="large")
with left:
    st.subheader("Annual Event Frequency")
    annual_frequency(regional)
    st.subheader("Depth Distribution")
    depth_distribution(regional)
with right:
    st.subheader("Magnitude vs Depth")
    magnitude_depth_scatter(regional)
st.subheader("Compare Two Regions")
a_col, b_col = st.columns(2)
with a_col: a = st.selectbox("Region A", list(REGIONS), index=0)
with b_col: b = st.selectbox("Region B", list(REGIONS), index=1)
sa, sb = summary(region_events(events, a)), summary(region_events(events, b))
rows = []
for label, key in [("Total Events", "events"), ("Maximum Magnitude", "max_magnitude"),
                   ("Average Depth · km", "avg_depth"), ("Major Earthquakes · M≥7", "major")]:
    def display(value):
        if key in ("max_magnitude", "avg_depth"):
            return "—" if value != value else f"{value:.1f}"
        return f"{value:,}"
    rows.append({"Metric": label, f"Region A · {a}": display(sa[key]), f"Region B · {b}": display(sb[key])})
st.dataframe(rows, hide_index=True, width="stretch")
footer()
