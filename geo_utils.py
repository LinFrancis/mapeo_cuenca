"""
geo_utils.py — Detección automática de cuenca/subcuenca/subsubcuenca
"""

import streamlit as st
from pathlib import Path
from config import CUENCAS_SHP, SUBCUENCAS_SHP, SUBSUBCUENCAS_SHP


@st.cache_resource(show_spinner="Cargando geometrías de cuencas...")
def load_shapefiles():
    import geopandas as gpd
    result = {"cuencas": None, "subcuencas": None, "subsubcuencas": None}
    for key, path in [("cuencas", CUENCAS_SHP), ("subcuencas", SUBCUENCAS_SHP), ("subsubcuencas", SUBSUBCUENCAS_SHP)]:
        if Path(path).exists():
            try:
                gdf = gpd.read_file(path)
                if gdf.crs and gdf.crs.to_epsg() != 4326:
                    gdf = gdf.to_crs(epsg=4326)
                result[key] = gdf
            except Exception as e:
                print(f"Error cargando {key}: {e}")
    return result


def identify_cuenca(lat, lon):
    from shapely.geometry import Point
    point = Point(lon, lat)
    result = {"cuenca": "No identificada", "subcuenca": "No identificada", "subsubcuenca": "No identificada"}
    shps = load_shapefiles()
    name_cols = ["NOM_CUEN", "NOM_CUENCA", "NOMBRE", "nombre", "Name", "NAME", "NOM_SUBE", "NOM_SUBC", "NOM_SUB", "NOM_SUBSU", "NOM_DGA"]
    for level, gdf_key in [("cuenca", "cuencas"), ("subcuenca", "subcuencas"), ("subsubcuenca", "subsubcuencas")]:
        gdf = shps.get(gdf_key)
        if gdf is None:
            continue
        try:
            matches = gdf[gdf.geometry.contains(point)]
            if len(matches) > 0:
                row = matches.iloc[0]
                for col in name_cols:
                    if col in row.index and row[col]:
                        result[level] = str(row[col]).strip()
                        break
                else:
                    for col in row.index:
                        if col != "geometry" and isinstance(row[col], str) and row[col].strip():
                            result[level] = row[col].strip()
                            break
        except Exception:
            pass
    return result


def get_cuencas_geojson():
    shps = load_shapefiles()
    gdf = shps.get("cuencas")
    if gdf is None:
        return None
    try:
        s = gdf.copy()
        s["geometry"] = s.geometry.simplify(0.01, preserve_topology=True)
        return s
    except Exception:
        return None
