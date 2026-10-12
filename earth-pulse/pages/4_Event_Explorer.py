"""Record inspection and time/space proximity search."""

import streamlit as st

from components.maps import render_global_map
from components.sidebar import footer, frame
from utils.analytics import nearby_events


_, events = frame("SEISMIC EVENT EXPLORER", "Inspect individual earthquake records and nearby events.")
st.subheader("Event Search & Filters")
if events.empty:
    footer()
    st.stop()
q1, q2, q3 = st.columns([2, 1, 1])
with q1: search = st.text_input("Event ID contains", placeholder="Search an ID")
with q2: date_range = st.date_input("Event dates", value=(events["datetime"].min().date(),
                                                    events["datetime"].max().date()))
with q3: min_mag = st.number_input("Magnitude at least", min_value=0.0, max_value=10.5,
                                   value=float(events["magnitude"].min()), step=.1)
min_depth, max_depth = float(events["depth"].min()), float(events["depth"].max())
depth_range = st.slider("Depth · km", min_value=0.0, max_value=max(1.0, max_depth + 1),
                        value=(min_depth, max_depth))
view = events.loc[events["magnitude"].ge(min_mag) & events["depth"].between(*depth_range)]
if len(date_range) == 2:
    view = view.loc[view["datetime"].dt.date.between(*date_range)]
if search:
    view = view.loc[view["ID"].astype(str).str.contains(search, case=False, regex=False, na=False)]
st.subheader("Earthquake Records")
st.caption(f"{len(view):,} records · Select a row to inspect its profile. Table columns can be sorted.")
display_cols = [c for c in ["datetime", "ID", "magnitude", "depth", "latitude", "longitude", "Source"] if c in view]
table = view[display_cols].sort_values("datetime", ascending=False).reset_index(drop=True)
selected = st.dataframe(table, hide_index=True, width="stretch", height=410,
                        on_select="rerun", selection_mode="single-row",
                        column_config={"magnitude": st.column_config.NumberColumn(format="%.1f"),
                                       "depth": st.column_config.NumberColumn(format="%.1f"),
                                       "latitude": st.column_config.NumberColumn(format="%.3f"),
                                       "longitude": st.column_config.NumberColumn(format="%.3f")})
st.download_button("Download Filtered Data · CSV", data=view.to_csv(index=False).encode("utf-8-sig"),
                   file_name="earth_pulse_filtered.csv", mime="text/csv", disabled=view.empty)
if view.empty:
    st.info("No Data · 当前事件搜索没有结果。")
    footer()
    st.stop()
row_index = selected.selection.rows[0] if selected.selection.rows else 0
row_index = min(row_index, len(table)-1)
event_id = table.iloc[row_index]["ID"]
event = view.loc[view["ID"].eq(event_id)].iloc[0]
st.subheader("Selected Event Profile")
profile, location = st.columns([2, 3], gap="large")
with profile:
    st.markdown(f"### M {event['magnitude']:.1f}")
    st.write(f"**Date / Time:** {event['datetime']:%Y-%m-%d %H:%M:%S} UTC")
    st.write(f"**Latitude / Longitude:** {event['latitude']:.3f}°, {event['longitude']:.3f}°")
    st.write(f"**Depth:** {event['depth']:.1f} km")
    st.write(f"**Event ID:** {event['ID']}")
    st.write(f"**Source:** {event.get('Source', '—')}")
with location:
    st.markdown("#### Selected Event Location Map")
    render_global_map(view.loc[view["ID"].eq(event_id)], height=320)
st.subheader("Nearby Events")
st.caption("Records within ±30 days and 300 km. Proximity alone does not identify aftershocks.")
nearby = nearby_events(events, event)
if nearby.empty:
    st.info("No nearby records under the current global filters.")
else:
    cols = ["datetime", "ID", "magnitude", "depth", "distance_km", "latitude", "longitude"]
    st.dataframe(nearby[cols], hide_index=True, width="stretch",
                 column_config={"distance_km": st.column_config.NumberColumn(format="%.1f km")})
footer()
