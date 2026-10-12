"""Cached loading of the local Kaggle CSV."""

from pathlib import Path

import pandas as pd
import streamlit as st

from utils.constants import DATA_PATH
from utils.preprocessing import clean_earthquakes


@st.cache_data(show_spinner="Loading historical earthquake records…")
def _read_clean(path: str, modified_ns: int) -> pd.DataFrame:
    _ = modified_ns  # Cache invalidation when the source file changes.
    return clean_earthquakes(pd.read_csv(path, low_memory=False))


def load_data(path: Path = DATA_PATH) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return _read_clean(str(path), path.stat().st_mtime_ns)
