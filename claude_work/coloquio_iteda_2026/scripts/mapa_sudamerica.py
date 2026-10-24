"""Draw a text-free base map of South America for the "impact" slide.

Same projection as mapa_argentina.py (equirectangular, x scaled by
cos(LAT_REF)); the TikZ macro \\geoSA in sections/00_preambulo.tex uses the
same extent, so labels placed in LaTeX land on the right spot.

Run from the project root:
    python scripts/mapa_sudamerica.py
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

# Keep in sync with \geoSA in sections/00_preambulo.tex
LON_MIN, LON_MAX = -82.0, -32.0
LAT_MIN, LAT_MAX = -56.0, 6.0
LAT_REF = -25.0
X_SCALE = np.cos(np.radians(LAT_REF))

COLOR_SEA = "#0F2A36"
COLOR_LAND = "#1E4656"
COLOR_ARGENTINA = "#2F6F8C"
COLOR_BRAZIL = "#285E77"
COLOR_BORDER = "#5E8FA3"


def polygons_of(geometry):
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
    return np.column_stack([points[:, 0] * X_SCALE, points[:, 1]])


def main():
    countries = json.loads((RAW / "ne_50m_admin_0_countries.geojson").read_text())

    width_deg = (LON_MAX - LON_MIN) * X_SCALE
    height_deg = LAT_MAX - LAT_MIN
    figure_height_in = 6.0
    figure = plt.figure(figsize=(figure_height_in * width_deg / height_deg, figure_height_in))
    axis = figure.add_axes([0, 0, 1, 1])
    axis.set_facecolor(COLOR_SEA)

    for feature in countries["features"]:
        name = feature["properties"]["ADMIN"]
        if name in ("Argentina", "Falkland Islands"):
            facecolor = COLOR_ARGENTINA
        elif name == "Brazil":
            facecolor = COLOR_BRAZIL
        else:
            facecolor = COLOR_LAND
        for ring in polygons_of(feature["geometry"]):
            axis.add_patch(Polygon(project(ring), closed=True, facecolor=facecolor,
                                   edgecolor=COLOR_BORDER, linewidth=0.4))

    axis.set_xlim(LON_MIN * X_SCALE, LON_MAX * X_SCALE)
    axis.set_ylim(LAT_MIN, LAT_MAX)
    axis.set_aspect("equal")
    axis.axis("off")

    OUT.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUT / "mapa_sudamerica.pdf", facecolor=COLOR_SEA)
    print(f"aspect (w/h) = {width_deg / height_deg:.5f}")


if __name__ == "__main__":
    main()
