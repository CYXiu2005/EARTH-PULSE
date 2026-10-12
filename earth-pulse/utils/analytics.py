"""Statistics and geographical queries, independent of Streamlit."""

import numpy as np
import pandas as pd

from utils.constants import REGIONS


def summary(df: pd.DataFrame) -> dict:
    return {
        "events": len(df),
        "max_magnitude": df["magnitude"].max() if len(df) else np.nan,
        "avg_depth": df["depth"].mean() if len(df) else np.nan,
        "major": int(df["magnitude"].ge(7).sum()),
    }


def region_events(df: pd.DataFrame, name: str) -> pd.DataFrame:
    south, north, west, east = REGIONS[name]
    lon = df["longitude"].between(west, east) if west <= east else (
        df["longitude"].ge(west) | df["longitude"].le(east))
    return df.loc[df["latitude"].between(south, north) & lon]


def nearby_events(df: pd.DataFrame, event: pd.Series, days: int = 30, km: int = 300) -> pd.DataFrame:
    """Find other records within a time window and great-circle radius."""
    candidate = df.loc[df["datetime"].between(
        event["datetime"] - pd.Timedelta(days=days),
        event["datetime"] + pd.Timedelta(days=days))].copy()
    if "ID" in candidate and pd.notna(event.get("ID")):
        candidate = candidate.loc[candidate["ID"] != event["ID"]]
    else:
        candidate = candidate.loc[candidate.index != event.name]
    lat1, lon1 = np.radians([float(event["latitude"]), float(event["longitude"])])
    lat2 = np.radians(candidate["latitude"].to_numpy(dtype=float))
    lon2 = np.radians(candidate["longitude"].to_numpy(dtype=float))
    a = np.sin((lat2-lat1)/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin((lon2-lon1)/2)**2
    candidate["distance_km"] = 6371.0088 * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
    return candidate.loc[candidate["distance_km"] <= km].sort_values("distance_km")
