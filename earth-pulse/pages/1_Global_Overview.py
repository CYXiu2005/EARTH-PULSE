"""Global overview of the filtered historical catalogue."""

from components.charts import annual_frequency, depth_distribution, magnitude_distribution
from components.kpi_cards import render_kpis
from components.maps import render_earthquake_globe, render_global_map
from components.sidebar import footer, frame
import streamlit as st


_, events = frame("GLOBAL SEISMIC OVERVIEW", "Explore historical earthquake activity across the globe.")
render_kpis(events)
left, right = st.columns([7, 3], gap="large")
with left:
    st.subheader("Global Seismic Map")
    map_mode = st.radio("Map view", ["3D Globe", "2D Map"], horizontal=True, key="overview_map_mode")
    if map_mode == "3D Globe":
        st.caption("Drag to rotate · Scroll to zoom · Hover to inspect an event")
        render_earthquake_globe(events, height=650)
    else:
        render_global_map(events, height=650)
with right:
    st.subheader("Magnitude Distribution")
    magnitude_distribution(events)
    st.subheader("Depth Distribution")
    depth_distribution(events)
st.subheader("Historical Earthquake Frequency")
annual_frequency(events)
footer()
