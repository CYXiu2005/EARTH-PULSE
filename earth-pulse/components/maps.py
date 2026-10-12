"""Reusable 2D geographic maps and a WebGL 3D earthquake globe."""

import json

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from PIL import Image, ImageDraw

from components.charts import no_data, show
from utils.constants import MAG_CATEGORIES, MAG_COLORS, MUTED, PANEL, REGIONS, ROOT, TEXT


def _map(df, *, region=None, height=540):
    if no_data(df): return
    fig = go.Figure()
    for category in MAG_CATEGORIES:
        subset = df.loc[df["magnitude_category"].eq(category)]
        if subset.empty: continue
        hover = [
            f"<b>{row.datetime:%Y-%m-%d %H:%M} UTC</b><br>Magnitude M {row.magnitude:.1f}"
            f"<br>Depth {row.depth:.1f} km<br>{row.latitude:.3f}°, {row.longitude:.3f}°"
            for row in subset.itertuples()
        ]
        fig.add_trace(go.Scattergeo(
            lat=subset["latitude"], lon=subset["longitude"], mode="markers", name=category,
            marker=dict(size=(subset["magnitude"] - 4.5).clip(lower=1) * 3.8,
                        color=MAG_COLORS[category], opacity=.72, line=dict(width=0)),
            text=hover, hovertemplate="%{text}<extra></extra>"))
    geo = dict(bgcolor=PANEL, showland=True, landcolor="#172B3B", showocean=True,
               oceancolor="#0B1828", showcountries=True, countrycolor="#304458",
               coastlinecolor="#304458", showcoastlines=True,
               projection_type="natural earth")
    if region:
        south, north, west, east = REGIONS[region]
        center_lon = ((west + ((east-west) % 360) / 2 + 180) % 360) - 180
        geo.update(projection_scale=3.2, center=dict(lat=(south+north)/2, lon=center_lon))
    fig.update_geos(**geo)
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor=PANEL,
                      font=dict(color=TEXT), legend=dict(orientation="h", y=0, x=.02,
                                                       bgcolor="rgba(16,27,43,.75)", font=dict(color=MUTED)))
    show(fig)


def render_global_map(df, height=540):
    _map(df, height=height)


def render_regional_map(df, region, height=450):
    _map(df, region=region, height=height)


def _xyz(latitude, longitude, radius=1.0):
    """Convert degrees to a point on a unit sphere."""
    lat, lon = np.broadcast_arrays(np.radians(latitude), np.radians(longitude))
    return (radius * np.cos(lat) * np.cos(lon),
            radius * np.cos(lat) * np.sin(lon),
            radius * np.sin(lat))


@st.cache_data(show_spinner=False)
def _globe_land_mask(width=241, height=121):
    """Rasterize bundled Natural Earth polygons onto the globe's surface grid."""
    source = ROOT / "assets" / "ne_110m_land.geojson"
    geojson = json.loads(source.read_text(encoding="utf-8"))
    canvas = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(canvas)
    for feature in geojson["features"]:
        geometry = feature["geometry"]
        polygons = ([geometry["coordinates"]] if geometry["type"] == "Polygon"
                    else geometry["coordinates"])
        for polygon in polygons:
            for ring_index, ring in enumerate(polygon):
                coords = np.asarray(ring, dtype=float)
                longitude = np.degrees(np.unwrap(np.radians(coords[:, 0])))
                x = (longitude + 180) / 360 * (width - 1)
                y = (90 - coords[:, 1]) / 180 * (height - 1)
                for shift in (-width + 1, 0, width - 1):
                    points = list(zip((x + shift).tolist(), y.tolist()))
                    draw.polygon(points, fill=255 if ring_index == 0 else 0)
    return np.asarray(canvas, dtype=np.uint8)[::-1, :] / 255.0


def _graticule():
    x, y, z = [], [], []
    for lat in range(-60, 90, 30):
        a, b, c = _xyz(lat, np.linspace(-180, 180, 145), 1.004)
        x.extend([*a, None]); y.extend([*b, None]); z.extend([*c, None])
    for lon in range(-180, 180, 30):
        a, b, c = _xyz(np.linspace(-90, 90, 73), lon, 1.004)
        x.extend([*a, None]); y.extend([*b, None]); z.extend([*c, None])
    return go.Scatter3d(x=x, y=y, z=z, mode="lines", hoverinfo="skip",
                        line=dict(color="rgba(130,180,200,.18)", width=1), showlegend=False)


def build_earthquake_globe(df, height=620):
    """Build an offline WebGL globe with land, graticule and earthquake markers."""
    latitudes = np.linspace(-90, 90, 121)
    longitudes = np.linspace(-180, 180, 241)
    lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)
    sx, sy, sz = _xyz(lat_grid, lon_grid)
    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=sx, y=sy, z=sz, surfacecolor=_globe_land_mask(),
        colorscale=[[0, "#0C2338"], [0.49, "#0C2338"], [0.5, "#285261"], [1, "#285261"]],
        cmin=0, cmax=1, showscale=False, hoverinfo="skip", name="Earth",
        lighting=dict(ambient=.72, diffuse=.65, specular=.22, roughness=.8, fresnel=.12),
        lightposition=dict(x=2, y=3, z=4)))
    fig.add_trace(_graticule())
    for category in MAG_CATEGORIES:
        subset = df.loc[df["magnitude_category"].eq(category)]
        if subset.empty:
            continue
        x, y, z = _xyz(subset["latitude"].to_numpy(), subset["longitude"].to_numpy(), 1.025)
        hover = [
            f"<b>{row.datetime:%Y-%m-%d %H:%M} UTC</b><br>Magnitude M {row.magnitude:.1f}"
            f"<br>Depth {row.depth:.1f} km<br>{row.latitude:.3f}°, {row.longitude:.3f}°"
            for row in subset.itertuples()
        ]
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z, mode="markers", name=category,
            marker=dict(size=(subset["magnitude"] - 4.5).clip(lower=1) * 2.6,
                        color=MAG_COLORS[category], opacity=.82, line=dict(width=0)),
            text=hover, hovertemplate="%{text}<extra></extra>"))
    axis = dict(visible=False, range=[-1.12, 1.12], showbackground=False)
    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=PANEL, font=dict(color=TEXT),
        scene=dict(xaxis=axis, yaxis=axis, zaxis=axis, aspectmode="cube",
                   bgcolor=PANEL, dragmode="orbit",
                   camera=dict(eye=dict(x=-2.1, y=.75, z=.7)), uirevision="earth-pulse-globe"),
        legend=dict(orientation="h", y=0, x=.02, bgcolor="rgba(16,27,43,.75)",
                    font=dict(color=MUTED)))
    return fig


def render_earthquake_globe(df, height=620):
    """Render a rotatable, zoomable globe; respects the caller's filtered data."""
    if no_data(df):
        return
    show(build_earthquake_globe(df, height=height), key="earthquake_globe")
