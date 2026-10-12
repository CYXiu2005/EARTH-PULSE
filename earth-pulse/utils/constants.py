"""Shared scientific dashboard settings."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "database.csv"

BG = "#070D18"
PANEL = "#101B2B"
TEXT = "#E8F0F7"
MUTED = "#8294AB"
CYAN = "#4FC3F7"
TEAL = "#45D6C0"
RED = "#FF654F"
MAG_COLORS = {
    "5.5–6.0": CYAN,
    "6.0–7.0": "#F4D35E",
    "7.0–8.0": "#FF9F50",
    "8.0+": RED,
}
MAG_CATEGORIES = list(MAG_COLORS)
DEPTH_CATEGORIES = ["Shallow", "Intermediate", "Deep"]

# Approximate bounding boxes, not tectonic boundaries. Longitude may cross the dateline.
REGIONS = {
    "Japan & Kuril": (25, 55, 125, 160),
    "Indonesia": (-12, 8, 95, 141),
    "Chile & Peru": (-57, 1, -82, -66),
    "Alaska & Aleutian": (45, 72, 170, -125),
    "Mediterranean": (28, 47, -11, 43),
}
