"""Persistent global filter state shared by every Streamlit page."""

import pandas as pd
import streamlit as st

from utils.constants import MAG_CATEGORIES


def defaults(df: pd.DataFrame) -> dict:
    return {
        "start": df["datetime"].min().date(),
        "end": df["datetime"].max().date(),
        "min_mag": float(df["magnitude"].min()),
        "max_mag": float(df["magnitude"].max()),
        "min_depth": float(df["depth"].min()),
        "max_depth": float(df["depth"].max()),
        "categories": MAG_CATEGORIES.copy(),
    }


def filter_events(df: pd.DataFrame, state: dict) -> pd.DataFrame:
    dates = df["datetime"].dt.date
    mask = (dates.ge(state["start"]) & dates.le(state["end"])
            & df["magnitude"].between(state["min_mag"], state["max_mag"])
            & df["depth"].between(state["min_depth"], state["max_depth"])
            & df["magnitude_category"].isin(state["categories"]))
    return df.loc[mask]


def global_controls(df: pd.DataFrame, page: str) -> pd.DataFrame:
    base = defaults(df)
    if "applied_filters" not in st.session_state:
        st.session_state.applied_filters = base
    applied = st.session_state.applied_filters
    # Page-specific draft keys avoid Streamlit discarding widget state on navigation.
    page = page.lower().replace(" ", "_")
    keys = {name: f"draft_{page}_{name}" for name in base}
    revision_key = f"revision_{page}"
    if st.session_state.get(revision_key) != st.session_state.get("filter_revision", 0):
        for name, key in keys.items():
            st.session_state[key] = applied[name]
        st.session_state[keys["start"] + "_range"] = (applied["start"], applied["end"])
        st.session_state[keys["min_depth"] + "_range"] = (applied["min_depth"], applied["max_depth"])
        st.session_state[revision_key] = st.session_state.get("filter_revision", 0)

    with st.sidebar:
        st.markdown('<div class="side-brand">◉ &nbsp; GLOBAL CONTROL CENTER</div>', unsafe_allow_html=True)
        with st.form(f"filters_{page}"):
            dates = st.date_input("Date Range",
                                  min_value=base["start"], max_value=base["end"], key=keys["start"] + "_range")
            min_mag = st.number_input("Minimum Magnitude", min_value=0.0, max_value=10.5,
                                      step=0.1, format="%.1f", key=keys["min_mag"])
            max_mag = st.number_input("Maximum Magnitude", min_value=0.0, max_value=10.5,
                                      step=0.1, format="%.1f", key=keys["max_mag"])
            depth = st.slider("Depth Range · km", min_value=0.0,
                              max_value=max(1.0, float(round(base["max_depth"] + 1))),
                              key=keys["min_depth"] + "_range")
            cats = st.multiselect("Magnitude Category", MAG_CATEGORIES, key=keys["categories"])
            left, right = st.columns(2)
            apply = left.form_submit_button("Apply Filters", width="stretch", type="primary")
            reset = right.form_submit_button("Reset Filters", width="stretch")
        if reset:
            st.session_state.applied_filters = base
            st.session_state.filter_revision = st.session_state.get("filter_revision", 0) + 1
            st.rerun()
        if apply:
            if len(dates) != 2 or min_mag > max_mag or depth[0] > depth[1]:
                st.error("请选择完整日期范围，并确保最小值不大于最大值。")
            else:
                st.session_state.applied_filters = {
                    "start": dates[0], "end": dates[1],
                    "min_mag": min_mag, "max_mag": max_mag,
                    "min_depth": depth[0], "max_depth": depth[1], "categories": cats,
                }
                st.session_state.filter_revision = st.session_state.get("filter_revision", 0) + 1
                st.rerun()
        st.caption("Filters apply across all pages. Data are historical, not live.")
    return filter_events(df, st.session_state.applied_filters)
