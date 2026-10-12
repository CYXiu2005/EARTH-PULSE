"""Validate and enrich the source earthquake table."""

import numpy as np
import pandas as pd


REQUIRED = {"Date", "Time", "Latitude", "Longitude", "Magnitude", "Depth", "ID"}


def clean_earthquakes(raw: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED.difference(raw.columns)
    if missing:
        raise ValueError(f"CSV 缺少必要字段: {', '.join(sorted(missing))}")

    df = raw.copy()
    # Keep all original columns, including their original spelling and values.
    date_text = df["Date"].astype("string").str.strip()
    time_text = df["Time"].astype("string").str.strip()
    df["datetime"] = pd.to_datetime(date_text + " " + time_text, format="mixed", errors="coerce", utc=True)
    # A few Kaggle rows repeat a complete ISO timestamp in both columns.
    bad_datetime = df["datetime"].isna()
    if bad_datetime.any():
        df.loc[bad_datetime, "datetime"] = pd.to_datetime(
            date_text.loc[bad_datetime], format="mixed", errors="coerce", utc=True)
    for source, target in (("Latitude", "latitude"), ("Longitude", "longitude"),
                           ("Magnitude", "magnitude"), ("Depth", "depth")):
        df[target] = pd.to_numeric(df[source], errors="coerce")

    valid = (df["datetime"].notna() & df["latitude"].between(-90, 90)
             & df["longitude"].between(-180, 180)
             & df["magnitude"].between(0, 10.5)
             & df["depth"].ge(0))
    df = df.loc[valid].copy()
    if "Type" in df:
        df = df.loc[df["Type"].astype("string").str.casefold().eq("earthquake")].copy()
    if "ID" in df:
        # Duplicate IDs represent the same event; retain the first source record.
        df = df.drop_duplicates(subset="ID", keep="first")

    df["year"] = df["datetime"].dt.year.astype(int)
    df["month"] = df["datetime"].dt.month.astype(int)
    df["depth_category"] = np.select(
        [df["depth"] <= 70, df["depth"] <= 300], ["Shallow", "Intermediate"], default="Deep")
    df["magnitude_category"] = pd.cut(
        df["magnitude"], bins=[-np.inf, 6, 7, 8, np.inf],
        labels=["5.5–6.0", "6.0–7.0", "7.0–8.0", "8.0+"], right=False).astype("string")
    return df.sort_values("datetime").reset_index(drop=True)
