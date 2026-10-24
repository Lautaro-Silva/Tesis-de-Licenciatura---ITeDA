"""Draw a text-free base map of Argentina for the colloquium slides.

The axes fill the whole figure, with an equirectangular projection whose
x axis is scaled by cos(LAT_REF). The TikZ macro \\geo{lon}{lat} in main.tex
uses exactly the same extent, so labels placed in LaTeX land on the right spot.

Run from the project root (needs data/raw/ne_*.geojson, Natural Earth):
    python scripts/mapa_argentina.py
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "figures" / "generadas"

# Keep in sync with \geo in main.tex
LON_MIN, LON_MAX = -76.0, -52.0
LAT_MIN, LAT_MAX = -56.0, -20.0
LAT_REF = -38.0
X_SCALE = np.cos(np.radians(LAT_REF))

COLOR_SEA = "#0F2A36"
COLOR_NEIGHBOR = "#1E4656"
COLOR_ARGENTINA = "#2F6F8C"
COLOR_BORDER = "#9CC3D3"
COLOR_HIGHLIGHT = "#F07E26"

HIGHLIGHTED_PROVINCES = ["Salta", "Mendoza", "San Juan"]


def polygons_of(geometry):
    """Return a list of exterior rings (lists of [lon, lat])."""
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"][0]]
    if geometry["type"] == "MultiPolygon":
        rings = []
        for polygon in geometry["coordinates"]:
            rings.append(polygon[0])
        return rings
    return []


def project(ring):
    points = np.array(ring)
    x = points[:, 0] * X_SCALE
    y = points[:, 1]
    return np.column_stack([x, y])


def draw_feature(axis, geometry, facecolor, edgecolor, linewidth):
    for ring in polygons_of(geometry):
        patch = Polygon(project(ring), closed=True, facecolor=facecolor,
                        edgecolor=edgecolor, linewidth=linewidth)
        axis.add_patch(patch)


def main():
    countries = json.loads((RAW / "ne_50m_admin_0_countries.geojson").read_text())
    provinces = json.loads((RAW / "ne_10m_admin_1_states_provinces.geojson").read_text())

    width_deg = (LON_MAX - LON_MIN) * X_SCALE
    height_deg = LAT_MAX - LAT_MIN
    figure_height_in = 6.0
    figure_width_in = figure_height_in * width_deg / height_deg

    figure = plt.figure(figsize=(figure_width_in, figure_height_in))
    axis = figure.add_axes([0, 0, 1, 1])
    axis.set_facecolor(COLOR_SEA)
    figure.patch.set_facecolor(COLOR_SEA)

    for feature in countries["features"]:
        name = feature["properties"]["ADMIN"]
        if name == "Argentina":
            continue
        # Islas Malvinas: drawn with the Argentine colour (Natural Earth lists
        # them as a separate admin-0 unit).
        if name == "Falkland Islands":
            draw_feature(axis, feature["geometry"], COLOR_ARGENTINA, COLOR_BORDER, 0.35)
            continue
        draw_feature(axis, feature["geometry"], COLOR_NEIGHBOR, COLOR_SEA, 0.6)

    for feature in provinces["features"]:
        if feature["properties"].get("admin") != "Argentina":
            continue
        name = feature["properties"].get("name")
        if name in HIGHLIGHTED_PROVINCES:
            facecolor = COLOR_HIGHLIGHT
        else:
            facecolor = COLOR_ARGENTINA
        draw_feature(axis, feature["geometry"], facecolor, COLOR_BORDER, 0.35)

    axis.set_xlim(LON_MIN * X_SCALE, LON_MAX * X_SCALE)
    axis.set_ylim(LAT_MIN, LAT_MAX)
    axis.set_aspect("equal")
    axis.axis("off")

    OUT.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUT / "mapa_argentina.pdf", facecolor=COLOR_SEA)
    figure.savefig(OUT / "mapa_argentina.png", dpi=250, facecolor=COLOR_SEA)
    print(f"aspect (w/h) = {width_deg / height_deg:.4f}")


if __name__ == "__main__":
    main()
