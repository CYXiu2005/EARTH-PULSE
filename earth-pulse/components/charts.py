"""Plotly charts with one visual language."""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.constants import BG, CYAN, MAG_CATEGORIES, MAG_COLORS, MUTED, PANEL, TEXT, TEAL


def style(fig, height=300):
    fig.update_layout(
        height=height, margin=dict(l=16, r=16, t=25, b=22),
        paper_bgcolor=PANEL, plot_bgcolor=PANEL, font=dict(color=TEXT, size=12),
        hoverlabel=dict(bgcolor="#1A2A40", font_color=TEXT),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED)),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(130,148,171,.16)", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(130,148,171,.16)", zeroline=False)
    return fig


def show(fig, key=None):
    st.plotly_chart(fig, width="stretch", key=key, config={"displayModeBar": True, "scrollZoom": True})


def no_data(df):
    if df.empty:
        st.info("No Data · 当前选择没有可绘制的事件。")
        return True
    return False


def magnitude_distribution(df):
    if no_data(df): return
    counts = df["magnitude_category"].value_counts().reindex(MAG_CATEGORIES, fill_value=0)
    fig = go.Figure(go.Bar(x=counts.index, y=counts.values,
                           marker_color=[MAG_COLORS[x] for x in counts.index],
                           hovertemplate="%{x}: %{y:,} events<extra></extra>"))
    style(fig).update_layout(showlegend=False, yaxis_title="Events", xaxis_title="Magnitude")
    show(fig)


def depth_distribution(df):
    if no_data(df): return
    labels = ["Shallow", "Intermediate", "Deep"]
    counts = df["depth_category"].value_counts().reindex(labels, fill_value=0)
    fig = go.Figure(go.Bar(x=counts.index, y=counts.values,
                           marker_color=[CYAN, TEAL, "#FF9F50"],
                           hovertemplate="%{x}: %{y:,} events<extra></extra>"))
    style(fig).update_layout(showlegend=False, yaxis_title="Events", xaxis_title="Depth category")
    show(fig)


def annual_frequency(df):
    if no_data(df): return
    counts = df.groupby("year", observed=True).size().rename("Events").reset_index()
    fig = px.line(counts, x="year", y="Events", markers=True)
    fig.update_traces(line_color=CYAN, marker_color=TEAL, line_width=2,
                      hovertemplate="%{x}: %{y:,} events<extra></extra>")
    style(fig, 320).update_layout(xaxis_title="Year", yaxis_title="Events")
    show(fig)


def depth_time_scatter(df):
    if no_data(df): return
    fig = px.scatter(df, x="datetime", y="depth", color="magnitude_category",
                     color_discrete_map=MAG_COLORS, category_orders={"magnitude_category": MAG_CATEGORIES},
                     hover_data={"magnitude": ":.1f", "depth": ":.1f", "datetime": True},
                     opacity=.58, render_mode="webgl")
    style(fig, 360).update_layout(xaxis_title="Date", yaxis_title="Depth · km", legend_title_text="Magnitude")
    show(fig)


def magnitude_depth_scatter(df):
    if no_data(df): return
    fig = px.scatter(df, x="magnitude", y="depth", color="magnitude_category",
                     color_discrete_map=MAG_COLORS, category_orders={"magnitude_category": MAG_CATEGORIES},
                     hover_data={"datetime": True, "latitude": ":.3f", "longitude": ":.3f"},
                     opacity=.6, render_mode="webgl")
    style(fig, 350).update_layout(xaxis_title="Magnitude", yaxis_title="Depth · km", legend_title_text="Magnitude")
    show(fig)
