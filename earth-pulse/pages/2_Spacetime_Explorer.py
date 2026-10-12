"""Year controlled evolution of earthquake records."""

import streamlit as st

from components.charts import annual_frequency, depth_time_scatter, magnitude_distribution
from components.kpi_cards import render_kpis
from components.maps import render_earthquake_globe, render_global_map
from components.sidebar import footer, frame


_, events = frame("SPATIOTEMPORAL EXPLORER", "Discover how recorded seismic events evolve over time.")
st.subheader("Time Controller")
if events.empty:
    footer()
    st.stop()
years = sorted(events["year"].unique().tolist())
year = st.slider("Year", min_value=int(years[0]), max_value=int(years[-1]),
                 value=int(years[-1]), step=1, key="spacetime_year")
mode = st.radio("Playback Mode", ["Single Year", "Cumulative"], horizontal=True)
selected = events.loc[events["year"].eq(year) if mode == "Single Year" else events["year"].le(year)]
st.caption(f"Showing {len(selected):,} earthquake records · {mode} through {year}")
render_kpis(selected)
st.subheader("Seismic Events by Year")
map_mode = st.radio("Map view", ["3D Globe", "2D Map"], horizontal=True, key="spacetime_map_mode")
if map_mode == "3D Globe":
    st.caption("Drag to rotate · Scroll to zoom · Hover to inspect an event")
    render_earthquake_globe(selected)
else:
    render_global_map(selected)
left, right = st.columns(2, gap="large")
with left:
    st.subheader("Annual Event Frequency")
    annual_frequency(selected)
with right:
    st.subheader("Magnitude Distribution")
    magnitude_distribution(selected)
st.subheader("Depth vs Time")
depth_time_scatter(selected)
footer()
